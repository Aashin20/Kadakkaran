import { reactive, ref, computed, nextTick } from 'vue'

export const shopName = ''
const API_BASE = (import.meta.env.VITE_API_BASE_URL || '/api').replace(/\/$/, '')

const now = () => new Date().toLocaleTimeString('ml-IN', { hour: '2-digit', minute: '2-digit' })

export const state = reactive({
  // navigation
  tab: 'home',
  sub: 'buy',
  q: '',
  flt: 'all',
  toast: '',

  // master data
  products: reactive([]),
  customers: reactive([]),
  bills: reactive([]),
  salesSummary: reactive({ totalSales: 0, profit: 0, quantitySold: 0 }),
  history: reactive([]),
  orders: reactive([]),
  buyList: reactive([]),

  // billing
  cart: reactive({}),
  checkout: false,
  disc: 0,
  mode: 'പണം',
  creditTo: null,
  ordWho: '',
  receipt: null,

  // stock dialogs
  showAdd: false,
  np: reactive({ n: '', sku: '', description: '', cost: 0, price: 0, stock: 0, min: 5, unit: 'കിലോ', expiryDays: null }),
  adj: null,
  adjQty: 0,

  // credit dialogs
  cust: null,
  amt: null,
  newCust: false,
  nc: reactive({ n: '', ph: '', amount: 0, payAt: '' }),

  // ai chat
  chatOpen: false,
  inp: '',
  listening: false,
  speaking: false,
  wakeListening: false,
  wakeTriggered: false,
  wakeSupported: true,
  msgs: reactive([]),
})

export const buyList = state.buyList
export const history = state.history

export const week = []
export const suggestions = ['ഇന്ന് എത്ര വിൽപ്പന?', 'സ്റ്റോക്ക് കുറവ് ഏതൊക്കെ?', 'ആർക്കൊക്കെ കടം ഉണ്ട്?']
export const navs = [
  { k: 'home', i: 'home', l: 'ഹോം' },
  { k: 'sales', i: 'receipt', l: 'ബിൽ' },
  { k: 'stock', i: 'box', l: 'സ്റ്റോക്ക്' },
  { k: 'credit', i: 'book', l: 'കടം' },
  { k: 'more', i: 'grid', l: 'കൂടുതൽ' },
]

let toastTimer = null
export const say = (text) => {
  state.toast = text
  clearTimeout(toastTimer)
  toastTimer = setTimeout(() => { state.toast = '' }, 2400)
}

export const bal = (c) => c.tx.reduce((s, t) => s + (t.k === 'give' ? t.a : -t.a), 0)

export const totalCredit = computed(() => state.customers.reduce((s, c) => s + Math.max(0, bal(c)), 0))
export const todaySales = computed(() => state.salesSummary.totalSales)
export const todayProfit = computed(() => state.salesSummary.profit)
export const weekRev = computed(() => week.reduce((s, d) => s + d.v, 0) + state.bills.reduce((s, b) => s + b.total, 0))
export const maxWeek = Math.max(...week.map((d) => d.v), 1)
export const invValue = computed(() => state.products.reduce((s, p) => s + p.stock * p.cost, 0))
export const lowItems = computed(() => state.products.filter((p) => p.stock <= p.min))
export const best = computed(() => [...state.products].sort((a, b) => b.sold - a.sold).slice(0, 5))
export const slow = computed(() => [...state.products].sort((a, b) => a.sold - b.sold).slice(0, 3))
export const filtered = computed(() => state.products.filter((p) => p.n.includes(state.q)))
export const stockList = computed(() => filtered.value.filter((p) =>
  state.flt === 'all' ||
  (state.flt === 'low' && p.stock > 0 && p.stock <= p.min) ||
  (state.flt === 'out' && p.stock <= 0) ||
  (state.flt === 'exp' && p.exp),
))

