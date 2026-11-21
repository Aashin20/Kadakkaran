<script setup>
import { computed } from 'vue'
import AppIcon from './AppIcon.vue'
import { state } from '../stores/shop.js'

defineProps({ scrolled: Boolean })

const titles = { home: 'ഇന്ന്', sales: 'പുതിയ ബിൽ', stock: 'സ്റ്റോക്ക്', credit: 'കടം', more: 'കൂടുതൽ' }
const add = computed(() => ({
  stock: { label: 'പുതിയ സാധനം', run: () => { state.showAdd = true } },
  credit: { label: 'പുതിയ ആൾ', run: () => { state.newCust = true } },
})[state.tab])
</script>

<template>
  <header class="bar" :class="{ scrolled }">
    <div class="bar-title">
      <h1 v-if="state.tab !== 'home'">{{ titles[state.tab] }}</h1>
    </div>
    <div class="bar-actions">
      <button v-if="add" class="icon-btn" :aria-label="add.label" @click="add.run">
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
  padding: calc(8px + env(safe-area-inset-top, 0px)) 8px 6px 20px;
  border-bottom: .5px solid transparent;
  transition: background .2s, border-color .2s;
}
.bar.scrolled { background: var(--bar); backdrop-filter: blur(20px) saturate(1.8); border-bottom-color: var(--sep); }
.bar-title { min-width: 0; padding-bottom: 2px; }
h1 { font-size: 32px; font-weight: 700; letter-spacing: -.02em; line-height: 1.25; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.bar-actions { flex: none; display: flex; align-items: center; }
</style>
