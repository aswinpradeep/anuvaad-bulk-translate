from service.pdf_modify import PDFModify
import glob
import os
import cv2
import time

pdf_modify = PDFModify()

input_files = glob.glob(os.path.join("/home/aswin/Downloads/sleepwell/Input/Staqo", '*'))
#input_files = glob.glob(os.path.join("/home/rathan/Downloads/Temp/", '*'))

input_files.sort()

files_to_convert = []
for each_file in input_files:
    if "_updated" not in each_file and each_file.replace(".pdf","_updated.pdf") not in input_files:
        files_to_convert.append(each_file)

print("Conversion Started")

for each_file in files_to_convert:
    print(each_file)
    pdf_modify.pdf_modify(each_file)

#https://github.com/stephanefschwarz/Hough-Transform