export const alerts = computed(() => {
  const a = []
  state.products.filter((p) => p.stock <= 0).forEach((p) => a.push({ tone: 'danger', t: p.n + ' തീർന്നു', to: ['stock'] }))
  state.products.filter((p) => p.stock > 0 && p.stock <= p.min).forEach((p) => a.push({ tone: 'warning', t: p.n + ' കുറവാണ് (ബാക്കി ' + p.stock + ' ' + p.unit + ')', to: ['stock'] }))
  state.products.filter((p) => p.exp).forEach((p) => a.push({ tone: 'warning', t: p.n + ' ' + p.exp + ' ദിവസത്തിനകം കാലാവധി തീരും', to: ['stock'] }))
  state.customers.filter((c) => bal(c) > 0).forEach((c) => a.push({ tone: 'info', t: c.n + ' ₹' + bal(c) + ' തരാനുണ്ട്', to: ['credit'] }))
  if (lowItems.value.length) a.push({ tone: 'info', t: lowItems.value.length + ' സാധനങ്ങൾ വാങ്ങാനുണ്ട്', to: ['more', { sub: 'buy' }] })
  return a
})

export const refreshBuy = () => {
  state.buyList.splice(0, state.buyList.length, ...lowItems.value.map((p) => ({
    id: p.id, n: p.n, stock: p.stock, qty: Math.max(1, Math.ceil(p.min * 2 - p.stock)), got: false,
  })))
}
refreshBuy()

export const goto = (tab, opts = {}) => {
  state.tab = tab
  state.q = ''
  state.flt = 'all'
  if (opts.sub) state.sub = opts.sub
}

const log = (p, d, why) => state.history.unshift({ n: p.n, d, why, t: now() })

export const inc = (p) => {
  if ((state.cart[p.id] || 0) < p.stock) state.cart[p.id] = (state.cart[p.id] || 0) + 1
  else say('സ്റ്റോക്ക് ഇല്ല')
}
export const dec = (p) => {
  state.cart[p.id]--
  if (!state.cart[p.id]) delete state.cart[p.id]
}

export const cartItems = computed(() => Object.keys(state.cart).map((id) => {
  const p = state.products.find((x) => x.id == id)
  return { ...p, q: state.cart[id] }
}))
export const cartCount = computed(() => cartItems.value.reduce((s, i) => s + i.q, 0))
export const cartTotal = computed(() => cartItems.value.reduce((s, i) => s + i.q * i.price, 0))
export const payable = computed(() => Math.max(0, cartTotal.value - (state.disc || 0)))

const clearCart = () => {
  Object.keys(state.cart).forEach((k) => delete state.cart[k])
  state.disc = 0
  state.mode = 'പണം'
  state.creditTo = null
  state.ordWho = ''
  state.checkout = false
}

export const makeBill = async () => {
  const items = cartItems.value.map((i) => ({ n: i.n, q: i.q, price: i.price }))
  const profit = cartItems.value.reduce((s, i) => s + i.q * (i.price - i.cost), 0) - (state.disc || 0)
  const b = { id: state.bills.length + 101, time: now(), items, disc: state.disc || 0, total: payable.value, mode: state.mode, profit }
  try {
    for (const item of cartItems.value) {
      const response = await fetch(`${API_BASE}/stock/${item.id}/remove`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ quantity: item.q, note: 'വിൽപ്പന' }),
      })
      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'വിൽപ്പന അപ്ഡേറ്റ് ചെയ്യാൻ കഴിഞ്ഞില്ല')
      }
    }
    if (state.mode === 'കടം' && state.creditTo) {
      state.customers.find((c) => c.id === state.creditTo)?.tx.push({ k: 'give', a: b.total, d: 'ഇന്ന്' })
    }
    state.bills.unshift(b)
    await Promise.all([loadProducts(), loadStockHistory(), loadSalesSummary()])
    clearCart()
    refreshBuy()
    state.receipt = b
  } catch (error) {
    say(error.message)
  }
}

export const saveOrder = () => {
  state.orders.unshift({
    id: state.orders.length + 1,
    who: state.ordWho.trim() || 'പുതിയ ഓർഡർ',
    items: cartItems.value.map((i) => i.n + ' ' + i.q).join(', '),
    total: payable.value,
    done: false,
  })
  clearCart()
  goto('more', { sub: 'orders' })
  say('ഓർഡർ സേവ് ചെയ്തു')
}

