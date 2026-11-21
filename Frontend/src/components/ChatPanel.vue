<script setup>
import { ref, watch } from 'vue'
import AppIcon from './AppIcon.vue'
import BaseSheet from './BaseSheet.vue'
import { state, ask, mic, suggestions, scrollMsgs } from '../stores/shop.js'

const box = ref(null)
watch(() => state.msgs.length, () => scrollMsgs(box.value))
watch(() => state.chatOpen, (v) => { if (v) scrollMsgs(box.value) })
</script>

<template>
  <BaseSheet :open="state.chatOpen" title="കടക്കാരൻ AI" tall @close="state.chatOpen = false">
    <div ref="box" class="messages" aria-live="polite">
      <div v-for="(m, i) in state.msgs" :key="i" class="message" :class="m.r">
        <div class="bubble">{{ m.t }}</div>
      </div>
      <p v-if="state.listening" class="listening">ശ്രദ്ധിക്കുന്നു…</p>
    </div>

    <template #footer>
      <div class="foot">
        <div class="suggestions">
          <button v-for="s in suggestions" :key="s" class="suggest" @click="ask(s)">{{ s }}</button>
        </div>
        <div class="composer">
          <button class="mic" :class="{ active: state.listening }" aria-label="വോയ്സ്" @click="mic">
            <AppIcon name="mic" :size="20" />
          </button>
          <input v-model="state.inp" class="input" placeholder="മലയാളത്തിൽ പറയൂ" aria-label="സന്ദേശം" @keyup.enter="ask(state.inp)" />
          <button class="send" aria-label="അയക്കുക" :disabled="!state.inp.trim()" @click="ask(state.inp)">
            <AppIcon name="send" :size="18" />
          </button>
        </div>
      </div>
    </template>
  </BaseSheet>
</template>

<style scoped>
.messages { display: flex; flex-direction: column; gap: 8px; padding: 4px 0 8px; }
.message { display: flex; }
.message.u { justify-content: flex-end; }
.bubble { max-width: 82%; padding: 9px 14px; border-radius: 18px; font-size: 17px; line-height: 1.4; white-space: pre-line; }
.message.b .bubble { background: var(--fill); border-bottom-left-radius: 6px; }
.message.u .bubble { background: var(--accent-fill); color: #fff; border-bottom-right-radius: 6px; }
.listening { font-size: 15px; color: var(--text-2); padding-left: 4px; }

.foot { width: 100%; display: flex; flex-direction: column; gap: 10px; }
.suggestions { display: flex; gap: 8px; overflow-x: auto; scrollbar-width: none; }
.suggestions::-webkit-scrollbar { display: none; }
.suggest { flex: none; min-height: 36px; padding: 0 14px; border-radius: 18px; background: var(--accent-tint); color: var(--accent); font-size: 15px; font-weight: 500; white-space: nowrap; }
.composer { display: flex; align-items: center; gap: 8px; }
.mic, .send { display: grid; place-items: center; width: 44px; height: 44px; flex: none; border-radius: 50%; }
.mic { background: var(--fill); color: var(--text-2); }
.mic.active { background: var(--red); color: #fff; }
.input { flex: 1; min-width: 0; height: 44px; padding: 0 16px; border: 0; border-radius: 22px; background: var(--fill); font-size: 17px; }
.input::placeholder { color: var(--text-2); }
.send { background: var(--accent-fill); color: #fff; }
.send:disabled { opacity: .35; }
</style>
