/* ============================================================
   app.js  ·  DataViz Portfolio — Rich Analytics Dashboard
   ============================================================ */
'use strict';

// ── Global state ──────────────────────────────────────────────
let activeSection = 'overview';
let isDark = true;
let charts = {};

// ── Chart.js global defaults ──────────────────────────────────
Chart.defaults.font.family = "'Inter', system-ui, sans-serif";
Chart.defaults.font.size = 11.5;
Chart.defaults.color = '#58534d';
Chart.defaults.borderColor = 'rgba(255,255,255,0.07)';

// ── Design palette ────────────────────────────────────────────
const P = {
  gold:    '#c9a84c',
  goldbr:  '#e8c56a',
  golddm:  '#8a6e2e',
  steel:   '#5b8fa8',
  sage:    '#7eaa72',
  terra:   '#b07856',
  violet:  '#8472b0',
  teal:    '#58a89e',
  green:   '#3d9970',
  red:     '#c0392b',
};

function hex2rgba(hex, a) {
  const [r,g,b] = [1,3,5].map(i => parseInt(hex.slice(i,i+2),16));
  return `rgba(${r},${g},${b},${a})`;
}

function makeGrad(ctx, color, h) {
  const g = ctx.createLinearGradient(0,0,0,h||300);
  g.addColorStop(0, hex2rgba(color, 0.55));
  g.addColorStop(1, hex2rgba(color, 0.02));
  return g;
}

// Chart colours in order
const CHART_COLORS = [P.gold, P.steel, P.sage, P.terra, P.violet, P.teal];

// ── Shared tooltip config ─────────────────────────────────────
const TIP = {
  backgroundColor: '#1a1915',
  borderColor: 'rgba(201,168,76,0.2)',
  borderWidth: 1,
  titleColor: '#f5f0e8',
  bodyColor: '#8e8880',
  padding: 12,
  cornerRadius: 8,
  displayColors: true,
  boxPadding: 4,
};

// ── Grid line colours (context-aware) ─────────────────────────
function gridColor() {
  return isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.07)';
}

function tickColor() {
  return isDark ? '#58534d' : '#9a9088';
}

// ── Shared scale config ───────────────────────────────────────
function xScale(extra = {}) {
  return {
    grid: { color: gridColor(), drawBorder: false },
    ticks: { color: tickColor(), maxTicksLimit: 8 },
    border: { display: false },
    ...extra
  };
}

function yScale(extra = {}) {
  return {
    grid: { color: gridColor(), drawBorder: false },
    ticks: { color: tickColor() },
    border: { display: false },
    ...extra
  };
}

// ============================================================
// DATE / CLOCK
// ============================================================
// ============================================================
// MARKET TICKER
// ============================================================
const TICKERS = [
  { name:'EMEA Rev',  val:'$1.82B', chg:'+22.4%', up:true  },
  { name:'APAC Rev',  val:'$1.46B', chg:'+31.7%', up:true  },
  { name:'Americas',  val:'$1.54B', chg:'+14.1%', up:true  },
  { name:'Enterprise',val:'38%',    chg:'share',   up:true  },
  { name:'Churn',     val:'11%',    chg:'−28pt',   up:true  },
  { name:'NPS',       val:'67',     chg:'+35pt',   up:true  },
  { name:'CAC',       val:'$30',    chg:'−38%',    up:true  },
  { name:'Conv Rate', val:'3.84%',  chg:'−1.2pt',  up:false },
  { name:'CSAT',      val:'94.7%',  chg:'+20pt',   up:true  },
  { name:'ARR',       val:'$4.82B', chg:'+18.4%',  up:true  },
];

function buildTicker() {
  const inner = document.getElementById('tickerInner');
  if (!inner) return;
  // Double the list so the scroll loop is seamless
  const items = [...TICKERS, ...TICKERS];
  inner.innerHTML = items.map(t => `
    <span class="ticker-item">
      <span class="t-name">${t.name}</span>
      <span>${t.val}</span>
      <span class="${t.up?'t-up':'t-dn'}">${t.up?'▲':'▼'} ${t.chg}</span>
    </span>
  `).join('');
}

// ============================================================
// RING PROGRESS ANIMATION
// ============================================================
function animateRing(id, pct) {
  const el = document.getElementById(id);
  if (!el) return;
  const circumference = 2 * Math.PI * 18; // r=18 → ≈ 113.1
  el.style.strokeDasharray = circumference;
  el.style.strokeDashoffset = circumference; // start fully hidden
  const offset = circumference * (1 - Math.min(pct, 100) / 100);
  setTimeout(() => { el.style.strokeDashoffset = offset; }, 250);
}

function updateClock() {
  const now = new Date();
  const utc = now.toUTCString().slice(17,22);
  const el = document.getElementById('metaClock');
  if (el) el.textContent = `${utc} UTC`;
  const db = document.getElementById('dateBadge');
  if (db) db.textContent = now.toLocaleDateString('en-US',{month:'short',day:'numeric',year:'numeric'});
}
updateClock();
setInterval(updateClock, 30000);

// ============================================================
// NAVIGATION
// ============================================================
const PAGE_META = {
  overview:     { title:'Overview',     sub:'Global market & performance analytics' },
  trends:       { title:'Trends',       sub:'Time-series analysis & pattern discovery' },
  distribution: { title:'Distribution', sub:'Statistical spread, scatter & frequency' },
  comparison:   { title:'Comparison',   sub:'Benchmarking across regions & products' },
  geospatial:   { title:'Geospatial',   sub:'Regional revenue on the world stage' },
  insights:     { title:'Insights',     sub:'Data story: The Q2 2024 growth inflection' },
};

function showSection(id, el) {
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  if (el) el.classList.add('active');

  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  const sec = document.getElementById('section-' + id);
  if (sec) sec.classList.add('active');

  const m = PAGE_META[id] || {};
  document.getElementById('pageHeading').textContent  = m.title || id;
  document.getElementById('pageSubtitle').textContent = m.sub   || '';

  activeSection = id;
  setTimeout(() => lazyInit(id), 60);

  if (window.innerWidth <= 860) document.getElementById('sidebar').classList.remove('open');
}

function lazyInit(id) {
  switch(id) {
    case 'overview':     initOverview();     break;
    case 'trends':       initTrends();       break;
    case 'distribution': initDistribution(); break;
    case 'comparison':   initComparison();   break;
    case 'geospatial':   initGeospatial();   break;
    case 'insights':     initInsights();     break;
  }
}

