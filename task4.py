import os
import math
from collections import Counter, defaultdict
from operator import contains

from task3 import build_inverted_index

TOKENS_DIR = 'RESULT'
LEMMAS_DIR = 'RESULT'

OUTPUT_TERMS = 'tf_idf_terms'
OUTPUT_LEMMAS = 'tf_idf_lemmas'
os.makedirs(OUTPUT_TERMS, exist_ok=True)
os.makedirs(OUTPUT_LEMMAS, exist_ok=True)

def read_docs(directory, filename_pattern, parse_line):
    docs = {}
    for filename in os.listdir(directory):
        if contains(filename, filename_pattern):
            with open(os.path.join(directory, filename), 'r', encoding='utf-8') as f:
                terms = []
                for line in f:
                    parsed = parse_line(line.strip())
                    if parsed:
                        terms.extend(parsed)
                docs[filename] = terms
    return docs

token_docs = read_docs(TOKENS_DIR, "tokens", lambda line: [line] if line else [])
lemma_docs = read_docs(LEMMAS_DIR, "lemmas", lambda line: [line.split()[0]] if line else [])

inverted_index = build_inverted_index()

def compute_tf_idf(docs):
    tf_idf_results = {}
    term_idf = {}
    docs_count = len(docs)

    # Считаем IDF
    df_counter = defaultdict(int)
    for doc_terms in docs.values():
        unique_terms = set(doc_terms)
        for term in unique_terms:
            df_counter[term] += 1

    for term, df in df_counter.items():
        term_idf[term] = math.log(docs_count / df)

    # Считаем TF-IDF
    for doc_name, terms in docs.items():
        total_terms = len(terms)
        term_tf = Counter(terms)
        result = []
        for term in term_tf:
            tf = term_tf[term] / total_terms  # доля
            idf = term_idf[term]
            tfidf = tf * idf
            result.append((term, idf, tfidf))
        tf_idf_results[doc_name] = result

    return tf_idf_results

def save_tf_idf(results, output_dir):
    for filename, data in results.items():
        with open(os.path.join(output_dir, filename), 'w', encoding='utf-8') as f:
            for term, idf, tfidf in data:
                f.write(f'{term} {idf:.6f} {tfidf:.6f}\n')

if __name__ == '__main__':
    term_results = compute_tf_idf(token_docs)
    lemma_results = compute_tf_idf(lemma_docs)
    save_tf_idf(term_results, OUTPUT_TERMS)
    save_tf_idf(lemma_results, OUTPUT_LEMMAS)
