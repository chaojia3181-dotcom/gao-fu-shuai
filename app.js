/**
 * 期货八种形态前端渲染逻辑
 */

// ===== 格式化工具 =====
function fmtNum(n) {
  return new Intl.NumberFormat('zh-CN').format(n);
}

function fmtBig(n) {
  if (n >= 100000000) return (n / 100000000).toFixed(2) + '亿';
  if (n >= 10000) return (n / 10000).toFixed(1) + '万';
  return fmtNum(n);
}

function pctClass(v) {
  return v > 0 ? 'up' : v < 0 ? 'down' : '';
}

// ===== 形态配置 =====
const PATTERN_CONFIG = {
  '高富帅': { tagClass: 'gold', color: '#e3b341' },
  '白富美': { tagClass: 'purple', color: '#a371f7' },
  '上涨乏力': { tagClass: 'orange', color: '#f0883e' },
  '下跌乏力': { tagClass: 'cyan', color: '#39c5cf' },
  '虚涨分歧': { tagClass: 'yellow', color: '#d29922' },
  '虚跌分歧': { tagClass: 'blue', color: '#58a6ff' },
  '涨势将尽': { tagClass: 'gray', color: '#8b949e' },
  '跌势将尽': { tagClass: 'green', color: '#3fb950' },
};

// ===== 渲染形态矩阵 =====
function renderPatternMatrix(data) {
  const container = document.getElementById('pattern-matrix');
  const order = ['高富帅', '白富美', '上涨乏力', '下跌乏力', '虚涨分歧', '虚跌分歧', '涨势将尽', '跌势将尽'];

  container.innerHTML = order.map(name => {
    const p = data.patterns[name];
    const config = PATTERN_CONFIG[name];
    const isZero = p.count === 0;

    return `
      <div class="pattern-cell ${isZero ? 'empty' : ''}" data-pattern="${name}" onclick="scrollToPattern('${name}')">
        <span class="cell-emoji">${p.emoji}</span>
        <div class="cell-name">${name}</div>
        <div class="cell-label">${p.label}</div>
        <div class="cell-count ${isZero ? 'zero' : ''}">${p.count}</div>
        <div class="cell-dims">
          <span>价${p.dims.price === 'up' ? '↑涨' : '↓跌'}</span>
          <span>量${p.dims.vol === 'up' ? '↑放' : '↓缩'}</span>
          <span>仓${p.dims.hold === 'up' ? '↑增' : '↓减'}</span>
        </div>
      </div>
    `;
  }).join('');
}

// ===== 渲染今日概览 =====
function renderOverview(data) {
  const container = document.getElementById('overview-stats');
  container.innerHTML = `
    <div class="overview-card">
      <div class="ov-value">${data.valid_count}</div>
      <div class="ov-label">有效品种</div>
    </div>
    <div class="overview-card" style="background:linear-gradient(135deg,rgba(227,179,65,0.1),rgba(227,179,65,0.05));border-color:#e3b341">
      <div class="ov-value" style="color:#e3b341">${data.strong_count || 0}</div>
      <div class="ov-label">⭐ 双20%强信号</div>
    </div>
    <div class="overview-card up">
      <div class="ov-value">${data.up_count}</div>
      <div class="ov-label">上涨品种</div>
    </div>
    <div class="overview-card down">
      <div class="ov-value">${data.down_count}</div>
      <div class="ov-label">下跌品种</div>
    </div>
  `;
}

// ===== 渲染形态详情 =====
function renderPatternDetails(data) {
  const container = document.getElementById('pattern-sections');
  const order = ['高富帅', '白富美', '上涨乏力', '下跌乏力', '虚涨分歧', '虚跌分歧', '涨势将尽', '跌势将尽'];

  container.innerHTML = order.map((name, idx) => {
    const p = data.patterns[name];
    const config = PATTERN_CONFIG[name];
    const isOpen = idx < 2 || p.count > 0;

    const itemsHtml = p.count > 0
      ? `<div class="pd-items">${p.items.map(item => renderItemCard(item, name)).join('')}</div>`
      : '<div class="empty-state">暂无该形态品种</div>';

    return `
      <div class="pattern-detail ${isOpen ? 'open' : ''}" id="pattern-${name}">
        <div class="pattern-detail-header" onclick="togglePattern(this)">
          <span class="pd-emoji">${p.emoji}</span>
          <span class="pd-name" style="color:${config.color}">${name}</span>
          <span class="pd-label">${p.label}</span>
          <span class="pd-count" style="color:${config.color}">${p.count} 个</span>
          <span class="pd-toggle">▼</span>
        </div>
        <div class="pattern-detail-body">
          <div class="pd-desc">${p.desc}</div>
          ${itemsHtml}
        </div>
      </div>
    `;
  }).join('');
}