export const share = async () => {
  const r = state.receipt
  if (!r) return
  const text = 'ബിൽ #' + r.id + '\n' + r.items.map((i) => i.n + ' ' + i.q + '×' + i.price).join('\n') + '\nആകെ: ₹' + r.total
  try {
    if (navigator.share) await navigator.share({ text })
    else { await navigator.clipboard.writeText(text); say('ബിൽ കോപ്പി ചെയ്തു') }
  } catch (e) {
    say('ഷെയർ ചെയ്യാൻ കഴിഞ്ഞില്ല')
  }
}

export const loadProducts = async () => {
  try {
    const response = await fetch(`${API_BASE}/products`)
    if (!response.ok) throw new Error('Could not load products')
    const products = await response.json()
    state.products.splice(0, state.products.length, ...products.map((p) => ({
      id: p.id,
      n: p.name,
      sku: p.sku,
      description: p.description,
      price: p.price,
      cost: p.cost,
      stock: p.stock,
      min: p.minimum_stock,
      unit: p.unit,
      sold: p.sold,
      exp: p.expiry_days,
    })))
    refreshBuy()
  } catch (error) {
    say('ERP സെർവർ ബന്ധിപ്പിക്കാൻ കഴിഞ്ഞില്ല')
  }
}

export const loadStock = async () => {
  try {
    const response = await fetch(`${API_BASE}/stock`)
    if (!response.ok) throw new Error('Could not load stock')
    const stock = await response.json()
    const byId = new Map(stock.map((item) => [item.id, item]))
    state.products.forEach((product) => {
      const item = byId.get(product.id)
      if (item) product.stock = item.stock
    })
  } catch (error) {
    say('സ്റ്റോക്ക് ലോഡ് ചെയ്യാൻ കഴിഞ്ഞില്ല')
  }
}

export const loadSalesSummary = async () => {
  try {
    const response = await fetch(`${API_BASE}/stock/sales/summary`)
    if (!response.ok) throw new Error('Could not load sales summary')
    const summary = await response.json()
    state.salesSummary.totalSales = summary.total_sales
    state.salesSummary.profit = summary.profit
    state.salesSummary.quantitySold = summary.quantity_sold
  } catch (error) {
    say('വിൽപ്പന വിവരങ്ങൾ ലോഡ് ചെയ്യാൻ കഴിഞ്ഞില്ല')
  }
}

export const loadStockHistory = async () => {
  try {
    const movements = []
    for (const product of state.products) {
      const response = await fetch(`${API_BASE}/stock/${product.id}/movements`)
      if (!response.ok) continue
      const rows = await response.json()
      rows.forEach((row) => movements.push({
        n: product.n,
        d: row.movement_type === 'IN' ? row.quantity : -row.quantity,
        why: row.note || (row.movement_type === 'IN' ? 'സ്റ്റോക്ക് ചേർത്തു' : 'സ്റ്റോക്ക് കുറച്ചു'),
        t: row.created_at ? new Date(row.created_at).toLocaleTimeString('ml-IN', { hour: '2-digit', minute: '2-digit' }) : '',
        createdAt: row.created_at,
      }))
    }
    movements.sort((a, b) => String(b.createdAt || '').localeCompare(String(a.createdAt || '')))
    state.history.splice(0, state.history.length, ...movements)
  } catch (error) {
    say('സ്റ്റോക്ക് ചരിത്രം ലോഡ് ചെയ്യാൻ കഴിഞ്ഞില്ല')
  }
}

export const loadCredits = async () => {
  try {
    const response = await fetch(`${API_BASE}/credits`)
    if (!response.ok) throw new Error('Could not load credits')
    const credits = await response.json()
    state.customers.splice(0, state.customers.length, ...credits.map((credit) => {
      const payDate = credit.pay_at ? new Date(credit.pay_at).toLocaleDateString('ml-IN') : ''
      return {
        id: credit.id,
        n: credit.name,
        ph: '-',
        amount: credit.amount,
        payAt: credit.pay_at,
        isPaid: credit.is_paid,
        tx: [{
          k: credit.is_paid ? 'pay' : 'give',
          a: credit.amount,
          d: payDate,
        }],
      }
    }))
  } catch (error) {
    say('കടം ലോഡ് ചെയ്യാൻ കഴിഞ്ഞില്ല')
  }
}

