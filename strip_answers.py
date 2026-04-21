from docx import Document
import re

def strip_answers(input_path, output_path):
    doc = Document(input_path)
    paras_to_delete = []

    for para in doc.paragraphs:
        text = para.text.strip()
        if text.startswith('Answer:') or text.startswith('Explanation:'):
            paras_to_delete.append(para)

    for para in paras_to_delete:
        para._element.getparent().remove(para._element)

    doc.save(output_path)
    print(f'Saved: {output_path}')

strip_answers(
    r'c:\Users\simon\OneDrive\Desktop\MSC FINANC\IESAT_Practice_Test.docx',
    r'c:\Users\simon\OneDrive\Desktop\MSC FINANC\IESAT_Exam.docx'
)
strip_answers(
    r'c:\Users\simon\OneDrive\Desktop\MSC FINANC\TAE_ESADE_Practice_Test.docx',
    r'c:\Users\simon\OneDrive\Desktop\MSC FINANC\TAE_ESADE_Exam.docx'
)
