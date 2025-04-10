import os
import re
import json

LEMMAS_DIR = 'RESULT'
INDEX_FILE = 'inverted_index.json'

def build_inverted_index(dir_with_lemmas = LEMMAS_DIR, index_file = INDEX_FILE):
    inverted_index = {}
    for doc_id, filename in enumerate(os.listdir(dir_with_lemmas), start=1):
        if "lemmas" in filename:
            with open(os.path.join(dir_with_lemmas, filename), 'r', encoding="utf-8") as file:
                lemmas = file.read().split()
                for lemma in set(lemmas):
                    if lemma not in inverted_index:
                        inverted_index[lemma] = []
                    inverted_index[lemma].append(doc_id)
    with open(index_file, 'w', encoding='utf-8') as file:
        json.dump(inverted_index, file, ensure_ascii=False, indent=4)
    return inverted_index

def evaluate_page_nums(expr, inverted_index, total_docs):
    if isinstance(expr, str):
        return set(inverted_index.get(expr, []))
    elif expr[0] == 'NOT':
        return set(range(1, total_docs + 1)) - evaluate_page_nums(expr[1], inverted_index, total_docs)
    elif expr[0] == 'AND':
        return evaluate_page_nums(expr[1], inverted_index, total_docs) & evaluate_page_nums(expr[2], inverted_index, total_docs)
    elif expr[0] == 'OR':
        return evaluate_page_nums(expr[1], inverted_index, total_docs) | evaluate_page_nums(expr[2], inverted_index, total_docs)

def build_query_pretty_struct(expr):
    if isinstance(expr, list):
        if len(expr) == 1:
            return expr[0]
        if 'NOT' in expr:
            idx = expr.index('NOT')
            return ('NOT', build_query_pretty_struct(expr[idx + 1]))
        if 'AND' in expr:
            idx = expr.index('AND')
            return ('AND', build_query_pretty_struct(expr[:idx][0]), build_query_pretty_struct(expr[idx + 1:][0]))
        if 'OR' in expr:
            idx = expr.index('OR')
            return ('OR', build_query_pretty_struct(expr[:idx][0]), build_query_pretty_struct(expr[idx + 1:][0]))
    return expr

def parse_query(query, inverted_index, total_docs=100):
    tokens = re.findall(r'\(|\)|\bAND\b|\bOR\b|\bNOT\b|\w+', query)
    stack = []
    for token in tokens:
        if token == ')':
            subexpr = []
            while stack and stack[-1] != '(':
                subexpr.insert(0, stack.pop())
            stack.pop()
            stack.append(subexpr)
        else:
            stack.append(token)

    tree = build_query_pretty_struct(stack)
    return evaluate_page_nums(tree, inverted_index, total_docs)


if __name__ == '__main__':
    inverted_index = build_inverted_index()

    query = ""
    print("Для выхода пишите - exit")
    while query != "exit":
        query = input("Напишите запрос: ")
        result = parse_query(query, inverted_index)
        if not result:
            print("Документы соответствующие запросу не найдены")
        else:
            print("Документы, соответствующие запросу:", result)

