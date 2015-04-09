#!/usr/bin/python
from pyelasticsearch import ElasticSearch

from tika import tika
from boilerpipe import boilerpipe

from datetime import datetime
import urlparse
import os
import sys
import base64
import hashlib
import requests

import linecache

from tempfile import mkstemp

def compute_index_entry(url, extractType='tika'):
    try:
        response = requests.get(url)
        html = response.text.encode('utf-8')
        header = response.headers

        retrieved = header['date']
        try:
            length = header['content-length']
        except KeyError:
            length = len(html)
        try:
            md5 = header['content-md5']
        except KeyError:
            md5 = hashlib.md5(html).hexdigest()

        trueurl = response.url

        if 'boilerpipe' in extractType:
            doc = boilerpipe(html=html)
        elif 'tika' in extractType:
            doc = extract_text(html,url)

        entry = {
            'url': trueurl,
            'html': base64.b64encode(html),
            'text': doc,
            'length': length,
            'md5': md5
        }

        if trueurl != url:
            entry['redirect'] = trueurl
        return entry
    except:
        _, exc_obj, tb = sys.exc_info()
        f = tb.tb_frame
        lineno = tb.tb_lineno
        filename = f.f_code.co_filename
        linecache.checkcache(filename)
        line = linecache.getline(filename, lineno, f.f_globals)
        print 'EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj)
        print url
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
        _, exc_obj, tb = sys.exc_info()
        f = tb.tb_frame
        lineno = tb.tb_lineno
        filename = f.f_code.co_filename
        linecache.checkcache(filename)
        line = linecache.getline(filename, lineno, f.f_globals)
        print 'EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj)
        print url
        pass
    os.unlink(tmppath)
    return doc
    

def add_document(entries, es = ElasticSearch('http://localhost:9200/')):
    es.bulk([es.index_op(doc) for doc in entries],
            index='memex',
            doc_type='page')

def update_document(url,doc, es = ElasticSearch('http://localhost:9200/')):
    es.update(index='memex',
              doc_type='page',
              id=url,
              script=doc)

if __name__ == "__main__":
    if len(sys.argv)>1:
        inputfile = sys.argv[1]
        urls = []
        with open(inputfile, 'r') as f:
            for line in f:
                urls.append(line.strip())
    else:
        urls = [
            'http://en.wikipedia.org/wiki/Dark_internet',
            'http://www.dailymail.co.uk/.../article-3017888/...details-sold-dark-web.html',
            'http://en.wikipedia.org/wiki/Deep_Web',
            'http://www.rogerdavies.com/2011/06/dark-internet',
            'http://www.straightdope.com/.../read/3092/how-can-i-access-the-deep-dark-web'
        ]
    entries = []
    for url in urls:
        print 'Retrieving url %s' % url
        e = compute_index_entry(url=url)

        if e: entries.append(e)
    
    if len(entries):
        add_document(entries)
