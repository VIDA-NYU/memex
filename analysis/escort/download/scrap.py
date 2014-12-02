#You need to install langdetect and boilerpipe, a python wrapper of boilerpipe java:
# pip install langdetect
# Boilerpipe: https://github.com/ptwobrussell/python-boilerpipe/
#Usage:
# Download html content from the given url list
#   python scrap.py <path_to_url_list_file> html <output_path>"
# Filter the urls that are not in English
#   python scrap.py <path_to_url_list_file> url <output_filename>"

import urllib2
import sys
import re
import urllib
from langdetect import detect_langs
from langdetect import detect
from boilerpipe.extract import Extractor
#from time import sleep
import socket

def encode(url):
  return urllib.quote(url).replace("/", "%2F")

def decode(url):
  return urllib.unquote(url).replace("%2F", "/")

def detect_english(text_content):
  try:
    lang = detect(text_content)
    if lang == 'en':
      return True
    else:
      return False
  except:
    print "error in english detection"
    return False

def extract_text(html_content):
  try:
    extractor = Extractor(extractor='KeepEverythingExtractor', html=html_content)
    #print extractor.getText()
    return extractor.getText()
  except:
    print "Exception in html extraction"
    return None

def download_html_content_no_check_english(filename, path):
  """ This function downloads page source and saves it to file
      Input: a file containing list of urls
      path: directory that the page source will be saved
  """
  with open(filename) as lines:
    for line in lines:
      try:
        url = line.strip("\n")
        handle = urllib2.urlopen(url)
        src = handle.read()
        #src = src.encode('utf-8')
        print "GOOD\t" + url
        encoded_url = encode(url)
        f = open(path + "/" + encoded_url, "w")
        f.write(src)
        f.close()
      except urllib2.HTTPError, e:
        print 'HTTPERROR=' + str(e.code) + "\t" + url
      except socket.timeout, e:
        print 'TIMEOUT=' + str(e) + "\t" + url
      except:
        print 'EXCEPTION' + "\t" + url

def download_html_content(filename, path):
  """ This function downloads page source and saves it to file
      Input: a file containing list of urls
      path: directory that the page source will be saved
  """
  with open(filename) as lines:
    for line in lines:
      try:
        url = line.strip("\n")
        handle = urllib2.urlopen(url)
        src = handle.read()
        #src = src.encode('utf-8')
        text_content = extract_text(src)
        if text_content:
          if detect_english(text_content):
            print "GOOD\t" + url
            encoded_url = encode(url)
            f = open(path + "/" + encoded_url, "w")
            f.write(src)
            f.close()
          else:
            print "NON-ENGLISH\t" + url
      except urllib2.HTTPError, e:
        print 'HTTPERROR=' + str(e.code) + "\t" + url
      except socket.timeout, e:
        print 'TIMEOUT=' + str(e) + "\t" + url
      except:
        print 'EXCEPTION' + "\t" + url

def filter_english(in_filename, out_filename):
  """ This function filter pages that are not in English
      Input: a file containing list of urls
      Output: a file containing list of filtered urls
  """
  out = open(out_filename, "w")
  with open(in_filename) as lines:
    for line in lines:
      try:
        url = line.strip("\n")
        handle = urllib2.urlopen(url)
        src = handle.read()
  #      src = src.encode('utf-8')
        text_content = extract_text(src)
        if text_content:
          if detect_english(text_content):
            print "GOOD" + "\t" + url
            out.write(line)
      except urllib2.HTTPError, e:
        print 'HTTPERROR=' + str(e.code) + "\t" + url
      except:
        print 'EXCEPTION' + '\t' + url
  out.close()

def main():
  if len(sys.argv) < 4:
      print "Wrong arguments"
      print "Usage:"
      print "  Download html: python scrap.py <path_url_list_file> html <output_path>"
      print "  Filter non-English pages: python scrap.py <path_url_list_file> url <output_filename>"
      return 
  if sys.argv[2] == 'html':
    filename = sys.argv[1]
    path = sys.argv[3]
    download_html_content_no_check_english(filename, path)
  elif sys.argv[2] == 'url':
    in_filename = sys.argv[1]
    out_filename = sys.argv[3]
    filter_english(in_filename, out_filename)

if __name__=="__main__":
    main()
