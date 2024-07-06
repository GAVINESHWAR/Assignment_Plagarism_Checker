import os
from flask import Flask, request, render_template
import fitz  # PyMuPDF
import numpy as np
import glob

def levenshtein(seq1, seq2):
    size_x = len(seq1) + 1
    size_y = len(seq2) + 1
 
  # defining a zero matrix of size of first string * second string
    matrix = np.zeros ((size_x, size_y)) 
 
    for x in range(size_x):
        matrix [x, 0] = x # row aray with elements of x
    for y in range(size_y):
        matrix [0, y] = y # column array with elements of y
    for x in range(1, size_x):
        for y in range(1, size_y):
            if seq1[x-1] == seq2[y-1]: # if the alphabets at the postion is same
                matrix [x,y] = min(
                    matrix[x-1, y] + 1,
                    matrix[x-1, y-1],
                    matrix[x, y-1] + 1
                )
            else:         # if the alphabbets at the position are different
                matrix [x,y] = min(
                    matrix[x-1,y] + 1,
                    matrix[x-1,y-1] + 1,
                    matrix[x,y-1] + 1
                )
 
    # returning the levenshtein distance i.e last element of the matrix
    return (matrix[size_x - 1, size_y - 1])

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'file' not in request.files:
        return 'No file part'
    files = request.files.getlist('file')
    plagarism  = request.form.get('num', type = int)
    pdf_dict = {}
    for file in files:
        if file.filename.endswith('.pdf'):
            # Create subdirectories if they do not exist
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            file.save(file_path)
            pdf_text = extract_text_from_pdf(file_path)
            pdf_dict[file.filename] = pdf_text
    plagfiles = []  
    k=0
    for key1,value1 in pdf_dict.items() :
        for key2,value2 in pdf_dict.items():
            if key1!=key2:
                str1=value1.replace(' ', '')
                str2=value2.replace(' ', '')
                if(len(str1)>len(str2)):
                    length=len(str1)
                else:
                    length=len(str2)
                n = 100-round((levenshtein(str1,str2)/length)*100,2)
                if plagarism<n:   
                    a1 = "For the files " 
                    a2 = str(key1) 
                    a3 = "  and  " 
                    a4 = str(key2)
                    a5 = " has " 
                    a6 = str(n)
                    a7 =  "  "
                    a8 =  "% plagiarised"
                    a= [a1,a2,a3,a4,a5,a6,a7,a8]                 
                    plagfiles.append(a)
                    k = k+1
    if k == 0:
        plagfiles.append("No documents are plagiarised")
    return render_template('index.html', plagfiles=plagfiles)

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
