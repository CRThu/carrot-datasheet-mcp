# /// script
# dependencies = ["pymupdf", "pymupdf4llm"]
# ///

import pymupdf
import pymupdf4llm
import argparse
import os
import re

def normalize_title(title):
    """去除 Markdown 标记和格式干扰，用于和 PDF TOC 进行精确匹配"""
    # 去除粗体、斜体标记
    t = re.sub(r'[\*\*_]{1,3}', '', title)
    # 去除多余空格和特殊空白字符
    return t.strip()

def convert_pdf_to_md(pdf_path, output_md, media_dir):
    # Ensure directories exist
    os.makedirs(os.path.dirname(os.path.abspath(output_md)), exist_ok=True)
    os.makedirs(media_dir, exist_ok=True)

    # Convert PDF to MD
    pymupdf4llm.use_layout(False)
    
    doc = pymupdf.open(pdf_path)

    # 1. 准备目录过滤数据
    toc = doc.get_toc()
    valid_titles = {normalize_title(item[1]) for item in toc}

    # TOC-driven: use the document's table of contents
    toc_headers = pymupdf4llm.TocHeaders(doc)
    md_text = pymupdf4llm.to_markdown(doc, write_images=True, image_path=media_dir, hdr_info=toc_headers, show_progress = True)

    # 3. 后处理：强制清理冗余的标题
    # 将转换出的 markdown 按行处理，如果标题不在 valid_titles 中，则将其降级为普通文本
    final_lines = []
    for line in md_text.splitlines():
        # 检测是否是 Markdown 标题行
        match = re.match(r'^(#+)\s+(.*)', line)
        if match:
            hashes, title = match.groups()
            norm_title = normalize_title(title)
            # 如果该标题不在 PDF 原生 TOC 中，则降级为正文
            if norm_title not in valid_titles:
                # 简单降级：去掉标题标记符，保留内容
                final_lines.append(norm_title) 
            else:
                final_lines.append(line) # 保留有效标题
        else:
            final_lines.append(line)

    # Write the cleaned markdown file
    with open(output_md, "w", encoding="utf-8") as f:
        f.write("\n".join(final_lines))

    print(f"Successfully converted {pdf_path} to {output_md} with TOC filtering.")
    print(f"Images saved in {media_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert PDF to Markdown using PyMuPDF4LLM")
    parser.add_argument("pdf_path", help="Path to the input PDF file")
    parser.add_argument("output_md", help="Path to the output markdown file")
    parser.add_argument("media_dir", help="Directory to save the images")

    args = parser.parse_args()

    convert_pdf_to_md(args.pdf_path, args.output_md, args.media_dir)
