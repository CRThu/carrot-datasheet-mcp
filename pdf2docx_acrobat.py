# /// script
# dependencies = [
#   "pywin32",
# ]
# ///
import os
import sys
import winerror
from win32com.client.dynamic import Dispatch, ERRORS_BAD_CONTEXT

ERRORS_BAD_CONTEXT.append(winerror.E_NOTIMPL)

def pdf2word(f_path, d_path):
    """Converts a PDF file to DOCX using Adobe Acrobat via COM."""
    f_path = os.path.abspath(f_path)
    d_path = os.path.abspath(d_path)
    try:
        AvDoc = Dispatch("AcroExch.AVDoc")
        if not AvDoc.Open(f_path, ""):
            raise Exception(f"Could not open PDF: {f_path}")
        pdDoc = AvDoc.GetPDDoc()
        jsObject = pdDoc.GetJSObject()
        jsObject.SaveAs(d_path, "com.adobe.acrobat.docx")
        print(f'Converted: {f_path} -> {d_path}')
    except Exception as e:
        print(f'Error converting {f_path}: {e}')
    finally:
        if 'pdDoc' in locals():
            pdDoc.Close()
        if 'AvDoc' in locals():
            AvDoc.Close(True)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python pdf2docx_acrobat.py <input_pdf> <output_docx>")
        sys.exit(1)

    pdf2word(sys.argv[1], sys.argv[2])
