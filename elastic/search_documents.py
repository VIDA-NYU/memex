#!/usr/bin/python
from pyelasticsearch import ElasticSearch
import sys
import pprint


if len(sys.argv) > 1:
    es = ElasticSearch('http://localhost:9200/')
    
    query = {
        "query" : {
            "query_string": {
                "query": "text:"+' '.join(sys.argv[1:])
            }
        }
    }
    res = es.search(query, index='memex', doc_type='page')
    hits = res['hits']
    print 'Document found: %d' % hits['total']
    for doc in hits['hits']:
        print '\turl: %s' % doc['_id']
    #pprint.pprint(res)

