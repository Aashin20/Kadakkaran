<script setup>
import BaseSheet from './BaseSheet.vue'
import { state, addProduct } from '../stores/shop.js'

const units = ['കിലോ', 'എണ്ണം', 'പാക്കറ്റ്', 'ലിറ്റർ']
const pick = (e) => e.target.select()
</script>

<template>
  <BaseSheet :open="state.showAdd" title="പുതിയ സാധനം" @close="state.showAdd = false">
    <div class="group">
      <label class="form-row"><span>പേര്</span><input v-model="state.np.n" placeholder="ഉദാ: ചെറുപയർ" /></label>
      <label class="form-row"><span>SKU</span><input v-model="state.np.sku" placeholder="ഉദാ: DAL-002" /></label>
      <label class="form-row"><span>യൂണിറ്റ്</span>
        <select v-model="state.np.unit"><option v-for="u in units" :key="u">{{ u }}</option></select>
      </label>
    </div>
    <div class="group gap">
      <label class="form-row"><span>വിവരണം</span><input v-model="state.np.description" placeholder="സാധനത്തിന്റെ വിവരണം" /></label>
    </div>
    <div class="group gap">
      <label class="form-row"><span>വാങ്ങൽ വില (₹)</span><input v-model.number="state.np.cost" class="num" type="number" inputmode="decimal" min="0" placeholder="0" @focus="pick" /></label>
      <label class="form-row"><span>വിൽപ്പന വില (₹)</span><input v-model.number="state.np.price" class="num" type="number" inputmode="decimal" min="0" placeholder="0" @focus="pick" /></label>
    </div>
    <div class="group gap">
      <label class="form-row"><span>ഇപ്പോഴത്തെ സ്റ്റോക്ക്</span><input v-model.number="state.np.stock" class="num" type="number" inputmode="decimal" min="0" placeholder="0" @focus="pick" /></label>
      <label class="form-row"><span>കുറഞ്ഞ പരിധി</span><input v-model.number="state.np.min" class="num" type="number" inputmode="decimal" min="0" placeholder="5" @focus="pick" /></label>
      <label class="form-row"><span>കാലാവധി (ദിവസം)</span><input v-model.number="state.np.expiryDays" class="num" type="number" inputmode="numeric" min="0" placeholder="ഒഴിവാക്കാം" @focus="pick" /></label>
    </div>
    <p class="footnote">സ്റ്റോക്ക് ഈ പരിധിയിൽ താഴെയായാൽ അറിയിപ്പ് കിട്ടും.</p>

    <template #footer>
      <button class="btn primary block" :disabled="!state.np.n || !state.np.price" @click="addProduct">സേവ് ചെയ്യുക</button>
    </template>
  </BaseSheet>
</template>

<style scoped>.gap { margin-top: 16px; }</style>
