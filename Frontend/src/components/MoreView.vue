<script setup>
import { computed } from 'vue'
import AppIcon from './AppIcon.vue'
import {
  state, goto, alerts, todaySales, todayProfit, weekRev, invValue,
  best, slow, week, maxWeek, receiveBuy, buyList,
} from '../stores/shop.js'

const tabs = [
  { k: 'buy', l: 'വാങ്ങൽ' },
  { k: 'orders', l: 'ഓർഡർ' },
  { k: 'report', l: 'റിപ്പോർട്ട്' },
  { k: 'alerts', l: 'അറിയിപ്പ്' },
]
const figures = computed(() => [
  { l: 'ഇന്നത്തെ വിൽപ്പന', v: todaySales.value },
  { l: 'ലാഭം (≈)', v: todayProfit.value },
  { l: 'ഈ ആഴ്ചയിലെ വരുമാനം', v: weekRev.value },
  { l: 'സ്റ്റോക്ക് മൂല്യം', v: invValue.value },
])
const topSold = computed(() => best.value[0]?.sold || 1)
const dot = { danger: 'var(--red)', warning: 'var(--orange)', info: 'var(--accent)' }
</script>

<template>
  <div class="view page">
    <div class="segmented" role="tablist">
      <button v-for="t in tabs" :key="t.k" role="tab" :aria-selected="state.sub === t.k" :class="{ on: state.sub === t.k }" @click="state.sub = t.k">{{ t.l }}</button>
    </div>

    <!-- Buy list -->
    <template v-if="state.sub === 'buy'">
      <div v-if="buyList.length" class="group gap">
        <label v-for="s in buyList" :key="s.id" class="row" :class="{ got: s.got }">
          <input v-model="s.got" type="checkbox" class="sr-only" />
          <span class="check" aria-hidden="true"><AppIcon name="check" :size="14" :stroke="3" /></span>
          <span class="row-main">
            <span class="row-title">{{ s.n }}</span>
            <span class="row-sub">ഇപ്പോൾ {{ s.stock }}</span>
          </span>
          <span class="stepper">
            <button class="round" :aria-label="`${s.n} കുറയ്ക്കുക`" @click.prevent="s.qty = Math.max(1, s.qty - 1)"><AppIcon name="minus" :size="16" :stroke="2.4" /></button>
            <b>{{ s.qty }}</b>
            <button class="round" :aria-label="`${s.n} ചേർക്കുക`" @click.prevent="s.qty++"><AppIcon name="plus" :size="16" :stroke="2.4" /></button>
          </span>
        </label>
      </div>
      <div v-else class="group gap"><p class="empty">ഒന്നും വാങ്ങാനില്ല</p></div>
      <p v-if="buyList.length" class="footnote">വിൽപ്പനയും സ്റ്റോക്കും നോക്കി ഉണ്ടാക്കിയ ലിസ്റ്റ്. കിട്ടിയവ ടിക്ക് ചെയ്യുക.</p>
      <button class="btn primary block cta" :disabled="!buyList.some((s) => s.got)" @click="receiveBuy">കിട്ടിയവ സ്റ്റോക്കിൽ ചേർക്കുക</button>
    </template>

    <!-- Orders -->
    <template v-else-if="state.sub === 'orders'">
      <div v-if="state.orders.length" class="group gap">
        <div v-for="o in state.orders" :key="o.id" class="row">
          <div class="row-main">
            <div class="row-title">{{ o.who }}</div>
            <div class="row-sub">{{ o.items }}</div>
          </div>
          <div class="row-value">
            <span class="num">₹{{ o.total }}</span>
            <button class="tag" :class="o.done ? 't-green' : 't-orange'" :aria-pressed="o.done" @click="o.done = !o.done">
              {{ o.done ? 'കൊടുത്തു' : 'ബാക്കി' }}
            </button>
          </div>
        </div>
      </div>
      <div v-else class="group gap"><p class="empty">ഓർഡറുകൾ ഇല്ല</p></div>
      <button class="btn block cta" @click="goto('sales')">ബില്ലിൽ നിന്ന് ഓർഡർ ഉണ്ടാക്കുക</button>
    </template>

    <!-- Report -->
    <template v-else-if="state.sub === 'report'">
      <div class="group gap">
        <div v-for="f in figures" :key="f.l" class="row">
          <span class="row-main row-title">{{ f.l }}</span>
          <span class="row-value num">₹{{ f.v }}</span>
        </div>
      </div>

      <div class="section-head"><h2 class="section-title">ഏറ്റവും കൂടുതൽ വിറ്റത്</h2></div>
      <div class="group bars">
        <div v-for="p in best" :key="p.id" class="bar-row">
          <span class="bar-name">{{ p.n }}</span>
          <span class="track"><span class="fill" :style="{ width: (p.sold / topSold * 100) + '%' }"></span></span>
          <span class="bar-val num">{{ p.sold }}</span>
        </div>
      </div>

      <div class="section-head"><h2 class="section-title">പതുക്കെ വിൽക്കുന്നവ</h2></div>
      <div class="group">
        <div v-for="p in slow" :key="p.id" class="row">
          <span class="row-main row-title">{{ p.n }}</span>
          <span class="row-value num t-2">{{ p.sold }}</span>
        </div>
      </div>

      <div class="section-head"><h2 class="section-title">ഈ ആഴ്ചയിലെ വിൽപ്പന (₹)</h2></div>
      <div class="group bars">
        <div v-for="d in week" :key="d.d" class="bar-row">
          <span class="bar-name">{{ d.d }}</span>
          <span class="track"><span class="fill" :style="{ width: (d.v / maxWeek * 100) + '%' }"></span></span>
          <span class="bar-val num">{{ d.v }}</span>
        </div>
      </div>
    </template>

    <!-- Alerts -->
    <template v-else>
      <div v-if="alerts.length" class="group gap">
        <button v-for="(a, i) in alerts" :key="i" class="row" @click="goto(...a.to)">
          <span class="dot" :style="{ background: dot[a.tone] }"></span>
          <span class="row-main row-title">{{ a.t }}</span>
          <AppIcon class="chev" name="chevron" :size="16" />
        </button>
      </div>
      <div v-else class="group gap"><p class="empty">അറിയിപ്പുകൾ ഇല്ല</p></div>
    </template>
  </div>
</template>

<style scoped>
.gap { margin-top: 16px; }
.cta { margin-top: 16px; }
.row-main > span { display: block; }
.dot { flex: none; width: 10px; height: 10px; border-radius: 50%; }

.check {
  flex: none;
  display: grid;
  place-items: center;
  width: 26px;
  height: 26px;
  border-radius: 50%;
  border: 1.5px solid var(--text-3);
  color: transparent;
}
.row:has(input:checked) .check { background: var(--accent-fill); border-color: var(--accent-fill); color: #fff; }
.row:has(input:focus-visible) .check { outline: 2px solid var(--accent); outline-offset: 2px; }
.row.got .row-main { opacity: .5; }

.tag { display: block; margin: 2px 0 0 auto; padding: 4px 0; font-size: 14px; font-weight: 600; }

.bars { padding: 6px 16px; }
.bar-row { display: flex; align-items: center; gap: 12px; min-height: 40px; }
.bar-name { flex: none; width: 84px; font-size: 15px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.track { flex: 1; height: 8px; border-radius: 4px; background: var(--fill); overflow: hidden; }
.fill { display: block; height: 100%; border-radius: 4px; background: var(--accent-fill); }
.bar-val { flex: none; width: 44px; text-align: right; font-size: 15px; color: var(--text-2); }
</style>
