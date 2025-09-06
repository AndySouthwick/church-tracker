import json, glob, re
from pathlib import Path

IN  = Path("data/raw")
OUT = Path("data/processed"); OUT.mkdir(parents=True, exist_ok=True)

def extract_locations(txt):
    # simple heuristic; upgrade later with spaCy NER + geocoding
    cities = re.findall(r"\b([A-Z][a-z]+(?:, [A-Z][a-z]+)?)\b", txt)
    return list({c for c in cities if len(c.split()) <= 3})

def main():
    for p in glob.glob(str(IN / "*.json")):
        rec = json.loads(open(p, "r", encoding="utf-8").read())
        text = rec.get("body","")
        norm = {
            **rec,
            "summary": text[:500] + ("..." if len(text)>500 else ""),
            "topics": [],
            "locations": extract_locations(text),
        }
        open(OUT / Path(p).name, "w", encoding="utf-8").write(json.dumps(norm, ensure_ascii=False))
    print("Normalized:", len(list(OUT.glob("*.json"))), "items.")

if __name__ == "__main__":
    main()
