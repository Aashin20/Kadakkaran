<script setup>
import BaseSheet from './BaseSheet.vue'
import { state, cartItems, cartCount, payable, makeBill, saveOrder } from '../stores/shop.js'

const modes = ['പണം', 'UPI', 'കടം', 'ഓർഡർ']
const isOrder = () => state.mode === 'ഓർഡർ'
const submit = () => (isOrder() ? saveOrder() : makeBill())
</script>

<template>
  <BaseSheet :open="state.checkout" title="ബിൽ" :subtitle="`${cartCount} സാധനങ്ങൾ`" @close="state.checkout = false">
    <div class="group">
      <div v-for="i in cartItems" :key="i.id" class="row">
        <div class="row-main">
          <div class="row-title">{{ i.n }}</div>
          <div class="row-sub num">{{ i.q }} × ₹{{ i.price }}</div>
        </div>
        <span class="row-value num">₹{{ i.q * i.price }}</span>
      </div>
    </div>

    <div class="group gap">
      <label class="form-row">
        <span>ഡിസ്കൗണ്ട് (₹)</span>
        <input v-model.number="state.disc" class="num" type="number" inputmode="decimal" min="0" placeholder="0" @focus="$event.target.select()" />
      </label>
      <div class="form-row total">
        <span>ആകെ</span>
        <strong class="num">₹{{ payable }}</strong>
      </div>
      <label class="form-row pdf-option">
        <span>PDF ബിൽ ഉണ്ടാക്കുക</span>
        <input v-model="state.generatePdf" type="checkbox" />
      </label>
    </div>

    <div class="section-head"><h3 class="section-title">പേയ്മെന്റ്</h3></div>
    <div class="segmented" role="tablist">
      <button v-for="m in modes" :key="m" :class="{ on: state.mode === m }" @click="state.mode = m">{{ m }}</button>
    </div>

    <div v-if="state.mode === 'കടം'" class="group gap">
      <label class="form-row">
        <span>ആർക്ക്</span>
        <select v-model="state.creditTo">
          <option :value="null" disabled>തിരഞ്ഞെടുക്കുക</option>
          <option v-for="c in state.customers" :key="c.id" :value="c.id">{{ c.n }}</option>
        </select>
      </label>
    </div>
    <div v-if="isOrder()" class="group gap">
      <label class="form-row">
        <span>പേര്</span>
        <input v-model="state.ordWho" placeholder="ഓർഡർ ചെയ്യുന്ന ആൾ" />
      </label>
    </div>

    <template #footer>
      <button class="btn primary block" :disabled="state.mode === 'കടം' && !state.creditTo" @click="submit">
        {{ isOrder() ? 'ഓർഡർ സേവ് ചെയ്യുക' : 'ബിൽ ഉണ്ടാക്കുക' }}
      </button>
    </template>
  </BaseSheet>
</template>

<style scoped>
.gap { margin-top: 16px; }
.total strong { flex: 1; text-align: right; font-size: 24px; font-weight: 700; letter-spacing: -.02em; }
.pdf-option input { width: 20px; height: 20px; flex: 0 0 20px; accent-color: var(--accent-fill); }
</style>
