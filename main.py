import os
import re
from bs4 import BeautifulSoup
import spacy

nlp = spacy.load("ru_core_news_sm")

# достаем текст без разметки
def extract_text_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    text = soup.get_text()
    return text

# очищаем от лишних слова
def clean_tokens(tokens):
    stop_words = nlp.Defaults.stop_words
    doc = nlp(" ".join(tokens))

    cleaned = set()
    for token in doc:
        if (token.text.lower() not in stop_words
                and token.pos_ not in {"ADP", "CCONJ", "SCONJ", "PART", "PRON", "PUNCT"}
        ):
            cleaned.add(token.text.lower())

    return cleaned

# токенизация
def tokenize_and_clean(text):
    tokens = clean_tokens(re.findall(r'\b[а-яА-ЯёЁ]+\b', text))
    return tokens

# распеделяем по леммам
def lemmatize_tokens(tokens):
    lemma_dict = {}
    doc = nlp(" ".join(tokens))
    for token in doc:
        lemma = token.lemma_
        if lemma not in lemma_dict:
            lemma_dict[lemma] = set()
        lemma_dict[lemma].add(token.text)
    return lemma_dict

#
def process_html_files(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(input_dir):
        if filename.endswith(".html"):
            file_path = os.path.join(input_dir, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                html_content = f.read()

            text = extract_text_from_html(html_content)
            tokens = tokenize_and_clean(text)
            lemma_dict = lemmatize_tokens(tokens)

            save_results(tokens, lemma_dict, output_dir, filename.removesuffix(".html"))

# сохранение в файл
def save_results(tokens, lemma_dict, output_dir, filename):
    with open(os.path.join(output_dir, f"tokens_{filename}.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(tokens))

    with open(os.path.join(output_dir, f"lemmas_{filename}.txt"), "w", encoding="utf-8") as f:
        for lemma, words in lemma_dict.items():
            f.write(f"{lemma} {' '.join(words)}\n")


if __name__ == '__main__':
    input_directory = "files"
    output_directory = "RESULT"

    process_html_files(input_directory, output_directory)