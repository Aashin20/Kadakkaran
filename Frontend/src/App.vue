<script setup>
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'
import AppHeader from './components/AppHeader.vue'
import BottomNav from './components/BottomNav.vue'
import CartBar from './components/CartBar.vue'
import HomeView from './components/HomeView.vue'
import SalesView from './components/SalesView.vue'
import StockView from './components/StockView.vue'
import CreditView from './components/CreditView.vue'
import MoreView from './components/MoreView.vue'
import CheckoutSheet from './components/CheckoutSheet.vue'
import ReceiptSheet from './components/ReceiptSheet.vue'
import AddProductSheet from './components/AddProductSheet.vue'
import AdjustSheet from './components/AdjustSheet.vue'
import CustomerSheet from './components/CustomerSheet.vue'
import NewCustomerSheet from './components/NewCustomerSheet.vue'
import ChatPanel from './components/ChatPanel.vue'
import RestockSheet from './components/RestockSheet.vue'
import { state, loadProducts, loadStock, loadCredits, loadStockHistory, loadSalesSummary } from './stores/shop.js'
import { startWakeWord, stopWakeWord } from './stores/shop.js'

const mainEl = ref(null)
const scrolled = ref(false)
const onScroll = () => { scrolled.value = (mainEl.value?.scrollTop || 0) > 4 }
const openVoiceAssistant = () => {
  state.chatOpen = true
  startWakeWord()
}
onMounted(() => {
  startWakeWord()
  loadProducts().then(() => Promise.all([loadStock(), loadStockHistory(), loadSalesSummary()]))
  loadCredits()
})
onBeforeUnmount(stopWakeWord)
watch(
  () => `${state.tab}|${state.sub}`,
  () => { if (mainEl.value) mainEl.value.scrollTop = 0; scrolled.value = false },
)
</script>

<template>
  <div class="app-shell">
    <AppHeader :scrolled="scrolled" />

    <main ref="mainEl" class="app-main" @scroll.passive="onScroll">
      <HomeView v-if="state.tab === 'home'" />
      <SalesView v-else-if="state.tab === 'sales'" />
      <StockView v-else-if="state.tab === 'stock'" />
      <CreditView v-else-if="state.tab === 'credit'" />
      <MoreView v-else />
    </main>

    <CartBar />
    <BottomNav />

    <button
      class="voice-orb"
      :style="{ '--audio-level': state.audioLevel }"
      :class="{ listening: state.wakeListening || state.wakeTriggered, detected: state.wakeTriggered }"
      aria-label="വോയ്സ് സഹായി"
      @click="openVoiceAssistant"
    >
      <span class="orb-waves">
        <i></i><i></i><i></i><i></i><i></i>
      </span>
    </button>

    <CheckoutSheet />
    <ReceiptSheet />
    <AddProductSheet />
    <AdjustSheet />
    <CustomerSheet />
    <NewCustomerSheet />
    <ChatPanel />
    <RestockSheet />

    <Transition name="toast">
      <div v-if="state.toast" class="toast-pop" role="status">{{ state.toast }}</div>
    </Transition>
  </div>
</template>

<style scoped>
.voice-orb {
  --audio-level: 0;
  position: absolute;
  right: 18px;
  bottom: calc(84px + env(safe-area-inset-bottom, 0px) + 16px);
  z-index: 40;
  display: grid;
  place-items: center;
  width: 68px;
  height: 68px;
  border: 1px solid rgba(255, 255, 255, .58);
  border-radius: 50%;
  overflow: visible;
  background: #111827;
  box-shadow:
    0 10px 26px rgba(34, 64, 140, .24),
    inset 0 0 16px rgba(255, 255, 255, .08);
  transition: transform .16s ease, box-shadow .16s ease;
}
.voice-orb:active { transform: scale(.94); }
.voice-orb::before {
  content: '';
  position: absolute;
  inset: 7px;
  border-radius: 50%;
  background:
    radial-gradient(ellipse at 28% 58%, rgba(255, 85, 196, .95) 0 8%, transparent 31%),
    radial-gradient(ellipse at 72% 38%, rgba(82, 179, 255, .95) 0 10%, transparent 34%),
    radial-gradient(ellipse at 58% 78%, rgba(113, 105, 255, .95) 0 9%, transparent 32%),
    conic-gradient(from 180deg, #6f7cff, #68d7ff, #72efc5, #ff77c8, #886cff);
  filter: saturate(1.25);
  box-shadow: inset 0 0 10px rgba(255, 255, 255, .38);
  animation: siri-morph 3.8s ease-in-out infinite alternate;
}
.voice-orb::after {
  content: '';
  position: absolute;
  inset: -5px;
  border: 1px solid rgba(119, 161, 255, .18);
  border-radius: 50%;
  animation: siri-halo 2.4s ease-out infinite;
}
.orb-waves {
  position: relative;
  z-index: 2;
  display: flex;
  align-items: center;
  gap: 3px;
  height: 28px;
}
.orb-waves i {
  width: 3px;
  height: 8px;
  border-radius: 999px;
  background: rgba(255, 255, 255, .9);
  box-shadow: 0 0 6px rgba(255, 255, 255, .8);
  animation: siri-wave 1.1s ease-in-out infinite;
}
.orb-waves i:nth-child(2) { animation-delay: -.16s; }
.orb-waves i:nth-child(3) { animation-delay: -.32s; }
.orb-waves i:nth-child(4) { animation-delay: -.48s; }
.orb-waves i:nth-child(5) { animation-delay: -.64s; }
@keyframes siri-wave {
  0%, 100% { height: calc(7px + var(--audio-level) * 17px); opacity: .72; }
  50% { height: calc(10px + var(--audio-level) * 18px); opacity: 1; }
}
@keyframes siri-morph {
  0% { transform: scale(calc(.94 + var(--audio-level) * .14)) rotate(0deg); border-radius: 48% 52% 58% 42%; }
  50% { transform: scale(calc(1.04 + var(--audio-level) * .18)) rotate(8deg); border-radius: 58% 42% 45% 55%; }
  100% { transform: scale(calc(.98 + var(--audio-level) * .16)) rotate(-7deg); border-radius: 42% 58% 52% 48%; }
}
@keyframes siri-halo {
  0% { transform: scale(.82); opacity: 0; }
  25% { opacity: .8; }
  100% { transform: scale(1.18); opacity: 0; }
}
.voice-orb.listening {
  animation: orb-breathe 2.4s ease-in-out infinite;
  box-shadow:
    0 0 0 8px rgba(88, 169, 255, .12),
    0 12px 28px rgba(62, 92, 170, .32),
    inset 0 0 12px rgba(255, 255, 255, .18);
}
@keyframes orb-breathe {
  50% { transform: scale(1.04); box-shadow: 0 0 0 13px rgba(88, 169, 255, .08), 0 12px 28px rgba(62, 92, 170, .32); }
}
@media (prefers-reduced-motion: reduce) {
  .voice-orb.listening { animation: none; }
  .voice-orb::before, .voice-orb::after, .orb-waves i { animation: none; }
}
</style>
