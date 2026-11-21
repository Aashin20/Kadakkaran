<script setup>
import AppIcon from './AppIcon.vue'
import { state, bal, totalCredit } from '../stores/shop.js'
</script>

<template>
  <div class="view page">
    <section class="group summary">
      <p class="label">ആകെ കിട്ടാനുള്ളത്</p>
      <p class="amount num">₹{{ totalCredit }}</p>
      <p class="meta">{{ state.customers.filter((c) => bal(c) > 0).length }} പേർക്ക് കടം ഉണ്ട്</p>
    </section>

    <div v-if="state.customers.length" class="group list">
      <button v-for="c in state.customers" :key="c.id" class="row" @click="state.cust = c">
        <span class="initial" aria-hidden="true">{{ c.n.charAt(0) }}</span>
        <span class="row-main">
          <span class="row-title">{{ c.n }}</span>
          <span class="row-sub">{{ c.ph }}</span>
        </span>
        <span class="row-value num" :class="{ 't-2': bal(c) <= 0 }">{{ bal(c) > 0 ? '₹' + bal(c) : 'തീർന്നു' }}</span>
        <AppIcon class="chev" name="chevron" :size="16" />
      </button>
    </div>
    <div v-else class="group list">
      <div class="empty">
        <p>ആളുകളെ ചേർക്കൂ</p>
        <button class="btn sm add" @click="state.newCust = true">പുതിയ ആൾ</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.summary { padding: 18px 16px 16px; }
.label { font-size: 15px; color: var(--text-2); }
.amount { margin-top: 2px; font-size: 44px; font-weight: 700; letter-spacing: -.03em; line-height: 1.15; }
.meta { margin-top: 2px; font-size: 15px; color: var(--text-2); }
.list { margin-top: 16px; }
.row-main > span { display: block; }
.initial {
  flex: none;
  display: grid;
  place-items: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--fill);
  color: var(--text-2);
  font-size: 17px;
  font-weight: 600;
}
.add { margin-top: 12px; }
</style>
