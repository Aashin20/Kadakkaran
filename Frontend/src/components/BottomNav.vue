<script setup>
import AppIcon from './AppIcon.vue'
import { navs, state, goto, cartCount } from '../stores/shop.js'
</script>

<template>
  <nav class="tabbar" aria-label="പ്രധാന മെനു">
    <button
      v-for="n in navs"
      :key="n.k"
      class="tab"
      :class="{ active: state.tab === n.k }"
      :aria-current="state.tab === n.k ? 'page' : undefined"
      @click="goto(n.k)"
    >
      <span class="tab-icon">
        <AppIcon :name="n.i" :size="24" :stroke="state.tab === n.k ? 2.2 : 1.7" />
        <span v-if="n.k === 'sales' && cartCount" class="badge">{{ cartCount }}</span>
      </span>
      <span class="tab-label">{{ n.l }}</span>
    </button>
  </nav>
</template>

<style scoped>
.tabbar {
  position: absolute;
  right: 12px;
  bottom: calc(10px + env(safe-area-inset-bottom, 0px));
  left: 12px;
  z-index: 45;
  display: flex;
  min-height: 64px;
  padding: 5px 6px;
  border: 1px solid rgba(255, 255, 255, .72);
  border-radius: 22px;
  background: rgba(249, 249, 249, .94);
  backdrop-filter: blur(20px) saturate(1.8);
  box-shadow: 0 10px 30px rgba(31, 78, 121, .18);
}
.tab {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  min-height: 52px;
  padding: 7px 2px 5px;
  color: var(--text-2);
  font-size: 11px;
  font-weight: 500;
  text-align: center;
}
.tab.active { color: var(--accent); }
.tab-icon { position: relative; display: grid; place-items: center; height: 26px; }
.badge {
  position: absolute;
  top: -4px;
  left: 55%;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  display: grid;
  place-items: center;
  border-radius: 9px;
  background: var(--red);
  color: #fff;
  font-size: 12px;
  font-weight: 600;
}
</style>
