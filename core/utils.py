import json
import pickle
import re
import string
import time
from pathlib import Path
from typing import List

import nltk
from langdetect import detect
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from nltk.tokenize import word_tokenize

# Download the stopwords
nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)
nltk.download("stopwords", quiet=True)


class Preprocessor:

    @staticmethod
    def preprocess(text: str, lang: str = "english") -> List[str]:

        if lang == "all":
            tmp_lang = detect(text)
            lang = "english" if tmp_lang == "en" else "italian"

        if lang not in stopwords.fileids():
            raise ValueError(
                f"Language '{lang}' is not supported. The language \
                should be one of the following: {stopwords.fileids()}"
            )

        # Lowercase the text
        text = text.lower()

        # Replace ampersand with 'and'
        text = text.replace("&", " and ")

        # Normalize special characters (smart quotes, dashes, etc.)
        text = text.translate(str.maketrans("‘’´“”–-", "'''\"\"--"))

        # Remove unnecessary periods in acronyms
        text = re.sub(r"\.(?!(\S[^. ])|\d)", "", text)

        # Remove punctuation and replace with spaces
        text = text.translate(
            str.maketrans(string.punctuation, " " * len(string.punctuation))
        )

        # Tokenize using NLTK (language aware)
        tokens = word_tokenize(text, language=lang)

        # Remove stopwords for the given language
        stop_words = set(stopwords.words(lang))
        tokens = [word for word in tokens if word not in stop_words]

        # Stemming
        stemmer = SnowballStemmer(lang)

        # Stem the tokens
        tokens = [stemmer.stem(token) for token in tokens]

        return tokens

    @staticmethod
    def profile(f):
        def f_timer(*args, **kwargs):
            start = time.time()
            result = f(*args, **kwargs)
            end = time.time()
            elapsed_time = end - start

            if elapsed_time >= 60:  # If the time is more than a minute
                minutes = int(elapsed_time // 60)
                seconds = elapsed_time % 60
                print(f"{f.__name__}: {minutes} min {seconds:.3f} s")
            elif elapsed_time >= 1:  # If the time is more than a second
                print(f"{f.__name__}: {elapsed_time:.3f} s")
            else:  # If the time is less than a second
                print(f"{f.__name__}: {elapsed_time * 1000:.3f} ms")

            return result

        return f_timer


class InvertedIndexManager:

    @staticmethod
    def load_index(input_file: str):

        input_file_path = Path(input_file)
        if not input_file_path.exists():
            raise ValueError(
                f"Input file {input_file} does not exist.\
                     Make sure the path is correct."
            )

        if not input_file_path.is_file():
            raise ValueError(
                f"Input file {input_file} is not a file. \
                    Make sure to provide a file as input."
            )

        # Load the index from the pickle file
        with open(input_file_path, "rb") as f:
            lexicon, inv, doc_index, stats = pickle.load(f)

        return lexicon, inv, doc_index, stats

    @staticmethod
    def save_index(
        output_folder_path: Path,
        lexicon: dict,
        inv_d: dict,
        inv_f: dict,
        doc_index: list,
        stats: dict,
    ):

        # Save the results as pickle files
        with open(f"{output_folder_path}/index.pkl", "wb") as f:
            pickle.dump(
                (lexicon, {"docids": inv_d, "freqs": inv_f}, doc_index, stats),
                f,
            )

        # Save each part to a separate JSONL file
        with open(
            f"{output_folder_path}/lexicon.json", "w", encoding="utf-8"
        ) as lex_file:
            lex_file.write(json.dumps(lexicon))

        with open(
            f"{output_folder_path}/inverted_file.jsonl", "w", encoding="utf-8"
        ) as inv_file:
            inv_file.write(json.dumps({"docids": inv_d, "freqs": inv_f}))

        with open(
            f"{output_folder_path}/doc_index.jsonl", "w", encoding="utf-8"
        ) as doc_file:
            doc_file.write(json.dumps(doc_index, ensure_ascii=False))

        with open(
            f"{output_folder_path}/stats.json", "w", encoding="utf-8"
        ) as stats_file:
            json.dump(stats, stats_file, ensure_ascii=False, indent=4)


if __name__ == "__main__":

    # Test the inverted index loading
    # input_folder = "./data/index/index_en2/index.pkl"
    # # Load the inverted index
    # lexicon, inv, doc_index, stats = InvertedIndexManager.load_index(
    #     input_folder
    # )  # noqa

    # Test the preprocessor

    text = "This is a sample text for testing the preprocessor function."
    tokens = Preprocessor.preprocess(text, lang="alls")
    print(tokens)
