// ── Clock ──────────────────────────────────────────────────────────────────
function updateClock() {
  const el = document.getElementById('live-clock');
  if (el) el.textContent = new Date().toLocaleTimeString();
}
setInterval(updateClock, 1000);
updateClock();

// ── Chart defaults ─────────────────────────────────────────────────────────
Chart.defaults.color = '#4a5a6e';
Chart.defaults.font.family = "'Share Tech Mono', monospace";

let hourlyChart, ipChart;

// ── Hourly Chart ───────────────────────────────────────────────────────────
async function loadHourlyChart() {
  const res  = await fetch('/api/hourly');
  const data = await res.json();

  const labels = data.map(d => d.hour);
  const total  = data.map(d => d.total);
  const failed = data.map(d => d.failed);

  if (hourlyChart) hourlyChart.destroy();
  const ctx = document.getElementById('hourlyChart').getContext('2d');
  hourlyChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: 'Total Logins',
          data: total,
          borderColor: '#2979ff',
          backgroundColor: 'rgba(41,121,255,.1)',
          tension: .4, fill: true, pointRadius: 3
        },
        {
          label: 'Failed',
          data: failed,
          borderColor: '#ff1744',
          backgroundColor: 'rgba(255,23,68,.08)',
          tension: .4, fill: true, pointRadius: 3
        }
      ]
    },
    options: {
      responsive: true,
      plugins: { legend: { labels: { boxWidth: 12 } } },
      scales: {
        x: { grid: { color: '#1e2a3a' } },
        y: { grid: { color: '#1e2a3a' }, beginAtZero: true }
      }
    }
  });
}

// ── IP Bar Chart ───────────────────────────────────────────────────────────
async function loadIpChart() {
  const res  = await fetch('/api/top-ips');
  const data = await res.json();

  const labels  = data.map(d => d.ip);
  const failed  = data.map(d => d.failed);

  if (ipChart) ipChart.destroy();
  const ctx = document.getElementById('ipChart').getContext('2d');
  ipChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Failed Logins',
        data: failed,
        backgroundColor: failed.map(v =>
          v >= 15 ? 'rgba(255,23,68,.8)' :
          v >= 8  ? 'rgba(255,109,0,.7)' :
          v >= 4  ? 'rgba(255,214,0,.6)' : 'rgba(0,230,118,.5)'
        ),
        borderRadius: 4
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { color: '#1e2a3a' }, beginAtZero: true },
        y: { grid: { color: '#1e2a3a' }, ticks: { font: { size: 11 } } }
      }
    }
  });
}

// ── Logs table ─────────────────────────────────────────────────────────────
async function loadLogs() {
  const res  = await fetch('/api/logs');
  const logs = await res.json();
  const tbody = document.getElementById('logs-body');
  if (!tbody) return;

  if (!logs.length) {
    tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;padding:2rem">No logs yet.</td></tr>';
    return;
  }

  tbody.innerHTML = logs.map(l => `
    <tr>
      <td>${l.id}</td>
      <td class="mono">${l.timestamp}</td>
      <td>${l.username}</td>
      <td class="mono">${l.ip}</td>
      <td class="${l.status === 'SUCCESS' ? 'status-success' : 'status-failed'}">${l.status}</td>
    </tr>
  `).join('');
}

// ── Stats cards ────────────────────────────────────────────────────────────
async function loadStats() {
  const res = await fetch('/api/stats');
  const s   = await res.json();
  document.getElementById('stat-total').textContent   = s.total;
  document.getElementById('stat-success').textContent = s.success;
  document.getElementById('stat-failed').textContent  = s.failed;
  document.getElementById('stat-alerts').textContent  = s.alerts;
}

// ── Refresh all ────────────────────────────────────────────────────────────
async function refreshAll() {
  await Promise.all([loadStats(), loadHourlyChart(), loadIpChart(), loadLogs()]);
}

// ── Simulator ──────────────────────────────────────────────────────────────
function openSimulator()  { document.getElementById('simulator-modal').classList.remove('hidden'); }
function closeSimulator() { document.getElementById('simulator-modal').classList.add('hidden'); }

async function sendLogin() {
  const body = {
    username: document.getElementById('sim-user').value,
    ip:       document.getElementById('sim-ip').value,
    status:   document.getElementById('sim-status').value
  };
  const res  = await fetch('/api/login', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(body) });
  const data = await res.json();
  const el   = document.getElementById('sim-result');
  el.textContent = data.alert
    ? `⚠ ALERT [${data.alert}]: ${data.message}`
    : `✓ Logged — no alert triggered`;
  el.style.color = data.alert ? (data.alert === 'CRITICAL' ? '#ff1744' : '#ffd600') : '#00e676';
  await refreshAll();
}

async function sendBurst() {
  const result = document.getElementById('sim-result');
  result.textContent = 'Sending burst…';
  for (let i = 0; i < 10; i++) {
    document.getElementById('sim-status').value = 'FAILED';
    await sendLogin();
    await new Promise(r => setTimeout(r, 120));
  }
}

// ── AI Anomaly Detection ───────────────────────────────────────────────────
async function loadAI() {
  const status = document.getElementById('ai-status');
  const wrap   = document.getElementById('ai-table-wrap');
  const tbody  = document.getElementById('ai-body');
  status.textContent = '⏳ Running Isolation Forest model…';
  status.style.color = 'var(--accent)';
  wrap.style.display = 'none';

  try {
    const res  = await fetch('/api/ai-detect');
    const data = await res.json();

    if (data.error) {
      status.textContent = '⚠ ' + data.error;
      status.style.color = 'var(--yellow)';
      return;
    }

    const riskColor = { NORMAL:'#00e676', SUSPICIOUS:'#ffd600', HIGH:'#ff6d00', CRITICAL:'#ff1744' };

    tbody.innerHTML = data.map(r => `
      <tr>
        <td class="mono">${r.ip}</td>
        <td>${r.total_attempts}</td>
        <td>${(r.failed_ratio * 100).toFixed(1)}%</td>
        <td>${(r.peak_hour_density * 100).toFixed(1)}%</td>
        <td>${r.unique_users}</td>
        <td class="mono" style="color:${r.anomaly_score < 0 ? 'var(--red)' : 'var(--green)'}">${r.anomaly_score}</td>
        <td><span class="badge" style="background:${riskColor[r.risk_label]}22;color:${riskColor[r.risk_label]};border:1px solid ${riskColor[r.risk_label]}44">${r.risk_label}</span></td>
      </tr>
    `).join('');

    const anomalies = data.filter(r => r.anomaly).length;
    status.textContent = `✓ Analysis complete — ${data.length} IPs analysed, ${anomalies} anomalies detected by AI.`;
    status.style.color = anomalies > 0 ? 'var(--red)' : 'var(--green)';
    wrap.style.display = 'block';

    // scroll to section
    document.getElementById('ai-section').scrollIntoView({ behavior: 'smooth' });
  } catch (e) {
    status.textContent = '✗ Error running AI: ' + e.message;
    status.style.color = 'var(--red)';
  }
}

// ── Init ───────────────────────────────────────────────────────────────────
window.addEventListener('DOMContentLoaded', refreshAll);