function toggleSidebar() {
  document.getElementById('sidebar').classList.toggle('open');
}

// ============================================================
// THEME
// ============================================================
function toggleTheme() {
  isDark = !isDark;
  document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light');

  Chart.defaults.color       = isDark ? '#58534d' : '#9a9088';
  Chart.defaults.borderColor = isDark ? 'rgba(255,255,255,0.07)' : 'rgba(0,0,0,0.08)';

  // Rebuild all Chart.js charts
  Object.keys(charts).forEach(k => { charts[k].destroy(); delete charts[k]; });

  // Reset D3 containers
  const hm = document.getElementById('heatmapContainer');
  if (hm) { hm.innerHTML = ''; delete hm.dataset.built; }
  const wc = document.getElementById('wordCloudContainer');
  if (wc) { wc.innerHTML = ''; delete wc.dataset.built; }
  const gm = document.getElementById('geoMap');
  if (gm) { gm.innerHTML = ''; delete gm.dataset.built; }
  const fc = document.getElementById('funnelChart');
  if (fc) { fc.innerHTML = ''; delete fc.dataset.built; }

  // Reset feed so it rebuilds with correct theme colors
  const fl = document.getElementById('feedList');
  if (fl) { fl.innerHTML = ''; delete fl.dataset.built; }

  // Re-enable ring animations
  document.querySelectorAll('.kpi-ring-fill').forEach(r => {
    r.style.strokeDashoffset = 2 * Math.PI * 18;
  });

  lazyInit(activeSection);
}

// ============================================================
// KPI COUNTER ANIMATION
// ============================================================
function animateKPI(el) {
  const target = parseFloat(el.dataset.target);
  const pre    = el.dataset.prefix  || '';
  const suf    = el.dataset.suffix  || '';
  const dur    = 1600;
  const t0     = performance.now();

  function step(now) {
    const p   = Math.min((now - t0) / dur, 1);
    const ease = 1 - Math.pow(1 - p, 3);
    const val  = target * ease;
    let disp;
    if (target >= 1000000) disp = (val/1000000).toFixed(1);
    else if (target >= 1000 && suf === 'K') disp = (val/1000).toFixed(1);
    else if (target < 10) disp = val.toFixed(1);
    else disp = Math.round(val).toLocaleString();

    let rs = suf;
    if (target >= 1000000 && suf !== '%') rs = 'B';

    el.textContent = `${pre}${disp}${rs}`;
    if (p < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

// ============================================================
// SPARKLINES
// ============================================================
function sparkline(id, data, color) {
  const el = document.getElementById(id);
  if (!el) return;
  if (charts[id]) charts[id].destroy();
  charts[id] = new Chart(el.getContext('2d'), {
    type: 'line',
    data: {
      labels: data.map((_,i)=>i),
      datasets:[{ data, borderColor: color, borderWidth: 1.5,
        pointRadius: 0, fill: true,
        backgroundColor: hex2rgba(color, 0.12), tension: 0.4 }]
    },
    options:{
      responsive:true, maintainAspectRatio:false,
      plugins:{ legend:{display:false}, tooltip:{enabled:false} },
      scales:{ x:{display:false}, y:{display:false} },
      animation:{ duration:1000 }
    }
  });
}

// ============================================================
// DATA
// ============================================================
const M12  = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
const M24  = [
  'Jan 24','Feb 24','Mar 24','Apr 24','May 24','Jun 24',
  'Jul 24','Aug 24','Sep 24','Oct 24','Nov 24','Dec 24',
  'Jan 25','Feb 25','Mar 25','Apr 25','May 25','Jun 25',
  'Jul 25','Aug 25','Sep 25','Oct 25','Nov 25','Dec 25'
];
const REV_ALL = [
  280,295,310,325,340,370,395,410,435,460,490,520,
  545,580,615,655,695,730,780,820,870,920,975,1030
];

// ============================================================
// SECTION: OVERVIEW
// ============================================================
let areaMode = 'all';

function initOverview() {
  document.querySelectorAll('.kpi-value').forEach(el => {
    if (!el.dataset.animated) { el.dataset.animated='1'; animateKPI(el); }
  });
  // Ring progress — pct of target reached
  animateRing('ring1', 78);  // revenue 78% of annual target
  animateRing('ring2', 84);  // users 84% of target
  animateRing('ring3', 96);  // conversion (near target)
  animateRing('ring4', 95);  // CSAT

  sparkline('spark1', [180,210,195,240,260,230,280,310,290,340,380,420], P.gold);
  sparkline('spark2', [90,120,110,130,160,145,175,200,185,220,250,280],  P.steel);
  sparkline('spark3', [3.9,3.7,4.1,3.8,3.6,3.9,4.0,3.7,3.5,3.8,3.9,3.84], P.terra);
  sparkline('spark4', [80,82,83,85,84,87,88,90,91,93,94,95], P.green);

  buildAreaChart(areaMode);
  if (!charts['donut']) buildDonut();
  buildFeed();
}

function switchAreaData(mode, btn) {
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  areaMode = mode;
  buildAreaChart(mode);
}

function buildAreaChart(mode) {
  const el = document.getElementById('areaChart');
  if (!el) return;
  if (charts['area']) charts['area'].destroy();
  const ctx = el.getContext('2d');

  let labels, d1, d2, d3;
  if (mode === '2024') {
    labels = M12;
    d1 = [160,172,181,196,210,228,242,258,275,291,312,335];
    d2 = [80,88,92,97,104,112,120,128,135,143,152,162];
    d3 = [40,35,37,32,26,30,33,24,25,26,26,23];
  } else if (mode === '2025') {
    labels = M12;
    d1 = [320,338,358,382,408,432,462,490,522,558,595,638];
    d2 = [150,163,176,191,207,221,238,256,274,294,316,340];
    d3 = [75,79,81,82,80,77,80,74,74,68,64,52];
  } else {
    labels = M24;
    d1 = [160,172,181,196,210,228,242,258,275,291,312,335,320,338,358,382,408,432,462,490,522,558,595,638];
    d2 = [80,88,92,97,104,112,120,128,135,143,152,162,150,163,176,191,207,221,238,256,274,294,316,340];
    d3 = [40,35,37,32,26,30,33,24,25,26,26,23,75,79,81,82,80,77,80,74,74,68,64,52];
  }

  const h = el.clientHeight || 280;

  charts['area'] = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [
        { label:'Enterprise', data:d1, borderColor:P.gold,  backgroundColor:makeGrad(ctx,P.gold,h),  borderWidth:2, fill:true, tension:0.4, pointRadius:0, pointHoverRadius:5, pointHoverBackgroundColor:P.gold },
        { label:'SMB',        data:d2, borderColor:P.steel, backgroundColor:makeGrad(ctx,P.steel,h), borderWidth:2, fill:true, tension:0.4, pointRadius:0, pointHoverRadius:5, pointHoverBackgroundColor:P.steel },
        { label:'Consumer',   data:d3, borderColor:P.terra, backgroundColor:makeGrad(ctx,P.terra,h), borderWidth:2, fill:true, tension:0.4, pointRadius:0, pointHoverRadius:5, pointHoverBackgroundColor:P.terra },
      ]
    },
    options: {
      responsive:true, maintainAspectRatio:false,
      interaction:{ mode:'index', intersect:false },
      plugins:{
        legend:{ display:true, position:'top', align:'end',
          labels:{ usePointStyle:true, pointStyle:'circle', boxWidth:7, padding:18, color: tickColor(), font:{size:11} }
        },
        tooltip:{ ...TIP, callbacks:{ label: c => ` ${c.dataset.label}: $${c.parsed.y}M` } },
        annotation: mode === 'all' ? {
          annotations:{
            pivotLine:{
              type:'line', xMin:5, xMax:5,
              borderColor: hex2rgba(P.gold, 0.5),
              borderWidth: 1.5, borderDash:[5,3],
              label:{ display:true, content:'Q2 Pivot ↕', position:'start',
                yAdjust:10, backgroundColor: hex2rgba(P.gold, 0.12),
                color: P.gold, font:{ size:10, family:"'Inter',sans-serif", weight:'600' },
                padding:{ x:8, y:4 }, borderRadius:4 }
            },
            targetLine:{
              type:'line', yMin:800, yMax:800,
              borderColor: hex2rgba(P.green, 0.35),
              borderWidth:1, borderDash:[3,4],
              label:{ display:true, content:'Target $800M', position:'end',
                yAdjust:-10, backgroundColor: hex2rgba(P.green,0.1),
                color: P.green, font:{ size:9.5, family:"'Inter',sans-serif", weight:'600' },
                padding:{ x:7, y:3 }, borderRadius:3 }
            }
          }
        } : {}
      },
      scales:{ x: xScale({ ticks:{...xScale().ticks, maxTicksLimit:8} }), y: yScale({ ticks:{ ...yScale().ticks, callback: v=>`$${v}M` } }) },
      animation:{ duration:700, easing:'easeInOutCubic' }
    }
  });
}

