import datetime
from ingestion import ingest_rss, ingest_apis
from agents import qa_chain
from utils.cache import set_cached_response

def find_trending_topics(k=5):
    # Simple heuristic: pull the latest RSS headlines and pick top k
    from vectorstore import STORE
    docs = STORE.query(expr=None, output_fields=["text"], limit=50)
    texts = [d.entity.get("text")[0] for d in docs]
    # For demo, just pick first k headlines
    return texts[:k]

def generate_technical_article():
    topics = find_trending_topics()
    prompt = (
        "Write a detailed technical analysis article covering the following topics:\n"
        + "\n".join(f"- {t[:80]}…" for t in topics)
        + "\nInclude diagrams where appropriate, explain F1 technical concepts, "
        + "and cite your data sources. Format as markdown."
    )
    resp = qa_chain({"query": prompt})
    article = resp["result"]
    # Cache the article under a timestamped key
    key = f"article_{datetime.datetime.utcnow().isoformat()}"
    set_cached_response(key, (article, ["auto-generated"]))
    # Optionally save to disk
    with open(f"./articles/{key}.md", "w") as f:
        f.write(article)
    return key, article