export const addProduct = async () => {
  const payload = {
    name: state.np.n,
    sku: state.np.sku || `SKU-${Date.now()}`,
    description: state.np.description || null,
    price: state.np.price,
    cost: state.np.cost,
    initial_stock: state.np.stock,
    unit: state.np.unit,
    minimum_stock: state.np.min,
    expiry_days: state.np.expiryDays,
  }
  try {
    const response = await fetch(`${API_BASE}/products`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Could not add product')
    }
    await Promise.all([loadProducts(), loadStockHistory()])
    state.showAdd = false
    Object.assign(state.np, { n: '', sku: '', description: '', cost: 0, price: 0, stock: 0, min: 5, unit: 'കിലോ', expiryDays: null })
    say('സാധനം ചേർത്തു')
  } catch (error) {
    say(error.message)
  }
}

export const deleteProduct = async (productId) => {
  try {
    const response = await fetch(`${API_BASE}/products/${productId}`, { method: 'DELETE' })
    if (!response.ok) throw new Error('സാധനം നീക്കം ചെയ്യാൻ കഴിഞ്ഞില്ല')
    await loadProducts()
    say('സാധനം നീക്കം ചെയ്തു')
  } catch (error) {
    say(error.message)
  }
}

export const deleteCredit = async (creditId) => {
  try {
    const response = await fetch(`${API_BASE}/credits/${creditId}`, { method: 'DELETE' })
    if (!response.ok) throw new Error('കടം നീക്കം ചെയ്യാൻ കഴിഞ്ഞില്ല')
    await loadCredits()
    if (state.cust?.id === creditId) state.cust = null
    say('കടം നീക്കം ചെയ്തു')
  } catch (error) {
    say(error.message)
  }
}

export const doAdj = async () => {
  if (!state.adj) return
  const productId = state.adj.id
  const quantity = state.adjQty || 0
  try {
    if (quantity) {
      const endpoint = quantity > 0 ? 'add' : 'remove'
      const response = await fetch(`${API_BASE}/stock/${productId}/${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ quantity: Math.abs(quantity), note: 'Frontend stock adjustment' }),
      })
      if (!response.ok) throw new Error('സ്റ്റോക്ക് മാറ്റാൻ കഴിഞ്ഞില്ല')
    }
    const response = await fetch(`${API_BASE}/products/${productId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ price: state.adj.price }),
    })
    if (!response.ok) throw new Error('വില അപ്ഡേറ്റ് ചെയ്യാൻ കഴിഞ്ഞില്ല')
    await Promise.all([loadProducts(), loadStockHistory()])
    state.adjQty = 0
    state.adj = null
    say('അപ്ഡേറ്റ് ചെയ്തു')
  } catch (error) {
    say(error.message)
  }
}

export const receiveBuy = async () => {
  const received = state.buyList.filter((s) => s.got)
  try {
    for (const item of received) {
      const response = await fetch(`${API_BASE}/stock/${item.id}/add`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ quantity: item.qty, note: 'Purchase/restock received' }),
      })
      if (!response.ok) throw new Error('സ്റ്റോക്ക് അപ്ഡേറ്റ് ചെയ്യാൻ കഴിഞ്ഞില്ല')
    }
    await Promise.all([loadProducts(), loadStockHistory()])
    say(received.length ? 'സ്റ്റോക്ക് അപ്ഡേറ്റ് ചെയ്തു' : 'എന്തെങ്കിലും സാധനം തിരഞ്ഞെടുക്കൂ')
  } catch (error) {
    say(error.message)
  }
}

