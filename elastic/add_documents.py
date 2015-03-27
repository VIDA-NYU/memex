#!/usr/bin/python
from pyelasticsearch import ElasticSearch

from tika import tika

from datetime import datetime
import urllib2
import urlparse
import sys
import os
import base64
import hashlib
from tempfile import mkstemp

def compute_index_entry(url, useTika=False):
    try:
        response = urllib2.urlopen(url)
        html = response.read()
        header = response.info()
        retrieved = apply(datetime, header.getdate('Date')[:6])
        length = header.getheader('Content-Length')
        if length is None:
            length = len(html)
        md5 = header.getheader('Content-MD5')
        if md5 is None:
            md5 = hashlib.md5(html).hexdigest()
        trueurl = response.geturl()

        if useTika:
            doc = extract_text(html, url)
        entry = {
            'url': trueurl,
            'html': base64.b64encode(html),
            'text': doc,
            'length': length,
            'md5': md5
        }
        last_mod = header.getdate('Last-Modified')
        if last_mod: 
            last_mod = apply(datetime, last_mod[:6])
            entry['last_modified'] = last_mod
        if trueurl != url:
            entry['redirect'] = trueurl
        return entry
    except:
        info = sys.exc_info()
        print >>sys.stderr, "Unexpected error:", info[0], info[1]
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
        info = sys.exc_info()
        print >>sys.stderr, "Unexpected error:", info[0], info[1]
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
