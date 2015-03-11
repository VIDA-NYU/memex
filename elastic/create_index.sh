curl -XPUT 'http://localhost:9200/memex/'
#  -d '{
#     "index" : {
# 	"analysis":{
# 	    "analyzer":{
# 		"html" : {
# 	            "type" : "custom",
# 		    "tokenizer" : "standard",
#                     "filter" : ["lowercase" , "stop"],
#                     "char_filter" : ["html_strip"]
#                 }
#             }
# 	}
#     }
# }'
