from docx import Document

doc = Document(r'c:\Users\simon\OneDrive\Desktop\MSC FINANC\MSc_Finance_CV_v3.docx')

for para in doc.paragraphs:
    for run in para.runs:
        if run.text.endswith('   |   '):
            run.text = run.text[:-7]  # remove trailing separator

doc.save(r'c:\Users\simon\OneDrive\Desktop\MSC FINANC\MSc_Finance_CV_v3.docx')
print('Fixed.')
