import json, hashlib, time, feedparser
from pathlib import Path
from dateutil import parser as dparser
import yaml

RAW = Path("data/raw"); RAW.mkdir(parents=True, exist_ok=True)

def stable_id(url, title):
    return hashlib.sha256(f"{url}|{title}".encode()).hexdigest()[:16]

def main():
    cfg = yaml.safe_load(open("config/sources.yaml"))
    for feed in cfg.get("rss", []):
        print(f"[rss] fetching {feed['name']} -> {feed['url']}")
        d = feedparser.parse(feed["url"])
        for e in d.entries:
            url = e.get("link") or ""
            title = e.get("title") or ""
            published = e.get("published") or e.get("updated") or ""
            rec = {
                "id": stable_id(url, title),
                "source_type": "rss",
                "source_name": feed["name"],
                "title": title,
                "url": url,
                "published_at": dparser.parse(published).isoformat() if published else None,
                "author": (e.get("author") or "").strip(),
                "body": (e.get("summary") or e.get("description") or "").strip()
            }
            Path(RAW / f"{rec['id']}.json").write_text(json.dumps(rec, ensure_ascii=False))
        time.sleep(1)  # polite pause

if __name__ == "__main__":
    main()
