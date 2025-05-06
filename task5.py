import os
import re
from collections import defaultdict

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

URLS_FILE_PATH = "files/index.txt"
TFIDF_DIR = "TF_IDF_LEMMAS"

def load_tfidf_idf(tfidf_dir = TFIDF_DIR):
    tfidf_docs_vectors = {} # doc number -> dict(term, tfidf)
    all_terms_idf_values = {} # term -> idf

    for fname in os.listdir(tfidf_dir):
        doc_id = int(re.search(r'\d+', fname).group())
        vector = {}
        with open(os.path.join(tfidf_dir, fname), encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split()
                term, idf, tfidf = parts
                vector[term] = float(tfidf)
                if term not in all_terms_idf_values:
                    all_terms_idf_values[term] = float(idf)
        tfidf_docs_vectors[doc_id] = vector
    return tfidf_docs_vectors, all_terms_idf_values

def load_pages_url(urls_file_path = URLS_FILE_PATH):
    page_urls_map = {}

    with open(urls_file_path, "r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue

            parts = line.strip().split("->")
            if len(parts) < 2:
                continue

            page_number_str = parts[0].strip()
            url = parts[1].strip()

            try:
                page_number = int(page_number_str)
                page_urls_map[page_number] = url
            except ValueError:
                continue

    return page_urls_map

def build_query_vector(query, idf_dict):
    tokens = re.findall(r'\b\w+\b', query.lower())
    token_count = defaultdict(int)
    for token in tokens:
        token_count[token] += 1
    total = len(tokens)
    tfidf = {}
    for token in token_count:
        idf = idf_dict.get(token, 0)
        tf = (token_count[token] / total)
        tfidf[token] = tf * idf
    return tfidf

def get_cos_similarity(query_vector, docs_vectors, vocabulary):
    query_array = np.array([query_vector.get(term, 0) for term in vocabulary])

    similarities = []
    for page_num, doc_vector in docs_vectors.items():
        doc_array = np.array([doc_vector.get(term, 0) for term in vocabulary])
        similarity = cosine_similarity([query_array], [doc_array])[0][0]
        similarities.append((page_num, similarity))

    similarities.sort(key=lambda x: x[1], reverse=True)
    return similarities

def search(query, limit = 10):
    result = []
    urls = load_pages_url()
    docs_vectors, all_terms_idf_values = load_tfidf_idf()
    query_vector = build_query_vector(query, all_terms_idf_values)

    similarities = get_cos_similarity(query_vector, docs_vectors, all_terms_idf_values.keys())
    for similarity in similarities:
        result.append((similarity[0], urls[similarity[0]], similarity[1]))
    return result[:limit]

def print_result(result):
    for item in result:
        print(f"Страница {item[0]}, сходство - {item[1]}, ссылка: {item[2]}")

if __name__ == '__main__':
    query = input("Введите запрос: ")
    print_result(search(query))