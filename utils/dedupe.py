from sentence_transformers import SentenceTransformer, util

_model = SentenceTransformer("all-mini-lm-L6-v2")

def is_duplicate(new_text: str, existing_texts: list[str], threshold: float) -> bool:
    if not existing_texts:
        return False
    emb1 = _model.encode(new_text, convert_to_tensor=True)
    embs2 = _model.encode(existing_texts, convert_to_tensor=True)
    sims = util.cos_sim(emb1, embs2)
    return (sims.max() >= threshold).item()
