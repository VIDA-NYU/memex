#!/usr/bin/python
from pyelasticsearch import ElasticSearch
import sys
import pprint


es = ElasticSearch('http://localhost:9200/')
query = {
    "query": {
        "match_all": {}
    },
    "fields": []
}
res = es.search(query, index='memex', doc_type='page')
hits = res['hits']
print 'Document found: %d' % hits['total']
ids = [hit['_id'] for hit in hits['hits']]
pprint.pprint(ids)
body={
    "ids": ids,
    "parameters": {
        "fields": [ "text" ]
    }
}
res = es.send_request('POST',
                      ['memex', 'page', '_mtermvectors'],
                      body=body, query_params={})
pprint.pprint(res)

