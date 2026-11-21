<script setup>
import AppIcon from './AppIcon.vue'
import { computed } from 'vue'
import { state, goto, alerts, todaySales, totalCredit, lowItems, week, maxWeek } from '../stores/shop.js'

const dot = { danger: 'var(--red)', warning: 'var(--orange)', info: 'var(--accent)' }

const salesGraph = computed(() => {
  const width = 300
  const height = 86
  const left = 8
  const bottom = 76
  const top = 12
  const step = (width - left * 2) / Math.max(1, week.length - 1)
  const points = week.map((item, index) => {
    const x = left + index * step
    const y = bottom - (item.v / maxWeek) * (bottom - top)
    return `${x},${y}`
  })
  return {
    points: points.join(' '),
    area: `${left},${bottom} ${points.join(' ')} ${width - left},${bottom}`,
  }
})
</script>

<template>
  <div class="view page">
    <section class="dashboard-card">
      <div class="sales-summary">
        <div>
          <p class="label">ഇന്നത്തെ മൊത്തം വിൽപ്പന</p>
          <p class="amount num">₹{{ todaySales }}</p>
        </div>

        <svg class="sales-chart" viewBox="0 0 300 86" preserveAspectRatio="none" aria-hidden="true">
          <polygon :points="salesGraph.area" class="chart-area" />
          <polyline :points="salesGraph.points" class="chart-line" />
          <circle
            v-for="(point, i) in salesGraph.points.split(' ')"
            :key="i"
            :cx="point.split(',')[0]"
            :cy="point.split(',')[1]"
            r="3"
            class="chart-dot"
          />
        </svg>
      </div>

      <div class="dashboard-actions">
        <button class="dashboard-action" @click="goto('credit')">
          <span class="action-icon blue">
            <AppIcon name="wallet" :size="20" />
          </span>
          <span class="action-copy">
            <span class="action-value num">₹{{ totalCredit }} <small>കടം</small></span>
          </span>
          <AppIcon class="action-chevron" name="chevron" :size="15" />
        </button>

        <button class="dashboard-action" @click="goto('stock', {})">
          <span class="action-icon orange">
            <AppIcon name="box" :size="20" />
          </span>
          <span class="action-copy">
            <span class="action-value num">{{ lowItems.length }} <small>സാധനം കുറവ്</small></span>
          </span>
          <AppIcon class="action-chevron" name="chevron" :size="15" />
        </button>
      </div>
    </section>

    <div class="quick-actions" aria-label="ദ്രുത പ്രവർത്തനങ്ങൾ">
      <button class="quick-action" @click="goto('sales')">
        <span class="quick-icon blue"><AppIcon name="receipt" :size="30" :stroke="2.2" /></span>
        <span>ഓർഡർ</span>
      </button>
      <button class="quick-action" @click="goto('stock')">
        <span class="quick-icon orange"><AppIcon name="box" :size="30" :stroke="2.2" /></span>
        <span>സ്റ്റോക്ക്</span>
      </button>
      <button class="quick-action" @click="goto('credit'); state.newCust = true">
        <span class="quick-icon purple"><AppIcon name="user" :size="30" :stroke="2.2" /></span>
        <span>കടം</span>
      </button>
      <button class="quick-action" @click="goto('credit')">
        <span class="quick-icon green"><AppIcon name="wallet" :size="30" :stroke="2.2" /></span>
        <span>ബാക്കി</span>
      </button>
      <button class="quick-action" @click="goto('more', { sub: 'report' })">
        <span class="quick-icon cyan"><AppIcon name="chart" :size="30" :stroke="2.2" /></span>
        <span>വിൽപ്പന</span>
      </button>
      <button class="quick-action" @click="goto('more', { sub: 'buy' })">
        <span class="quick-icon red"><AppIcon name="truck" :size="30" :stroke="2.2" /></span>
        <span>റീസ്റ്റോക്ക്</span>
      </button>
    </div>

    <div class="section-head">
      <h2 class="section-title">ശ്രദ്ധിക്കുക</h2>
      <button v-if="alerts.length > 3" class="link" @click="goto('more', { sub: 'alerts' })">എല്ലാം കാണുക</button>
    </div>
    <div v-if="alerts.length" class="group">
      <button v-for="(a, i) in alerts.slice(0, 3)" :key="i" class="row" @click="goto(...a.to)">
        <span class="dot" :style="{ background: dot[a.tone] }"></span>
        <span class="row-main row-title">{{ a.t }}</span>
        <AppIcon class="chev" name="chevron" :size="16" />
      </button>
    </div>
    <div v-else class="group"><p class="empty">എല്ലാം ശരിയാണ്</p></div>
  </div>
