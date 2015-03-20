import sys
import csv
import gzip
import json
from math import log
import os

#author: Kien Pham (kien.pham@nyu.edu)
#This class computes word salency which is described in termite paper: http://vis.stanford.edu/files/2012-Termite-AVI.pdf
class WordSaliency:

    def __init__(self, topic_term_file, term_file, output):
        #path to the topic term distributions file, because it is in gzip, we need to decompress it first
        topic_term_file = self.decompress(topic_term_file)
        self.topic_term_file = topic_term_file
        #path to the term index file
        self.term_file = term_file
        #Path to the output file that contains salient terms
        self.output = output
   
    def read_term_index(self):
        words = []
        with open(self.term_file) as f:
            for line in f:
                word = line.strip("\n")
                words.append(word)
        return words

    #Compute the distinctiveness of each word
    #distinctiveness(word) = SUM(P(Topic|word)*log(P(Topic|word)/P(Topic)))
    #Because log function returns negative number, the smaller the better
    def distinctiveness(self):
        pt = []#P(Topic)
        ptw = []#P(Topic|word)
        with open(self.topic_term_file) as f:
            csvreader = csv.reader(f)
            #For each topic
            for row in csvreader:
                pw = []
                s = 0.0
                #For each word
                for p in row:
                    p = float(p)
                    s += p
                    pw.append(p)
                    
                pt.append(s)
                ptw.append(pw)
        dw = []#distinctiveness(word)
        pw = []#P(word): marginal probability of word
        nTopics = len(pt)
        nWords = len(ptw[0])
        #for each word
        for i in range(nWords):
            d = 0.0
            p = 0.0
            #for each topic
            for j in range(nTopics):
                if ptw[j][i] != 0:
                    d += ptw[j][i]*log(ptw[j][i]/pt[j])    
                    p += ptw[j][i]
            dw.append(d)
            pw.append(p)
                    
        return dw, pw

    #Compute the saliency of each word
    #saliency(word) = P(word)*distinctiveness(word)
    def saliency(self, top):
        dw, pw = self.distinctiveness()
        #saliency of words
        sw = []
        #For each word
        words = self.read_term_index()
        for i in range(len(pw)):
            sw.append([pw[i]*dw[i], i])
        sw.sort()
        idx = -1
        for i in range(top):
            word = sw[idx][1]
            #print word
            idx -= 1
        #ret = []
        out = open(self.output, "w")
        for i in range(top):
            word = words[sw[i][1]]
            index = sw[i][1] #use if you want to find where it is in the term index
            out.write(word + "\n")
            #ret.append(words[sw[i][1]] + ":" + str(sw[i][1]))
        out.close()
       
        #with open(self.output, "w") as f:
        #    json.dump(ret, f)
    
    #Compress the output file into gzip
    def compress(self):
        if os.path.isfile(self.output):
            output = gzip.open(self.output + ".gz", "wb" )
            output.writelines(open(self.output).read())
            output.close()
    
    def decompress(self, topic_term_file):
        f = gzip.open(topic_term_file, 'rb')
        outputfile = topic_term_file[:-3]
        with open(outputfile, "w") as out:
            out.write(f.read())
        f.close()
        return outputfile

if __name__=="__main__":
    top = 10000
    path = "."
    topic_term_dist_file = path +  "/lda-e504ca40-100-4389f3fb/02000/topic-term-distributions.csv.gz"
    term_index_file = path +  "/lda-e504ca40-100-4389f3fb/02000/term-index.txt"
    outputfile = path + "/salient-terms.csv"
    ws = WordSaliency(topic_term_dist_file, term_index_file, outputfile)
    #ws = WordSaliency(path + "/lda-e504ca40-100-4389f3fb/02000/topic_term_distributions.csv.gz", path + "/lda-e504ca40-100-4389f3fb/02000/term-index.txt", "salient-terms.csv")
    ws.saliency(top)
    #ws.compress()
