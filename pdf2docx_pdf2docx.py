# /// script
# dependencies = [
#   "pdf2docx",
# ]
# ///

import os
import sys
from pdf2docx import Converter

def pdf2word(f_path, d_path):
    """使用 pdf2docx 将 PDF 转换为 DOCX"""
    try:
        print(f"正在转换: {f_path} -> {d_path}")
        cv = Converter(f_path)
        cv.convert(d_path, start=0, end=None)
        cv.close()
        print(f"转换成功: {d_path}")
    except Exception as e:
        print(f"转换失败: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python pdf2docx_pdf2docx.py <input_pdf> <output_docx>")
        sys.exit(1)

    pdf2word(sys.argv[1], sys.argv[2])
