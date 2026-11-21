<script setup>
import AppIcon from './AppIcon.vue'

defineProps({
  open: { type: Boolean, default: false },
  title: { type: String, default: '' },
  subtitle: { type: String, default: '' },
  tall: { type: Boolean, default: false },
})
defineEmits(['close'])
</script>

<template>
  <Teleport to="body">
    <Transition name="sheet">
      <div v-if="open" class="sheet-backdrop" @click.self="$emit('close')" @keydown.esc="$emit('close')">
        <div class="sheet-panel" :class="{ tall }" role="dialog" aria-modal="true" :aria-label="title || undefined">
          <div class="sheet-handle"></div>

          <header v-if="title || $slots.header" class="sheet-head">
            <slot name="header">
              <div>
                <h3>{{ title }}</h3>
                <p v-if="subtitle">{{ subtitle }}</p>
              </div>
            </slot>
            <button class="close-btn" aria-label="അടയ്ക്കുക" @click="$emit('close')">
              <AppIcon name="x" :size="15" :stroke="2.4" />
            </button>
          </header>

          <div class="sheet-body"><slot /></div>
          <div v-if="$slots.footer" class="sheet-foot"><slot name="footer" /></div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>
