import sys
import re
import tldextract

def read_target_log_1(filename):
    #Only extract the urls that have PROB:1.0
    PROB1 = re.compile("PROB:1.0")
    hosts = set()
    with open(filename) as lines:
        for line in lines:
            if (PROB1.search(line)):
                values = line.split()
                url = values[1].strip("/")
                result = tldextract.extract(url)
                host = result[1] + "." + result[2]
                hosts.add(host)
    return hosts

def read_target_log(filename):
    #Extract all urls that are relevant
    count = 0
    hosts = set()
    with open(filename) as lines:
        for line in lines:
            if "RELEVANT" in line:
                try:
                    values = line.split()
                    cur_rel = int(values[2].split(":")[1])
                    if cur_rel > count:
                        url = values[1][5:].strip("/")
                        result = tldextract.extract(url)
                        host = result[1] + "." + result[2]
                        hosts.add(host)
                        count = cur_rel
                except:
                    print line
    return hosts

def get_hosts(filename):
    hosts = set()
    with open(filename) as lines:
        for line in lines:
            url = line.strip("\n")
            result = tldextract.extract(url)
            host = result[1] + "." + result[2]
            hosts.add(host)
    return hosts

def save(s, outfile):
    out = open(outfile, "w")
    for e in s:
        try:
            out.write(e + "\n")
        except:
            print e

def evaluate(testfile, resultfile):
    test_hosts = get_hosts(testfile)
    result_hosts = read_target_log_1(resultfile)
    hit = 0
    for h in test_hosts:
        if h in result_hosts:
            hit += 1
    print hit/float(len(test_hosts))

def main(argvs):
    all = set()
    mode = argvs[0]
    if mode == "u": #union mode
        for filename in argvs[1:]:
            hosts = read_target_log(filename)
            print filename
            print len(hosts)
            all = all.union(hosts)
            print len(all)
        save(all, "escorts.txt")
    elif mode == "e": #evaluation mode
        testfile = argvs[1]
        resultfile = argvs[2]
        evaluate(testfile, resultfile)

if __name__=="__main__":
    main(sys.argv[1:])
