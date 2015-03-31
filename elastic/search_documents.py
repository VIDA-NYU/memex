#!/usr/bin/python
from pyelasticsearch import ElasticSearch
import sys
import base64

def search(field, query):

    if len(query) > 0:
        es = ElasticSearch('http://localhost:9200/')
        
        if field in ['html']:
            query = [base64.b64encode(q) for q in query]

        query = {
            "query" : {
                "query_string": {
                    "query": field +':'+' '.join(query[0:])
                }
            }
        }
        print query
        res = es.search(query, index='memex', doc_type='page')
        hits = res['hits']
        print 'Document found: %d' % hits['total']
        return hits['hits']


if __name__ == "__main__":
    print sys.argv[1:]
    docs = search(sys.argv[1],sys.argv[2:])
    for doc in docs:
        print '\turl: %s' % doc['_id']
        
