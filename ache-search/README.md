# ACHE Search

Just open the file `index.html` and adjust the line:

    .constant('euiHost', 'http://localhost:9200/')

to point to your ElasticSearch server. Then, configure the indexes in the variable `$scope.domains`.
You should provide an object with two properties:

    {
        name: 'a name of you domain',
        index 'the name of the index in elastic search for your domain'
    }

Open the `index.html` in your browser.
Alternatively, you can run in a server. Ex:

    cd ache-search
    python -m SimpleHTTPServer 8000

Then go to: `http://localhost:8000`

