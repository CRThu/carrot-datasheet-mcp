# /// script
# dependencies = [
#   "docling",
#   "easyocr",
# ]
# ///

import argparse
import os
from pathlib import Path

from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
from docling_core.types.doc import ImageRefMode, PictureItem, TableItem
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import EasyOcrOptions, PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption


def convert_pdf_to_md(pdf_path: str, output_md: str, media_dir: str | None = None, ocr: bool = True, cpu_threads: int = 4, max_pages: int | None = None):
    output_md = os.path.abspath(output_md)
    os.makedirs(os.path.dirname(output_md), exist_ok=True)

    if media_dir:
        media_dir = os.path.abspath(media_dir)
        os.makedirs(media_dir, exist_ok=True)

    if cpu_threads:
        os.environ["OMP_NUM_THREADS"] = str(cpu_threads)

    ocr_options = EasyOcrOptions(
        use_gpu=False,
        lang=["ch_sim", "en"],
    )

    pipeline_options = PdfPipelineOptions(
        do_ocr=ocr,
        do_table_structure=True,
        do_formula_enrichment=True,
        ocr_options=ocr_options,
    )
    if media_dir:
        pipeline_options.images_scale = 2.0
        pipeline_options.generate_page_images = True
        pipeline_options.generate_picture_images = True

    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=pipeline_options,
                backend=PyPdfiumDocumentBackend,
            )
        }
    )
    convert_kwargs = {}
    if max_pages is not None:
        convert_kwargs["max_num_pages"] = max_pages
    result = converter.convert(pdf_path, **convert_kwargs)

    if media_dir:
        media_path = Path(media_dir)
        doc_stem = Path(pdf_path).stem
        table_counter = 0
        picture_counter = 0
        for element, _level in result.document.iterate_items():
            if isinstance(element, TableItem):
                table_counter += 1
                img_path = media_path / f"{doc_stem}-table-{table_counter}.png"
                img = element.get_image(result.document)
                if img is not None:
                    img.save(str(img_path), "PNG")
            if isinstance(element, PictureItem):
                picture_counter += 1
                img_path = media_path / f"{doc_stem}-pic-{picture_counter}.png"
                img = element.get_image(result.document)
                if img is not None:
                    img.save(str(img_path), "PNG")
        print(f"Exported {table_counter} tables, {picture_counter} pictures to {media_dir}")
        result.document.save_as_markdown(output_md, image_mode=ImageRefMode.REFERENCED)
    else:
        md_text = result.document.export_to_markdown()
        with open(output_md, "w", encoding="utf-8") as f:
            f.write(md_text)

    print(f"Successfully converted {pdf_path} to {output_md}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert PDF to Markdown using Docling")
    parser.add_argument("pdf_path", help="Path to the input PDF file")
    parser.add_argument("output_md", help="Path to the output markdown file")
    parser.add_argument("--media-dir", default=None, help="Directory to export images (default: none)")
    parser.add_argument("--no-ocr", action="store_true", help="Disable OCR (default: enabled)")
    parser.add_argument("--cpu-threads", type=int, default=4, help="Number of CPU threads (default: 4)")
    parser.add_argument("--max-pages", type=int, default=None, help="Max pages to process (default: all)")

    args = parser.parse_args()
    convert_pdf_to_md(
        args.pdf_path, args.output_md,
        media_dir=args.media_dir,
        ocr=not args.no_ocr,
        cpu_threads=args.cpu_threads,
        max_pages=args.max_pages,
    )
