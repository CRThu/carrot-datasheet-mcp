# /// script
# dependencies = ["pymupdf", "pymupdf4llm"]
# ///

import pymupdf
import pymupdf4llm
import argparse
import os
import re


def normalize_title(title):
    t = title.lower()
    t = re.sub(r'[^a-z0-9]', '', t)
    return t


def fix_page_headings(page_text, toc_items):
    """用该页的 TOC 条目修正标题层级，并把匹配的粗体文本提升为标题"""
    if not toc_items:
        return page_text

    page_toc = {}
    for level, title, _page in toc_items:
        norm = normalize_title(title)
        if norm:
            page_toc[norm] = (level, title)

    lines = page_text.splitlines()
    result = []
    for line in lines:
        heading_match = re.match(r'^(#{1,6})\s+(.*)', line)
        if heading_match:
            hashes, raw_title = heading_match.groups()
            norm = normalize_title(raw_title)
            if norm in page_toc:
                correct_level = page_toc[norm][0]
                result.append(f"{'#' * correct_level} {raw_title}")
                continue
            result.append(line)
            continue

        stripped = line.strip()
        if not stripped:
            result.append(line)
            continue

        clean = re.sub(r'[\*\*_]{1,3}', '', stripped).strip()
        norm = normalize_title(clean)
        if norm and norm in page_toc:
            correct_level = page_toc[norm][0]
            result.append(f"{'#' * correct_level} {clean}")
            continue

        result.append(line)

    return '\n'.join(result)


def convert_pdf_to_md(pdf_path, output_md, media_dir):
    os.makedirs(os.path.dirname(os.path.abspath(output_md)), exist_ok=True)
    os.makedirs(media_dir, exist_ok=True)

    doc = pymupdf.open(pdf_path)

    pymupdf4llm.use_layout(False)

    chunks = pymupdf4llm.to_markdown(
        doc,
        write_images=True,
        image_path=media_dir,
        page_chunks=True,
        show_progress=True,
    )

    page_parts = []
    for chunk in chunks:
        page_num = chunk['metadata']['page']
        text = chunk['text']
        toc_items = chunk.get('toc_items', [])
        text = fix_page_headings(text, toc_items)
        page_parts.append(f'<!-- PAGE: {page_num} -->\n{text}\n<!-- /PAGE: {page_num} -->')

    md_text = '\n\n'.join(page_parts)

    toc = doc.get_toc()
    if toc:
        valid_titles = {item[1] for item in toc}
        normalized_toc = [normalize_title(t) for t in valid_titles]
        final_lines = []
        for line in md_text.splitlines():
            match = re.match(r'^(#+)\s+(.*)', line)
            if match:
                _, title = match.groups()
                norm_title = normalize_title(title)
                is_valid = any(
                    toc_item and norm_title in toc_item
                    for toc_item in normalized_toc
                )
                if not is_valid:
                    clean_title = re.sub(r'[\*\*_]{1,3}', '', title).strip()
                    final_lines.append(clean_title)
                else:
                    final_lines.append(line)
            else:
                final_lines.append(line)
        md_text = '\n'.join(final_lines)
        print("TOC filtering...")

    with open(output_md, 'w', encoding='utf-8') as f:
        f.write(md_text)

    print(f"Successfully converted {pdf_path} to {output_md}.")
    print(f"Images saved in {media_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert PDF to Markdown using PyMuPDF4LLM"
    )
    parser.add_argument("pdf_path", help="Path to the input PDF file")
    parser.add_argument("output_md", help="Path to the output markdown file")
    parser.add_argument("media_dir", help="Directory to save the images")

    args = parser.parse_args()

    convert_pdf_to_md(args.pdf_path, args.output_md, args.media_dir)
