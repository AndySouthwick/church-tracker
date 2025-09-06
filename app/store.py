import glob, json, sqlite3
from sentence_transformers import SentenceTransformer
import chromadb

def init():
    conn = sqlite3.connect("tracker.db")
    conn.execute("""CREATE TABLE IF NOT EXISTS posts(
        id TEXT PRIMARY KEY, source_type TEXT, source_name TEXT,
        title TEXT, url TEXT, published_at TEXT, author TEXT, body TEXT,
        summary TEXT)""")
    conn.commit()
    return conn

def load_processed(conn):
    for p in glob.glob("data/processed/*.json"):
        d = json.loads(open(p,"r",encoding="utf-8").read())
        conn.execute("""INSERT OR REPLACE INTO posts VALUES (?,?,?,?,?,?,?,?,?)""",
                     (d["id"], d["source_type"], d["source_name"], d["title"], d["url"],
                      d.get("published_at"), d.get("author"), d.get("body",""), d.get("summary","")))
    conn.commit()

def init_vectors():
    client = chromadb.Client()
    coll = client.get_or_create_collection("posts")
    return coll

def upsert_vectors(coll):
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    items = []
    for p in glob.glob("data/processed/*.json"):
        d = json.loads(open(p,"r",encoding="utf-8").read())
        items.append(d)
    if not items: return
    coll.upsert(
        ids=[x["id"] for x in items],
        documents=[x.get("body") or x.get("summary","") for x in items],
        metadatas=[{"title": x["title"], "url": x["url"], "source": x["source_name"]} for x in items]
    )
