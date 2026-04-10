import numpy as np

def cosine_similarity(vec1, vec2):
    dot_product = np.dot(vec1, vec2)
    norm_a = np.linalg.norm(vec1)
    norm_b = np.linalg.norm(vec2)
    return dot_product / (norm_a * norm_b)

def cosine_search(query_vector, document_vectors):
    scores = []
    for i, doc_vector in enumerate(document_vectors):
        score = cosine_similarity(query_vector, doc_vector)
        scores.append((i, score))
    
    # Sort by similarity score descending
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores

# Example
documents = [
    np.array([1, 0, 1]),
    np.array([1, 1, 0]),
    np.array([0, 1, 1])
]

query = np.array([1, 0, 1])

results = cosine_search(query, documents)
print(results)
