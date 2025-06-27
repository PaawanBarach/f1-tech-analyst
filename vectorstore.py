import os
from sentence_transformers import SentenceTransformer

# Detect Codespaces via the environment variable GitHub sets
IN_CODESPACE = "CODESPACE_NAME" in os.environ

# Embedding model
EMBED_MODEL = SentenceTransformer("all-mini-lm-L6-v2")

if IN_CODESPACE:
    # Use FAISS for a self-contained dev env
    from langchain.vectorstores import FAISS as VectorStore
    from langchain.embeddings import SentenceTransformerEmbeddings

    def init_collections():
        """
        Create or load a FAISS index stored on disk under ./faiss_index/.
        """
        if os.path.exists("faiss_index.pkl"):
            return VectorStore.load_local("faiss_index", SentenceTransformerEmbeddings(EMBED_MODEL))
        # start with an empty index
        return VectorStore.from_texts([], SentenceTransformerEmbeddings(EMBED_MODEL), persist_directory="faiss_index")

    def upsert_texts(texts, store):
        """
        Add new texts to FAISS, deduping via embeddings.
        """
        # Simple: just add all for dev; real dedupe logic can be added here
        if texts:
            store.add_texts(texts)
            store.persist()
else:
    # Use Milvus in non-Codespace (your prod or Docker host)
    from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection

    # 1) Connect
    connections.connect("default", host="127.0.0.1", port="19530")

    def init_collections():
        """
        Initialize a Milvus collection for F1 data.
        """
        fields = [
            FieldSchema("id", DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema("embedding", DataType.FLOAT_VECTOR, dim=384),
            FieldSchema("text", DataType.VARCHAR, max_length=65535)
        ]
        schema = CollectionSchema(fields, "F1 data store")
        if "f1_store" in [c.name for c in connections.list_collections()]:
            coll = Collection("f1_store")
        else:
            coll = Collection("f1_store", schema)
            coll.create_index("embedding", {"index_type":"IVF_FLAT", "params":{"nlist":128}})
        coll.load()
        return coll

    def upsert_texts(texts, collection):
        """
        Encode and insert non-duplicate texts into Milvus.
        """
        from utils.dedupe import is_duplicate
        # Fetch some existing texts to compare
        existing = [r.entity.get("text")[0]
                    for r in collection.query("text", output_fields=["text"], limit=1000)]
        nondup = [t for t in texts if not is_duplicate(t, existing, threshold=0.8)]
        if not nondup:
            return
        embs = EMBED_MODEL.encode(nondup).tolist()
        collection.insert([embs, nondup])

# Single global store
STORE = init_collections()
