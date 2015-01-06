import sys
from os import walk

def get_all_files(dirname):
    files = []
    for [path, dirnames, filenames] in walk(dirname):
        for filename in filenames:
          files.append(path + "/" + filename)
    return files

dirname = sys.argv[1]
files = get_all_files(dirname)
output = open("data/text.txt", "w")
for file in files:
    content = open(file).read().replace("\"", "")
    if len(content) > 200:
        output.write("\"" + content + "\"\n")
output.close()
