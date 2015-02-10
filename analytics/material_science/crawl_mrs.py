import sys
import re
import urllib2
import time
import traceback
import os.path
import requests
from os import walk

#ABSTRACT = re.compile("<li><a title=\"Abstract\" onclick=\"urchinTracker(\'/DisplayAbstract\')\;\"(.*?)\"")
#ABSTRACT = re.compile("<li><a title=\"Abstract\" onclick=\"urchinTracker\(\'/DisplayAbstract\'(.*?)href=\"(.*?)\">Abstract</a></li>")
ABSTRACT = re.compile("displayAbstract\?fromPage=online&amp;aid(.*?)\"")
PDF_ABSTRACT = re.compile("displayFulltext\?type=1&amp;pdftype=1(.*?)\"")
abstract_file_name = "abstracts_urls.csv"

def encode(url):
  return urllib2.quote(url).replace("/", "%2F")

def download_issues(id):
    #1760->
    url = "http://journals.cambridge.org/action/displayIssue?jid=OPL&volumeId=" + str(id)
    print url
    try:
        uniq_urls = set()
        src = open("issues/volume_" + str(id) + ".html", "r").read()
        ##issue_file.write(src)
        ##issue_file.close()
        abstract_file = open(abstract_file_name, "a")
        src = src.replace("\n", " ")
        matches = ABSTRACT.findall(src)
        if matches:
            for match in matches:
                t = match
                print t
                #if len(t) < 20:
                #    continue
                t = t.replace("&amp;", "&").strip()
                #abstract =  "http://journals.cambridge.org/action/" + t
                abstract =  "http://journals.cambridge.org/action/displayAbstract?fromPage=online&aid" + t
                if abstract not in uniq_urls:
                    abstract_file.write(str(id) + "\t" + abstract + "\n")
                    uniq_urls.add(abstract)
        abstract_file.close() 
        return
    except:
        print "Exception: " + url
        print traceback.format_exc()
        return None

def download_abstracts():
    lines = open(abstract_file_name).read().split("\n")
    count = 0
    for line in lines:
        try:
            values = line.strip().split("\t")
            if len(values) < 2:
                print line
                continue
            id = values[0]
            url = values[1]
            filename = "../abstracts_novolume/" + encode(url) + ".html"
            if os.path.isfile(filename):
                continue
            count += 1
            newfilename = "abstracts/" + encode(url) + ".html"
            f = open(newfilename, "w")
            handle = urllib2.urlopen(url)
            src = handle.read()
            f.write(src)
            #f.close()
        except:
            print "Exception: " + url
            print traceback.format_exc()
            print line
            continue
    print count 

def download_issues_cookie(id, cookies):
    #1760->
    filename = "issues/volume_" + str(id) + ".html"
    if os.path.isfile(filename):
        return
    issue_file = open(filename, "w")
    uniq_urls = set()
    url = "http://journals.cambridge.org/action/displayIssue?jid=OPL&volumeId=" + str(id)
    try:
        print id
        res = requests.get(url, cookies = cookies)
        src = res.text
        issue_file.write(src.encode('utf-8'))
        issue_file.close()
        src = src.replace("\n", " ")
        matches = PDF_ABSTRACT.findall(src)
        if matches:
            for match in matches:
                t = match
                t = t.replace("&amp;", "&").strip()
                abstract =  "http://journals.cambridge.org/action/displayFulltext?type=1&amp;pdftype=1" + t + "&toPdf=true"
                if abstract not in uniq_urls:
                    uniq_urls.add(abstract)
        else:
            print "not matched"

        abstract_file = open(abstract_file_name, "a")
        for abstract in uniq_urls:
            abstract_file.write(str(id) + "\t" + abstract + "\n")
        abstract_file.close() 
        return
    except:
        print "Exception: " + url
        print traceback.format_exc()
        return None

def log_in():
    url = "http://journals.cambridge.org/action/login?firstPage=false"
    payload = {'userName' : '198554', 'passWord' : 'Main'}
    s = requests.session()
    r = s.post(url, payload)
    cookies = r.cookies

    return cookies
    """
    volume_url = "http://journals.cambridge.org/action/displayIssue?jid=OPL&volumeId=1717"
    res = requests.get(volume_url, cookies = cookies)
    src = res.text
    src = src.encode('utf-8')
    print src
    """

def download_pdf(cookies):
    with open (abstract_file_name) as lines:
        for line in lines:
            values = line.strip("\n").split("\t")
            volume = values[0]
            url = values[1]
            filename = "pdf/" + encode(url) + ".pdf"
            if os.path.isfile(filename):
                continue
            handle = open(filename, "wb")
            response = requests.get(url, cookies=cookies, stream=True)
            for block in response.iter_content(1024):
                if not block:
                    break
                handle.write(block)
            handle.close()
            
def main(argv):
    mode = argv[0]
    if mode == "issue":
        for i in range(1760, 0, -1):
            download_issues(i)
    if mode == "abstract":
            download_abstracts()

    if mode == "cookie":
            cookies = log_in()
            for i in range(1760, 0, -1):
                download_issues_cookie(i, cookies)
    """        with open("volume.txt") as lines:
                for line in lines:
                    id = line.strip("\n")
                    download_issues_cookie(id, cookies)
    """
    if mode == "pdf":
            cookies = log_in()
            download_pdf(cookies)
if __name__=="__main__":
    main(sys.argv[1:])