// ============================================================
// LIVE ACTIVITY FEED
// ============================================================
const FEED_EVENTS = [
  { icon:'💰', text:'Enterprise deal closed — Deutsche Bank, EMEA',   tag:'win',   badge:'badge-win'   },
  { icon:'📊', text:'Q3 2025 forecast revised upward to $3.4B',        tag:'update',badge:'badge-info'  },
  { icon:'🚀', text:'APAC ARR crossed $1.46B milestone',               tag:'growth',badge:'badge-up'    },
  { icon:'👥', text:'234 new enterprise accounts onboarded this week',  tag:'users', badge:'badge-up'    },
  { icon:'🎯', text:'NPS score reached all-time high of 67',           tag:'quality',badge:'badge-win'  },
  { icon:'⚠️', text:'Conversion rate dipped −1.2pt vs last month',     tag:'alert', badge:'badge-alert' },
  { icon:'🔄', text:'Retention program #12 launched in LATAM',         tag:'launch',badge:'badge-event' },
  { icon:'📈', text:'SMB segment grew 28.3% quarter over quarter',     tag:'growth',badge:'badge-up'    },
  { icon:'🌍', text:'Germany became top EMEA contributor at $340M',     tag:'win',   badge:'badge-win'   },
  { icon:'🤝', text:'Partnership signed with SAP — 12 markets',        tag:'event', badge:'badge-event' },
  { icon:'📱', text:'Mobile MAU exceeded desktop for the first time',  tag:'update',badge:'badge-info'  },
  { icon:'💡', text:'AI upsell feature drove $42M incremental ARR',    tag:'growth',badge:'badge-up'    },
];

let feedIdx = 0;
let feedMinutes = 1;

function buildFeed() {
  const list = document.getElementById('feedList');
  if (!list || list.dataset.built) return;
  list.dataset.built = '1';

  // Show first 6 events immediately
  FEED_EVENTS.slice(0, 6).forEach((ev, i) => {
    const mins = (i + 1) * 2;
    list.appendChild(makeFeedItem(ev, `${mins}m ago`));
  });
  feedIdx = 6;

  // New event every 5 seconds
  setInterval(() => {
    if (document.getElementById('feedList')) {
      const ev = FEED_EVENTS[feedIdx % FEED_EVENTS.length];
      const item = makeFeedItem(ev, 'just now');
      item.classList.add('feed-new');
      list.prepend(item);
      // Update all "just now" to proper times
      list.querySelectorAll('.feed-time').forEach((t, i) => {
        if (i > 0) {
          const existing = parseInt(t.textContent) || 0;
          if (t.textContent.includes('m ago')) t.textContent = `${Math.min(existing + 1, 30)}m ago`;
        }
      });
      // Remove last if too long
      if (list.children.length > 10) list.removeChild(list.lastChild);
      feedIdx++;
    }
  }, 5000);
}

function makeFeedItem(ev, time) {
  const div = document.createElement('div');
  div.className = 'feed-item';
  div.innerHTML = `
    <div class="feed-icon">${ev.icon}</div>
    <div class="feed-body">
      <p class="feed-text">${ev.text}</p>
      <p class="feed-time">${time}</p>
    </div>
    <span class="feed-badge ${ev.badge}">${ev.tag}</span>
  `;
  return div;
}

