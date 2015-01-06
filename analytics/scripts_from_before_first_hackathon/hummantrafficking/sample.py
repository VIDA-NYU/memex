import sys
import random

'''
Usage:
  python sample.py input output X
This script randomly picks X urls from input
'''

def main(argv):
  input = argv[0]
  output = argv[1]
  output_file = open(output, "w")
  x = int(argv[2])
  n = 0
  with open(input) as lines:
    for line in lines:
      n += 1
  rands = set([])  
  while (len(rands) < x):
    rands.add(random.randrange(0, n))
  count = 0
  with open(input) as lines:
    for line in lines:  
      count += 1
      if count in rands:
        output_file.write(line)
  output_file.close()

if __name__=="__main__":
  main(sys.argv[1:])
