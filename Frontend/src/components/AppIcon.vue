<script setup>
import { computed } from 'vue'

const props = defineProps({
  name: { type: String, required: true },
  size: { type: [Number, String], default: 20 },
  stroke: { type: [Number, String], default: 1.8 },
})

const icons = {
  home: '<path d="M3 10.6 12 3l9 7.6"/><path d="M5.5 9.5V21h13V9.5"/><path d="M9.5 21v-6h5v6"/>',
  receipt: '<path d="M6 3h12v18l-3-2-3 2-3-2-3 2z"/><path d="M9 8h6M9 12h6"/>',
  box: '<path d="M21 8 12 3 3 8v8l9 5 9-5z"/><path d="m3 8 9 5 9-5M12 13v8"/>',
  book: '<path d="M4 4h6.5A2.5 2.5 0 0 1 13 6.5V20a3 3 0 0 0-3-2.5H4z"/><path d="M20 4h-3.5A2.5 2.5 0 0 0 14 6.5V20a3 3 0 0 1 3-2.5h3z"/>',
  grid: '<rect x="3" y="3" width="7.5" height="7.5" rx="2"/><rect x="13.5" y="3" width="7.5" height="7.5" rx="2"/><rect x="3" y="13.5" width="7.5" height="7.5" rx="2"/><rect x="13.5" y="13.5" width="7.5" height="7.5" rx="2"/>',
  bell: '<path d="M18 8.5a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9"/><path d="M10 21h4"/>',
  search: '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.6-3.6"/>',
  mic: '<rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5.5 11a6.5 6.5 0 0 0 13 0M12 17.5V21"/>',
  plus: '<path d="M12 5v14M5 12h14"/>',
  minus: '<path d="M5 12h14"/>',
  check: '<path d="m5 12.5 4.5 4.5L19 7"/>',
  x: '<path d="M18 6 6 18M6 6l12 12"/>',
  send: '<path d="m21.5 2.5-7 19-4-8.5-8.5-4z"/><path d="M21.5 2.5 10.5 13"/>',
  edit: '<path d="M12 20h9"/><path d="M16.6 3.4a2.1 2.1 0 0 1 3 3L7.5 18.5 3.5 19.5l1-4z"/>',
  arrow: '<path d="M5 12h14M13 6l6 6-6 6"/>',
  chart: '<path d="M3 3v18h18"/><path d="m7 15 4-5 3 3 5-7"/>',
  alert: '<path d="M12 3 2.5 20h19z"/><path d="M12 9v5M12 17.2h.01"/>',
  cart: '<circle cx="9" cy="20" r="1.4"/><circle cx="18" cy="20" r="1.4"/><path d="M2.5 3.5H5l2.6 12h11L21 7H6.2"/>',
  wallet: '<rect x="3" y="6" width="18" height="14" rx="3"/><path d="M3.5 10h17M16.5 14.5h2"/>',
  trending: '<path d="m3 17 6-6 4 4 8-8"/><path d="M15 7h6v6"/>',
  clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5.2l3.2 2"/>',
  user: '<circle cx="12" cy="8" r="4"/><path d="M4.5 21a7.5 7.5 0 0 1 15 0"/>',
  users: '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0 1 13 0"/><path d="M16 5.2a3.5 3.5 0 0 1 0 6.6M18 14.5a6.5 6.5 0 0 1 3.5 5.5"/>',
  bag: '<path d="M6 8h12l1 13H5z"/><path d="M9 8V6a3 3 0 0 1 6 0v2"/>',
  sparkles: '<path d="m12 3 1.7 4.8L18.5 9.5l-4.8 1.7L12 16l-1.7-4.8-4.8-1.7 4.8-1.7z"/><path d="m18.5 15 .8 2.2 2.2.8-2.2.8-.8 2.2-.8-2.2-2.2-.8 2.2-.8z"/>',
  phone: '<path d="M6.5 3h3.2l1.8 4.8-2.3 1.4a12 12 0 0 0 5.6 5.6l1.4-2.3L21 14.3v3.2a2 2 0 0 1-2.2 2A16.5 16.5 0 0 1 4.5 5.2 2 2 0 0 1 6.5 3z"/>',
  chevron: '<path d="m9 5 7 7-7 7"/>',
  truck: '<path d="M2.5 6h11v11h-11z"/><path d="M13.5 9.5h4l3.5 3.5v4h-7.5z"/><circle cx="7" cy="18.5" r="2"/><circle cx="18" cy="18.5" r="2"/>',
  calendar: '<rect x="3" y="5" width="18" height="16" rx="2.5"/><path d="M7.5 3v4M16.5 3v4M3 10h18"/>',
  info: '<circle cx="12" cy="12" r="9"/><path d="M12 11.5V16M12 8h.01"/>',
  refresh: '<path d="M20.5 11a8.5 8.5 0 1 0-2.2 6.2"/><path d="M20.5 4.5v6.5H14"/>',
  share: '<path d="M12 3v12M8 7l4-4 4 4"/><path d="M5 13v6a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-6"/>',
  menu: '<path d="M4 7h16M4 12h16M4 17h16"/>',
  tag: '<path d="M20.5 12 12 20.5 3.5 12V3.5H12z"/><circle cx="7.8" cy="7.8" r="1.1"/>',
  chat: '<path d="M21 11.5a8.5 8.5 0 0 1-12.4 7.6L3 21l1.9-5.6A8.5 8.5 0 1 1 21 11.5z"/>',
  shield: '<path d="M12 22s8-3.5 8-10V5.5L12 2 4 5.5V12c0 6.5 8 10 8 10z"/><path d="m9 12 2 2 4-4"/>',
  store: '<path d="M4 9.5 5.6 4h12.8L20 9.5"/><path d="M4.5 9.5V20h15V9.5"/><path d="M9.5 20v-5.5h5V20"/><path d="M4 9.5a2.7 2.7 0 0 0 5.4 0 2.7 2.7 0 0 0 5.3 0 2.7 2.7 0 0 0 5.3 0"/>',
  leaf: '<path d="M20.5 3.5c-8.5 0-14 4-14 10a6 6 0 0 0 6 6c6 0 8-5.5 8-16z"/><path d="M4 21c1.5-6 5-9.5 10-12"/>',
}

const path = computed(() => icons[props.name] || icons.info)
</script>

<template>
  <svg
    :width="size"
    :height="size"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    :stroke-width="stroke"
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
    focusable="false"
    v-html="path"
  />
</template>
