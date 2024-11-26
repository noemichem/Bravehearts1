import math
import heapq

class InvertedIndex:

    class PostingListIterator:
        def __init__(self, docids, freqs, doc):
            self.docids = docids
            self.freqs = freqs
            self.pos = 0
            self.doc = doc

        def docid(self):
            if self.is_end_list():
                return math.inf
            return self.docids[self.pos]

        def score(self):
            if self.is_end_list():
                return math.inf
            return self.freqs[self.pos]/self.doc[self.docid()]['doclen']

        def next(self, target = None):
            if not target:
                if not self.is_end_list():
                    self.pos += 1
            else:
                if target > self.docid():
                    try:
                        self.pos = self.docids.index(target, self.pos)
                    except ValueError:
                        self.pos = len(self.docids)

        def is_end_list(self):
            return self.pos == len(self.docids)


        def len(self):
            return len(self.docids)


    def __init__(self, lex, inv, doc, stats):
        self.lexicon = lex
        self.inv = inv
        self.doc = doc
        self.stat = stats

    def num_docs(self):
        return self.stats['num_docs']

    def get_posting(self, termid):
        return InvertedIndex.PostingListIterator(self.inv['docids'][termid], self.inv['freqs'][termid], self.doc)

    def get_termids(self, tokens):
        return [self.lexicon[token][0] for token in tokens if token in self.lexicon]

    def get_postings(self, termids):
        return [self.get_posting(termid) for termid in termids]


class TopQueue:
    def __init__(self, k=10, threshold=0.0):
        self.queue = []
        self.k = k
        self.threshold = threshold

    def size(self):
        return len(self.queue)

    def would_enter(self, score):
        return score > self.threshold

    def clear(self, new_threshold=None):
        self.queue = []
        if new_threshold:
            self.threshold = new_threshold

    def __repr__(self):
        return f'<{self.size()} items, th={self.threshold} {self.queue}'

    def insert(self, docid, score):
        if score > self.threshold:
            if self.size() >= self.k:
                heapq.heapreplace(self.queue, (score, docid))
            else:
                heapq.heappush(self.queue, (score, docid))
            if self.size() >= self.k:
                self.threshold = max(self.threshold, self.queue[0][0])
            return True
        return False