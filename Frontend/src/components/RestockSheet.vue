<script setup>
import AppIcon from './AppIcon.vue'
import BaseSheet from './BaseSheet.vue'
import { state, buyList, receiveBuy, refreshBuy } from '../stores/shop.js'

const open = () => {
  refreshBuy()
  state.restockOpen = true
}

defineExpose({ open })
</script>

<template>
  <BaseSheet :open="state.restockOpen" title="റീസ്റ്റോക്ക്" subtitle="വാങ്ങേണ്ട സാധനങ്ങളും അഭിപ്രായ അളവും" @close="state.restockOpen = false">
    <div v-if="buyList.length" class="group restock-list">
      <label v-for="item in buyList" :key="item.id" class="row restock-row" :class="{ checked: item.got }">
        <input v-model="item.got" type="checkbox" class="sr-only" />
        <span class="check" aria-hidden="true"><AppIcon name="check" :size="14" :stroke="3" /></span>
        <span class="row-main">
          <span class="row-title">{{ item.n }}</span>
          <span class="row-sub">ഇപ്പോഴത്തെ സ്റ്റോക്ക് {{ item.stock }}</span>
        </span>
        <span class="restock-qty">
          <small>ചേർക്കേണ്ടത്</small>
          <span class="stepper">
            <button class="round" :aria-label="`${item.n} കുറയ്ക്കുക`" @click.prevent="item.qty = Math.max(1, item.qty - 1)">
              <AppIcon name="minus" :size="16" :stroke="2.4" />
            </button>
            <b class="num">{{ item.qty }}</b>
            <button class="round" :aria-label="`${item.n} കൂട്ടുക`" @click.prevent="item.qty++">
              <AppIcon name="plus" :size="16" :stroke="2.4" />
            </button>
          </span>
        </span>
      </label>
    </div>
    <div v-else class="group">
      <p class="empty">റീസ്റ്റോക്ക് ചെയ്യേണ്ട സാധനങ്ങൾ ഒന്നുമില്ല</p>
    </div>

    <template #footer>
      <button class="btn primary block" :disabled="!buyList.some((item) => item.got)" @click="receiveBuy">
        തെരഞ്ഞെടുത്തവ സ്റ്റോക്കിൽ ചേർക്കുക
      </button>
    </template>
  </BaseSheet>
</template>

<style scoped>
.restock-list { margin-top: 4px; }
.restock-row { min-height: 72px; }
.restock-row.checked .row-main { opacity: .55; }
.check {
  flex: none;
  display: grid;
  place-items: center;
  width: 26px;
  height: 26px;
  border-radius: 50%;
  border: 1.5px solid var(--text-3);
  color: transparent;
}
.restock-row:has(input:checked) .check { background: var(--accent-fill); border-color: var(--accent-fill); color: #fff; }
.restock-row:has(input:focus-visible) .check { outline: 2px solid var(--accent); outline-offset: 2px; }
.restock-row .row-main { transition: opacity .25s ease, color .25s ease; }
.restock-row .row-title { position: relative; display: block; width: fit-content; max-width: 100%; }
.restock-row .row-title::after {
  content: '';
  position: absolute;
  left: 0;
  top: 52%;
  width: 100%;
  height: 2px;
  border-radius: 2px;
  background: var(--text-2);
  transform: scaleX(0);
  transform-origin: left center;
  transition: transform .38s cubic-bezier(.22, 1, .36, 1);
}
.restock-row.checked .row-main { opacity: .55; }
.restock-row.checked .row-title::after { transform: scaleX(1); }
.restock-row.checked .restock-qty { opacity: .55; }
.restock-row .row-sub { display: block; }
.restock-row.checked .check { animation: check-pop .32s cubic-bezier(.22, 1.35, .36, 1); }
.restock-qty { transition: opacity .25s ease; }
.restock-row .restock-qty { flex: none; }
.restock-qty { flex: none; display: flex; flex-direction: column; align-items: flex-end; gap: 4px; }
.restock-qty small { font-size: 12px; color: var(--text-2); }
.restock-qty b { min-width: 28px; text-align: center; }

@keyframes check-pop {
  0% { transform: scale(.72); }
  55% { transform: scale(1.12); }
  100% { transform: scale(1); }
}
@media (prefers-reduced-motion: reduce) {
  .restock-row .row-title::after,
  .restock-row .row-main,
  .restock-qty { transition: none; }
  .restock-row.checked .check { animation: none; }
}
</style>
