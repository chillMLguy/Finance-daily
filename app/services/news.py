from typing import List, Dict
import feedparser


RSS_SOURCES = {
    "Reuters Markets": "https://feeds.reuters.com/reuters/marketsNews",
    "Reuters Business": "https://feeds.reuters.com/reuters/businessNews",
    "ECB Press": "https://www.ecb.europa.eu/press/pressconf/2024/html/index.en.rss.xml",
    "BoE News": "https://www.bankofengland.co.uk/news/news.xml",
}


def get_news_items(limit: int = 15) -> List[Dict]:
    items: List[Dict] = []
    for name, url in RSS_SOURCES.items():
        feed = feedparser.parse(url)
        for e in feed.entries[: min(20, len(feed.entries))]:
            items.append(
                {
                    "source": name,
                    "title": e.get("title", "(no title)"),
                    "link": e.get("link", ""),
                    "published": e.get("published", e.get("updated", "")),
                    "summary": e.get("summary", ""),
                }
            )
    # sortowanie "best effort" po polu published
    items.sort(key=lambda x: x.get("published", ""), reverse=True)
    return items[:limit]
