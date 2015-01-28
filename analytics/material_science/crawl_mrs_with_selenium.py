# pip install -U selenium or sudo easy_install selenium

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import sys
import re
import urllib
import time
import traceback
import os.path

def download_abstracts(url, driver):
	try:
		print url	
		driver.get(url)
		select_all = driver.find_element_by_link_text('Select All')	
		select_all.click()	
		select_abstract = driver.find_element_by_link_text('View Selected Abstracts')
		select_abstract.click()
		src = driver.page_source.encode('utf-8')
		return src	
	except:
		print "Exception: " + url
		print traceback.format_exc()
		return None

def download_abstracts_given_id(id, driver):
	filename = "data/volumne_" + str(id) + ".html"
	#if os.path.isfile(filename):
	#		return
	out = open(filename, "w")
	url = "http://journals.cambridge.org/action/displayIssue?jid=OPL&volumeId=" + str(id)
	src = download_abstracts(url, driver)
	if src:
		out.write(src)
	out.close()

def main():
	driver = webdriver.Chrome()
	driver.set_page_load_timeout(20)
	for i in range(1760, 0, -1):
		download_abstracts_given_id(i, driver)
	driver.close()

if __name__=="__main__":
	main()
