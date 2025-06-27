# Drop in new logic: e.g. ingest team press releases
import requests
from vectorstore import upsert_texts

def ingest_team_press(team: str):
    url = f"https://cms.example.com/{team}/news.json"
    data = requests.get(url).json()
    texts = [item["title"] + "\n" + item["body"] for item in data]
    upsert_texts(texts, None)  # pass STORE if needed
