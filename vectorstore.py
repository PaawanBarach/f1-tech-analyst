from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType
from sentence_transformers import SentenceTransformer

# 1) Connect
connections.connect("default", host="127.0.0.1", port="19530")

# 2) Define schema and create
def init_collections():
    fields = [
        FieldSchema("id", DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema("embedding", DataType.FLOAT_VECTOR, dim=384),
        FieldSchema("text", DataType.VARCHAR, max_length=65535)
    ]
    schema = CollectionSchema(fields, "F1 data store")
    coll = Collection("f1_store", schema)
    coll.create_index("embedding", {"index_type":"IVF_FLAT", "params":{"nlist":128}})
    coll.load()
    return coll

# 3) Upsert
_model = SentenceTransformer("all-mini-lm-L6-v2")
def upsert_texts(texts: list[str], collection: Collection):
    from utils.dedupe import is_duplicate
    existing = [r.entity.get("text")[0] for r in collection.query("text", output_fields=["text"], limit=1000)]
    nondup = [t for t in texts if not is_duplicate(t, existing, threshold=0.8)]
    if not nondup:
        return
    embs = _model.encode(nondup).tolist()
    collection.insert([embs, nondup])
