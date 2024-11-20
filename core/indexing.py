import sys
import json
from pathlib import Path

from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
from tqdm.auto import tqdm
from typing import Literal

from .utils import Preprocessor, InvertedIndexManager
from .models import LexiconEntry

class Indexing:

    def __init__(self, input_folder: str, output_folder: str , lang: Literal["en", "it"]) -> None:
        
        input_folder_path = Path(input_folder)
        if not input_folder_path.exists():
            raise ValueError(f"Input folder {input_folder} does not exist. Make sure the path is correct.")
        
        if not input_folder_path.is_dir():
            raise ValueError(f"Input folder {input_folder} is not a directory. Make sure to provide a directory as input.")

        # Get all files that end with .jsonl
        jsonl_files = list(input_folder_path.glob('*.jsonl'))
        
        if len(jsonl_files) == 0:
            raise ValueError(f"No .jsonl files found in the input folder {input_folder}. Make sure to provide a folder with .jsonl files.")

        jsonl_files = [file for file in jsonl_files if lang in str(file)]
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.input_files = jsonl_files
        self.lang = "english" if lang == "en" else "italian"

        # Initialize data structures
        self.lexicon = {}               # Term to LexiconEntry mapping
        self.doc_index = []             # Document index
        self.inv_d = defaultdict(list)  # TermID to list of DocIDs
        self.inv_f = defaultdict(list)  # TermID to list of term frequencies in each DocID
        self.termid = 0                 # TermID counter 

        self.num_docs = 0
        self.total_dl = 0
        self.total_toks = 0


    def build_index(self):

        # Create the output folder if it does not exist
        output_folder_path = Path(self.output_folder)
        if not output_folder_path.exists():
            output_folder_path.mkdir(parents=True)

        for fileid, file in tqdm(enumerate(self.input_files), desc="Indexing Files", total=len(self.input_files)):
            # Open and read the JSONL file
            with open(file, 'r', encoding='utf-8') as file_content:
                for line in file_content:
                    doc = json.loads(line)                                             # Parse JSON line
                    docid = len(self.doc_index)                                        # Assign a new docid incrementally
                    tokens = Preprocessor.preprocess(doc['text'], self.lang)           # Preprocessed text is already tokenized
                    token_tf = Counter(tokens)                                         # Count term frequencies in the document

                    # Update lexicon, inverted file, and document index
                    for token, tf in token_tf.items():
                        # Add term to lexicon if not already present
                        if token not in self.lexicon:
                            # self.lexicon[token] = LexiconEntry(termid=self.termid)
                            # self.termid += 1
                            
                            self.lexicon[token] = [self.termid, 0, 0]
                            self.inv_d[self.termid], self.inv_f[self.termid] =  [], []
                            self.termid += 1

                        # Update posting lists and term frequency

                        token_id = self.lexicon[token][0]
                        self.inv_d[token_id].append(docid)
                        self.inv_f[token_id].append(tf)
                        self.lexicon[token][1] += 1
                        self.lexicon[token][2] += tf


                        # lex_entry = self.lexicon[token]
                        # term_id = lex_entry.termid
                        # self.inv_d[term_id].append(docid)          # Add docid to posting list
                        # self.inv_f[term_id].append(tf)             # Add term frequency in docid
                        # lex_entry.doc_freq += 1               # Update document frequency
                        # lex_entry.col_freq += tf              # Update collection term frequency

                    # Document length and statistics
                    # doclen = len(tokens)
                    # self.doc_index.append({"docid": str(doc['doc_id']), "length": doclen})  # Add to document index
                    # self.total_dl += doclen                            # Accumulate total doc length
                    doclen = len(tokens)
                    self.doc_index.append((str(doc['doc_id']), doclen))
                    self.total_dl += doclen
                    self.num_docs += 1
                    
        # Properties file with collection statistics
        stats = {
            'num_docs': len(self.doc_index),
            'num_terms': len(self.lexicon),
            'total_tokens': self.total_dl,
        }

        InvertedIndexManager.save_index(
            output_folder_path = output_folder_path,
            lexicon = self.lexicon,
            inv_d = self.inv_d,
            inv_f = self.inv_f,
            doc_index = self.doc_index,
            stats = stats
        )




# Entry point for command-line execution
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Indexing Script")
    parser.add_argument("input_folder", type=Path, help="Path to the input folder")
    parser.add_argument("output_folder", type=Path, help="Path to the output folder")
    parser.add_argument("--lang", type=str, default="en", help="Language to use (default: 'en')")

    args = parser.parse_args()

    # Instantiate and run the Indexing class
    indexer = Indexing(str(args.input_folder), str(args.output_folder), args.lang)
    indexer.build_index()