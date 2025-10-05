from __future__ import annotations
import time
from typing import Dict, List
import pandas as pd
import yfinance as yf


# Mapowanie etykieta -> ticker (Yahoo Finance)
DEFAULT_ASSETS: Dict[str, str] = {
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
    "ETH-USD": "ETH-USD",
}


# Prosty cache w pamięci z TTL (sekundy)
_CACHE: dict[tuple[str, str, str], tuple[float, pd.DataFrame]] = {}
_TTL = 60 * 5  # 5 minut


def _download(symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    key = (symbol, period, interval)
    now = time.time()
    if key in _CACHE and now - _CACHE[key][0] < _TTL:
        return _CACHE[key][1]
    df = yf.download(
        symbol, period=period, interval=interval, auto_adjust=False, progress=False
    )
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0] for c in df.columns]
    _CACHE[key] = (now, df)
    return df


def get_history(symbol: str, period: str = "6mo") -> pd.DataFrame:
    interval = (
        "1d" if period not in {"1d", "5d"} else ("1m" if period == "1d" else "5m")
    )
    return _download(symbol, period=period, interval=interval)


def get_daily_changes(symbols: List[str]) -> pd.DataFrame:
    rows = []
    for s in symbols:
        df = _download(s, period="5d", interval="1d")
        if df.empty or len(df) < 2:
            continue
        last = df.iloc[-1]
        prev = df.iloc[-2]
        pct = (last["Close"] / prev["Close"] - 1.0) * 100.0
        rows.append(
            {
                "asset": next((k for k, v in DEFAULT_ASSETS.items() if v == s), s),
                "symbol": s,
                "prev_close": float(prev["Close"]),
                "last_close": float(last["Close"]),
                "pct_change": float(pct),
                "as_of": str(df.index[-1].date()),
            }
        )
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    return out.sort_values("pct_change", ascending=False).reset_index(drop=True)
