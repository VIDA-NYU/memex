import sys
import re
import urllib
'''
USAGE:
python htsearch.py keyword max
'''

LINK = re.compile("<td class=\"sr-resultrow\" valign=\"top\" width=\"\"><a href=\"(.*)\">")
PDF = re.compile("\.pdf")
#http://www.humantraffickingsearch.net/searchres.php?query=organ&pr=htlive_meta&prox=page&rorder=500&rprox=500&rdfreq=500&rwfreq=500&rlead=500&rdepth=0&sufs=0&order=r&cq=&jump=0&sk=7.2..2,10.5..6&dropXSL=no
#http://www.humantraffickingsearch.net/searchres.php?query=organ&pr=htlive_meta&prox=page&rorder=500&rprox=500&rdfreq=500&rwfreq=500&rlead=500&rdepth=0&sufs=0&order=r&cq=&jump=10&sk=7.2..2&dropXSL=no

def get_links(content):
  for line in content:
      match = LINK.search(line)
      if match:
        link = match.group(1)
        if PDF.search(link):
          continue
        else:
          print link

def get_links_from_file(filename):
  with open(filename) as lines:
    for line in lines:
      content = urllib.urlopen(line.strip("\n"))
      get_links(content)

def get_links_from_keyword(keyword, max):
  for i in range(max):
    url = "http://www.humantraffickingsearch.net/searchres.php?query=" + \
        keyword + \
        "&pr=htlive_meta&prox=page&rorder=500&rprox=500&rdfreq=500&rwfreq=500&rlead=500&rdepth=0&sufs=0&order=r&cq=&jump=" + \
        str(i) + \
        "0&sk=7.2..2&dropXSL=no"
    content = urllib.urlopen(url)
    get_links(content)

def main(argv):
  #filename = argv[0]
  #get_links_from_file(filename)
  max  = 5
  keyword = argv[0]
  if len(argv) == 2:
    max = int(argv[1])
  get_links_from_keyword(keyword, max)

if __name__=="__main__":
  main(sys.argv[1:])
