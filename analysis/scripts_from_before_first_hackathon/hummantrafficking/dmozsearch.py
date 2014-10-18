import sys
import re

'''
This script extracts urls from dmoz given list of topic.
If limit is true, the script saves at most 1 url for each leaf topic to have better coverage
Usage:
  $python dmozsearch.py file_contains_topics outputfile_contains_urls limit
  limit can be set 0 or 1

'''

RDF = "content.rdf.u8"
START = re.compile("<Topic r:id=\"(.*)\">")
END = re.compile("</Topic>")
LINK = re.compile("<link r:resource=\"(.*)\"></link>")

def get_links(topics, output, limit):
  links = []
  inTopic = False
  rightTopic = False
  count = 0
  topic = ""
  with open(RDF)as lines:
    for line in lines:
      count += 1
      if (count % 1000000) == 0:
        print "Processing..." + str(count)
      if inTopic:
        END_match = END.search(line)
        if END_match:
          inTopic = False
          rightTopic = False
        else:
          if rightTopic:
            LINK_match = LINK.search(line)
            if LINK_match:
              output.write(LINK_match.group(1) + "\t" + topic + "\n")
              if limit:
                rightTopic = False 
      else:
        START_match = START.search(line)
        if START_match:
          inTopic = True
          topic = START_match.group(1)
          if check_topic(topics, topic):
            rightTopic = True

def check_topic(topics, topic):
  topic = "/" + topic + "/"
  for t in topics:
    if t in topic:
      return True
  else:
      return False

def main(argv):
  topics_file = argv[0]
  output_file = open(argv[1], "w")
  limit = True
  if len(argv) == 3:
    limit = int(argv[2])
  topics = []
  with open(topics_file) as lines:
    for line in lines:
      topics.append("/" + line.strip("\n/") + "/")
  get_links(topics, output_file, limit)
  output_file.close()

if __name__=="__main__":
  main(sys.argv[1:])
