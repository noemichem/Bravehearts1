import math

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
            return self.freqs[self.pos]/self.doc[self.docid()][1]

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