import os
import tempfile
import threading
import time
import wave
from pathlib import Path

import numpy as np
from dotenv import load_dotenv
from openwakeword.model import Model


load_dotenv(Path(__file__).resolve().parent / "app" / ".env")


SAMPLE_RATE = 16000
CHUNK = 1280  # 80 ms of audio; the size openwakeword expects


def _with_model_download(loader, model_names):
    """openwakeword >= 0.6 does not ship its model files. Download on first use."""
    try:
        return loader()
    except Exception:
        import openwakeword.utils

        openwakeword.utils.download_models(model_names)
        return loader()


class WakeWordDetector:
    SAMPLE_RATE = SAMPLE_RATE
    CHUNK_SIZE = CHUNK
    WAKE_MODEL = "hey_jarvis"

    def __init__(self, threshold=0.50, cooldown=2.0):
        self.threshold = float(os.getenv("WAKE_THRESHOLD", threshold))
        self.vad_threshold = float(os.getenv("VAD_THRESHOLD", "0.5"))
        self.cooldown = cooldown
        self.last_detection = 0.0
        self.last_score_log = 0.0
        # Set WAKE_DEBUG=1 to print scores while tuning the threshold.
        self.debug = os.getenv("WAKE_DEBUG", "0") == "1"

        self.model = _with_model_download(
            lambda: Model(
                wakeword_models=[self.WAKE_MODEL],
                inference_framework="onnx",
            ),
            [self.WAKE_MODEL],
        )

        # Silero voice-activity detector (ships with openwakeword).
        from openwakeword.vad import VAD

        self.vad = _with_model_download(VAD, [self.WAKE_MODEL])

    def process_audio(self, audio):
        predictions = self.model.predict(audio)
        now = time.monotonic()
        if self.debug and predictions:
            top_word, top_score = max(predictions.items(), key=lambda item: item[1])
            if now - self.last_score_log >= 2.0:
                print(f"Wake score: {top_word}={top_score:.3f}", flush=True)
                self.last_score_log = now

        current_time = time.time()

        # Prevent repeated detections
        if current_time - self.last_detection < self.cooldown:
            return None

        for wake_word, score in predictions.items():
            if score >= self.threshold:
                self.last_detection = current_time
                return wake_word

        return None

    def is_speech(self, audio):
        """True if this 80 ms int16 chunk contains speech (Silero VAD)."""
        score = float(self.vad.predict(audio, frame_size=640))
        return score >= self.vad_threshold

    def reset(self):
        """Clear streaming state so old audio never leaks into the next detection."""
        self.model.reset()
        self.vad.reset_states()


def _prepare_for_stt(chunks):
    """Join int16 chunks and lift quiet audio without ever clipping it."""
    audio = np.concatenate(chunks).astype(np.float32) / 32768.0
    peak = float(np.max(np.abs(audio))) if audio.size else 0.0
    if 0.0 < peak < 0.7:
        audio *= min(0.9 / peak, 10.0)
    return np.clip(audio * 32767.0, -32768, 32767).astype(np.int16)


