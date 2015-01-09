import sys
import re
import urllib2
import time
import traceback
import os.path
from os import walk

#ABSTRACT = re.compile("<li><a title=\"Abstract\" onclick=\"urchinTracker(\'/DisplayAbstract\')\;\"(.*?)\"")
ABSTRACT = re.compile("<li><a title=\"Abstract\" onclick=\"urchinTracker\(\'/DisplayAbstract\'(.*?)href=\"(.*?)\">Abstract</a></li>")
abstract_file_name = "abstracts_urls.csv"

def encode(url):
  return urllib2.quote(url).replace("/", "%2F")

def download_issues(id):
    url = "http://journals.cambridge.org/action/displayIssue?jid=OPL&volumeId=" + str(id)
    print url
    try:
        handle = urllib2.urlopen(url)
        src = handle.read()
        issue_file = open("issues/volume_" + str(id) + ".html", "w")
        issue_file.write(src)
        issue_file.close()
        abstract_file = open(abstract_file_name, "a")
        src = src.replace("\n", " ")
        matches = ABSTRACT.findall(src)
        if matches:
            for match in matches:
                for t in match:
                    if len(t) < 20:
                        continue
                    t = t.replace("&amp;", "&").strip()
                    abstract =  "http://journals.cambridge.org/action/" + t
                    abstract_file.write(str(id) + "\t" + abstract + "\n")
        abstract_file.close()    
    except:
        print "Exception: " + url
        print traceback.format_exc()
        return None

def download_abstracts():
    lines = open(abstract_file_name).read().split("\n")
    for line in lines:
        try:
            values = line.strip().split("\t")
            id = values[0]
            url = values[1]
            filename = "abstracts_html/" + encode(url) + ".html"
            if os.path.isfile(filename):
                continue
            print line
            f = open(filename, "w")
            handle = urllib2.urlopen(url)
            src = handle.read()
            f.write(src)
            f.close()
        except:
            print "Exception: " + url
            print traceback.format_exc()

def main(argv):
    mode = argv[0]
    if mode == "issue":
        for i in range(1760, 0, -1):
            download_issues(i)
    if mode == "abstract":
            download_abstracts()

if __name__=="__main__":
    main(sys.argv[1:])
