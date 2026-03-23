from app.core.embeddings import get_embeddings
from app.core.vector_store import search

def retrieve(query):
    q_emb = get_embeddings([query])
    results = search(q_emb)
    return results