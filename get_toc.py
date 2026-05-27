# /// script
# dependencies = [
#   "pymupdf",
# ]
# ///

import argparse
import sys
import fitz  # PyMuPDF
import re
from pathlib import Path

def format_tree_line(title, level, max_level):
    """根据层级格式化输出"""
    if level <= max_level:
        # 使用缩进模拟树状结构
        indent = "  " * (level - 1)
        print(f"{indent}└── {title}")

def process_md(file_path, max_level):
    """解析 Markdown 文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                # 匹配 Markdown 标题格式 # Header
                match = re.match(r'^(#+)\s+(.*)', line)
                if match:
                    hashes, title = match.groups()
                    level = len(hashes)
                    format_tree_line(title, level, max_level)
    except FileNotFoundError:
        print(f"错误: 文件未找到 {file_path}")

def process_pdf(file_path, max_level):
    """解析 PDF 文件 TOC"""
    try:
        doc = fitz.open(file_path)
        toc = doc.get_toc()
        for item in toc:
            # toc item 格式为 [level, title, page_number]
            level, title, page = item
            format_tree_line(title, level, max_level)
        doc.close()
    except Exception as e:
        print(f"解析 PDF 失败: {e}")

def main():
    # 强制将标准输出编码设置为 utf-8，解决 Windows 下特殊字符导致的 UnicodeEncodeError
    sys.stdout.reconfigure(encoding='utf-8')

    parser = argparse.ArgumentParser(description="识别 Markdown 或 PDF 文件的 TOC 并以树状结构输出。")
    parser.add_argument('file_path', help='要处理的文件路径')
    parser.add_argument('-l', '--level', type=int, default=2, help='显示的最大章节深度 (默认: 2)')
    
    args = parser.parse_args()
    
    path = Path(args.file_path)
    if not path.exists():
        print(f"错误: 文件不存在 {args.file_path}")
        sys.exit(1)

    print(f"--- {path.name} 的目录结构 ---")
    
    if path.suffix.lower() == '.md':
        process_md(path, args.level)
    elif path.suffix.lower() == '.pdf':
        process_pdf(path, args.level)
    else:
        print(f"错误: 不支持的文件格式 {path.suffix}")

if __name__ == '__main__':
    main()
