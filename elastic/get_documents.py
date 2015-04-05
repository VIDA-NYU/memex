#!/usr/bin/python
from pyelasticsearch import ElasticSearch
import sys

def get_documents(urls):
    if len(urls) > 0:
        es = ElasticSearch('http://localhost:9200/')
        
        results = {}

        for url in urls:
            query = {
                "query": {
                    "term": {
                        "url": url
                    }
                },
                "fields": ["text"]
            }
        
            res = es.search(query, index='memex', doc_type='page')
            hits = res['hits']
            try:
                results[url] = hits['hits'][0]['fields']['text'][0]
            except KeyError, e:
                print url, " not found in database"
            except IndexError, e:
                print url, " not found in database"

        return results

if __name__ == "__main__":
    urls = []
    with open(environ['MEMEX_HOME']+'/seed_crawler/seeds_generator/results.txt', 'r') as f:
        urls = f.readlines()
    urls = [url.strip() for url in urls]

    docs = get_documents(urls)

