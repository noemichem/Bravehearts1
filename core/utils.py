import pickle
import json
import re
import string
import nltk
from nltk.tokenize import word_tokenize
from nltk.tokenize import regexp_tokenize
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from typing import List
from pathlib import Path
from dataclasses import dataclass, asdict

from .models import LexiconEntry

# Download the stopwords
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)
nltk.download('stopwords', quiet=True)

class Preprocessor:
   
    @staticmethod
    def preprocess(text: str, lang: str = "english") -> List[str]:
        
        if lang not in stopwords.fileids():
          raise ValueError(f"Language '{lang}' is not supported. The language should be one of the following: {stopwords.fileids()}")

        # Lowercase the text
        text = text.lower()
        
        # Replace ampersand with 'and'
        text = text.replace("&", " and ")
        
        # Normalize special characters (smart quotes, dashes, etc.)
        text = text.translate(str.maketrans("‘’´“”–-", "'''\"\"--"))
        
        # Remove unnecessary periods in acronyms
        text = re.sub(r"\.(?!(\S[^. ])|\d)", "", text)
        
        # Remove punctuation and replace with spaces
        text = text.translate(str.maketrans(string.punctuation, " " * len(string.punctuation)))
        
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


class InvertedIndexManager:

    @staticmethod
    def load_index(input_file: str) :

        input_file_path = Path(input_file)
        if not input_file_path.exists():
            raise ValueError(f"Input file {input_file} does not exist. Make sure the path is correct.")
        
        if not input_file_path.is_file():
            raise ValueError(f"Input file {input_file} is not a file. Make sure to provide a file as input.")


        # Load the index from the pickle file
        with open(input_file_path, 'rb') as f:
            lexicon, inv, doc_index, stats = pickle.load(f)


        return lexicon, inv, doc_index, stats




    @staticmethod
    def save_index(output_folder_path: Path, lexicon: dict, inv_d: dict, inv_f: dict, doc_index: list, stats: dict):

        # Save the results as pickle files
        with open(f"{output_folder_path}/index.pkl", 'wb') as f:
            pickle.dump((lexicon, {'docids': inv_d, 'freqs': inv_f}, doc_index, stats), f)
        
        # Save each part to a separate JSONL file
        with open(f"{output_folder_path}/lexicon.json", 'w', encoding='utf-8') as lex_file:
            lex_file.write(json.dumps(lexicon))

        with open(f"{output_folder_path}/inverted_file.jsonl", 'w', encoding='utf-8') as inv_file:
            inv_file.write(json.dumps({'docids': inv_d, 'freqs': inv_f}) )

        with open(f"{output_folder_path}/doc_index.jsonl", 'w', encoding='utf-8') as doc_file:
            for doc_entry in doc_index:
                doc_file.write(json.dumps(doc_entry, ensure_ascii=False) + '\n')

        with open(f"{output_folder_path}/stats.json", 'w', encoding='utf-8') as stats_file:
            json.dump(stats, stats_file, ensure_ascii=False, indent=4)




if __name__ == "__main__":
   
    input_folder = "./outputs/index_en/index.pkl"
    # Load the inverted index
    lexicon, inv, doc_index, stats = InvertedIndexManager.load_index(input_folder)

    import pdb; pdb.set_trace()

