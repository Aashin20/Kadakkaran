<script setup>
import AppIcon from './AppIcon.vue'
import BaseSheet from './BaseSheet.vue'
import { state, bal, txn, remind } from '../stores/shop.js'
</script>

<template>
  <BaseSheet :open="!!state.cust" :title="state.cust?.n || ''" :subtitle="state.cust?.ph || ''" @close="state.cust = null">
    <div v-if="state.cust">
      <div class="group">
        <div class="row">
          <span class="row-main row-title">ബാക്കി തുക</span>
          <strong class="balance num" :class="{ 't-2': bal(state.cust) <= 0 }">{{ bal(state.cust) > 0 ? '₹' + bal(state.cust) : 'തീർന്നു' }}</strong>
        </div>
        <label class="form-row">
          <span>തുക (₹)</span>
          <input v-model.number="state.amt" class="num" type="number" inputmode="decimal" min="0" placeholder="0" @focus="$event.target.select()" />
        </label>
      </div>

      <div class="actions">
        <button class="btn grow" :disabled="!state.amt" @click="txn('give')">കടം കൊടുത്തു</button>
        <button class="btn primary grow" :disabled="!state.amt" @click="txn('pay')">പണം കിട്ടി</button>
      </div>
      <button v-if="bal(state.cust) > 0" class="btn block remind" @click="remind">
        <AppIcon name="phone" :size="18" /> ഓർമ്മപ്പെടുത്തൽ അയക്കുക
      </button>

      <div class="section-head"><h3 class="section-title">ഇടപാടുകൾ</h3></div>
      <div v-if="state.cust.tx.length" class="group">
        <div v-for="(t, i) in state.cust.tx.slice().reverse()" :key="i" class="row">
          <div class="row-main">
            <div class="row-title">{{ t.k === 'give' ? 'കടം കൊടുത്തു' : 'പണം തന്നു' }}</div>
            <div class="row-sub">{{ t.d }}</div>
          </div>
          <span class="row-value num" :class="t.k === 'give' ? '' : 't-green'">{{ t.k === 'give' ? '+' : '−' }}₹{{ t.a }}</span>
        </div>
      </div>
      <div v-else class="group"><p class="empty">ഇടപാടുകൾ ഇല്ല</p></div>
    </div>
  </BaseSheet>
</template>

<style scoped>
.balance { font-size: 24px; font-weight: 700; letter-spacing: -.02em; }
.actions { display: flex; gap: 10px; margin-top: 16px; }
.remind { margin-top: 10px; }
</style>
