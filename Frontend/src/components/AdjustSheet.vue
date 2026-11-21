<script setup>
import { computed } from 'vue'
import AppIcon from './AppIcon.vue'
import BaseSheet from './BaseSheet.vue'
import { state, doAdj, displayUnit } from '../stores/shop.js'

const next = computed(() => (state.adj ? Math.max(0, state.adj.stock + (state.adjQty || 0)) : 0))
</script>

<template>
  <BaseSheet :open="!!state.adj" :title="state.adj?.n || ''" subtitle="സ്റ്റോക്ക് മാറ്റം" @close="state.adj = null">
    <div v-if="state.adj">
      <div class="group">
        <div class="row">
          <span class="row-main row-title">ഇപ്പോഴത്തെ സ്റ്റോക്ക്</span>
          <span class="row-value num">{{ state.adj.stock }} {{ displayUnit(state.adj.unit) }}</span>
        </div>
        <div class="row qty">
          <span class="row-main row-title">ചേർക്കുക / കുറയ്ക്കുക</span>
          <span class="stepper">
            <button class="round" aria-label="കുറയ്ക്കുക" @click="state.adjQty = (state.adjQty || 0) - 1"><AppIcon name="minus" :size="16" :stroke="2.4" /></button>
            <input v-model.number="state.adjQty" class="qty-input num" type="number" inputmode="numeric" placeholder="0" aria-label="അളവ്" @focus="$event.target.select()" />
            <button class="round" aria-label="ചേർക്കുക" @click="state.adjQty = (state.adjQty || 0) + 1"><AppIcon name="plus" :size="16" :stroke="2.4" /></button>
          </span>
        </div>
        <div class="row">
          <span class="row-main row-title">പുതിയ സ്റ്റോക്ക്</span>
          <span class="row-value num"><b>{{ next }} {{ displayUnit(state.adj.unit) }}</b></span>
        </div>
      </div>

      <div class="group gap">
        <label class="form-row">
          <span>വിൽപ്പന വില (₹)</span>
          <input v-model.number="state.adj.price" class="num" type="number" inputmode="decimal" min="0" @focus="$event.target.select()" />
        </label>
      </div>
    </div>

    <template #footer>
      <button class="btn primary block" @click="doAdj">അപ്ഡേറ്റ് ചെയ്യുക</button>
    </template>
  </BaseSheet>
</template>

<style scoped>
.gap { margin-top: 16px; }
.qty-input { width: 64px; height: 34px; border: 0; border-radius: 8px; background: var(--fill); text-align: center; font-size: 17px; font-weight: 600; }
</style>