function buildDonut() {
  const el = document.getElementById('donutChart');
  if (!el) return;
  const ctx = el.getContext('2d');
  const labels = ['Enterprise','SMB','Consumer','Partners','Other'];
  const values = [38,28,17,12,5];
  const colors = CHART_COLORS;

  charts['donut'] = new Chart(ctx, {
    type: 'doughnut',
    data:{
      labels,
      datasets:[{
        data: values,
        backgroundColor: colors.map(c=>hex2rgba(c,0.85)),
        borderColor: colors,
        borderWidth:2,
        hoverOffset:10,
        borderRadius:4,
      }]
    },
    options:{
      responsive:true, maintainAspectRatio:false,
      cutout:'74%',
      plugins:{
        legend:{display:false},
        tooltip:{ ...TIP, callbacks:{ label: c=>`  ${c.label}: ${c.raw}%` } }
      },
      animation:{ animateRotate:true, duration:900 }
    }
  });

  const lg = document.getElementById('donutLegend');
  if (lg) lg.innerHTML = labels.map((l,i)=>
    `<div class="dl-row">
      <div class="dl-dot" style="background:${colors[i]}"></div>
      <span>${l}</span>
      <span class="dl-pct">${values[i]}%</span>
    </div>`
  ).join('');
}

// ============================================================
// SECTION: TRENDS
// ============================================================
function initTrends() {
  buildMultiLine();
  buildHeatmap();
  buildBandChart();
}

function buildMultiLine() {
  const el = document.getElementById('multiLineChart');
  if (!el || charts['multiline']) return;
  const ctx = el.getContext('2d');

  charts['multiline'] = new Chart(ctx, {
    type: 'line',
    data:{
      labels: M24,
      datasets:[
        { label:'Revenue ($M)', data:REV_ALL, borderColor:P.gold, borderWidth:2, tension:0.4, pointRadius:0, pointHoverRadius:5, yAxisID:'y', fill:false },
        { label:'Users (K)',    data:[82,91,96,104,118,128,138,149,158,172,185,200,212,228,245,263,283,302,325,350,375,403,432,464], borderColor:P.steel, borderWidth:2, tension:0.4, pointRadius:0, pointHoverRadius:5, yAxisID:'y1', fill:false },
        { label:'Margin (%)',   data:[24,22,23,21,20,22,23,21,21,22,22,23,25,26,26,27,26,25,27,25,25,24,23,22], borderColor:P.terra, borderWidth:1.5, tension:0.4, pointRadius:0, pointHoverRadius:5, yAxisID:'y2', fill:false, borderDash:[5,4] }
      ]
    },
    options:{
      responsive:true, maintainAspectRatio:false,
      interaction:{ mode:'index', intersect:false },
      plugins:{
        legend:{ display:true, position:'top', align:'end', labels:{ usePointStyle:true, pointStyle:'circle', boxWidth:7, padding:18, color:tickColor(), font:{size:11} } },
        tooltip:{ ...TIP }
      },
      scales:{
        x: xScale({ ticks:{...xScale().ticks, maxTicksLimit:10} }),
        y:  yScale({ position:'left',  ticks:{...yScale().ticks, callback:v=>`$${v}M`, color:P.gold} }),
        y1: yScale({ position:'right', grid:{drawOnChartArea:false}, ticks:{...yScale().ticks, callback:v=>`${v}K`, color:P.steel} }),
        y2: { display:false }
      },
      animation:{ duration:800 }
    }
  });
}

function buildHeatmap() {
  const cont = document.getElementById('heatmapContainer');
  if (!cont || cont.dataset.built) return;
  cont.dataset.built = '1';

  const days  = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'];
  const hours = Array.from({length:12},(_,i)=>`${i*2}:00`);
  const data  = days.flatMap((d,di) =>
    hours.map((h,hi) => ({
      day:di, hour:hi,
      value: Math.round(20 + Math.random()*80 + (di<5 && hi>3 && hi<9 ? 40:0))
    }))
  );

  const w = cont.clientWidth || 340;
  const h = 210;
  const cellW = (w-44)/hours.length;
  const cellH = (h-28)/days.length;

  const svg = d3.select(cont).append('svg').attr('width',w).attr('height',h);

  const colorScale = d3.scaleSequential()
    .domain([0,140])
    .interpolator(d3.interpolate(
      isDark ? 'rgba(201,168,76,0.06)' : 'rgba(201,168,76,0.08)',
      isDark ? 'rgba(201,168,76,0.85)' : 'rgba(176,120,86,0.9)'
    ));

  svg.selectAll('rect.cell')
    .data(data).enter().append('rect')
    .attr('x', d=>44 + d.hour*cellW)
    .attr('y', d=>d.day*cellH + 2)
    .attr('width', cellW-3).attr('height', cellH-3).attr('rx',4)
    .attr('fill', d=>colorScale(d.value))
    .style('cursor','default')
    .on('mouseover', function(){ d3.select(this).attr('stroke',P.gold).attr('stroke-width',1.2); })
    .on('mouseout',  function(){ d3.select(this).attr('stroke',null); });

  svg.selectAll('text.day').data(days).enter().append('text')
    .attr('class','day')
    .attr('x',38).attr('y',(_,i)=>i*cellH+cellH/2+4)
    .attr('text-anchor','end')
    .attr('fill', tickColor())
    .attr('font-size',9.5).attr('font-family',"'Inter',sans-serif")
    .text(d=>d);

  svg.selectAll('text.hr').data(hours.filter((_,i)=>i%2===0)).enter().append('text')
    .attr('class','hr')
    .attr('x', (_,i)=>44+i*2*cellW+cellW)
    .attr('y', h-4)
    .attr('text-anchor','middle')
    .attr('fill', tickColor())
    .attr('font-size',8.5).attr('font-family',"'Inter',sans-serif")
    .text(d=>d);
}

