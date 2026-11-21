<script setup>
import AppIcon from './AppIcon.vue'
import { computed } from 'vue'
import { state, goto, alerts, todaySales, totalCredit, lowItems, week, maxWeek } from '../stores/shop.js'

const dot = { danger: 'var(--red)', warning: 'var(--orange)', info: 'var(--accent)' }

// dummy data for the background graph
const dummyWeek = [30, 45, 38, 60, 52, 78, 90]

const salesGraph = computed(() => {
  const W = 300, H = 100
  const left = 10, top = 15, bottom = 85
  const max = Math.max(...dummyWeek)
  const step = (W - left * 2) / (dummyWeek.length - 1)
  const pts = dummyWeek.map((v, i) => ({
    x: left + i * step,
    y: bottom - (v / max) * (bottom - top),
  }))
  const line = pts.map(p => `${p.x},${p.y}`).join(' ')
  return {
    points: line,
    area: `${left},${H} ${line} ${W - left},${H}`,
    dots: pts.map(p => ({ left: (p.x / W) * 100, top: (p.y / H) * 100 })),
  }
})
// dummy percentage for the chip
const change = 14
const tiles = [
  { label: 'ഓർഡർ', icon: 'receipt', tone: 'blue', go: () => goto('sales') },
  { label: 'സ്റ്റോക്ക്', icon: 'box', tone: 'green', go: () => goto('stock') },
  { label: 'കടം', icon: 'user', tone: 'purple', go: () => { goto('credit'); state.newCust = true } },
  { label: 'ബാക്കി', icon: 'wallet', tone: 'orange', go: () => goto('credit') },
  { label: 'വിൽപ്പന', icon: 'chart', tone: 'cyan', go: () => goto('more', { sub: 'report' }) },
  { label: 'റീസ്റ്റോക്ക്', icon: 'truck', tone: 'red', go: () => goto('more', { sub: 'buy' }) },
]
</script>

<template>
  <div class="view page">
    <!-- Hero revenue card -->
   <section class="hero">
  <div class="hero-content">
    <p class="hero-label">ഇന്നത്തെ മൊത്തം വിൽപ്പന</p>
    <p class="hero-amount num">₹{{ todaySales }}</p>
    <p class="hero-chip-row">
      <span class="chip">↑ {{ change }}%</span>
      <span class="hero-sub">ഇന്നലെയെ അപേക്ഷിച്ച്</span>
    </p>
  </div>

  <div class="hero-graph">
    <svg viewBox="0 0 300 100" preserveAspectRatio="none" aria-hidden="true">
      <defs>
        <linearGradient id="areaFill" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stop-color="#0066cc" stop-opacity=".28" />
          <stop offset="1" stop-color="#0066cc" stop-opacity="0" />
        </linearGradient>
      </defs>
      <polygon :points="salesGraph.area" fill="url(#areaFill)" />
      <polyline :points="salesGraph.points" class="chart-line" />
    </svg>
    <span
      v-for="(d, i) in salesGraph.dots"
      :key="i"
      class="chart-dot"
      :style="{ left: d.left + '%', top: d.top + '%' }"
    ></span>
  </div>
</section>
    <!-- Two stat cards -->
    <div class="stats">
      <button class="stat" @click="goto('credit')">
        <span class="stat-icon blue"><AppIcon name="wallet" :size="22" /></span>
        <span class="stat-copy">
          <span class="stat-label">കിട്ടാനുള്ള കടം</span>
          <span class="stat-value num">₹{{ totalCredit }}</span>
        </span>
        <AppIcon class="stat-chev" name="chevron" :size="15" />
      </button>

      <button class="stat" @click="goto('stock', {})">
        <span class="stat-icon orange"><AppIcon name="box" :size="22" /></span>
        <span class="stat-copy">
          <span class="stat-label">സ്റ്റോക്ക് കുറവ്</span>
          <span class="stat-value num">{{ lowItems.length }} <small>സാധനം</small></span>
        </span>
        <AppIcon class="stat-chev" name="chevron" :size="15" />
      </button>
    </div>

    <!-- 3 x 2 tiles -->
    <div class="tiles" aria-label="ദ്രുത പ്രവർത്തനങ്ങൾ">
      <button v-for="t in tiles" :key="t.label" class="tile" :class="t.tone" @click="t.go">
        <AppIcon class="tile-icon" :name="t.icon" :size="34" :stroke="2" />
        <span class="tile-label">{{ t.label }}</span>
        <span class="tile-go"><AppIcon name="chevron" :size="14" :stroke="2.6" /></span>
      </button>
    </div>

    <!-- Alerts card -->
    <section class="alerts">
      <div class="alerts-head">
        <h2 class="section-title">ശ്രദ്ധിക്കുക</h2>
        <button v-if="alerts.length > 3" class="link" @click="goto('more', { sub: 'alerts' })">എല്ലാം കാണുക →</button>
      </div>
      <template v-if="alerts.length">
        <button v-for="(a, i) in alerts.slice(0, 3)" :key="i" class="alert-row" @click="goto(...a.to)">
          <span class="dot" :style="{ background: dot[a.tone] }"></span>
          <span class="alert-text">{{ a.t }}</span>
          <AppIcon class="chev" name="chevron" :size="16" />
        </button>
      </template>
      <p v-else class="empty">എല്ലാം ശരിയാണ്</p>
    </section>
  </div>
</template>

