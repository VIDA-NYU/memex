'''
'''
from bs4 import BeautifulSoup
import sys
import re
from os import walk
import os.path
from boilerpipe.extract import Extractor


def process(text):
    return text.replace("\n", " ").encode('utf-8')

def get_all_files(dirname):
    files = []
    names = []
    for [path, dirnames, filenames] in walk(dirname):
        for filename in filenames:
          files.append(path + "/" + filename)
          names.append(filename)
    return [files, names]

def get_text_boilerpipe(html_text):
    try:
        extractor = Extractor(extractor='ArticleExtractor', html=html_text)
        return extractor.getText()
    except:
        print "Exception"
        return None

def get_text_beautifulsoup(html_text):
     soup = BeautifulSoup(html_doc)
     return soup.get_text()

def save(text, file):
    f = open(file, "w")
    f.write(text)
    f.close()

def main(argv):
    input_path = argv[0]
    output_path = argv[1]
    files, names = get_all_files(input_path)
    for i in range(len(files)):
        file = files[i]
        name = names[i]
        output_file = output_path + "/" + name
        if not os.path.isfile(output_file):
            html_text = open(file).read()
            print output_file
            text = get_text_boilerpipe(html_text)
            if text:
                save(process(text), output_file)

if __name__=="__main__":
    main(sys.argv[1:])