function buildBandChart() {
  const el = document.getElementById('bandChart');
  if (!el || charts['band']) return;
  const ctx = el.getContext('2d');

  const trend  = REV_ALL.map((v,i)=>v+Math.sin(i/3)*14);
  const upper  = trend.map(v=>v+50+Math.random()*15);
  const lower  = trend.map(v=>v-50-Math.random()*15);

  charts['band'] = new Chart(ctx, {
    data:{
      labels: M24,
      datasets:[
        { type:'line', label:'Upper band', data:upper, borderColor:hex2rgba(P.gold,0.15), borderWidth:1, fill:'+1', backgroundColor:hex2rgba(P.gold,0.05), tension:0.4, pointRadius:0 },
        { type:'line', label:'Trend',      data:trend, borderColor:P.gold, borderWidth:2.5, fill:false, tension:0.4, pointRadius:0, pointHoverRadius:5 },
        { type:'line', label:'Lower band', data:lower, borderColor:hex2rgba(P.gold,0.15), borderWidth:1, fill:'-1', backgroundColor:hex2rgba(P.gold,0.05), tension:0.4, pointRadius:0 },
        { type:'bar',  label:'Actual',     data:REV_ALL, backgroundColor:hex2rgba(P.steel,0.18), borderColor:hex2rgba(P.steel,0.45), borderWidth:1, borderRadius:3, yAxisID:'y' }
      ]
    },
    options:{
      responsive:true, maintainAspectRatio:false,
      interaction:{ mode:'index', intersect:false },
      plugins:{
        legend:{ display:true, position:'top', align:'end', labels:{ usePointStyle:true, pointStyle:'circle', boxWidth:7, padding:16, color:tickColor(), font:{size:11} } },
        tooltip:{ ...TIP }
      },
      scales:{
        x: xScale({ ticks:{...xScale().ticks, maxTicksLimit:10} }),
        y: yScale({ ticks:{...yScale().ticks, callback:v=>`$${v}M`} })
      },
      animation:{ duration:800 }
    }
  });
}

// ============================================================
// SECTION: DISTRIBUTION
// ============================================================
function initDistribution() {
  buildHistogram(); buildScatter(); buildBubble(); buildBoxPlot(); buildWordCloud();
}

function buildHistogram() {
  const el = document.getElementById('histogramChart');
  if (!el || charts['hist']) return;
  const ctx = el.getContext('2d');
  const h = el.clientHeight || 260;
  const g = ctx.createLinearGradient(0,0,0,h);
  g.addColorStop(0, hex2rgba(P.gold, 0.8));
  g.addColorStop(1, hex2rgba(P.terra, 0.4));

  charts['hist'] = new Chart(ctx, {
    type:'bar',
    data:{
      labels:['18–24','25–31','32–38','39–45','46–52','53–59','60–66','67+'],
      datasets:[{ data:[18,26,22,15,10,5,3,1], backgroundColor:g, borderRadius:5, borderSkipped:false }]
    },
    options:{
      responsive:true, maintainAspectRatio:false,
      plugins:{ legend:{display:false}, tooltip:{ ...TIP, callbacks:{ label:c=>` ${c.raw}% of users` } } },
      scales:{
        x: xScale({ grid:{display:false} }),
        y: yScale({ ticks:{...yScale().ticks, callback:v=>`${v}%`} })
      },
      animation:{ duration:800 }
    }
  });
}

function buildScatter() {
  const el = document.getElementById('scatterChart');
  if (!el || charts['scatter']) return;
  const ctx = el.getContext('2d');

  const cluster = (cx,cy,n,spread,color,label) => ({
    label, data: Array.from({length:n},()=>({
      x: cx+(Math.random()-0.5)*spread*2,
      y: cy+(Math.random()-0.5)*spread*2
    })),
    backgroundColor: hex2rgba(color,0.5),
    borderColor: color,
    borderWidth:1.5, pointRadius:5, pointHoverRadius:7
  });

  charts['scatter'] = new Chart(ctx, {
    type:'scatter',
    data:{ datasets:[
      cluster(60,75,20,14,P.gold,'EMEA'),
      cluster(45,55,18,11,P.steel,'Americas'),
      cluster(80,62,15,13,P.sage,'APAC'),
      cluster(25,40,12,9, P.terra,'LATAM'),
    ]},
    options:{
      responsive:true, maintainAspectRatio:false,
      plugins:{
        legend:{ display:true, position:'top', align:'end', labels:{ usePointStyle:true, pointStyle:'circle', boxWidth:7, padding:14, color:tickColor(), font:{size:11} } },
        tooltip:{ ...TIP, callbacks:{ label:c=>` ${c.dataset.label}: (${c.parsed.x.toFixed(1)}, ${c.parsed.y.toFixed(1)})` } }
      },
      scales:{
        x: xScale({ title:{display:true, text:'Engagement Score', color:tickColor(), font:{size:10}} }),
        y: yScale({ title:{display:true, text:'Revenue Index',    color:tickColor(), font:{size:10}} })
      },
      animation:{ duration:800 }
    }
  });
}

function buildBubble() {
  const el = document.getElementById('bubbleChart');
  if (!el || charts['bubble']) return;
  const ctx = el.getContext('2d');
  const sectors = [
    { label:'SaaS',       x:72,y:34,r:26, color:P.gold   },
    { label:'E-Comm',     x:55,y:22,r:20, color:P.steel  },
    { label:'FinTech',    x:88,y:41,r:17, color:P.sage   },
    { label:'HealthTech', x:40,y:28,r:14, color:P.terra  },
    { label:'EdTech',     x:30,y:15,r:10, color:P.violet },
    { label:'GovTech',    x:18,y:8, r:7,  color:P.teal   },
  ];
  charts['bubble'] = new Chart(ctx, {
    type:'bubble',
    data:{ datasets: sectors.map(s=>({ label:s.label, data:[{x:s.x,y:s.y,r:s.r}], backgroundColor:hex2rgba(s.color,0.45), borderColor:s.color, borderWidth:1.5 })) },
    options:{
      responsive:true, maintainAspectRatio:false,
      plugins:{
        legend:{ display:true, position:'top', align:'end', labels:{ usePointStyle:true, pointStyle:'circle', boxWidth:7, padding:10, color:tickColor(), font:{size:10} } },
        tooltip:{ ...TIP, callbacks:{ label:c=>` ${c.dataset.label}: Growth ${c.raw.y}%, Mkt ~${c.raw.r*2}B` } }
      },
      scales:{
        x: xScale({ title:{display:true, text:'Profitability Index', color:tickColor(), font:{size:10}} }),
        y: yScale({ title:{display:true, text:'YoY Growth (%)',      color:tickColor(), font:{size:10}} })
      },
      animation:{ duration:800 }
    }
  });
}

