<script setup>
import { computed } from 'vue'
import AppIcon from './AppIcon.vue'
import { state, goto } from '../stores/shop.js'

defineProps({ scrolled: Boolean })

const userName = 'ആശിൻ' // swap for your store value if you have one
const titles = { sales: 'പുതിയ ബിൽ', stock: 'സ്റ്റോക്ക്', credit: 'കടം', more: 'കൂടുതൽ' }
const add = computed(() => ({
  stock: { label: 'പുതിയ സാധനം', run: () => { state.showAdd = true } },
  credit: { label: 'പുതിയ ആൾ', run: () => { state.newCust = true } },
})[state.tab])
</script>

<template>
  <header class="bar" :class="{ scrolled }">
    <div class="bar-title">
<div v-if="state.tab === 'home'" class="greet">
  <h1 class="greet-name">നമസ്കാരം 👋</h1>
</div>
      <h1 v-else>{{ titles[state.tab] }}</h1>
    </div>
    <div class="bar-actions">
      <button v-if="state.tab === 'home'" class="bell" aria-label="അറിയിപ്പുകൾ" @click="goto('more', { sub: 'alerts' })">
        <AppIcon name="bell" :size="22" />
        <span class="bell-dot"></span>
      </button>
      <button v-else-if="add" class="icon-btn" :aria-label="add.label" @click="add.run">
        <AppIcon name="plus" :size="24" />
      </button>
    </div>
  </header>
</template>

<style scoped>
.bar {
  flex: none;
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 8px;
  padding: calc(8px + env(safe-area-inset-top, 0px)) 16px 6px 20px;
  border-bottom: .5px solid transparent;
  transition: background .2s, border-color .2s;
}
.bar.scrolled { background: var(--bar); backdrop-filter: blur(20px) saturate(1.8); border-bottom-color: var(--sep); }
.bar-title { min-width: 0; padding-bottom: 2px; }
h1 { font-size: 32px; font-weight: 700; letter-spacing: -.02em; line-height: 1.25; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.greet { padding-top: 16px; padding-bottom: 6px; }
.greet-name { font-size: 22px; font-weight: 600; line-height: 1.25; }
.bar-actions { flex: none; display: flex; align-items: center; }
.bell {
  position: relative;
  display: grid;
  place-items: center;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: #fff;
  box-shadow: 0 4px 12px rgba(31, 78, 121, .12);
}
.bell-dot { position: absolute; top: 9px; right: 11px; width: 9px; height: 9px; border-radius: 50%; background: var(--red); }
</style>