<script setup>
import BaseSheet from './BaseSheet.vue'
import { state, addCust } from '../stores/shop.js'
</script>

<template>
  <BaseSheet :open="state.newCust" title="പുതിയ ആൾ" @close="state.newCust = false">
    <div class="group">
      <label class="form-row"><span>പേര്</span><input v-model="state.nc.n" placeholder="ഉദാ: രവി" /></label>
      <label class="form-row"><span>ഫോൺ</span><input v-model="state.nc.ph" type="tel" inputmode="tel" placeholder="98470 00000" /></label>
      <label class="form-row"><span>കടം തുക (₹)</span><input v-model.number="state.nc.amount" class="num" type="number" inputmode="decimal" min="1" placeholder="0" /></label>
      <label class="form-row"><span>തരേണ്ട തീയതി</span><input v-model="state.nc.payAt" type="datetime-local" /></label>
    </div>
    <template #footer>
      <button class="btn primary block" :disabled="!state.nc.n || !state.nc.amount || !state.nc.payAt" @click="addCust">ചേർക്കുക</button>
    </template>
  </BaseSheet>
</template>