function buildBoxPlot() {
  const el = document.getElementById('boxPlotChart');
  if (!el || charts['boxplot']) return;
  const ctx = el.getContext('2d');

  const qs = ['Q1 2024','Q2 2024','Q3 2024','Q4 2024','Q1 2025','Q2 2025'];
  const boxes = [
    {min:240,q1:270,med:295,q3:320,max:350},
    {min:295,q1:330,med:355,q3:385,max:415},
    {min:370,q1:408,med:435,q3:465,max:500},
    {min:450,q1:490,med:520,q3:555,max:595},
    {min:520,q1:558,med:590,q3:625,max:665},
    {min:590,q1:630,med:668,q3:710,max:755},
  ];

  charts['boxplot'] = new Chart(ctx, {
    type:'bar',
    data:{
      labels: qs,
      datasets:[
        { label:'Min–Q1',     data:boxes.map(b=>b.q1-b.min),  base:boxes.map(b=>b.min),  backgroundColor:hex2rgba(P.gold,0.08),  borderColor:'transparent', barThickness:36, stack:'box' },
        { label:'Q1–Median',  data:boxes.map(b=>b.med-b.q1),  base:boxes.map(b=>b.q1),   backgroundColor:hex2rgba(P.gold,0.50),  borderColor:P.gold,  borderWidth:1, borderSkipped:false, barThickness:36, stack:'box' },
        { label:'Median–Q3',  data:boxes.map(b=>b.q3-b.med),  base:boxes.map(b=>b.med),  backgroundColor:hex2rgba(P.steel,0.40), borderColor:P.steel, borderWidth:1, borderSkipped:false, borderRadius:4,  barThickness:36, stack:'box' },
        { label:'Q3–Max',     data:boxes.map(b=>b.max-b.q3),  base:boxes.map(b=>b.q3),   backgroundColor:hex2rgba(P.steel,0.08), borderColor:'transparent', barThickness:36, stack:'box' },
      ]
    },
    options:{
      responsive:true, maintainAspectRatio:false,
      plugins:{
        legend:{display:false},
        tooltip:{ ...TIP, callbacks:{
          title:c=>qs[c[0].dataIndex],
          label:c=>{ const b=boxes[c[0].dataIndex]; return [`Min $${b.min}M`,`Q1 $${b.q1}M`,`Median $${b.med}M`,`Q3 $${b.q3}M`,`Max $${b.max}M`]; },
          filter: ()=>true
        }}
      },
      scales:{
        x: xScale({ stacked:true, grid:{display:false} }),
        y: yScale({ stacked:true, ticks:{...yScale().ticks, callback:v=>`$${v}M`} })
      },
      animation:{ duration:800 }
    }
  });
}

function buildWordCloud() {
  const cont = document.getElementById('wordCloudContainer');
  if (!cont || cont.dataset.built) return;
  cont.dataset.built = '1';

  const words = [
    {text:'Intuitive',size:38},{text:'Fast',size:34},{text:'Reliable',size:30},
    {text:'Support',size:28},{text:'Design',size:26},{text:'Scalable',size:24},
    {text:'Secure',size:22},{text:'Simple',size:20},{text:'Powerful',size:20},
    {text:'Flexible',size:18},{text:'Great UX',size:18},{text:'Affordable',size:16},
    {text:'Responsive',size:16},{text:'Innovative',size:15},{text:'Easy',size:15},
    {text:'Modern',size:14},{text:'Smooth',size:14},{text:'Quality',size:13},
    {text:'Updates',size:12},{text:'Docs',size:12},
  ];

  const palette = CHART_COLORS;
  const w = cont.clientWidth || 340;
  const h = 265;

  d3.layout.cloud()
    .size([w,h])
    .words(words.map(d=>({...d})))
    .padding(5)
    .rotate(()=>Math.random()>0.65?90:0)
    .fontSize(d=>d.size)
    .on('end', wds=>{
      const svg = d3.select(cont).append('svg').attr('width',w).attr('height',h);
      svg.append('g').attr('transform',`translate(${w/2},${h/2})`)
        .selectAll('text').data(wds).enter().append('text')
        .style('font-family',"'Syne',sans-serif")
        .style('font-weight',700)
        .style('fill',(_,i)=>palette[i%palette.length])
        .style('opacity',0)
        .attr('text-anchor','middle')
        .attr('font-size',d=>d.size+'px')
        .attr('transform',d=>`translate(${d.x},${d.y})rotate(${d.rotate})`)
        .text(d=>d.text)
        .transition().delay((_,i)=>i*35).duration(500).style('opacity',0.88);
    })
    .start();
}

// ============================================================
// SECTION: COMPARISON
// ============================================================
function initComparison() { buildGroupedBar(); buildRadar(); buildWaterfall(); }

function buildGroupedBar() {
  const el = document.getElementById('groupedBarChart');
  if (!el || charts['grouped']) return;
  const ctx = el.getContext('2d');

  charts['grouped'] = new Chart(ctx, {
    type:'bar',
    data:{
      labels:['EMEA','Americas','APAC','LATAM','MEA'],
      datasets:[
        { label:'2024', data:[1490,1350,1110,480,320], backgroundColor:hex2rgba(P.steel,0.45), borderColor:P.steel, borderWidth:1.5, borderRadius:5, borderSkipped:false },
        { label:'2025', data:[1820,1540,1460,620,380], backgroundColor:hex2rgba(P.gold, 0.55), borderColor:P.gold,  borderWidth:1.5, borderRadius:5, borderSkipped:false }
      ]
    },
    options:{
      responsive:true, maintainAspectRatio:false,
      plugins:{
        legend:{ display:true, position:'top', align:'end', labels:{ usePointStyle:true, pointStyle:'circle', boxWidth:7, padding:18, color:tickColor(), font:{size:11} } },
        tooltip:{ ...TIP, callbacks:{ label:c=>` ${c.dataset.label}: $${c.raw}M` } }
      },
      scales:{
        x: xScale({ grid:{display:false} }),
        y: yScale({ ticks:{...yScale().ticks, callback:v=>`$${(v/1000).toFixed(1)}B`} })
      },
      animation:{ duration:800 }
    }
  });
}

