/**
 * 高富帅策略前端渲染逻辑
 */

// 格式化数字
function fmtNum(n) {
  return new Intl.NumberFormat('zh-CN').format(n);
}

// 格式化大数字（万/亿）
function fmtBig(n) {
  if (n >= 100000000) return (n / 100000000).toFixed(2) + '亿';
  if (n >= 10000) return (n / 10000).toFixed(1) + '万';
  return fmtNum(n);
}

// 判断涨跌颜色类
function pctClass(v) {
  return v > 0 ? 'up' : v < 0 ? 'down' : '';
}

// 渲染统计面板
function renderStats(data) {
  document.getElementById('stat-total').textContent = data.total_scanned;
  document.getElementById('stat-gao').textContent = data.gao_fu_shuai_count;
  document.getElementById('stat-high').textContent = data.high_count;
  document.getElementById('stat-up').textContent = data.up_count;

  document.getElementById('data-date').textContent = data.data_date;
  document.getElementById('scan-date').textContent = data.scan_date;
}

// 渲染高富帅卡片
function renderGaoFuShuai(data) {
  const container = document.getElementById('gao-fu-shuai-cards');
  const emptyState = document.getElementById('gao-empty');
  const countBadge = document.getElementById('gao-count');

  countBadge.textContent = data.gao_fu_shuai_count;

  if (!data.gao_fu_shuai || data.gao_fu_shuai.length === 0) {
    container.innerHTML = '';
    emptyState.style.display = 'block';
    return;
  }

  emptyState.style.display = 'none';

  container.innerHTML = data.gao_fu_shuai.map(item => {
    const holdBarWidth = Math.min(Math.abs(item.hold_change_pct) / 50 * 100, 100);
    const priceClass = pctClass(item.price_change_pct);

    return `
      <div class="gfs-card">
        <div class="gfs-badge">高富帅</div>
        <div class="gfs-header">
          <span class="gfs-symbol">${item.symbol}</span>
          <span class="gfs-name">${item.name}</span>
          <span class="gfs-exchange">${item.exchange}</span>
        </div>
        <div class="gfs-stats">
          <div class="gfs-stat">
            <div class="gfs-stat-label">持仓变化</div>
            <div class="gfs-stat-value">
              ${item.hold_change_pct > 0 ? '+' : ''}${item.hold_change_pct.toFixed(2)}%
            </div>
            <div class="progress-bar">
              <div class="progress-fill" style="width: ${holdBarWidth}%"></div>
            </div>
            <div class="gfs-stat-label" style="margin-top:4px">
              ${fmtNum(item.prev_hold)} → ${fmtNum(item.today_hold)}
            </div>
          </div>
          <div class="gfs-stat">
            <div class="gfs-stat-label">涨跌幅</div>
            <div class="gfs-stat-value ${priceClass}">
              ${item.price_change_pct > 0 ? '+' : ''}${item.price_change_pct.toFixed(2)}%
            </div>
            <div class="gfs-stat-label" style="margin-top:4px">
              ¥${item.prev_close} → ¥${item.today_close}
            </div>
          </div>
          <div class="gfs-stat">
            <div class="gfs-stat-label">成交量</div>
            <div class="gfs-stat-value">${fmtBig(item.today_vol)}</div>
            <div class="gfs-stat-label" style="margin-top:4px">
              5日均: ${fmtBig(item.vol_5ma)} · 20日均: ${fmtBig(item.vol_20ma)}
            </div>
          </div>
          <div class="gfs-stat">
            <div class="gfs-stat-label">条件满足</div>
            <div class="conditions" style="margin-top:6px">
              <span class="cond-dot gold">高</span>
              <span class="cond-dot gold">富</span>
              <span class="cond-dot gold">帅</span>
            </div>
          </div>
        </div>
      </div>
    `;
  }).join('');
}

// 渲染全部品种表格
function renderAllResults(data) {
  const tbody = document.getElementById('all-results-body');
  const maxVol = Math.max(...data.all_results.map(r => Math.max(r.today_vol, r.vol_5ma, r.vol_20ma)));

  tbody.innerHTML = data.all_results.map((item, index) => {
    const rank = index + 1;
    const isGfs = item.is_gao_fu_shuai;
    const priceClass = pctClass(item.price_change_pct);

    // 成交量相对5日均的比例条
    const volRatio = item.vol_5ma > 0 ? (item.today_vol / item.vol_5ma) : 0;
    const volBarWidth = Math.min(volRatio * 50, 100);
    const volBarClass = item.today_vol > item.vol_5ma && item.today_vol > item.vol_20ma ? 'above' : 'below';

    return `
      <tr class="${isGfs ? 'gfs-row' : ''}">
        <td class="rank">${rank}</td>
        <td class="symbol-cell">
          ${item.symbol}
          <div class="symbol-name">${item.name}</div>
        </td>
        <td>${item.exchange}</td>
        <td>
          ${item.hold_change_amount > 0 ? '+' : ''}${fmtBig(item.hold_change_amount)}
        </td>
        <td class="change-pct ${item.hold_change_pct > 0 ? 'up' : item.hold_change_pct < 0 ? 'down' : ''}">
          ${item.hold_change_pct > 0 ? '+' : ''}${item.hold_change_pct.toFixed(2)}%
        </td>
        <td>
          ${fmtBig(item.today_vol)}
          <span class="vol-bar">
            <span class="vol-bar-fill ${volBarClass}" style="width: ${volBarWidth}%"></span>
          </span>
        </td>
        <td>${fmtBig(item.vol_5ma)}</td>
        <td>${fmtBig(item.vol_20ma)}</td>
        <td>¥${item.today_close}</td>
        <td class="change-pct ${priceClass}">
          ${item.price_change_pct > 0 ? '+' : ''}${item.price_change_pct.toFixed(2)}%
        </td>
        <td>
          <div class="conditions">
            <span class="cond-dot ${item.is_high ? 'gold' : 'off'}">高</span>
            <span class="cond-dot ${item.is_rich ? 'on' : 'off'}">富</span>
            <span class="cond-dot ${item.is_handsome ? 'on' : 'off'}">帅</span>
          </div>
        </td>
      </tr>
    `;
  }).join('');
}

// 主渲染函数
function render(data) {
  renderStats(data);
  renderGaoFuShuai(data);
  renderAllResults(data);
}

// 加载数据
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

// 页面加载完成后执行
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', loadData);
} else {
  loadData();
}
