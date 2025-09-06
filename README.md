# 📖 Church Updates Scraper & API

This project collects **official public updates** from Church sources (Newsroom, Church News, YouTube channels) and exposes them through a simple **FastAPI service** with search.

## ✨ Features
- Pulls **official RSS feeds** (Newsroom, Church News).
- Collects videos from **official YouTube channels**.
- (Optional) Collects allowed web pages (if robots/ToS permit).
- Normalizes into a single schema (JSON).
- Stores in **SQLite + Chroma** for fast semantic search.
- Provides API endpoints for **recent updates** and **search**.

## 📂 Project Structure
```
church-tracker/
├─ config/
│  └─ sources.yaml        # RSS, YouTube, and optional web sources
├─ pipelines/
│  ├─ rss_collect.py      # collect from RSS feeds
│  ├─ youtube_collect.py  # collect from YouTube Data API
│  ├─ web_collect.py      # polite scraper (allowed pages only)
│  └─ normalize.py        # clean + enrich records
├─ data/
│  ├─ raw/                # raw JSON files
│  └─ processed/          # normalized files
├─ app/
│  ├─ api.py              # FastAPI endpoints
│  └─ store.py            # SQLite + Chroma storage
├─ requirements.txt
└─ README.md
```

## 🔑 Config: `config/sources.yaml`
```yaml
rss:
  - name: Church Newsroom (global)
    url: https://newsroom.churchofjesuschrist.org/rss
  - name: Church News (All News & Events)
    url: https://feeds.lds.org/church-news-and-events-eng

youtube:
  - name: Church (official)
    handle: "@churchofjesuschrist"
  - name: Church Newsroom (YouTube)
    handle: "@churchnewsroom"
  - name: Church News (YouTube)
    channel_id: "UCbpG_4CUzJD3gUSS6wN8-2w"

web:
  - name: Newsroom – Worldwide Events page
    url: https://newsroom.churchofjesuschrist.org/events
    allowed: false
```

## 🧑‍💻 Setup
1. **Clone repo + install deps**
   ```bash
   pip install -r requirements.txt
   ```
2. **YouTube API Key**
   - Create at Google Cloud Console.
   - Save as environment variable:
     ```bash
     export YOUTUBE_API_KEY="your-key-here"
     ```
3. **Download models** (first run will auto-download):
   ```bash
   python -m spacy download en_core_web_sm
   ```

## ▶️ Run the Pipeline
Collect & normalize:
```bash
python pipelines/rss_collect.py
python pipelines/youtube_collect.py   # requires $YOUTUBE_API_KEY
python pipelines/normalize.py
```
Start the API:
```bash
uvicorn app.api:app --reload
```

## 🌐 API Endpoints
- **Recent updates**: `GET /recent`
- **Semantic search**: `GET /search?q=service`

## 🛠️ Next Steps
- Add **regional newsroom RSS feeds** (Europe, Africa, etc.).
- Enable **web_collect.py** only if robots.txt/ToS allow.
- Add **summarizer** (e.g. Hugging Face `facebook/bart-large-cnn`) to generate 2–3 sentence summaries.
- Deploy API on **Render** or **Fly.io** for shared use.
- Automate with **GitHub Actions** to refresh hourly/daily.
