import sys
import csv
import nltk
from nltk.corpus import stopwords
import numpy as np
from matplotlib import pyplot as plt
from nltk.stem import *
from nltk.stem.porter import * 


stemmer = PorterStemmer()
def get_vocabulary_all(filename):
    #Union tokens from all abstracts to generate vocabulary
    #Remove stopword list in nltk from vocabulary
    count = 0
    voca = set()
    stoplist = set(stopwords.words('english'))
    with open(filename) as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',')
        for row in csvreader:
            count += 1
            if count == 1:
                continue
            #abstract = row[6].lower().decode('utf-8')
            abstract = row[6].lower()
            #year = row[8] 
            tokens = abstract.split()
            for token in tokens:
                #token = stemmer.stem(token)
                if token not in stoplist:
                    voca.add(token)
    print "Size of vocabulary: " + str(len(voca))
    return voca

def get_vocabulary_filter(filename):
    #Union tokens from all abstracts to generate vocabulary
    #Remove stopword list in nltk from vocabulary
    #Remove all common words
    count = 0
    voca2counter = {}
    stoplist = set(stopwords.words('english'))
    with open(filename) as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',')
        for row in csvreader:
            count += 1
            if count == 1:
                continue
            #abstract = row[6].lower().decode('utf-8')
            abstract = row[6].lower()
            #year = row[8] 
            tokens = abstract.split()
            for token in tokens:
                #token = stemmer.stem(token)
                if token not in stoplist:
                    if token in voca2counter:
                        voca2counter[token] += 1
                    else:
                        voca2counter[token] = 1
    threshold = len(voca2counter)/100
    voca = set()
    for token in voca2counter:
        if voca2counter[token] < threshold:
            voca.add(token)
    print "Size of vocabulary: " + str(len(voca))
    return voca

def get_vocabulary_lda(term_file):
    print "Building vocabulary using lda words..."
    tokens = []
    with open(term_file) as lines:
        for line in lines:
            token = line.strip("\n")
            tokens.append(token)
    print "Number of all lda terms: " + str(len(tokens))
    voca = set(tokens)
    return voca
           

def compute_simpson_index(filename, voca):
    print "Size of vocabulary: " + str(len(voca))
    #Counting vocabulary
    year2counter = {}
    year2N = {}
    count = 0
    with open(filename) as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',')
        N = 0 #Number of occurences of all tokens
        for row in csvreader:
            count += 1
            if count == 1:
                continue
            abstract = row[6].lower()
            #abstract = row[6].lower().decode('utf-8')
            year = row[8] 
            if year in year2counter:
                counter = year2counter[year]
            else:
                counter = {}
                year2counter[year] = counter
                year2N[year] = 0
            tokens = abstract.split()
            for token in tokens:
                #token = stemmer.stem(token)
                if token in voca:
                #if token:
                    year2N[year] += 1
                    if token in counter:
                        counter[token] += 1
                    else:
                        counter[token] = 1
    #Compute the Simpson index
    year2index = []
    N = 0
    for year in year2counter:
            print "Year: \t" + str(year)
            if not year.isdigit():
                continue
            counter = year2counter[year]
            print "Number of voca words: \t" + str(len(counter))
            N = year2N[year]
            print "Number of occurences of voca words: \t" + str(N)
            #X = N*(N-1)
            X = N*N
            sum = 0
            for token in counter:
                print counter[token]
                #sum += (counter[token] * (counter[token] - 1))/float(X)
                sum += (counter[token] * (counter[token] ))/float(X)
            year2index.append([int(year), sum])
    year2index = sorted(year2index, key=lambda item: item[0]) 
    return year2index

def get_vocabulary_dict(filename):
    voca = set()
    with open(filename) as file:
        csvreader = csv.reader(file)
        for row in csvreader:
            term = row[1]
            voca.add(term)

    return voca

def plot(year2index):
    OX = []
    OY = []
    for item in year2index:
        OX.append(item[0]) #year
        OY.append(item[1]) #index

    fig = plt.figure()
    ax = plt.subplot(111)
    width = 0.8
    ind = np.arange(len(OY))
    ax.bar(ind, OY, width=width)
    ax.set_xticks(ind + width/2)
    ax.set_xticklabels(OX, rotation=90)
    plt.savefig("figure.pdf")

def main(argv):
    filename = "mrs.csv"
    #voca = get_vocabulary_all(filename)
    #voca = get_vocabulary_filter(filename)
    voca = get_vocabulary_lda("lda-bd92346b-100-c1fbb8bd/05000/term-index.txt")
    #voca = get_vocabulary_dict("materialsdictionary_v1.csv")
    year2index = compute_simpson_index(filename, voca)
    plot(year2index)

if __name__=="__main__":
    main(sys.argv[1:])
