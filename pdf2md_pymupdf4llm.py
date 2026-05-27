# /// script
# dependencies = ["pymupdf", "pymupdf4llm"]
# ///

import pymupdf
import pymupdf4llm
import argparse
import os
import re

def normalize_title(title):
    """
    通用归一化方案：
    将标题转化为纯粹的字母数字序列，彻底忽略空格、换行、标点和Markdown符号。
    """
    # 1. 转小写
    t = title.lower()
    # 2. 剔除所有非字母数字字符（包括Markdown的#、*、_，以及PDF中的[2]、/等）
    t = re.sub(r'[^a-z0-9]', '', t)
    return t

def filter_redundant_headers(md_text, valid_titles):
    """根据归一化后的字符串包含关系过滤冗余标题"""
    # 预先生成 TOC 的归一化列表
    normalized_toc = [normalize_title(t) for t in valid_titles]
    
    final_lines = []
    for line in md_text.splitlines():
        match = re.match(r'^(#+)\s+(.*)', line)
        if match:
            _, title = match.groups()
            norm_title = normalize_title(title)
            
            # 检查 TOC 中的任何一个标题是否‘包含’了当前 MD 标题的归一化字符串
            # 这样即使 MD 标题因为换行被截断，只要它存在于 TOC 完整标题中，就匹配成功
            is_valid = any(toc_item and norm_title in toc_item for toc_item in normalized_toc)
            
            if not is_valid:
                # 降级：去掉标题标记符，保留内容
                clean_title = re.sub(r'[\*\*_]{1,3}', '', title).strip()
                final_lines.append(clean_title) 
            else:
                final_lines.append(line)
        else:
            final_lines.append(line)
    return "\n".join(final_lines)

def convert_pdf_to_md(pdf_path, output_md, media_dir):
    # Ensure directories exist
    os.makedirs(os.path.dirname(os.path.abspath(output_md)), exist_ok=True)
    os.makedirs(media_dir, exist_ok=True)

    # Convert PDF to MD
    pymupdf4llm.use_layout(False)
    
    doc = pymupdf.open(pdf_path)

    # 1. 准备目录过滤数据
    toc = doc.get_toc()
    valid_titles = {item[1] for item in toc}

    # TOC-driven: use the document's table of contents
    toc_headers = pymupdf4llm.TocHeaders(doc)
    md_text = pymupdf4llm.to_markdown(
        doc, 
        write_images=True, 
        image_path=media_dir, 
        hdr_info=toc_headers, 
        show_progress=True
    )

    # 3. 后处理：强制清理冗余的标题
    md_text = filter_redundant_headers(md_text, valid_titles)

    # Write the cleaned markdown file
    with open(output_md, "w", encoding="utf-8") as f:
        f.write(md_text)

    print(f"Successfully converted {pdf_path} to {output_md} with TOC filtering.")
    print(f"Images saved in {media_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert PDF to Markdown using PyMuPDF4LLM")
    parser.add_argument("pdf_path", help="Path to the input PDF file")
    parser.add_argument("output_md", help="Path to the output markdown file")
    parser.add_argument("media_dir", help="Directory to save the images")

    args = parser.parse_args()

    convert_pdf_to_md(args.pdf_path, args.output_md, args.media_dir)
