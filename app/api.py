from fastapi import FastAPI, Query
import sqlite3
import chromadb
from sentence_transformers import SentenceTransformer

app = FastAPI(title="Church Updates (Public)")

def get_conn():
    conn = sqlite3.connect("tracker.db")
    conn.row_factory = sqlite3.Row
    return conn

client = chromadb.Client()
coll = client.get_or_create_collection("posts")
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

@app.get("/recent")
def recent(limit: int = 20):
    c = get_conn()
    rows = c.execute("SELECT * FROM posts ORDER BY IFNULL(published_at,'') DESC LIMIT ?", (limit,)).fetchall()
    return [dict(r) for r in rows]

@app.get("/search")
def search(q: str = Query(..., min_length=2), k: int = 10):
    q_emb = model.encode(q, normalize_embeddings=True).tolist()
    res = coll.query(query_embeddings=[q_emb], n_results=k)
    results = []
    for i in range(len(res["ids"][0])):
        results.append({
            "id": res["ids"][0][i],
            "score": res["distances"][0][i],
            **res["metadatas"][0][i]
        })
    return {"query": q, "results": results}
