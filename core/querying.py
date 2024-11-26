import math
from collections import defaultdict
from .models import InvertedIndex, TopQueue
from .utils import InvertedIndexManager, Preprocessor


class QueryProcessor:

    def __init__(self, index_file):
        lex, inv, doc, stats = InvertedIndexManager.load_index(index_file)
        self.inv_index = InvertedIndex(lex, inv, doc, stats)
        self.doc = doc

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
    def taat(self, postings, k=10):
        A = defaultdict(float)
        for posting in postings:
            current_docid = posting.docid()
            while current_docid != math.inf:
                A[current_docid] += posting.score()
                posting.next()
                current_docid = posting.docid()
        top = TopQueue(k)
        for docid, score in A.items():
            top.insert(docid, score)
        return sorted(top.queue, reverse=True)

    def query_process_taat(self, query):
        qtokens = set(Preprocessor.preprocess(query))
        qtermids = self.inv_index.get_termids(qtokens)
        postings = self.inv_index.get_postings(qtermids)
        return self.taat(postings)

    ## DAAT Algorithm
    def daat(self, postings, k=10):
        top = TopQueue(k)
        current_docid = self.min_docid(postings)
        while current_docid != math.inf:
            score = 0
            next_docid = math.inf
            for posting in postings:
                if posting.docid() == current_docid:
                    score += posting.score()
                    posting.next()
                if not posting.is_end_list():
                    next_docid = posting.docid()
            top.insert(current_docid, score)
            current_docid = next_docid
        return sorted(top.queue, reverse=True)

    def query_process_daat(self, query):
        qtokens = set(Preprocessor.preprocess(query))
        qtermids = self.inv_index.get_termids(qtokens)
        postings = self.inv_index.get_postings(qtermids)
        return self.daat(postings)

    def prepare_final_result(self, scores_docids):
        final_result = []
        for score, docid in scores_docids:
            doc = self.doc[docid]
            final_result.append({'docid': docid, 'title': doc['title'], 'url': doc['url'], 'score': score,})

        return final_result


if __name__ == '__main__':
    
    input_folder = "./outputs/index_en2/index.pkl"
    
    query_processor = QueryProcessor(input_folder)
    result = query_processor.query_process_taat('Marco Raugi')
    # print(result)
    print(query_processor.prepare_final_result(result))