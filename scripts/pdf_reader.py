import PyPDF2
import os

path1 = "/mnt/c/Users/harshj/odrive/Dropbox/my tax files/20-21/airtel_act_bills"

for (dirpath, dirname, filenames) in os.walk(path1):
    for filename in filenames:
        file_path = os.path.join(dirpath,filename)
        with open(file_path, "rb") as f:
            print (file_path)
            pdfReader = PyPDF2.PdfFileReader(f)
            print (pdfReader.numPages) 
            pageObj = pdfReader.getPage(0) 
            pageText = str(pageObj.extractText())
            print (pageText)
            break
