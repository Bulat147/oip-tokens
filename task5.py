import os
import re
from collections import defaultdict
from math import sqrt

lemmas_tfidf_folder = "tf_idf_lemmas"
pages_limit = 10

def load_tfidf_vectors(folder_path = lemmas_tfidf_folder):
    vectors = {}
    idf_values = {}

    for fname in os.listdir(folder_path):
        doc_id = os.path.splitext(fname)[0]
        vector = {}
        with open(os.path.join(folder_path, fname), encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split()
                term, idf, tfidf = parts
                vector[term] = float(tfidf)
                if term not in idf_values:
                    idf_values[term] = float(idf)
        vectors[doc_id] = vector
    return vectors, idf_values

def similar_by_cos(a, b):
    dot = sum(a[k]*b.get(k, 0) for k in a)
    norm_a = sqrt(sum(x**2 for x in a.values()))
    norm_b = sqrt(sum(x**2 for x in b.values()))
    return dot / (norm_a * norm_b + 1e-5)

def build_query_vector(query, idf_dict):
    tokens = re.findall(r'\b\w+\b', query.lower())
    tf = defaultdict(int)
    for token in tokens:
        tf[token] += 1
    total = len(tokens)
    tfidf = {}
    for token in tf:
        idf = idf_dict.get(token, 0)
        tfidf[token] = (tf[token] / total) * idf
    return tfidf

def search(query, doc_vectors, idf_dict):
    result = {}
    query_vec = build_query_vector(query, idf_dict)

    scores = []
    for doc_id, vec in doc_vectors.items():
        score = similar_by_cos(query_vec, vec)
        scores.append((score, doc_id))

    scores.sort(reverse=True)
    for score, doc in scores[:pages_limit]:
        if score != float(0):
            doc_num = re.findall("\d+", doc)[0]
            result[doc_num] = score
            print(f"Страница {doc_num} — соответствие: {score:.5f}")

    return result

if __name__ == "__main__":
    doc_vectors, idf_dict = load_tfidf_vectors()
    query = ""
    while query != "exit":
        query = input("Введите поисковый запрос (или exit для выхода): ")
        search(query, doc_vectors, idf_dict)
