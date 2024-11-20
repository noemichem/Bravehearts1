import math
from collections import defaultdict
from .models import InvertedIndex
from .utils import InvertedIndexManager, Preprocessor


class QueryProcessor:

    def __init__(self, index_file):
        lex, inv, doc, stats = InvertedIndexManager.load_index(index_file)
        self.inv_index = InvertedIndex(lex, inv, doc, stats)

    # Conjunctive processing
    def boolean_and(self, postings):
        results = []
        # We sort the posting lists from the shortest to the longest
        postings = sorted(postings, key=lambda p: p.len())
        # We scan sequentially through the shortest posting list only
        current_docid = postings[0].docid()
        while current_docid != math.inf:
            found = True
            # We look for the current docid is all remaining posting lists
            for posting in postings[1:]:
                posting.next(current_docid)
                if posting.docid() != current_docid:
                    found = False
                    break
            # If the current docid is in all posting lists, we add it to results
            if found:
                results.append(current_docid)
            # We move forward in the shortest posting list
            postings[0].next()
            current_docid = postings[0].docid()
        return results

    def query_process_and(self, query):
        qtokens = set(Preprocessor.preprocess(query))
        qtermids = self.inv_index.get_termids(qtokens)
        postings = self.inv_index.get_postings(qtermids)
        return self.boolean_and(postings)


    # Disjunctive processing
    def min_docid(self, postings):
        min_docid = math.inf
        for p in postings:
            if not p.is_end_list():
                min_docid = min(p.docid(), min_docid)
        return min_docid

    def boolean_or(self, postings):
        results = []
        current_docid = self.min_docid(postings)
        while current_docid != math.inf:
            results.append(current_docid)
            for posting in postings:
                if posting.docid() == current_docid:
                    posting.next()
            current_docid = self.min_docid(postings)
        return results

    def query_process_or(self, query):
        qtokens = set(Preprocessor.preprocess(query))
        qtermids = self.inv_index.get_termids(qtokens)
        postings = self.inv_index.get_postings(qtermids)
        return self.boolean_or(postings)



# TAAT Algorithm



if __name__ == '__main__':
    
    input_folder = "./outputs/index_en/index.pkl"
    
    query_processor = QueryProcessor(input_folder)
    print(query_processor.query_process_and('unipi'))