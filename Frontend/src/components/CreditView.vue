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
      <button v-for="c in state.customers" :key="c.id" class="row" :class="{ paid: bal(c) <= 0 }" @click="state.cust = c">
        <span class="initial" :class="{ 'paid-indicator': bal(c) <= 0 }" aria-hidden="true">
          <span v-if="bal(c) <= 0" class="paid-dot"></span>
          <span v-else>{{ c.n.charAt(0) }}</span>
        </span>
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
.summary {
  position: relative;
  overflow: hidden;
  min-height: 112px;
  padding: 18px 16px 16px;
  border: 1px solid rgba(0, 102, 204, .1);
  background:
    radial-gradient(circle at 88% 18%, rgba(77, 163, 255, .16), transparent 34%),
    linear-gradient(145deg, #f8fbff 0%, #ffffff 58%, #edf5ff 100%);
  box-shadow: 0 10px 28px rgba(31, 78, 121, .08);
}
.summary::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(77, 163, 255, .07) 1px, transparent 1px),
    linear-gradient(90deg, rgba(77, 163, 255, .07) 1px, transparent 1px);
  background-size: 28px 28px;
  mask-image: linear-gradient(to left, #000 18%, transparent 95%);
  pointer-events: none;
}
.summary > * {
  position: relative;
  z-index: 1;
}
.label { font-size: 15px; color: #64748b; }
.amount { margin-top: 2px; font-size: 44px; font-weight: 750; letter-spacing: -.03em; line-height: 1.15; color: #111827; }
.meta { margin-top: 2px; font-size: 15px; color: #64748b; }
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
.paid-indicator {
  background: rgba(26, 127, 55, .12);
  border: 1px solid rgba(26, 127, 55, .25);
}
.paid-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: var(--green);
  box-shadow: 0 0 0 4px rgba(26, 127, 55, .12);
}
.row.paid .row-title,
.row.paid .row-sub {
  text-decoration: line-through;
  text-decoration-thickness: 1.5px;
  color: var(--text-2);
}
.add { margin-top: 12px; }
</style>
