<script setup>
import { state, cartCount, cartTotal } from '../stores/shop.js'
</script>

<template>
  <Transition name="rise">
    <div v-if="state.tab === 'sales' && cartCount" class="cartbar">
      <button class="btn primary block" @click="state.checkout = true">
        <span>ബിൽ കാണുക · {{ cartCount }} സാധനം</span>
        <span class="num">₹{{ cartTotal }}</span>
      </button>
    </div>
  </Transition>
</template>

<style scoped>
.cartbar { flex: none; padding: 8px 16px; background: var(--bar); backdrop-filter: blur(20px); }
.btn { justify-content: space-between; padding: 0 18px; }
.rise-enter-active, .rise-leave-active { transition: opacity .2s, transform .2s; }
.rise-enter-from, .rise-leave-to { opacity: 0; transform: translateY(8px); }
</style>