function buildRadar() {
  const el = document.getElementById('radarChart');
  if (!el || charts['radar']) return;
  const ctx = el.getContext('2d');

  charts['radar'] = new Chart(ctx, {
    type:'radar',
    data:{
      labels:['Performance','Reliability','Design','Support','Value','Innovation'],
      datasets:[
        { label:'Product A', data:[88,92,85,90,78,94], borderColor:P.gold,  backgroundColor:hex2rgba(P.gold,0.15),  borderWidth:2, pointBackgroundColor:P.gold,  pointRadius:3 },
        { label:'Product B', data:[72,78,90,72,88,80], borderColor:P.steel, backgroundColor:hex2rgba(P.steel,0.12), borderWidth:2, pointBackgroundColor:P.steel, pointRadius:3 },
        { label:'Product C', data:[80,70,75,82,92,70], borderColor:P.terra, backgroundColor:hex2rgba(P.terra,0.10), borderWidth:2, pointBackgroundColor:P.terra, pointRadius:3 }
      ]
    },
    options:{
      responsive:true, maintainAspectRatio:false,
      plugins:{
        legend:{ display:true, position:'top', labels:{ usePointStyle:true, pointStyle:'circle', boxWidth:7, padding:14, color:tickColor(), font:{size:11} } },
        tooltip:{ ...TIP }
      },
      scales:{
        r:{
          min:0, max:100,
          grid:{ color: isDark ? 'rgba(255,255,255,0.07)' : 'rgba(0,0,0,0.07)' },
          angleLines:{ color: isDark ? 'rgba(255,255,255,0.07)' : 'rgba(0,0,0,0.07)' },
          pointLabels:{ font:{size:11}, color:tickColor() },
          ticks:{ display:false, stepSize:25 }
        }
      },
      animation:{ duration:800 }
    }
  });
}

function buildWaterfall() {
  const el = document.getElementById('waterfallChart');
  if (!el || charts['waterfall']) return;
  const ctx = el.getContext('2d');

  const items   = ['2024 Base','Enterprise +','APAC Exp.','New Products','Churn -','FX -','Acq.','2025 Total'];
  const deltas  = [3200,+820,+460,+380,-280,-120,+360,null];
  let running   = 0;
  const bases=[],bars=[],colors=[];
  for (let i=0;i<deltas.length;i++) {
    if (i===0||i===deltas.length-1) {
      bases.push(0); bars.push(deltas[i]??running);
      colors.push(hex2rgba(P.gold,0.65));
    } else {
      const d=deltas[i];
      if (d>0) { bases.push(running); bars.push(d); colors.push(hex2rgba(P.green,0.65)); }
      else { bases.push(running+d); bars.push(-d); colors.push(hex2rgba(P.red,0.65)); }
    }
    if (deltas[i]!==null) running+=deltas[i];
  }

  charts['waterfall'] = new Chart(ctx, {
    type:'bar',
    data:{
      labels: items,
      datasets:[
        { label:'base', data:bases, backgroundColor:'transparent', borderColor:'transparent', stack:'wf' },
        { label:'change', data:bars, backgroundColor:colors, borderColor:colors.map(c=>c.replace(/[\d.]+\)$/,'0.9)')), borderWidth:1, borderRadius:4, borderSkipped:false, stack:'wf' }
      ]
    },
    options:{
      responsive:true, maintainAspectRatio:false,
      plugins:{
        legend:{display:false},
        tooltip:{ ...TIP, callbacks:{
          label:c=>{ if(c.datasetIndex===0)return null; const d=deltas[c.dataIndex]; return d===null?` Total: $${bars[c.dataIndex]}M`:` ${d>=0?'+':''}${d}M`; },
          filter:c=>c.datasetIndex===1
        }}
      },
      scales:{
        x: xScale({ stacked:true, grid:{display:false}, ticks:{...xScale().ticks, maxRotation:0} }),
        y: yScale({ stacked:true, ticks:{...yScale().ticks, callback:v=>`$${v}M`} })
      },
      animation:{ duration:800 }
    }
  });
}

// ============================================================
// SECTION: GEOSPATIAL
// ============================================================
function initGeospatial() { buildGeoMap(); }

