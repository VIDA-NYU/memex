#!/usr/bin/python
from pyelasticsearch import ElasticSearch
import sys
import base64
import pprint
from os import environ
        
def search(field, query):

    if len(query) > 0:
        es = ElasticSearch('http://localhost:9200/')

        query = {
            "query": {
                "query_string": {
                    "fields" : [field],
                    "query": ' and  '.join(query[0:]),
                }
            },
            "fields": [field]
        }
        print query
        res = es.search(query, index='memex', doc_type='page')
        hits = res['hits']
        print 'Document found: %d' % hits['total']
        return hits['hits']

def get_context(query):

    if len(query) > 0:
        es = ElasticSearch('http://localhost:9200/')

        query = {
            "query": {
                "match": {
                    "text": {
                        "query": ' and  '.join(query[0:]),
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
    #search(sys.argv[1], sys.argv[2:])
    print get_context(sys.argv[1:])
