# /// script
# dependencies = [
#   "markitdown[all]",
# ]
# ///

import os
import re
import base64
import argparse
from markitdown import MarkItDown


def convert_pdf_to_md(pdf_path, output_md):
    output_dir = os.path.dirname(os.path.abspath(output_md))
    image_dir = os.path.join(output_dir, "image")
    os.makedirs(image_dir, exist_ok=True)

    md_converter = MarkItDown()
    result = md_converter.convert(pdf_path)
    md_text = result.text_content

    pattern = r'!\[([^\]]*)\]\(data:image/([^;]+);base64,([^)]+)\)'
    img_count = 0

    def replace_image(match):
        nonlocal img_count
        img_count += 1
        name = match.group(1) or f"img_{img_count}"
        ext = match.group(2)
        b64_data = match.group(3)
        img_bytes = base64.b64decode(b64_data)
        img_name = f"{name}.{ext}"
        img_path = os.path.join(image_dir, img_name)
        with open(img_path, "wb") as f:
            f.write(img_bytes)
        return f"![{img_name}](image/{img_name})"

    md_text = re.sub(pattern, replace_image, md_text)

    with open(output_md, "w", encoding="utf-8") as f:
        f.write(md_text)

    print(f"Successfully converted {pdf_path} to {output_md}")
    print(f"Extracted {img_count} images to {image_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert PDF to Markdown using MarkItDown")
    parser.add_argument("pdf_path", help="Path to the input PDF file")
    parser.add_argument("output_md", help="Path to the output markdown file")

    args = parser.parse_args()
    convert_pdf_to_md(args.pdf_path, args.output_md)
