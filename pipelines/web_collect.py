import json, hashlib, time, requests, yaml
from pathlib import Path
from bs4 import BeautifulSoup

RAW = Path("data/raw"); RAW.mkdir(parents=True, exist_ok=True)
HEADERS = {"User-Agent": "ChurchTracker/0.1 (contact: you@example.com)"}

def sid(url, title): return hashlib.sha256(f"{url}|{title}".encode()).hexdigest()[:16]

def main():
    cfg = yaml.safe_load(open("config/sources.yaml"))
    for site in cfg.get("web", []):
        if not site.get("allowed"):
            print(f"[web] skipping {site['name']} (allowed=false).")
            continue
        print(f"[web] fetching list: {site['name']} -> {site['url']}")
        html = requests.get(site["url"], headers=HEADERS, timeout=30).text
        soup = BeautifulSoup(html, "html.parser")
        articles = soup.select("article a") or soup.select(".post a")
        for a in articles[:25]:
            href = a.get("href"); title = a.get_text(strip=True)
            if not href or not title: continue
            rid = sid(href, title)
            print(f"[web] detail -> {href}")
            detail = requests.get(href, headers=HEADERS, timeout=30).text
            s2 = BeautifulSoup(detail, "html.parser")
            body = "\n".join(p.get_text(" ", strip=True) for p in s2.select("article p, .content p"))
            rec = {"id": rid, "source_type": "web", "source_name": site["name"], "title": title,
                   "url": href, "published_at": None, "author": None, "body": body}
            Path(RAW / f"{rid}.json").write_text(json.dumps(rec, ensure_ascii=False))
            time.sleep(1)
        time.sleep(1)

if __name__ == "__main__":
    main()
