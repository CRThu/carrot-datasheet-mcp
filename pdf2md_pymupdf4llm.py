# /// script
# dependencies = ["pymupdf4llm"]
# ///

import pymupdf
import pymupdf4llm
import argparse
import os

def convert_pdf_to_md(pdf_path, output_md, media_dir):
    # Ensure directories exist
    os.makedirs(os.path.dirname(os.path.abspath(output_md)), exist_ok=True)
    os.makedirs(media_dir, exist_ok=True)

    # Convert PDF to MD
    pymupdf4llm.use_layout(False)
    
    doc = pymupdf.open(pdf_path)

    # TOC-driven: use the document's table of contents
    toc_headers = pymupdf4llm.TocHeaders(doc)
    md_text = pymupdf4llm.to_markdown(doc, write_images=True, image_path=media_dir, hdr_info=toc_headers, show_progress = True)

    # Write the markdown file
    with open(output_md, "w", encoding="utf-8") as f:
        f.write(md_text)

    print(f"Successfully converted {pdf_path} to {output_md}")
    print(f"Images saved in {media_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert PDF to Markdown using PyMuPDF4LLM")
    parser.add_argument("pdf_path", help="Path to the input PDF file")
    parser.add_argument("output_md", help="Path to the output markdown file")
    parser.add_argument("media_dir", help="Directory to save the images")

    args = parser.parse_args()

    convert_pdf_to_md(args.pdf_path, args.output_md, args.media_dir)
