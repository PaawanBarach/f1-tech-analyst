import yaml, os, glob, requests, feedparser
from PyPDF2 import PdfReader
from PIL import Image
from vectorstore import init_collections, upsert_texts
import newspaper


with open("config.yml") as f:
    cfg = yaml.safe_load(f)

STORE = init_collections()

def ingest_rss():
    texts = []
    for url in cfg["rss_feeds"]:
        feed = feedparser.parse(url)
        for e in feed.entries:
            art = newspaper.Article(e.link)
            art.download(); art.parse()
            texts.append(art.title + "\n" + art.text)
    upsert_texts(texts, STORE)

def ingest_json():
    texts = []
    for url in cfg.get("json_feeds", []):
        data = requests.get(url).json()
        for art in data.get("articles", []):
            texts.append(art["title"] + "\n" + art.get("body",""))
    upsert_texts(texts, STORE)



def ingest_apis():
    # Ergast example
    r = requests.get(f"{cfg['apis']['ergast']}/current/last/results.json")
    data = r.json()["MRData"]["RaceTable"]["Races"][0]
    txt = f"Race: {data['raceName']} Results: {data['Results']}"
    upsert_texts([txt], STORE)
    # Weather example
    w = requests.get(cfg["apis"]["weather"], params={
        "latitude": 52.07, "longitude": 1.15, "hourly": "temperature_2m"
    }).json()
    upsert_texts([str(w["hourly"])], STORE)

def ingest_pdfs():
    texts = []
    for fp in glob.glob(os.path.join(cfg["pdf_dirs"][0], "*.pdf")):
        reader = PdfReader(fp)
        txt = "\n".join([p.extract_text() for p in reader.pages if p.extract_text()])
        texts.append(txt)
    upsert_texts(texts, STORE)

def ingest_images():
    # OCR or alt-text extraction placeholder
    pass

def run_full_ingest():
    ingest_rss()
    ingest_apis()
    ingest_pdfs()
    ingest_images()
    ingest_json()

