# app/services/news.py
from __future__ import annotations
import asyncio
from typing import List, Dict, Iterable
import hashlib, time
import feedparser, httpx

RSS_SOURCES: dict[str, str] = {
    "Reuters Markets": "https://feeds.reuters.com/reuters/marketsNews",
    "Reuters Business": "https://feeds.reuters.com/reuters/businessNews",
    "Reuters World": "https://feeds.reuters.com/Reuters/worldNews",
    "Yahoo Finance": "https://finance.yahoo.com/news/rssindex",
    "MarketWatch": "https://www.marketwatch.com/feeds/topstories",
    "Federal Reserve": "https://www.federalreserve.gov/feeds/press_all.xml",
    "ECB Press": "https://www.ecb.europa.eu/press/pressconf/2024/html/index.en.rss.xml",
    "Bank of England": "https://www.bankofengland.co.uk/news/news.xml",
}

DEFAULT_TIMEOUT = 10.0
MAX_PER_SOURCE = 30


def _hash_key(*parts: str) -> str:
    m = hashlib.sha256()
    for p in parts:
        m.update((p or "").encode("utf-8", errors="ignore"))
    return m.hexdigest()[:16]


def _now_ts() -> float:
    return time.time()


async def _fetch(client: httpx.AsyncClient, name: str, url: str) -> list[Dict]:
    try:
        r = await client.get(url, timeout=DEFAULT_TIMEOUT)
        r.raise_for_status()
        feed = feedparser.parse(r.content)
        out: list[Dict] = []
        for e in feed.entries[:MAX_PER_SOURCE]:
            title = e.get("title") or "(no title)"
            link = e.get("link") or ""
            summary = e.get("summary") or e.get("subtitle") or ""
            published = e.get("published") or e.get("updated") or ""
            ts_struct = e.get("published_parsed") or e.get("updated_parsed")
            ts_epoch = time.mktime(ts_struct) if ts_struct else _now_ts()
            out.append(
                {
                    "id": _hash_key(name, title, link),
                    "source": name,
                    "title": title.strip(),
                    "link": link,
                    "summary": summary.strip(),
                    "published": published,
                    "ts": ts_epoch,
                }
            )
        return out
    except Exception:
        return []


async def get_news_items_async(
    limit: int = 25, query: str | None = None, only_sources: Iterable[str] | None = None
) -> List[Dict]:
    sources = {
        k: v for k, v in RSS_SOURCES.items() if (not only_sources or k in only_sources)
    }
    async with httpx.AsyncClient(headers={"User-Agent": "MarketMonitor/1.0"}) as client:
        results = await asyncio.gather(
            *[_fetch(client, n, u) for n, u in sources.items()], return_exceptions=False
        )

    seen: set[str] = set()
    items: list[Dict] = []
    for chunk in results:
        for it in chunk:
            k = _hash_key(it["title"], it["link"])
            if k in seen:
                continue
            seen.add(k)
            items.append(it)

    if query:
        q = query.lower().strip()
        items = [
            it
            for it in items
            if q in it["title"].lower() or q in (it.get("summary") or "").lower()
        ]

    items.sort(key=lambda x: x.get("ts", 0), reverse=True)
    return items[:limit]


# (opcjonalny) sync wrapper do użycia poza FastAPI
def get_news_items(
    limit: int = 25, query: str | None = None, only_sources: Iterable[str] | None = None
) -> List[Dict]:
    return asyncio.run(
        get_news_items_async(limit=limit, query=query, only_sources=only_sources)
    )