async function buildGeoMap() {
  const cont = document.getElementById('geoMap');
  if (!cont || cont.dataset.built) return;
  cont.dataset.built = '1';

  const regionMap = {
    840:1200,124:800,484:120,76:180,32:80,152:40,604:40,
    276:420,250:380,826:350,380:180,724:160,528:140,752:130,
    578:120,208:110,246:90,756:200,40:110,56:130,620:80,442:60,
    156:580,392:520,356:220,410:300,360:180,764:100,682:150,
    784:120,792:80,36:140,554:40,818:60,566:40,710:50,12:30,643:120
  };

  let geoData;
  try {
    const r = await fetch('https://cdn.jsdelivr.net/npm/world-atlas@2.0.2/countries-110m.json');
    geoData = await r.json();
  } catch(e) {
    cont.innerHTML = '<p style="color:var(--text-muted);text-align:center;padding:60px;font-size:0.8rem">Map data unavailable. Please check your connection.</p>';
    return;
  }

  const maxV = Math.max(...Object.values(regionMap));
  const colorScale = d3.scaleSequential()
    .domain([0, maxV])
    .interpolator(d3.interpolate(
      isDark ? 'rgba(201,168,76,0.07)' : 'rgba(201,168,76,0.1)',
      isDark ? 'rgba(201,168,76,0.82)' : 'rgba(176,120,86,0.85)'
    ));

  const w = cont.clientWidth || 700;
  const h = Math.min(380, w*0.5);

  const svg = d3.select(cont).append('svg').attr('width','100%').attr('height',h).attr('viewBox',`0 0 ${w} ${h}`);

  const proj = d3.geoNaturalEarth1().scale(w/6.5).translate([w/2,h/2]);
  const path = d3.geoPath().projection(proj);

  // Use globally loaded topojson (via <script> in index.html)
  let countries;
  try {
    countries = topojson.feature(geoData, geoData.objects.countries);
  } catch(e) {
    cont.innerHTML = '<p style="color:var(--text-muted);text-align:center;padding:60px;font-size:0.8rem">Map rendering failed. Please check your connection.</p>';
    return;
  }

  // Graticule
  svg.append('path').datum(d3.geoGraticule()())
    .attr('d',path).attr('fill','none')
    .attr('stroke', isDark ? 'rgba(255,255,255,0.03)' : 'rgba(0,0,0,0.04)')
    .attr('stroke-width',0.5);

  svg.selectAll('path.land')
    .data(countries.features).enter().append('path')
    .attr('class','land').attr('d',path)
    .attr('fill', d=>colorScale(regionMap[+d.id]||8))
    .attr('stroke', isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.1)')
    .attr('stroke-width',0.5)
    .style('cursor','default')
    .on('mouseover', function(){ d3.select(this).attr('stroke',P.gold).attr('stroke-width',1.2); })
    .on('mouseout',  function(){ d3.select(this).attr('stroke', isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.1)').attr('stroke-width',0.5); });
}

// ============================================================
// SECTION: INSIGHTS
// ============================================================
function initInsights() { buildInsightChart(); buildFunnelChart(); animateStory(); }

// ============================================================
// D3 FUNNEL CHART
// ============================================================
function buildFunnelChart() {
  const cont = document.getElementById('funnelChart');
  if (!cont || cont.dataset.built) return;
  cont.dataset.built = '1';

  const stages = [
    { label:'Prospects',    value:10000, pct:100 },
    { label:'Qualified',    value:6400,  pct:64  },
    { label:'Proposal',     value:3800,  pct:38  },
    { label:'Negotiation',  value:2200,  pct:22  },
    { label:'Closed Won',   value:1400,  pct:14  },
  ];

  const w = cont.clientWidth || 320;
  const h = cont.clientHeight || 280;
  const barH = 36;
  const gap = 8;
  const totalH = stages.length * (barH + gap);
  const startY = (h - totalH) / 2;

  const fColors = [P.gold, '#d4a040', '#b87d30', P.green, '#2d7a56'];

  const svg = d3.select(cont).append('svg')
    .attr('width', '100%').attr('height', h)
    .attr('viewBox', `0 0 ${w} ${h}`);

  stages.forEach((s, i) => {
    const barW = w * 0.82 * (s.pct / 100);
    const x = (w - barW) / 2;
    const y = startY + i * (barH + gap);
    const color = fColors[i];

    // Bar bg
    svg.append('rect')
      .attr('x', (w - w*0.82)/2).attr('y', y)
      .attr('width', w*0.82).attr('height', barH)
      .attr('rx', 6)
      .attr('fill', isDark ? 'rgba(255,255,255,0.04)' : 'rgba(0,0,0,0.04)');

    // Animated fill bar
    svg.append('rect')
      .attr('class','funnel-segment')
      .attr('x', x).attr('y', y)
      .attr('width', 0).attr('height', barH)
      .attr('rx', 6)
      .attr('fill', hex2rgba(color, 0.75))
      .transition().delay(i * 130).duration(700).ease(d3.easeCubicOut)
      .attr('width', barW);

    // Label left
    svg.append('text')
      .attr('x', (w - w*0.82)/2 - 8).attr('y', y + barH/2 + 4)
      .attr('text-anchor','end')
      .attr('fill', tickColor())
      .attr('font-size', 10).attr('font-family',"'Inter',sans-serif").attr('font-weight',500)
      .text(s.label);

    // Value right
    svg.append('text')
      .attr('x', (w + w*0.82)/2 + 8).attr('y', y + barH/2 + 4)
      .attr('text-anchor','start')
      .attr('fill', color)
      .attr('font-size', 10).attr('font-family',"'JetBrains Mono',monospace").attr('font-weight',500)
      .text(`${s.pct}% · ${(s.value/1000).toFixed(1)}K`);

    // Drop rate label (between bars)
    if (i < stages.length - 1) {
      const drop = stages[i].pct - stages[i+1].pct;
      svg.append('text')
        .attr('x', w/2).attr('y', y + barH + gap/2 + 1)
        .attr('text-anchor','middle')
        .attr('fill', isDark ? 'rgba(192,57,43,0.7)' : 'rgba(192,57,43,0.8)')
        .attr('font-size', 8.5).attr('font-family',"'Inter',sans-serif")
        .text(`▼ ${drop}% drop-off`);
    }
  });
}

function buildInsightChart() {
  const el = document.getElementById('insightChart');
  if (!el || charts['insight']) return;
  const ctx = el.getContext('2d');

  charts['insight'] = new Chart(ctx, {
    type:'bar',
    data:{
      labels:['Revenue Growth','Retention Rate','CAC','NPS Score','CSAT','Churn Rate'],
      datasets:[
        { label:'Q1 2024 (Before)', data:[6.2,61,48,32,74,39], backgroundColor:hex2rgba(P.terra,0.45), borderColor:P.terra, borderWidth:1.5, borderRadius:5, borderSkipped:false },
        { label:'Q4 2024 (After)',  data:[22.4,89,30,67,94.7,11], backgroundColor:hex2rgba(P.gold,0.55), borderColor:P.gold, borderWidth:1.5, borderRadius:5, borderSkipped:false }
      ]
    },
    options:{
      responsive:true, maintainAspectRatio:false,
      plugins:{
        legend:{ display:true, position:'top', align:'end', labels:{ usePointStyle:true, pointStyle:'circle', boxWidth:7, padding:18, color:tickColor(), font:{size:11} } },
        tooltip:{ ...TIP }
      },
      scales:{
        x: xScale({ grid:{display:false} }),
        y: yScale()
      },
      animation:{ duration:1000, delay:ctx=>ctx.dataIndex*60 }
    }
  });
}

function animateStory() {
  document.querySelectorAll('.story-step').forEach((el,i)=>{
    el.style.opacity='0'; el.style.transform='translateY(14px)';
    setTimeout(()=>{
      el.style.transition='opacity 0.4s ease, transform 0.4s ease';
      el.style.opacity='1'; el.style.transform='translateY(0)';
    }, i*100+80);
  });
}

// ============================================================
// BOOT
// ============================================================
window.addEventListener('DOMContentLoaded', ()=>{
  document.documentElement.setAttribute('data-theme','dark');
  isDark = true;

  // Build the market ticker immediately
  buildTicker();

  setTimeout(()=>lazyInit('overview'), 80);

  // Click outside to close mobile sidebar
  document.addEventListener('click', e=>{
    const sb = document.getElementById('sidebar');
    if (sb.classList.contains('open') && !sb.contains(e.target)) {
      sb.classList.remove('open');
    }
  });

  // Pause ticker on hover
  const ti = document.getElementById('tickerInner');
  if (ti) {
    ti.addEventListener('mouseenter', ()=>ti.style.animationPlayState='paused');
    ti.addEventListener('mouseleave', ()=>ti.style.animationPlayState='running');
  }
});