<style scoped>
/* ---------- Hero ---------- */
.hero {
  position: relative;
  overflow: hidden;
  min-height: 190px;
  padding: 16px 18px 78px;
  border-radius: 22px;
  color: #0f172a;
  background: linear-gradient(135deg, #eef6ff 0%, #ffffff 60%, #e6f1ff 100%);
  border: 1px solid rgba(0, 102, 204, .12);
  box-shadow: 0 10px 24px rgba(31, 78, 121, .10);
}
.hero-graph {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  height: 70px;
  pointer-events: none;
}
.hero-graph svg {
  width: 100%;
  height: 100%;
  display: block;
}
.hero-content { position: relative; z-index: 2; }
.hero-label { font-size: 14px; color: #475569; }
.hero-amount {
  margin-top: 2px;
  font-size: 44px;
  font-weight: 800;
  letter-spacing: -.03em;
  line-height: 1.1;
  color: #0f172a;
}
.hero-chip-row { display: flex; align-items: center; gap: 8px; margin-top: 6px; }
.chip {
  padding: 2px 9px;
  border-radius: 10px;
  background: rgba(26, 127, 55, .14);
  color: #1a7f37;
  font-size: 13px;
  font-weight: 700;
}
.chip.down { background: rgba(215, 0, 21, .12); color: #d70015; }
.hero-sub { font-size: 12px; color: #64748b; }
.hero-chart {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}
.chart-line {
  fill: none;
  stroke: #0066cc;
  stroke-width: 3;
  stroke-linecap: round;
  stroke-linejoin: round;
  vector-effect: non-scaling-stroke;
}
.chart-dot {
  position: absolute;
  z-index: 1;
  width: 10px;
  height: 10px;
  margin: -5px 0 0 -5px;
  border-radius: 50%;
  background: #fff;
  border: 2.5px solid #0066cc;
  pointer-events: none;
}/* ---------- Stat cards ---------- */
.stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-top: 14px;
}
.stat {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
  padding: 14px 10px 14px 12px;
  border: 1px solid rgba(60, 60, 67, .06);
  border-radius: 18px;
  background: #fff;
  box-shadow: 0 6px 18px rgba(31, 78, 121, .08);
  text-align: left;
}
.stat:active { background: var(--fill); }
.stat-icon {
  flex: none;
  display: inline-grid;
  place-items: center;
  width: 44px;
  height: 44px;
  border-radius: 14px;
}
.stat-icon.blue { background: #dcebff; color: #0066cc; }
.stat-icon.orange { background: #ffe8d1; color: #c25a00; }
.stat-copy { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 2px; }
.stat-label { overflow: hidden; color: var(--text-2); font-size: 12px; text-overflow: ellipsis; white-space: nowrap; }
.stat-value { color: var(--text); font-size: 22px; font-weight: 800; line-height: 1.1; white-space: nowrap; }
.stat-value small { font-size: 13px; font-weight: 700; }
.stat-chev { flex: none; color: var(--text-3); }

/* ---------- Tiles ---------- */
.tiles {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  margin-top: 14px;
}
.tile {
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: flex-start;
  aspect-ratio: 1 / 1.02;
  min-width: 0;
  padding: 14px 12px 12px;
  border: 1px solid rgba(255, 255, 255, .7);
  border-radius: 20px;
  text-align: left;
  overflow: hidden;
  box-shadow: 0 6px 16px rgba(31, 78, 121, .08);
}
.tile::after {            /* soft decorative blob */
  content: '';
  position: absolute;
  right: -28px;
  top: -10px;
  width: 80px;
  height: 120px;
  border-radius: 50%;
  background: rgba(255, 255, 255, .28);
  pointer-events: none;
}
.tile:active { filter: brightness(.95); }
.tile-icon { position: relative; z-index: 1; }
.tile-label { position: relative; z-index: 1; font-size: 15px; font-weight: 700; line-height: 1.15; }
.tile-go {
  position: absolute;
  right: 10px;
  bottom: 10px;
  z-index: 1;
  display: inline-grid;
  place-items: center;
  width: 26px;
  height: 26px;
  border-radius: 50%;
  color: #fff;
}
.tile.blue   { background: linear-gradient(145deg, #dbeafe, #9cc7ff); color: #0b3f8f; }
.tile.green  { background: linear-gradient(145deg, #dcf5e4, #9ddbb0); color: #14683a; }
.tile.purple { background: linear-gradient(145deg, #ece4ff, #c2aaf5); color: #4b2a9b; }
.tile.orange { background: linear-gradient(145deg, #ffe9d4, #ffb98a); color: #9a4300; }
.tile.cyan   { background: linear-gradient(145deg, #d6f6f6, #8adbe0); color: #0a6270; }
.tile.red    { background: linear-gradient(145deg, #ffe0e3, #ff9aa5); color: #a50f24; }
.tile.blue .tile-go   { background: #1d5fd1; }
.tile.green .tile-go  { background: #1a8a4b; }
.tile.purple .tile-go { background: #6a43c8; }
.tile.orange .tile-go { background: #d9772b; }
.tile.cyan .tile-go   { background: #168a99; }
.tile.red .tile-go    { background: #d12a3f; }

/* ---------- Alerts ---------- */
.alerts {
  margin-top: 16px;
  padding: 6px 14px 4px;
  border-radius: 20px;
  background: #fff;
  box-shadow: 0 6px 18px rgba(31, 78, 121, .08);
}
.alerts-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid rgba(60, 60, 67, .1);
}
.alerts-head .section-title { margin: 0; }
.alert-row {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 14px 2px;
  text-align: left;
}
.alert-row + .alert-row { border-top: 1px solid rgba(60, 60, 67, .08); }
.alert-text { flex: 1; min-width: 0; font-size: 16px; font-weight: 600; }
.chev { flex: none; color: var(--text-3); }
.dot { flex: none; width: 10px; height: 10px; border-radius: 50%; }
.empty { padding: 16px 0; text-align: center; color: var(--text-2); }
</style>