class WakeWordService:
    # Stop recording after this much continuous silence (once speech has started).
    SILENCE_SECONDS = float(os.getenv("SILENCE_SECONDS", "2.0"))
    # Sarvam's REST speech-to-text only accepts clips under 30 s.
    MAX_RECORDING_SECONDS = 25.0
    # Give up if nobody starts speaking after the wake word.
    NO_SPEECH_TIMEOUT_SECONDS = 6.0
    # Total voiced audio needed before a recording counts as "speech".
    MIN_SPEECH_SECONDS = 0.4
    # Silence kept after the last word when trimming the clip for transcription.
    TAIL_SECONDS = 0.5

    def __init__(self):
        self.detector = None
        self.thread = None
        self.stop_event = threading.Event()
        self.callbacks = []
        self.recording_lock = threading.Lock()
        self.audio_lock = threading.Lock()
        self._pending = np.empty(0, dtype=np.int16)
        self.finalizing = False
        self._reset_recording_state()

    # ---- state helpers -------------------------------------------------

    def _reset_recording_state(self):
        self.recording = False
        self.recording_chunks = []
        self.recorded_samples = 0
        self.speech_samples = 0
        self.silence_samples = 0
        self.last_speech_end = 0

    @property
    def ready(self):
        return self.detector is not None

    def add_callback(self, callback):
        self.callbacks.append(callback)

    def remove_callback(self, callback):
        if callback in self.callbacks:
            self.callbacks.remove(callback)

    def _publish(self, payload):
        for callback in list(self.callbacks):
            try:
                callback(payload)
            except Exception as error:
                print(f"Wake callback error: {error}", flush=True)

    # ---- recording control ---------------------------------------------

    def _begin_recording(self):
        with self.recording_lock:
            if self.recording or self.finalizing or self.detector is None:
                return False
            self._reset_recording_state()
            self.recording = True
        print("Listening for speech...", flush=True)
        return True

    def start_manual_recording(self):
        if not self._begin_recording():
            return False
        self._publish({"type": "status", "status": "recording"})
        return True

    def _cancel_recording(self, reason):
        with self.recording_lock:
            if not self.recording:
                return
            self._reset_recording_state()
        self.detector.reset()
        print("No speech detected.", flush=True)
        self._publish({"type": "status", "status": "listening", "reason": reason})

    def _finish_recording(self, reason="Silence detected"):
        with self.recording_lock:
            if not self.recording or self.finalizing:
                return
            self.finalizing = True
            # Drop the trailing silence, keeping a short tail after the last word.
            keep_samples = self.last_speech_end + int(self.TAIL_SECONDS * SAMPLE_RATE)
            keep_chunks = -(-keep_samples // CHUNK)  # ceiling division
            chunks = self.recording_chunks[:keep_chunks]
            self._reset_recording_state()

        self.detector.reset()
        print(f"{reason}. Processing speech...", flush=True)

        threading.Thread(
            target=self._transcribe_and_publish,
            args=(chunks,),
            name="sarvam-transcription",
            daemon=True,
        ).start()

    def _record_chunk(self, chunk):
        # Timing is counted in audio samples, not wall-clock time, so a burst of
        # delayed audio can never end (or extend) a recording by mistake.
        if self.recorded_samples == 0:
            self.detector.vad.reset_states()
        is_speech = self.detector.is_speech(chunk)

        action = None
        with self.recording_lock:
            if not self.recording:
                return
            self.recording_chunks.append(chunk.copy())
            self.recorded_samples += chunk.size
            if is_speech:
                self.speech_samples += chunk.size
                self.silence_samples = 0
                self.last_speech_end = self.recorded_samples
            else:
                self.silence_samples += chunk.size

            elapsed = self.recorded_samples / SAMPLE_RATE
            has_speech = self.speech_samples >= self.MIN_SPEECH_SECONDS * SAMPLE_RATE
            if has_speech and self.silence_samples >= self.SILENCE_SECONDS * SAMPLE_RATE:
                action = "finish"
            elif elapsed >= self.MAX_RECORDING_SECONDS:
                action = "max_length" if has_speech else "cancel"
            elif not has_speech and elapsed >= self.NO_SPEECH_TIMEOUT_SECONDS:
                action = "cancel"

        if action == "finish":
            self._finish_recording()
        elif action == "max_length":
            self._finish_recording("Maximum recording length reached")
        elif action == "cancel":
            self._cancel_recording("no_speech")

    # ---- audio input ---------------------------------------------------

    def process_external_audio(self, pcm_bytes):
        """Feed 16 kHz mono int16 little-endian audio from the browser."""
        if not pcm_bytes or self.detector is None:
            return

        usable_bytes = len(pcm_bytes) - (len(pcm_bytes) % 2)
        if usable_bytes == 0:
            return

        with self.audio_lock:
            incoming = np.frombuffer(pcm_bytes[:usable_bytes], dtype="<i2")
            # The browser sends 4096-sample blocks, which are not a multiple of
            # 1280. Carry the remainder over so the detector never hears gaps.
            samples = np.concatenate((self._pending, incoming))
            usable = (samples.size // CHUNK) * CHUNK
            self._pending = samples[usable:]

            for offset in range(0, usable, CHUNK):
                chunk = samples[offset:offset + CHUNK]
                if self.recording:
                    self._record_chunk(chunk)
                elif not self.finalizing:
                    self._detect(chunk)

    def _detect(self, chunk):
        wake_word = self.detector.process_audio(chunk)
        if not wake_word:
            return
        print(f">>> Wake word detected: {wake_word}", flush=True)
        if self._begin_recording():
            self._publish({
                "type": "wake",
                "wakeWord": "Hey Jarvis" if "jarvis" in str(wake_word).lower() else str(wake_word),
            })
            self._publish({"type": "status", "status": "recording"})

    # ---- speech to text ------------------------------------------------

    def _transcribe(self, wav_path):
        from sarvamai import SarvamAI

        api_key = os.getenv("SARVAM_API_KEY") or os.getenv("SARVAM_API_SUBSCRIPTION_KEY")
        if not api_key:
            raise RuntimeError("SARVAM_API_KEY is not configured")

        client = SarvamAI(api_subscription_key=api_key)
        with open(wav_path, "rb") as audio_file:
            response = client.speech_to_text.transcribe(
                file=audio_file,
                model=os.getenv("SARVAM_STT_MODEL", "saaras:v4"),
                language_code="ml-IN",
                mode="transcribe",
            )
        return str(getattr(response, "transcript", "") or "").strip()

    def _transcribe_and_publish(self, chunks):
        temp_path = None
        try:
            if not chunks:
                return

            pcm = _prepare_for_stt(chunks)
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_path = temp_file.name
            with wave.open(temp_path, "wb") as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(SAMPLE_RATE)
                wav_file.writeframes(pcm.tobytes())

            self._publish({"type": "status", "status": "transcribing"})
            transcript = self._transcribe(temp_path)

            if transcript:
                print(f"Sarvam output: {transcript}", flush=True)
                self._publish({"type": "transcript", "transcript": transcript})
            else:
                print("Sarvam output: No transcript returned", flush=True)
                self._publish({
                    "type": "status",
                    "status": "listening",
                    "reason": "no_transcript",
                })
        except Exception as error:
            print(f"Sarvam transcription error: {error}", flush=True)
            self._publish({
                "type": "status",
                "status": "error",
                "message": f"Transcription failed: {error}",
            })
        finally:
            if temp_path:
                try:
                    os.unlink(temp_path)
                except OSError:
                    pass
            with self.recording_lock:
                self.finalizing = False
            self._publish({"type": "status", "status": "listening"})

    # ---- lifecycle -----------------------------------------------------

    def start(self):
        if self.thread and self.thread.is_alive():
            return

        self.stop_event.clear()

        def run():
            try:
                self.detector = WakeWordDetector(
                    threshold=float(os.getenv("WAKE_THRESHOLD", "0.50")),
                    cooldown=2.0,
                )
                self._publish({"type": "status", "status": "listening"})
                self.stop_event.wait()
            except Exception as error:
                print(f"Wake-word listener error: {error}", flush=True)
                self._publish({"type": "status", "status": "error", "message": str(error)})

        self.thread = threading.Thread(target=run, name="wake-word-listener", daemon=True)
        self.thread.start()

    def stop(self):
        self.stop_event.set()


wake_word_service = WakeWordService()


def main():
    wake_word_service.add_callback(
        lambda payload: print(payload) if payload.get("type") == "wake" else None
    )
    wake_word_service.start()

    try:
        while not wake_word_service.stop_event.wait(timeout=0.1):
            pass
    except KeyboardInterrupt:
        print("\nStopping wake-word detector...")
        wake_word_service.stop()


if __name__ == "__main__":
    main()
