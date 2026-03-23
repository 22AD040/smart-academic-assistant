import faiss
import numpy as np

index = None
documents = []

def create_index(embeddings, docs):
    global index, documents
    dim = len(embeddings[0])
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings))
    documents = docs

def search(query_embedding, k=3):
    global index, documents

    if index is None:
        return []

    D, I = index.search(query_embedding, k)
    return [documents[i] for i in I[0]]