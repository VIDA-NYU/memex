# ACHE Search

Just open the file `index.html` and adjust the line:

    .constant('euiHost', 'http://localhost:9200/')

to point to your ElasticSearch server. Then, configure the indexes in the variable `$scope.domains`.
You should provide an object with two properties:

    {
        name: 'a name of you domain',
        index 'the name of the index in elastic search for your domain'
    }

Open the `index.html` in your browser. In order for this to work, you might have to enable [CORS](http://www.elastic.co/guide/en/elasticsearch/reference/current/modules-http.html) (option `http.cors.enabled`) and allow requests to Elasticsearch from any host (this is not enabled by default for security reasons and should not be used in production).

Alternatively, you can serve the static files in a web server, e.g.:

    cd ache-search
    python -m SimpleHTTPServer 8000

Then go to: `http://localhost:8000`