export const txn = async (k) => {
  if (!state.cust || !state.amt) return
  try {
    if (k === 'give') {
      const nextAmount = bal(state.cust) + state.amt
      const response = await fetch(`${API_BASE}/credits/${state.cust.id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ amount: nextAmount }),
      })
      if (!response.ok) throw new Error('കടം അപ്ഡേറ്റ് ചെയ്യാൻ കഴിഞ്ഞില്ല')
    } else {
      const remaining = bal(state.cust) - state.amt
      if (remaining > 0) {
        const response = await fetch(`${API_BASE}/credits/${state.cust.id}`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ amount: remaining }),
        })
        if (!response.ok) throw new Error('പണം രേഖപ്പെടുത്താൻ കഴിഞ്ഞില്ല')
      } else {
        const response = await fetch(`${API_BASE}/credits/${state.cust.id}/pay`, {
          method: 'POST',
        })
        if (!response.ok) throw new Error('പണം രേഖപ്പെടുത്താൻ കഴിഞ്ഞില്ല')
      }
    }
    await loadCredits()
    const updated = state.customers.find((customer) => customer.id === state.cust.id)
    if (updated) state.cust = updated
    state.amt = null
    say(k === 'give' ? 'കടം രേഖപ്പെടുത്തി' : 'പണം രേഖപ്പെടുത്തി')
  } catch (error) {
    say(error.message)
  }
}

export const remind = () => {
  const c = state.cust
  const text = 'നമസ്കാരം ' + c.n + ', ₹' + bal(c) + ' ബാക്കിയുണ്ട്. സൗകര്യം പോലെ തരുമല്ലോ. നന്ദി 🙏'
  window.open('https://wa.me/91' + c.ph.replace(/\D/g, '') + '?text=' + encodeURIComponent(text), '_blank')
}

export const addCust = async () => {
  if (!state.nc.n || !state.nc.amount || !state.nc.payAt) return
  try {
    const response = await fetch(`${API_BASE}/credits`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: state.nc.n,
        amount: state.nc.amount,
        pay_at: new Date(state.nc.payAt).toISOString(),
      }),
    })
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'കടം ചേർക്കാൻ കഴിഞ്ഞില്ല')
    }
    await loadCredits()
    state.nc.n = ''
    state.nc.ph = ''
    state.nc.amount = 0
    state.nc.payAt = ''
    state.newCust = false
    say('പുതിയ ആൾ ചേർത്തു')
  } catch (error) {
    say(error.message)
  }
}

// ---- AI assistant ----
const push = (r, t) => state.msgs.push({ r, t })
let lastCustomer = null
let askInFlight = 0

// ---- spoken replies (Sarvam TTS through the backend) ----
let speechToken = 0
let currentSource = null
let currentAudioEl = null

const base64ToBuffer = (b64) => {
  const binary = atob(b64)
  const bytes = new Uint8Array(binary.length)
  for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i)
  return bytes.buffer
}

export const stopSpeaking = () => {
  speechToken++
  try { currentSource?.stop() } catch (_) {}
  currentSource = null
  if (currentAudioEl) {
    currentAudioEl.pause()
    currentAudioEl = null
  }
  state.speaking = false
}

const playBuffer = async (buffer) => {
  // Prefer the AudioContext that is already running for the microphone: it is
  // allowed to make sound, so the browser's autoplay rules can't block the reply.
  if (wakeAudioContext && wakeAudioContext.state === 'running') {
    const decoded = await wakeAudioContext.decodeAudioData(buffer)
    await new Promise((resolve) => {
      const source = wakeAudioContext.createBufferSource()
      source.buffer = decoded
      source.connect(wakeAudioContext.destination)
      source.onended = resolve
      currentSource = source
      source.start()
    })
    return
  }
  const url = URL.createObjectURL(new Blob([buffer], { type: 'audio/wav' }))
  try {
    const audio = new Audio(url)
    currentAudioEl = audio
    await new Promise((resolve, reject) => {
      audio.onended = resolve
      audio.onerror = reject
      audio.play().catch(reject)
    })
  } finally {
    URL.revokeObjectURL(url)
  }
}

export const speak = async (text) => {
  const clean = (text || '').trim()
  if (!clean) return
  stopSpeaking()
  const token = speechToken
  state.speaking = true // the microphone sends silence while this is true
  try {
    const response = await fetch(`${API_BASE}/ai/tts`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: clean }),
    })
    if (!response.ok) throw new Error('TTS request failed')
    const { audios } = await response.json()
    for (const b64 of audios) {
      if (token !== speechToken) return // interrupted
      await playBuffer(base64ToBuffer(b64))
    }
  } catch (error) {
    console.warn('Could not speak the reply:', error)
    say('ശബ്ദം പ്ലേ ചെയ്യാൻ കഴിഞ്ഞില്ല')
  } finally {
    if (token === speechToken) state.speaking = false
  }
}

// voice = true when the question came from the microphone: the reply is read out.
export const ask = async (text, { voice = false } = {}) => {
  const t = (text || '').trim()
  if (!t) return
  state.inp = ''
  push('u', t)
  state.listening = true
  askInFlight++

  let reply = ''
  try {
    const response = await fetch(`${API_BASE}/ai/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: t }),
    })
    const payload = await response.json()
    if (!response.ok) {
      throw new Error(payload.detail || 'AI Anfrage luktathu')
    }

    reply = payload.reply || 'മുൻകൂട്ടി തിരിച്ചറിഞ്ഞതൊന്നും ലഭിച്ചില്ല.'
    push('b', reply)

    // The backend already ran the function the model picked (once, server side).
    // The screen only needs to reload the data it changed.
    if (payload.tool && payload.tool !== 'general') {
      await Promise.all([loadProducts(), loadStockHistory(), loadSalesSummary(), loadCredits()])
    }
  } catch (error) {
    push('b', `AI ബന്ധപ്പെട്ടതിൽ പിഴവ്: ${error.message}`)
  } finally {
    askInFlight--
    state.listening = false
  }

  if (voice && reply) await speak(reply)
}

