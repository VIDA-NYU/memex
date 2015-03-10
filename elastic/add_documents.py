#!/usr/bin/python
from pyelasticsearch import ElasticSearch

from datetime import datetime
import urllib2
import sys

def compute_index_entry(url):
    try:
        doc = urllib2.urlopen(url).read()
        entry = {
            'url': url,
            'text': doc,
            'fetched': datetime.now(),
        }
        return entry
    except:
        pass
    return None




def main(argv):
    entries = []
    for url in argv:
        e = compute_index_entry(url)
        if e: entries.append(e)
    if len(entries):
        es = ElasticSearch('http://localhost:9200/')
        es.bulk((es.index_op(doc) for doc in entries),
                index='memex',
                doc_type='page')


if __name__ == "__main__":
   main(sys.argv[1:])

