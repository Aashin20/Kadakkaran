<script setup>
import AppIcon from './AppIcon.vue'
import BaseSheet from './BaseSheet.vue'
import { state, share } from '../stores/shop.js'
</script>

<template>
  <BaseSheet
    :open="!!state.receipt"
    :title="state.receipt ? `ബിൽ #${state.receipt.id}` : ''"
    :subtitle="state.receipt ? `${state.receipt.time} · ${state.receipt.mode}` : ''"
    @close="state.receipt = null"
  >
    <div v-if="state.receipt">
      <div class="group">
        <div v-for="(i, idx) in state.receipt.items" :key="idx" class="row">
          <div class="row-main">
            <div class="row-title">{{ i.n }}</div>
            <div class="row-sub num">{{ i.q }} × ₹{{ i.price }}</div>
          </div>
          <span class="row-value num">₹{{ i.q * i.price }}</span>
        </div>
        <div v-if="state.receipt.disc" class="row">
          <span class="row-main row-title">ഡിസ്കൗണ്ട്</span>
          <span class="row-value num t-red">− ₹{{ state.receipt.disc }}</span>
        </div>
        <div class="row total">
          <span class="row-main row-title">ആകെ</span>
          <strong class="num">₹{{ state.receipt.total }}</strong>
        </div>
      </div>
      <p class="footnote thanks">നന്ദി! വീണ്ടും വരിക.</p>
    </div>

    <template #footer>
      <button class="btn grow" @click="state.receipt = null">അടയ്ക്കുക</button>
      <button class="btn primary grow" @click="share"><AppIcon name="share" :size="18" /> ഷെയർ</button>
    </template>
  </BaseSheet>
</template>

<style scoped>
.shop { margin: 0 4px 12px; font-size: 15px; color: var(--text-2); }
.total strong { font-size: 24px; font-weight: 700; letter-spacing: -.02em; }
.thanks { text-align: center; margin-top: 16px; }
</style>