</template>

<style scoped>
.dashboard-card {
  overflow: hidden;
  border: 1px solid rgba(0, 102, 204, .1);
  border-radius: 18px;
  background:
    radial-gradient(circle at 88% 18%, rgba(77, 163, 255, .16), transparent 34%),
    linear-gradient(145deg, #f8fbff 0%, #ffffff 58%, #edf5ff 100%);
  box-shadow: 0 10px 28px rgba(31, 78, 121, .08);
}
.sales-summary {
  position: relative;
  min-height: 178px;
  padding: 20px 18px 14px;
  overflow: hidden;
}
.sales-summary::before {
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
.sales-summary > div { position: relative; z-index: 2; }
.label { color: #64748b; font-size: 15px; }
.amount {
  margin-top: 3px;
  color: #111827;
  font-size: 52px;
  font-weight: 750;
  letter-spacing: -.04em;
  line-height: 1.12;
}
.sales-chart {
  position: absolute;
  right: -18px;
  bottom: -4px;
  width: 82%;
  height: 92px;
  opacity: .9;
  pointer-events: none;
}
.chart-area { fill: rgba(77, 163, 255, .12); }
.chart-line {
  fill: none;
  stroke: #8bbcf1;
  stroke-width: 3;
  stroke-linecap: round;
  stroke-linejoin: round;
  vector-effect: non-scaling-stroke;
}
.chart-dot {
  fill: #ffffff;
  stroke: #0066cc;
  stroke-width: 2;
  vector-effect: non-scaling-stroke;
}
.dashboard-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  border-top: 1px solid rgba(60, 60, 67, .12);
  background: rgba(255, 255, 255, .86);
  backdrop-filter: blur(12px);
}
.dashboard-action {
  display: flex;
  align-items: center;
  gap: 9px;
  min-width: 0;
  min-height: 76px;
  padding: 12px 10px 12px 12px;
}
.dashboard-action + .dashboard-action { border-left: 1px solid rgba(60, 60, 67, .12); }
.dashboard-action:active { background: var(--fill); }
.action-icon {
  flex: none;
  display: inline-grid;
  place-items: center;
  width: 38px;
  height: 38px;
  border-radius: 12px;
}
.action-icon.blue { background: rgba(0, 102, 204, .1); color: #0066cc; }
.action-icon.orange { background: rgba(178, 80, 0, .1); color: #b25000; }
.action-copy { flex: 1; min-width: 0; display: flex; flex-direction: column; }
.action-label { margin-top: 1px; overflow: hidden; color: var(--text-2); font-size: 11px; line-height: 1.1; text-overflow: ellipsis; white-space: nowrap; }
.action-value { display: flex; align-items: baseline; gap: 5px; color: var(--text); font-size: 20px; font-weight: 750; line-height: 1.05; white-space: nowrap; }
.action-value small { color: var(--text-2); font-size: 11px; font-weight: 600; line-height: 1; }
.action-chevron { flex: none; color: var(--text-3); }
.quick-actions {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
  margin-top: 14px;
}
.quick-action {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 9px;
  aspect-ratio: 1;
  min-width: 0;
  padding: 9px 6px;
  border: 0;
  border-radius: 14px;
  color: #fff;
  font-size: 15px;
  font-weight: 700;
  line-height: 1.15;
  text-align: center;
  box-shadow: none;
}
.quick-action:active { filter: brightness(.88); }
.quick-icon {
  flex: none;
  display: inline-grid;
  place-items: center;
  width: 52px;
  height: 52px;
  color: #fff;
}
.quick-action:has(.blue) { background: #0066cc; }
.quick-action:has(.orange) { background: #b25000; }
.quick-action:has(.purple) { background: #7d52c4; }
.quick-action:has(.green) { background: #1a7f37; }
.quick-action:has(.cyan) { background: #0088aa; }
.quick-action:has(.red) { background: #d70015; }
.dot { flex: none; width: 10px; height: 10px; border-radius: 50%; }

</style>
