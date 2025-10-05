from fastapi import FastAPI, Request, Query
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List


from .services.market_data import DEFAULT_ASSETS, get_daily_changes, get_history
from .services.news import get_news_items_async, RSS_SOURCES


app = FastAPI(title="Market Monitor")


app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


# ---- Views ----
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "assets": list(DEFAULT_ASSETS.keys()),
            "news_sources": list(RSS_SOURCES.keys()),
        },
    )


# ---- API ----
class MoversItem(BaseModel):
    asset: str
    symbol: str
    prev_close: float
    last_close: float
    pct_change: float
    as_of: str


@app.get("/api/movers", response_model=List[MoversItem])
async def api_movers(watchlist: str | None = None):
    labels = watchlist.split(",") if watchlist else list(DEFAULT_ASSETS.keys())
    symbols = [DEFAULT_ASSETS[l] for l in labels if l in DEFAULT_ASSETS]
    df = get_daily_changes(symbols)
    payload = df.to_dict(orient="records")
    return JSONResponse(payload)


@app.get("/api/prices")
async def api_prices(symbol: str, period: str = "6mo"):
    hist = get_history(symbol, period=period)
    if hist.empty:
        return JSONResponse({"symbol": symbol, "data": []})
    out = {
        "symbol": symbol,
        "index": [str(i) for i in hist.index],
        "open": hist["Open"].round(6).tolist(),
        "high": hist["High"].round(6).tolist(),
        "low": hist["Low"].round(6).tolist(),
        "close": hist["Close"].round(6).tolist(),
        "volume": (hist["Volume"] if "Volume" in hist else []).tolist(),
    }
    return JSONResponse(out)


@app.get("/api/news")
async def api_news(
    limit: int = 15,
    q: str | None = Query(default=None),
    sources: str | None = Query(default=None),
):
    only = sources.split(",") if sources else None
    data = await get_news_items_async(
        limit=limit, query=q, only_sources=only
    )  # 👈 tu jest await
    return JSONResponse(data)
