# /// script
# dependencies = [
#   "pywin32",
# ]
# ///

"""
Convert legacy Office files to modern formats using local MS Office (COM automation).
No external downloads required — uses the Office installation on this machine.

Supported conversions:
  .doc  -> .docx
  .xls  -> .xlsx
  .ppt  -> .pptx

Requires: MS Office 2007+ installed on Windows.

Usage:
  python office2modern.py <input_file> [output_file]
  python office2modern.py input.doc              # -> input.docx
  python office2modern.py input.doc output.docx  # explicit output
  python office2modern.py folder/                # batch convert all legacy files in folder
"""

import argparse
import os
import sys
import time
import win32com.client

REQUIRED_PROG_IDS = ["Word.Application", "Excel.Application", "PowerPoint.Application"]


def check_office():
    for prog_id in REQUIRED_PROG_IDS:
        try:
            app = win32com.client.Dispatch(prog_id)
            app.Quit()
        except Exception:
            component = prog_id.split(".")[0]
            print(f"Error: MS Office {component} is not installed or not registered.")
            print("Please install Microsoft Office 2007 or later.")
            sys.exit(1)


FORMAT_MAP = {
    ".doc": ("Word.Document", "docx"),
    ".xls": ("Excel.Workbook", "xlsx"),
    ".ppt": ("PowerPoint.Presentation", "pptx"),
}

EXTENSION_TO_PROGID = {
    ".doc": "Word.Document",
    ".docx": "Word.Document",
    ".xls": "Excel.Workbook",
    ".xlsx": "Excel.Workbook",
    ".ppt": "PowerPoint.Presentation",
    ".pptx": "PowerPoint.Presentation",
}


def convert_file(input_path: str, output_path: str | None = None):
    input_path = os.path.abspath(input_path)
    if not os.path.isfile(input_path):
        print(f"Error: file not found: {input_path}")
        return False

    ext = os.path.splitext(input_path)[1].lower()
    if ext not in FORMAT_MAP:
        print(f"Error: unsupported format '{ext}'. Supported: {list(FORMAT_MAP.keys())}")
        return False

    prog_id, target_ext = FORMAT_MAP[ext]

    if output_path is None:
        output_path = os.path.splitext(input_path)[0] + "." + target_ext
    output_path = os.path.abspath(output_path)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    word = None
    wb = None
    ppt = None

    try:
        if ext in (".doc", ".docx"):
            word = win32com.client.Dispatch("Word.Application")
            word.Visible = False
            doc = word.Documents.Open(input_path)
            doc.SaveAs2(output_path, FileFormat=16)  # 16 = wdFormatXMLDocument (.docx)
            doc.Close(False)
            print(f"Converted: {input_path} -> {output_path}")

        elif ext in (".xls", ".xlsx"):
            excel = win32com.client.Dispatch("Excel.Application")
            excel.Visible = False
            excel.DisplayAlerts = False
            wb = excel.Workbooks.Open(input_path)
            wb.SaveAs(output_path, FileFormat=51)  # 51 = xlOpenXMLWorkbook (.xlsx)
            wb.Close(False)
            excel.Quit()
            print(f"Converted: {input_path} -> {output_path}")

        elif ext in (".ppt", ".pptx"):
            powerpoint = win32com.client.Dispatch("PowerPoint.Application")
            ppt = powerpoint.Presentations.Open(input_path, WithWindow=False)
            ppt.SaveAs(output_path, FileFormat=32)  # 32 = ppSaveAsOpenXMLPresentation
            ppt.Close()
            print(f"Converted: {input_path} -> {output_path}")

        return True

    except Exception as e:
        print(f"Error converting {input_path}: {e}")
        return False

    finally:
        try:
            if ppt:
                ppt.Close()
        except Exception:
            pass
        try:
            if wb:
                wb.Close(False)
        except Exception:
            pass
        try:
            if word:
                word.Quit()
        except Exception:
            pass


def batch_convert(folder: str):
    folder = os.path.abspath(folder)
    if not os.path.isdir(folder):
        print(f"Error: directory not found: {folder}")
        return

    legacy_exts = set(FORMAT_MAP.keys())
    files = []
    for f in os.listdir(folder):
        if os.path.splitext(f)[1].lower() in legacy_exts:
            files.append(os.path.join(folder, f))

    if not files:
        print(f"No legacy Office files found in {folder}")
        return

    print(f"Found {len(files)} files to convert")
    success = 0
    for f in sorted(files):
        if convert_file(f):
            success += 1
        time.sleep(0.5)  # avoid COM race conditions

    print(f"\nDone: {success}/{len(files)} converted successfully")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert legacy Office files to modern formats via local MS Office")
    parser.add_argument("input", help="Input file or folder path (.doc, .xls, .ppt)")
    parser.add_argument("output", nargs="?", default=None, help="Output file path (optional, file mode only)")
    args = parser.parse_args()

    check_office()

    if os.path.isdir(args.input):
        batch_convert(args.input)
    else:
        convert_file(args.input, args.output)
