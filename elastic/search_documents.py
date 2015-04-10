#!/usr/bin/python
from pyelasticsearch import ElasticSearch
import sys
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
        res = es.search(query, index='memex', doc_type='page')
        hits = res['hits']
        pprint.pprint(hits)
        print 'Document found: %d' % hits['total']
        return hits['hits']

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
        term_search(sys.argv[2], sys.argv[3:])
    elif 'context' in sys.argv[1]:
        print get_context(sys.argv[2:])
