#!/usr/bin/python
from pyelasticsearch import ElasticSearch
import sys
import urllib2
import base64
import pprint
from os import environ
        
def search(field, queryStr):
    print "field = ",field, "query str =", queryStr
    es_server = 'http://localhost:9200/'
    if environ.get('ELASTICSEARCH_SERVER'):
        es_server = environ['ELASTICSEARCH_SERVER']
    es = ElasticSearch(es_server)

    if len(queryStr) > 0:
        query = {
            "query": {
                "query_string": {
                    "fields" : [field],
                    "query": ' and  '.join(queryStr[0:]),
                }
            },
            "fields": [field]
        }
        print query
        res = es.search(query, index='memex', doc_type='page')
        hits = res['hits']
        print 'Document found: %d' % hits['total']
        return hits['hits']

def term_search(field, queryStr):
    es_server = 'http://localhost:9200/'
    if environ.get('ELASTICSEARCH_SERVER'):
        es_server = environ['ELASTICSEARCH_SERVER']
    es = ElasticSearch(es_server)

    if len(queryStr) > 0:
        query = {
            "query" : {
                "match": {
                    field: {
                        "query": queryStr,
                        "operator" : "and"
                        }
                    }
                },
            "fields": ["url"]
            }
        print query
        res = es.search(query, index='memex', doc_type='page', size=500)
        hits = res['hits']
        urls = []
        for hit in hits['hits']:
            urls.append(hit['_id'])
        print len(urls), len(hits['hits'])
        return urls

def get_image(url, output_path=""):
    es_server = 'http://localhost:9200/'
    if environ.get('ELASTICSEARCH_SERVER'):
        es_server = environ['ELASTICSEARCH_SERVER']
    es = ElasticSearch(es_server)

    if output_path:
        output_path = output_path+'/'

    if url:
        query = {
            "query": {
                "term": {
                    "url": url
                }
            },
            "fields": ["thumbnail"]
        }
        res = es.search(query, index='memex', doc_type='page')
        hits = res['hits']
        if (len(hits) > 0):
            img = base64.b64decode(hits['hits'][0]['fields']['thumbnail'][0])
            with open(output_path+urllib2.quote(url).replace("/", "%2F")+'.png','wb') as f:
                f.write(img)
        else:
            print "No thumbnail found"

def get_context(terms):
    es_server = 'http://localhost:9200/'
    if environ.get('ELASTICSEARCH_SERVER'):
        es_server = environ['ELASTICSEARCH_SERVER']
    es = ElasticSearch(es_server)

    if len(terms) > 0:

        query = {
            "query": { 
                "match": {
                    "text": {
                        "query": ' and  '.join(terms[0:]),
                        "operator" : "and"
                    }
                }
             },
            "highlight" : {
                "fields" : {
                    "text": {
                        "fragment_size" : 100, "number_of_fragments" : 1
                    }
                }
            }
        }
        print query
        res = es.search(query, index='memex', doc_type='page')
        hits = res['hits']
        print 'Document found: %d' % hits['total']
        highlights = []
        for hit in hits['hits']:
            highlights.append(hit['highlight']['text'])
        return highlights

if __name__ == "__main__":
    print sys.argv[1:]
    if 'string' in sys.argv[1]:
        search(sys.argv[2], sys.argv[3:])
    elif 'term' in sys.argv[1]:
        for url in term_search(sys.argv[2], sys.argv[3:]):
            print url
    elif 'context' in sys.argv[1]:
        print get_context(sys.argv[2:])
    elif 'image' in sys.argv[1]:
        get_image(sys.argv[2])
