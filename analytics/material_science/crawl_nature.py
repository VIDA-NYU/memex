#Instructions: 
#Notes: you must execute these following tasks in order:
#Task 3 and 4 could run "multiprocess", in other words, you could start multiple crawls.
#1. Crawl level 0: $python crawl_nature.py 0
#2. Crawl level 1: $python crawl_nature.py 1
#3. Crawl fulltext: $python crawl_nature.py text 
#4. Crawl pdf: $python crawl_nature.py pdf
import re
import sys
import requests
import traceback
import os
import urllib2

def encode(url):
    return urllib2.quote(url).replace("/", "%2F")

def crawl_pdf():
    dir = "pdf/"
    if not os.path.exists(dir):
        os.makedirs(dir)
    with open("pdf.txt") as lines:
        for line in lines:
            try:
                url = line.strip("\n")
                srcfile = dir + "/" + encode(url)
                if not os.path.isfile(srcfile):
                    print url
                    f = open(srcfile, "w")
                    response = requests.get(url, stream=True)
                    for block in response.iter_content(1024):
                        if not block:
                            break
                        f.write(block)
                    f.close()
            except:
                traceback.print_exc()
                continue

def crawl_fulltext():
    dir = "fulltext/"
    if not os.path.exists(dir):
        os.makedirs(dir)
    with open("fulltext.txt") as lines:
        for line in lines:
            try:
                url = line.strip("\n")
                srcfile = dir + "/" + encode(url)
                if os.path.isfile(srcfile):
                    src = open(srcfile).read()
                else:
                    print url
                    f = open(srcfile, "w")
                    src = requests.get(url).text
                    src = src.encode("utf-8")
                    f.write(src)
                    f.close()                  
            except:
                traceback.print_exc()
                continue

def crawl_level1():
    FULLTEXT = re.compile("<a class=\"fulltext\" href=\"(/nmat/journal/.*?/full/nmat.*?\.html)\">")
    PDF = re.compile(" <a href=\"(/nmat/journal/.*i?/pdf/nmat.*?\.pdf)\"><abbr title=\"Portable Document Format\">PDF</abbr>")
    dir = "level1/"
    if not os.path.exists(dir):
        os.makedirs(dir)
    fulltextlinks = set()
    pdflinks = set()
    with open("level0.txt") as lines:
        for line in lines:
            try:
                url = line.strip("\n")
                srcfile = dir + "/" + encode(url)
                if os.path.isfile(srcfile):
                    src = open(srcfile).read()
                else:
                    print url
                    f = open(srcfile, "w")
                    src = requests.get(url).text
                    src = src.encode("utf-8")
                    f.write(src)
                    f.close()
                #Get full text links
                matches = FULLTEXT.findall(src)
                if matches:
                    for match in matches:
                        link = "http://www.nature.com/" + match
                        fulltextlinks.add(link)
                else:
                    print "not matches from the link: " + url
    
                #Get pdf links
                matches = PDF.findall(src)
                if matches:
                    for match in matches:
                        link = "http://www.nature.com/" + match
                        pdflinks.add(link)
                else:
                    print "not matches from the link: " + url
               
            except:
                traceback.print_exc()
                continue
    fulltextfile = "fulltext.txt"
    pdffile = "pdf.txt"
    with open(fulltextfile, "w") as out:
        for link in fulltextlinks:
            out.write(link + "\n")
    with open(pdffile, "w") as out:
        for link in pdflinks:
            out.write(link + "\n")
           

def crawl_level0():
    ISSUE = re.compile("href=\"(/nmat/journal.*?)\">")
    try:
        dir = "level0/"
        if not os.path.exists(dir):
            os.makedirs(dir)
        url = "http://www.nature.com/nmat/archive/index.html"
        src = requests.get(url).text
        srcfile = dir + "/" + encode(url)
        with open(srcfile, "w") as f:
            f.write(src)
        urlfile = "level0.txt"
        out = open(urlfile, "w")
        links = set()
        matches = ISSUE.findall(src)
        if matches:
            for match in matches:
                link = "http://www.nature.com/" + match
                links.add(link)
        else:
            print "no match"
        for link in links:
            out.write(link + "\n")
        out.close()
    except:
        traceback.print_exc()

def main(argv):
    if argv[0] == "0":
        crawl_level0()
    elif argv[0] == "1":
        crawl_level1()
    elif argv[0] == "pdf":
        crawl_pdf()
    elif argv[0] == "text":
        crawl_fulltext()

if __name__=="__main__":
    main(sys.argv[1:])
