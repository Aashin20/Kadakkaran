<script setup>
import AppIcon from './AppIcon.vue'
import { state, stockList, history } from '../stores/shop.js'

const filters = [
  { k: 'all', l: 'എല്ലാം' },
  { k: 'low', l: 'കുറവ്' },
  { k: 'out', l: 'തീർന്നു' },
  { k: 'exp', l: 'കാലാവധി' },
]
const tone = (p) => (p.stock <= 0 ? 't-red' : p.stock <= p.min ? 't-orange' : '')
const status = (p) => (p.stock <= 0 ? 'തീർന്നു' : p.stock <= p.min ? 'കുറവ്' : '')
</script>

<template>
  <div class="view page">
    <label class="search">
      <AppIcon name="search" :size="18" />
      <input v-model="state.q" type="search" placeholder="സാധനം തിരയുക" aria-label="സാധനം തിരയുക" />
    </label>

    <div class="segmented filters" role="tablist">
      <button v-for="f in filters" :key="f.k" :class="{ on: state.flt === f.k }" @click="state.flt = f.k">{{ f.l }}</button>
    </div>

    <div v-if="stockList.length" class="group list">
      <button v-for="p in stockList" :key="p.id" class="row" @click="state.adj = p">
        <span class="row-main">
          <span class="row-title">{{ p.n }}</span>
          <span class="row-sub">
            വാങ്ങൽ ₹{{ p.cost }} · വിൽപ്പന ₹{{ p.price }}
            <span v-if="p.exp" class="t-orange"> · കാലാവധി {{ p.exp }} ദിവസം</span>
          </span>
        </span>
        <span class="row-value">
          <span class="num" :class="tone(p)">{{ p.stock }} {{ p.unit }}</span>
          <small v-if="status(p)" :class="tone(p)">{{ status(p) }}</small>
        </span>
        <AppIcon class="chev" name="chevron" :size="16" />
      </button>
    </div>
    <div v-else class="group list"><p class="empty">ഒന്നുമില്ല</p></div>

    <template v-if="history.length">
      <div class="section-head"><h2 class="section-title">സ്റ്റോക്ക് ചരിത്രം</h2></div>
      <div class="group">
        <div v-for="(h, i) in history.slice(0, 5)" :key="i" class="row">
          <div class="row-main">
            <div class="row-title">{{ h.n }}</div>
            <div class="row-sub">{{ h.why }} · {{ h.t }}</div>
          </div>
          <span class="row-value num" :class="h.d > 0 ? 't-green' : 't-red'">{{ h.d > 0 ? '+' : '' }}{{ h.d }}</span>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.filters { margin-top: 12px; }
.list { margin-top: 12px; }
.row-main > span { display: block; }
</style>
