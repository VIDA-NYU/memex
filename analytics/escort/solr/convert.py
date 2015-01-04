'''
This script converts dowloaded html pages from the crawler to xml format so that it could be indexed by SOLR
Usage:
  python convert.py <data_target> <output_directory>
  data_target is the output directory of the crawler
'''
import sys
#from boilerpipe.extract import Extractor
#from bs4 import BeautifulSoup
from os import walk
import urllib
import os.path
import re
import traceback
import os.path

N=5000 #Number of pages per file
TITLE = re.compile('<title>(.*?)</title>', re.IGNORECASE|re.DOTALL)
KEYWORDS = re.compile('<meta name=\"keywords\" content=(.*?)>', re.IGNORECASE|re.DOTALL)
DESCRIPTION = re.compile('<meta name=\"description\" content=(.*?)>', re.IGNORECASE|re.DOTALL)

def get_stopwords(filename):
  sw = set()
  with open(filename) as lines:
    for line in lines:
      sw.add(line.strip("\n"))
  return sw

stopwords = get_stopwords("data/stopwords.txt")

def get_locations(filename):
  l2latlon = {}
  with open(filename) as lines:
    for line in lines:
      values = line.split(",")
      location = values[0].lower()
      lat = values[-2]
      lon = values[-1].strip("\n")
      l2latlon[location] = [lat, lon]
  return l2latlon

cities = get_locations("data/cities.csv")
countries = get_locations("data/countries.csv")

def decode_url(url):
  return urllib.unquote(url).replace("%2F", "/")

def get_all_files(dirname):
    #It takes 10 mins to list 100k files
    allfiles = dirname.replace("/", "_").replace(".", "") + ".txt" #File that contains full path to all files in dirname
    files = []
    if os.path.isfile(allfiles):
      with open(allfiles) as lines:
        for line in lines:
          files.append(line.strip("\n"))
    else:
      f = open(allfiles, "w")
      for [path, dirnames, filenames] in walk(dirname):
          for filename in filenames:
            f.write(path + "/" + filename + "\n")
            files.append(path + "/" + filename)
      f.close()
    return files

def encode_xml(value):
  value = value.replace("\"", "&quot;")
  value = value.replace("\'", "&apos;")
  value = value.replace("<", "&lt;")
  value = value.replace(">", "&gt;")
  value = value.replace("&", "&amp;")
  return value

def get_title(html_content):
  res = TITLE.search(html_content)
  if res:
    title = res.group(1)
    title = title.strip("\"")
    return title
  else:
    return None


def get_keywords(html_content):
  res = KEYWORDS.search(html_content)
  if res:
    kw = res.group(1)
    kw = kw.strip("\"/")
    return kw
  else:
    return None

def get_description(html_content):
  res = DESCRIPTION.search(html_content)
  if res:
    desc = res.group(1)
    desc = desc.strip("\"/")
    return desc
  else:
    return None

def get_metadata(html_content):
  if len(html_content) > 5000:
     html_content = html_content[:5000]
  title = get_title(html_content) 
  keywords = get_keywords(html_content)
  description = get_description(html_content)
  return [title, keywords, description]
 
def extract_locations(text):
  locations = []
  text = text.lower()
  tokens = text.split()
  bigram = zip(tokens, tokens[1:])
  for w in bigram:
    tokens.append(' '.join(w))
  tokens = set(tokens)
  for tk in tokens:
    if tk in cities:
      latlon = cities[tk]
      locations.append([tk, latlon[0], latlon[1]])
    elif tk in countries:
      latlon = countries[tk]
      locations.append([tk, latlon[0], latlon[1]])
  return locations
  
def tokenize_keywords(keywords_str):
  keywords = set(keywords_str.lower().replace(",", " ").split())
  return keywords

def convert(filename, domain):
  '''
  Convert a html page to xml file
  '''
  try:
    html_content = open(filename).read()
    #soup = BeautifulSoup(html_content) #by default, bs uses lxml but lxml causes segfault, html5lib is super slow.
    #soup = BeautifulSoup(html_content, "html5lib")
    #text = soup.get_text()
    #text = " ".join(text.split())
    '''
    title_tag = soup.title
    title = "None"
    if title_tag:
      title = title_tag.string
      if title == None:
        title = "None"
      else:
        title = encode_xml(title.encode('utf8'))
    '''
    title, keywords_str, description = get_metadata(html_content)
    #title = encode_xml(title.encode('utf8'))
    if title:
      title = encode_xml(title)
    else:
      title = " "

    if description:
      description = encode_xml(description)
    else:
      description = " "

    if keywords_str:
      keywords_str = encode_xml(keywords_str)
    else:
      keywords_str = " "

    locations = extract_locations(description)
    keywords = tokenize_keywords(keywords_str)
    
    url = decode_url(filename.split("/")[-1])
    url = encode_xml(url)
    xml = '<doc>\n' + \
          '  <field name=\"id\">' + url + '</field>\n' + \
          '  <field name=\"url\">' + url + '</field>\n' + \
          '  <field name=\"domain\">' + domain + '</field>\n' + \
          '  <field name=\"title\">' + title + '</field>\n' + \
          '  <field name=\"description\">' + description + '</field>\n'
    for loc in locations:
      xml = xml + '  <field name=\"location\">' + loc[0] + '</field>\n'
      xml = xml + '  <field name=\"coordinate\">' + loc[1] + "," + loc[2] + '</field>\n'
    for kw in keywords:
      if kw not in stopwords:
        xml = xml + '  <field name=\"keywords\">' + kw + '</field>\n'
    xml = xml + '</doc>\n'
    return xml
  except:
    traceback.print_exc(file=sys.stdout)
    print filename
    return None

def convert_all(input_dir, output_dir, domain):
  filenames = get_all_files(input_dir)
  print "Done read directories"
  count = 0
  docs = []
  skip = False
  for filename in filenames:
    if (count % N) == 0:
	#Reserve the file, so that other process will not work on this
      f = output_dir + "/" + str(count + N) + '.xml'
      if os.path.isfile(f):
        #Other process is working on this file
        skip = True
        count += 1
        continue
      else:
        skip = False
      print f
      out = open(f, 'w')    
      out.close()
    count += 1
    if skip:
      continue
    doc = convert(filename, domain)
    if doc:
      docs.append(doc + "\n")
    if (count % N) == 0:
      out = open(output_dir + "/" + str(count) + '.xml', 'w')    
      data = ''.join(docs)
      out.write('<add>\n' + data + '\n</add>')
      out.close()
      docs = []
  if len(docs) > 0:
    out = open(output_dir + "/" + str(count) + '.xml', 'w')
    data = ''.join(docs)
    out.write('<add>\n' + data + '\n</add>')
    out.close()

def main(argv):
  input_dir = argv[0]
  output_dir = argv[1]
  domain = argv[2]
  convert_all(input_dir, output_dir, domain)

if __name__=="__main__":
  main(sys.argv[1:])
