import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Literal

from tqdm.auto import tqdm

from .utils import InvertedIndexManager, Preprocessor


class Indexing:

    def __init__(
        self,
        input_folder: str,
        output_folder: str,
        lang: Literal["en", "it", "all"],  # noqa
    ) -> None:

        input_folder_path = Path(input_folder)
        if not input_folder_path.exists():
            raise ValueError(
                f"Input folder {input_folder} does not exist.\
                     Make sure the path is correct."
            )

        if not input_folder_path.is_dir():
            raise ValueError(
                f"Input folder {input_folder} is not a directory. \
                    Make sure to provide a directory as input."
            )

        # Get all files that end with .jsonl
        jsonl_files = list(input_folder_path.glob("*.jsonl"))

        if len(jsonl_files) == 0:
            raise ValueError(
                f"No .jsonl files found in the input folder {input_folder}. \
                    Make sure to provide a folder with .jsonl files."
            )

        # Filter files based on language
        if lang != "all":
            self.lang = "english" if lang == "en" else "italian"
            jsonl_files = [
                file for file in jsonl_files if f".{lang}" in file.suffixes[1:]
            ]
        else:
            self.lang = "all"

        self.input_folder = input_folder
        self.output_folder = output_folder
        self.input_files = jsonl_files

        # Initialize data structures
        # "term": [docid, doc_freq, col_freq] where doc_freq is the number of
        # documents in which the term appears and col_freq is the total number
        # of times the term appears in the collection
        self.lexicon = {}
        self.doc_index = {}  # Document index
        self.inv_d = defaultdict(list)  # TermID to list of DocIDs
        # TermID to list of term frequencies in each DocID
        self.inv_f = defaultdict(list)
        self.termid = 0  # TermID counter

        self.num_docs = 0  # Number of documents
        self.total_dl = 0  # Total document length
        self.total_toks = 0  # Total number of tokens

    @Preprocessor.profile
    def build_index(self):

        # Create the output folder if it does not exist
        output_folder_path = Path(self.output_folder)
        if not output_folder_path.exists():
            output_folder_path.mkdir(parents=True)

        for fileid, file in tqdm(
            enumerate(self.input_files),
            desc="Indexing Files",
            total=len(self.input_files),
        ):
            # Open and read the JSONL file
            with open(file, "r", encoding="utf-8") as file_content:
                for line in file_content:
                    doc = json.loads(line)  # Parse JSON line
                    # Assign a new docid incrementally
                    docid = len(self.doc_index)
                    # Tokenize and preprocess text
                    tokens = Preprocessor.preprocess(doc["text"], self.lang)
                    # Count term frequencies in the document
                    token_tf = Counter(tokens)

                    # Update lexicon, inverted file, and document index
                    for token, tf in token_tf.items():
                        # Add term to lexicon if not already present
                        if token not in self.lexicon:
                            # [termid, doc_freq, col_freq] i.e. termid is the term identifier, # noqa
                            #  doc_freq is the number of documents in which the term appears, # noqa
                            # and col_freq is the total number of times the term appears in the # noqa
                            # collection
                            self.lexicon[token] = [
                                self.termid,
                                0,
                                0,
                            ]
                            # Initialize posting lists
                            self.inv_d[self.termid], self.inv_f[self.termid] = (  # noqa
                                [],
                                [],
                            )  # noqa
                            self.termid += 1  # Increment termid

                        # Update posting lists and term frequency
                        token_id = self.lexicon[token][0]  # Get termid
                        # Add docid to posting list
                        self.inv_d[token_id].append(docid)
                        # Add term frequency in posting list
                        self.inv_f[token_id].append(tf)
                        # Increment document frequency i.e the number of
                        # documents in which the term appears
                        self.lexicon[token][1] += 1
                        # Increment collection frequency i.e the total
                        # number of times the term appears in the collection
                        self.lexicon[token][2] += tf

                    # Update document index
                    doclen = len(tokens)  # Document length
                    self.doc_index[docid] = {
                        "doclen": doclen,
                        "url": doc["url"],
                        "title": doc["title"],
                    }
                    self.total_dl += doclen
                    self.num_docs += 1

        # Properties file with collection statistics
        stats = {
            "num_docs": len(self.doc_index),
            "num_terms": len(self.lexicon),
            "total_tokens": self.total_dl,
        }

        InvertedIndexManager.save_index(
            output_folder_path=output_folder_path,
            lexicon=self.lexicon,
            inv_d=self.inv_d,
            inv_f=self.inv_f,
            doc_index=self.doc_index,
            stats=stats,
        )


# Entry point for command-line execution
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Indexing Script")
    parser.add_argument(
        "input_folder", type=Path, help="Path to the input folder"
    )  # noqa
    parser.add_argument(
        "output_folder", type=Path, help="Path to the output folder"
    )  # noqa
    parser.add_argument(
        "--lang", type=str, default="en", help="Language to use (default: 'en')"  # noqa
    )

    args = parser.parse_args()

    # Instantiate and run the Indexing class
    indexer = Indexing(
        str(args.input_folder), str(args.output_folder), args.lang
    )  # noqa
    indexer.build_index()
