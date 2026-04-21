from docx import Document
from docx.shared import Pt
from docx.oxml.ns import qn

doc = Document(r'c:\Users\simon\OneDrive\Desktop\MSC FINANC\MSc_Finance_CV_v2.docx')

FERRARI_B1 = 'Built multi-stage DCF model in Excel/Python; estimated WACC via CAPM; derived intrinsic value range through sensitivity analysis on terminal growth rate and discount rate'
FERRARI_B2 = 'Stress-tested assumptions under bull/base/bear scenarios using Ferrari annual reports, investor presentations, and sell-side consensus estimates'
FERRARI_MERGED = 'Built multi-stage DCF in Excel/Python; estimated WACC via CAPM; performed sensitivity analysis on terminal growth rate and discount rate; stress-tested under bull/base/bear scenarios using Ferrari annual reports and sell-side consensus estimates'

VAR_B1 = 'Constructed diversified 10-stock EU portfolio; applied Mean-Variance Optimisation to derive efficient frontier and minimise VaR subject to return constraints'
VAR_B2 = 'Implemented Historical and Parametric VaR at 95%/99% confidence; back-tested estimates against realised returns and analysed sector correlation structure'
VAR_MERGED = 'Constructed diversified 10-stock EU portfolio in Python; derived efficient frontier via Mean-Variance Optimisation; implemented Historical and Parametric VaR at 95%/99% confidence; back-tested estimates against realised returns'

paras_to_delete = []

for i, para in enumerate(doc.paragraphs):
    text = para.text.strip()

    if FERRARI_B1 in text:
        for run in para.runs:
            if FERRARI_B1 in run.text:
                run.text = run.text.replace(FERRARI_B1, FERRARI_MERGED)

    if FERRARI_B2 in text:
        paras_to_delete.append(para)

    if VAR_B1 in text:
        for run in para.runs:
            if VAR_B1 in run.text:
                run.text = run.text.replace(VAR_B1, VAR_MERGED)

    if VAR_B2 in text:
        paras_to_delete.append(para)

# Remove merged paragraphs
for para in paras_to_delete:
    p = para._element
    p.getparent().remove(p)

doc.save(r'c:\Users\simon\OneDrive\Desktop\MSC FINANC\MSc_Finance_CV_v3.docx')
print(f'Saved v3. Removed {len(paras_to_delete)} bullet(s).')
