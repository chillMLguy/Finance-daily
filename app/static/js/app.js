const SYMBOL_MAP = {
    "EURUSD": "EURUSD=X",
    "USDJPY": "JPY=X",
    "Brent": "BZ=F",
    "WTI": "CL=F",
    "Złoto": "GC=F",
    "BTC-USD": "BTC-USD",
    "ETH-USD": "ETH-USD"
};


async function fetchJSON(url) {
    const r = await fetch(url);
    if (!r.ok) throw new Error('HTTP ' + r.status);
    return await r.json();
}


window.loadMovers = async () => {
    const select = document.getElementById('watchlist');
    const label = select.value;
    const url = `/api/movers?watchlist=${encodeURIComponent(label)}`;
    const data = await fetchJSON(url);
    const tbody = document.querySelector('#movers-table tbody');
    tbody.innerHTML = '';
    data.forEach(row => {
        const tr = document.createElement('tr');
        const pct = row.pct_change;
        tr.innerHTML = `
<td class="py-2">${row.asset}</td>
<td class="font-medium ${pct >= 0 ? 'text-green-600' : 'text-red-600'}">${pct.toFixed(2)}%</td>
<td>${row.last_close.toFixed(2)}</td>
<td class="text-slate-500">${row.as_of}</td>`;
        tr.addEventListener('click', () => {
            document.getElementById('symbol').value = row.asset; window.drawChart();
        });
        tbody.appendChild(tr);
    });
};


document.getElementById('btn-load-movers').onclick = window.loadMovers;


window.loadNews = async () => {
    const list = document.getElementById('news-list');
    list.innerHTML = '';
    const data = await fetchJSON('/api/news?limit=15');
    data.forEach(n => {
        const li = document.createElement('li');
        li.className = 'p-3 rounded border border-slate-200';
        li.innerHTML = `<div class="font-medium">${n.title}</div>
<div class="text-sm text-slate-500">${n.source} — ${n.published || ''}</div>
<a class="text-sm text-blue-700" href="${n.link}" target="_blank" rel="noopener">Czytaj</a>`;
        list.appendChild(li);
    });
};


document.getElementById('btn-load-news').onclick = window.loadNews;


window.drawChart = async () => {
    const label = document.getElementById('symbol').value;
    const symbol = SYMBOL_MAP[label];
    const period = document.getElementById('period').value;
    const data = await fetchJSON(`/api/prices?symbol=${encodeURIComponent(symbol)}&period=${encodeURIComponent(period)}`);
    const x = data.index;
    const y = data.close;
    const trace = { x: x, y: y, mode: 'lines', name: symbol };
    const layout = { margin: { l: 40, r: 20, t: 10, b: 40 } };
    Plotly.newPlot('chart', [trace], layout, { responsive: true });
};


document.getElementById('btn-load-chart').onclick = window.drawChart;