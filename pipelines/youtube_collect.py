import json, hashlib, os, time
from pathlib import Path
from googleapiclient.discovery import build
import yaml

RAW = Path("data/raw"); RAW.mkdir(parents=True, exist_ok=True)
API_KEY = os.getenv("YOUTUBE_API_KEY")

def sid(*xs):
    return hashlib.sha256("|".join(xs).encode()).hexdigest()[:16]

def resolve_channel_id(yt, handle=None, channel_id=None):
    if channel_id:
        return channel_id
    if handle:
        r = yt.search().list(part="snippet", q=handle, type="channel", maxResults=1).execute()
        items = r.get("items", [])
        if items:
            return items[0]["snippet"]["channelId"]
    raise RuntimeError("Could not resolve channel id")

def main():
    if not API_KEY:
        print("YOUTUBE_API_KEY not set; skipping YouTube collection.")
        return
    yt = build("youtube", "v3", developerKey=API_KEY)
    cfg = yaml.safe_load(open("config/sources.yaml"))

    for ch in cfg.get("youtube", []):
        cid = resolve_channel_id(yt, handle=ch.get("handle"), channel_id=ch.get("channel_id"))
        print(f"[youtube] fetching {ch['name']} -> channelId={cid}")
        req = yt.search().list(part="snippet", channelId=cid, order="date", maxResults=25)
        res = req.execute()
        for it in res.get("items", []):
            if it.get("id", {}).get("videoId") is None:
                continue
            sn = it["snippet"]
            url = f"https://www.youtube.com/watch?v={it['id'].get('videoId','')}"
            rid = sid(url, sn["title"])
            rec = {
                "id": rid,
                "source_type": "youtube",
                "source_name": ch["name"],
                "title": sn["title"],
                "url": url,
                "published_at": sn["publishedAt"],
                "author": ch["name"],
                "body": sn.get("description","")
            }
            Path(RAW / f"{rec['id']}.json").write_text(json.dumps(rec, ensure_ascii=False))
        time.sleep(1)

if __name__ == "__main__":
    main()
