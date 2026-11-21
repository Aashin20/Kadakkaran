<script setup>
import AppIcon from './AppIcon.vue'
import { state, filtered, inc, dec } from '../stores/shop.js'

const stockText = (p) => (p.stock <= 0 ? 'തീർന്നു' : 'ബാക്കി ' + p.stock)
const stockTone = (p) => (p.stock <= 0 ? 't-red' : p.stock <= p.min ? 't-orange' : '')
</script>

<template>
  <div class="view page">
    <label class="search">
      <AppIcon name="search" :size="18" />
      <input v-model="state.q" type="search" placeholder="സാധനം തിരയുക" aria-label="സാധനം തിരയുക" />
    </label>

    <div v-if="filtered.length" class="group list">
      <div v-for="p in filtered" :key="p.id" class="row">
        <div class="row-main">
          <div class="row-title">{{ p.n }}</div>
          <div class="row-sub">₹{{ p.price }} / {{ p.unit }} · <span :class="stockTone(p)">{{ stockText(p) }}</span></div>
        </div>
        <div v-if="state.cart[p.id]" class="stepper">
          <button class="round" :aria-label="`${p.n} കുറയ്ക്കുക`" @click="dec(p)"><AppIcon name="minus" :size="16" :stroke="2.4" /></button>
          <b>{{ state.cart[p.id] }}</b>
          <button class="round" :aria-label="`${p.n} ചേർക്കുക`" @click="inc(p)"><AppIcon name="plus" :size="16" :stroke="2.4" /></button>
        </div>
        <button v-else-if="p.stock > 0" class="round" :aria-label="`${p.n} ചേർക്കുക`" @click="inc(p)">
          <AppIcon name="plus" :size="18" :stroke="2.4" />
        </button>
      </div>
    </div>
    <div v-else class="group list"><p class="empty">സാധനം കണ്ടെത്തിയില്ല</p></div>

    <template v-if="state.bills.length">
      <div class="section-head"><h2 class="section-title">കഴിഞ്ഞ ബില്ലുകൾ</h2></div>
      <div class="group">
        <button v-for="b in state.bills.slice(0, 5)" :key="b.id" class="row" @click="state.receipt = b">
          <span class="row-main">
            <span class="row-title">ബിൽ #{{ b.id }}</span>
            <span class="row-sub">{{ b.time }} · {{ b.items.length }} സാധനം · {{ b.mode }}</span>
          </span>
          <span class="row-value num">₹{{ b.total }}</span>
          <AppIcon class="chev" name="chevron" :size="16" />
        </button>
      </div>
    </template>
  </div>
</template>

<style scoped>
.list { margin-top: 12px; }
.row-main > span { display: block; }
</style>
