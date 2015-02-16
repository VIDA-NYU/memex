#Convert pdf to txt
#Usage:
#python parse_pdf.py <inputdir> <outputdir>
import sys
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from cStringIO import StringIO
from os import walk
import os.path

def convert_single_pdf_to_txt(path):
    try:
         rsrcmgr = PDFResourceManager()
         retstr = StringIO()
         laparams = LAParams()
         device = TextConverter(rsrcmgr, retstr, codec='utf-8', laparams=laparams)
         interpreter = PDFPageInterpreter(rsrcmgr, device)
         pagenos=set()
         fp = file(path, 'rb')
         for page in PDFPage.get_pages(fp, pagenos, maxpages=0, password="",caching=True, check_extractable=True):
             try:  
                interpreter.process_page(page)
             except:
                continue
         fp.close()
         device.close()
         str = retstr.getvalue()
         retstr.close()
         return str
    except:
        print "filename: " + path
        return None

def list_dir(dir):
    filepaths = []
    for dirpath, dirnames, filenames in walk(dir):
        for filename in filenames:
            filepaths.append(dirpath + "/" + filename)
    return filepaths

def convert_all_pdf_to_txt(filepaths, outputdir):
    for file in filepaths:
        filename = file.split("/")[-1]
        outputfile = outputdir + "/" + filename + ".txt"
        if os.path.isfile(outputfile):
            continue
        else:
            output = open(outputfile, "w")
            str = convert_single_pdf_to_txt(file)
            if str:
                output.write(str)
            output.close()
        

def main(argv):
    inputdir = argv[0]
    outputdir = argv[1]
    filepaths = list_dir(inputdir)
    print convert_all_pdf_to_txt(filepaths, outputdir)

if __name__=="__main__":
    main(sys.argv[1:])