let wakeRecognition = null
let wakeEnabled = false
let wakeRestartTimer = null
let lastWakeTime = 0
let wakeTriggerTimer = null
let wakeMediaStream = null
let wakeAudioContext = null
let wakeProcessor = null
let wakeWatchdog = null
let lastWakeMessage = 0

const floatToPcm16 = (samples) => {
  const pcm = new Int16Array(samples.length)
  for (let i = 0; i < samples.length; i++) {
    const value = Math.max(-1, Math.min(1, samples[i]))
    pcm[i] = value < 0 ? value * 32768 : value * 32767
  }
  return pcm.buffer
}

const startFrontendMicrophone = async () => {
  if (!navigator.mediaDevices?.getUserMedia) {
    say('ഈ ബ്രൗസറിൽ മൈക്രോഫോൺ ലഭ്യമല്ല')
    return false
  }
  if (wakeMediaStream) return true

  try {
    wakeMediaStream = await navigator.mediaDevices.getUserMedia({
      audio: {
        channelCount: 1,
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true,
      },
      video: false,
    })

    wakeAudioContext = new AudioContext({ sampleRate: 16000 })
    await wakeAudioContext.resume()
    const source = wakeAudioContext.createMediaStreamSource(wakeMediaStream)
    wakeProcessor = wakeAudioContext.createScriptProcessor(4096, 1, 1)
    wakeProcessor.onaudioprocess = (event) => {
      if (
        wakeEnabled &&
        wakeRecognition?.readyState === WebSocket.OPEN
      ) {
        const samples = event.inputBuffer.getChannelData(0)
        // While a reply is playing, send silence so the detector never hears it
        // (the stream keeps flowing, so the backend's timeline stays continuous).
        const pcm = floatToPcm16(state.speaking ? new Float32Array(samples.length) : samples)
        wakeRecognition.send(pcm)
      }
    }
    source.connect(wakeProcessor)
    wakeProcessor.connect(wakeAudioContext.destination)
    state.wakeListening = true
    say('മൈക്രോഫോൺ സജീവമായി')
    return true
  } catch (error) {
    wakeMediaStream = null
    state.wakeListening = false
    say(error.name === 'NotAllowedError'
      ? 'മൈക്രോഫോൺ അനുമതി അനുവദിക്കൂ'
      : 'മൈക്രോഫോൺ തുറക്കാൻ കഴിഞ്ഞില്ല')
    return false
  }
}

const triggerWakeWord = (phrase) => {
  const now = Date.now()
  if (now - lastWakeTime < 2500) return
  lastWakeTime = now
  state.wakeTriggered = true
  state.chatOpen = true
  say('Wake word detected: Hey Jarvis')

  clearTimeout(wakeTriggerTimer)
  wakeTriggerTimer = setTimeout(() => { state.wakeTriggered = false }, 1800)
}

