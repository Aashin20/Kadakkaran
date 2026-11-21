<script setup>
import AppIcon from './AppIcon.vue'
import { state, stockList, history, displayUnit, movementLabel } from '../stores/shop.js'

const filters = [
  { k: 'all', l: 'എല്ലാം' },
  { k: 'low', l: 'കുറവ്' },
  { k: 'out', l: 'തീർന്നു' },
  { k: 'exp', l: 'കാലാവധി' },
]
const tone = (p) => (p.stock <= 0 || p.stock <= p.min ? 't-red' : '')
const isLow = (p) => p.stock <= p.min
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
          <span class="row-title">
            <span v-if="isLow(p)" class="stock-indicator" aria-label="കുറവ്"></span>
            {{ p.n }}
          </span>
          <span class="row-sub">
            <span v-if="p.exp" class="t-orange">കാലാവധി {{ p.exp }} ദിവസം</span>
          </span>
        </span>
        <span class="row-value">
          <span class="stock-price num">
            <span :class="tone(p)">{{ p.stock }}{{ displayUnit(p.unit) }}</span>
            <span class="stock-divider">|</span>
            ₹{{ p.price }}
          </span>
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
            <div class="row-sub">{{ movementLabel(h.d > 0 ? 'IN' : 'OUT', h.why) }} · {{ h.t }}</div>
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
.stock-indicator { display: inline-block; width: 7px; height: 7px; margin-right: 6px; border-radius: 50%; background: var(--red); vertical-align: 2px; }
.stock-price { white-space: nowrap; }
.stock-divider { margin: 0 5px; color: var(--text-2); }
</style>
