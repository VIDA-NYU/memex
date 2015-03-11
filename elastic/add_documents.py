#!/usr/bin/python
from pyelasticsearch import ElasticSearch

from tika import tika

from datetime import datetime
import urllib2
import urlparse
import sys
import os
from tempfile import mkstemp

def compute_index_entry(url, useTika=False):
    try:
        doc = urllib2.urlopen(url).read()
        if useTika:
            doc = extract_text(doc, url)
        entry = {
            'url': url,
            'text': doc,
            'fetched': datetime.now(),
        }
        return entry
    except:
        print >>sys.stderr, "Unexpected error:", sys.exc_info()[0]
        pass
    return None

def extract_text(doc, url):
    o = urlparse.urlparse(url)
    _, ext = os.path.splitext(o.path)
    handle, tmppath = mkstemp(suffix=ext)
    try:
        os.write(handle, doc)
        os.close(handle)
        (doc, metadata) = tika(tmppath, url)
    except:
        print >>sys.stderr, "Unexpected error:", sys.exc_info()[0]
        pass
    os.unlink(tmppath)
    return doc



if __name__ == "__main__":
    if len(sys.argv)>1:
        urls = sys.argv[1:]
    else:
        urls = [
            'https://docs.python.org/2/library/urlparse.html',
            'http://logging.apache.org/log4j/1.2/manual.html',
            'http://en.wikipedia.org/wiki/Paris'
        ]
    entries = []
    for url in urls:
        print 'Retrieving url %s' % url
        e = compute_index_entry(url,True)
        if e: entries.append(e)
    if len(entries):
        es = ElasticSearch('http://localhost:9200/')
        es.bulk((es.index_op(doc) for doc in entries),
                index='memex',
                doc_type='page')