const startWakeWatchdog = () => {
  if (wakeWatchdog) return
  wakeWatchdog = setInterval(() => {
    // The server sends a heartbeat every 10 s. 30 s of silence means the
    // connection is dead even though the browser hasn't noticed: replace it.
    if (
      wakeEnabled &&
      wakeRecognition?.readyState === WebSocket.OPEN &&
      Date.now() - lastWakeMessage > 30000
    ) {
      const dead = wakeRecognition
      wakeRecognition = null
      try { dead.close() } catch (_) {}
      startWakeWord()
    }
  }, 5000)
}

const connectWakeSocket = () => {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const socket = new WebSocket(`${protocol}//${window.location.host}/ws/wake`)
  wakeRecognition = socket

  socket.onopen = () => {
    lastWakeMessage = Date.now()
    state.wakeListening = true
    startWakeWatchdog()
  }
  socket.onmessage = (event) => {
    lastWakeMessage = Date.now()
    try {
      const payload = JSON.parse(event.data)
      if (payload.type === 'wake') triggerWakeWord(payload.wakeWord)
      if (payload.type === 'transcript' && payload.transcript) {
        state.chatOpen = true
        ask(payload.transcript, { voice: true })
      }
      if (payload.type === 'status') {
        state.wakeListening = payload.status === 'listening'
        if (payload.status === 'recording') state.listening = true
        if (payload.status === 'transcribing') state.listening = true
        // 'listening' arrives right after the transcript; keep the indicator on while the AI answers
        if (payload.status === 'listening' && !askInFlight) state.listening = false
        if (payload.status === 'error') say(payload.message || 'Wake-word listener unavailable')
        if (payload.reason === 'no_speech') say('ഒന്നും കേട്ടില്ല')
      }
    } catch (error) {
      console.warn('Bad wake-word message:', error)
    }
  }
  socket.onerror = () => { state.wakeListening = false }
  socket.onclose = () => {
    // Ignore sockets that were already replaced or stopped on purpose.
    if (wakeRecognition !== socket) return
    wakeRecognition = null
    state.wakeListening = false
    if (!wakeEnabled) return
    clearTimeout(wakeRestartTimer)
    wakeRestartTimer = setTimeout(startWakeWord, 1000)
  }
}

export const startWakeWord = async () => {
  state.wakeSupported = true
  wakeEnabled = true
  const socketState = wakeRecognition?.readyState
  // CONNECTING counts too, otherwise a slow connect spawns duplicate sockets.
  if (socketState !== WebSocket.OPEN && socketState !== WebSocket.CONNECTING) {
    connectWakeSocket()
  }

  await startFrontendMicrophone()
  return true
}

export const stopWakeWord = () => {
  wakeEnabled = false
  clearTimeout(wakeRestartTimer)
  clearInterval(wakeWatchdog)
  wakeWatchdog = null
  stopSpeaking()
  state.wakeListening = false
  if (wakeProcessor) {
    wakeProcessor.disconnect()
    wakeProcessor.onaudioprocess = null
    wakeProcessor = null
  }
  if (wakeAudioContext) {
    wakeAudioContext.close().catch(() => {})
    wakeAudioContext = null
  }
  if (wakeMediaStream) {
    wakeMediaStream.getTracks().forEach((track) => track.stop())
    wakeMediaStream = null
  }
  if (wakeRecognition) {
    const socket = wakeRecognition
    wakeRecognition = null
    try { socket.close() } catch (_) {}
  }
}

export const mic = () => {
  stopSpeaking()
  if (!wakeEnabled) startWakeWord()

  const sendCommand = () => {
    if (wakeRecognition?.readyState === WebSocket.OPEN) {
      wakeRecognition.send(JSON.stringify({ type: 'start_recording' }))
    } else {
      say('ബാക്കെൻഡ് മൈക്ക് തയ്യാറായിട്ടില്ല')
    }
  }

  if (wakeRecognition?.readyState === WebSocket.OPEN) {
    sendCommand()
  } else {
    setTimeout(sendCommand, 300)
  }
}

export const scrollMsgs = (el) => {
  if (!el) return
  nextTick(() => { el.scrollTop = el.scrollHeight })
}

