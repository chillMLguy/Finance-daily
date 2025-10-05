const SYMBOL_MAP = {
    "S&P 500": "^GSPC",
    "Nasdaq 100": "^NDX",
    "DAX": "^GDAXI",
    "WIG20": "^WIG20",
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


function setStatus(id, text) {
    const el = document.getElementById(id);
    if (el) el.textContent = text || '';
}

window.loadMovers = async () => {
    const url = `/api/movers`;
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
    const q = document.getElementById('news-q').value.trim();
    const src = document.getElementById('news-source').value.trim();
    const limit = document.getElementById('news-limit').value || '20';


    list.innerHTML = '';
    setStatus('news-status', 'Ładowanie…');


    const params = new URLSearchParams();
    params.set('limit', limit);
    if (q) params.set('q', q);
    if (src) params.set('sources', src);


    try {
        const data = await fetchJSON(`/api/news?${params.toString()}`);
        setStatus('news-status', data.length ? `Znaleziono ${data.length} wpisów` : 'Brak wyników');


        data.forEach(n => {
            const li = document.createElement('li');
            li.className = 'p-3 rounded border border-slate-200';
            const when = n.published ? ` — ${n.published}` : '';
            li.innerHTML = `<div class="font-medium">${n.title}</div>
<div class="text-sm text-slate-500">${n.source}${when}</div>
${n.summary ? `<div class="text-sm mt-1">${n.summary}</div>` : ''}
<a class="text-sm text-blue-700" href="${n.link}" target="_blank" rel="noopener">Czytaj</a>`;
            list.appendChild(li);
        });
    } catch (err) {
        console.error(err);
        setStatus('news-status', 'Błąd ładowania newsów');
    }
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