// ===== 渲染品种卡片 =====
function renderItemCard(item, patternName) {
  const config = PATTERN_CONFIG[patternName];
  const priceClass = pctClass(item.price_change_pct);
  const holdBarWidth = Math.min(Math.abs(item.hold_change_pct) / 30 * 100, 100);
  const strongBadge = item.is_strong ? '<span style="background:#e3b341;color:#000;padding:2px 8px;border-radius:12px;font-size:0.7rem;font-weight:700;margin-left:auto">⭐双20%</span>' : '';

  return `
    <div class="item-card">
      <div class="item-card-header">
        <span class="item-symbol" style="color:${config.color}">${item.symbol}</span>
        <span class="item-name">${item.name}</span>
        <span class="item-exchange">${item.exchange}</span>
        ${strongBadge}
      </div>
      <div class="item-stats">
        <div class="item-stat">
          <div class="item-stat-label">持仓变化</div>
          <div class="item-stat-value">${item.hold_change_pct > 0 ? '+' : ''}${item.hold_change_pct.toFixed(2)}%</div>
          <div class="progress-bar">
            <div class="progress-fill" style="width:${holdBarWidth}%;background:${config.color}"></div>
          </div>
        </div>
        <div class="item-stat">
          <div class="item-stat-label">涨跌幅</div>
          <div class="item-stat-value ${priceClass}">${item.price_change_pct > 0 ? '+' : ''}${item.price_change_pct.toFixed(2)}%</div>
        </div>
        <div class="item-stat">
          <div class="item-stat-label">成交量</div>
          <div class="item-stat-value">${fmtBig(item.today_vol)}</div>
        </div>
        <div class="item-stat">
          <div class="item-stat-label">收盘价</div>
          <div class="item-stat-value">¥${item.today_close}</div>
        </div>
      </div>
    </div>
  `;
}

// ===== 渲染全部品种表格 =====
function renderAllResults(data) {
  const tbody = document.getElementById('all-results-body');

  tbody.innerHTML = data.all_results.map((item, index) => {
    const rank = index + 1;
    const config = PATTERN_CONFIG[item.pattern] || { tagClass: 'gray' };
    const priceClass = pctClass(item.price_change_pct);
    const strongStar = item.is_strong ? ' <span style="color:#e3b341">⭐</span>' : '';

    const volRatio = item.vol_5ma > 0 ? (item.today_vol / item.vol_5ma) : 0;
    const volBarWidth = Math.min(volRatio * 40, 100);
    const volBarColor = item.today_vol > item.vol_5ma && item.today_vol > item.vol_20ma ? '#3fb950' : '#f85149';

    const priceDim = item.price_change_pct > 0 ? 'up' : 'down';
    const volDim = item.today_vol > item.vol_5ma && item.today_vol > item.vol_20ma ? 'vol-up' : 'vol-down';
    const holdDim = item.hold_change_pct > 0 ? 'hold-up' : 'hold-down';

    return `
      <tr>
        <td class="rank">${rank}</td>
        <td class="symbol-cell">
          ${item.symbol}${strongStar}
          <div class="symbol-name">${item.name}</div>
        </td>
        <td>${item.exchange}</td>
        <td><span class="pattern-tag ${config.tagClass}">${item.pattern}</span></td>
        <td>${item.hold_change_amount > 0 ? '+' : ''}${fmtBig(item.hold_change_amount)}</td>
        <td class="change-pct ${item.hold_change_pct > 0 ? 'up' : item.hold_change_pct < 0 ? 'down' : ''}">
          ${item.hold_change_pct > 0 ? '+' : ''}${item.hold_change_pct.toFixed(2)}%
        </td>
        <td>
          ${fmtBig(item.today_vol)}
          <span class="vol-bar" style="display:inline-block;width:50px;height:5px;background:#161b22;border-radius:3px;vertical-align:middle;margin-left:6px;overflow:hidden">
            <span style="display:block;height:100%;width:${volBarWidth}%;background:${volBarColor};border-radius:3px"></span>
          </span>
        </td>
        <td>${fmtBig(item.vol_5ma)}</td>
        <td>${fmtBig(item.vol_20ma)}</td>
        <td>¥${item.today_close}</td>
        <td class="change-pct ${priceClass}">
          ${item.price_change_pct > 0 ? '+' : ''}${item.price_change_pct.toFixed(2)}%
        </td>
        <td>
          <div class="dims-badges">
            <span class="dim-badge ${priceDim}">价${item.price_change_pct > 0 ? '↑' : '↓'}</span>
            <span class="dim-badge ${volDim}">量${item.today_vol > item.vol_5ma ? '↑' : '↓'}</span>
            <span class="dim-badge ${holdDim}">仓${item.hold_change_pct > 0 ? '↑' : '↓'}</span>
          </div>
        </td>
      </tr>
    `;
  }).join('');
}

// ===== 渲染头部信息 =====
function renderHeader(data) {
  document.getElementById('data-date').textContent = data.data_date;
  document.getElementById('scan-date').textContent = data.scan_date;
  document.getElementById('stat-total').textContent = data.total_scanned;
}

// ===== 主渲染函数 =====
function render(data) {
  renderHeader(data);
  renderPatternMatrix(data);
  renderOverview(data);
  renderPatternDetails(data);
  renderAllResults(data);
}

// ===== 交互函数 =====
function togglePattern(header) {
  const detail = header.closest('.pattern-detail');
  detail.classList.toggle('open');
}

function scrollToPattern(name) {
  const el = document.getElementById(`pattern-${name}`);
  if (el) {
    el.classList.add('open');
    el.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }
}

window.togglePattern = togglePattern;
window.scrollToPattern = scrollToPattern;

// ===== 加载数据 =====
async function loadData() {
  try {
    const response = await fetch('data.json?t=' + Date.now());
    if (!response.ok) throw new Error('Failed to load data.json');
    const data = await response.json();
    render(data);
  } catch (err) {
    console.error('加载数据失败:', err);
    document.querySelector('.container').innerHTML = `
      <div style="text-align:center;padding:60px 20px">
        <div style="font-size:3rem;margin-bottom:16px">⚠️</div>
        <h2 style="margin-bottom:8px">数据加载失败</h2>
        <p style="color:var(--text-secondary)">请确保 data.json 文件存在且格式正确</p>
        <p style="color:var(--text-muted);font-size:0.85rem;margin-top:8px">错误: ${err.message}</p>
      </div>
    `;
  }
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', loadData);
} else {
  loadData();
}
