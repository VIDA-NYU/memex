"""
This script transforms the summary.txt file into a csv file with the purpose of inputing the file into Blaze-Bokeh for visualization.

"""
import csv
import sys

with open('topics_data.csv', 'wb') as outfile:
    writer = csv.writer(outfile, delimiter=',')
    with open('summary.txt', 'rb') as f:
        reader = csv.reader(f, delimiter='\t')
        try:
            for row in reader:
                if any(row):
                    if row[0].startswith("Topic"):
                        topic = row[0]
                        writer.writerow(row)
                    else:
                        pass
        except csv.Error as e:
            sys.exit('file %s, line %d: %s' % (filename, reader.line_num, e))