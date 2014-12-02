'''
This script expand urls.
For example given an url, it get the host from url, download it, get the outlinks belong to the domain.
We can use this technique to expand urls for getting more training data.

Usage:
	python expand_urls.py <url_list_file> <output_directory>
'''
import sys
import traceback
from urlparse import urlparse
from langdetect import detect_langs
from langdetect import detect
from boilerpipe.extract import Extractor
import urllib2

def get_url(page):
    """
    :param page: html of web page (here: Python home page) 
    :return: urls in that page 
    """
    start_link = page.find("a href")
    if start_link == -1:
        return None, 0
    start_quote = page.find('"', start_link)
    end_quote = page.find('"', start_quote + 1)
    url = page[start_quote + 1: end_quote]
    return url, end_quote

def get_all_urls(page, url):
	links = set([url])
	while True:
		link, n = get_url(page)
		page = page[n:]
		if link:
			if url in link:
				links.add(link)
		else:
			break
	return links

def encode(url):
  return urllib2.quote(url).replace("/", "%2F")

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


def extract_and_save(url, path):
	try:
		handle = urllib2.urlopen(url)
		html_content = handle.read()
		extractor = Extractor(extractor='KeepEverythingExtractor', html=html_content)
		text = extractor.getText()
		if text:
			if detect_english(text):
				links = get_all_urls(html_content, url)
				for link in links:
					try:
						handle = urllib2.urlopen(url)
						html_content = handle.read()
						#extractor = Extractor(extractor='KeepEverythingExtractor', html=html_content)		
						#text_content = extractor.getText()
						#if text_content:
						#	if detect_english(text_content):
						encoded_url = encode(link)
						f = open(path + "/" + encoded_url, "w")
						f.write(html_content)
						f.close()
					except:
						print url
						traceback.print_exc()
						return None
	except:
		print url
		traceback.print_exc()
		return None

def get_domain_name(url):
	parsed_uri = urlparse(url)
	domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
	return domain

def expand_all(url_file, out_path):
	with open(url_file) as lines:
		for line in lines:
			try:
				url = line.strip("\n")
				domain = get_domain_name(url)
				extract_and_save(domain, out_path)			
	#			break
			except:
				print line
				traceback.print_exc()

def main(argv):
	if len(sys.argv) < 3:
		print "Wrong arguments"
		print "Usage:"
		print "	python expand_urls.py <url_list_file> <output_directory>"
		return
	url_list_file = argv[0]
	output_directory = argv[1]
	expand_all(url_list_file, output_directory)

if __name__=="__main__":
	main(sys.argv[1:])
