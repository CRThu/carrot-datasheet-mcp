# /// script
# dependencies = [
#   "markdown",
# ]
# ///

import os
import re
import argparse
from pathlib import Path

def split_markdown(file_path, output_dir_path=None, max_level=2):
    path = Path(file_path)
    if not path.exists():
        print(f"Error: {file_path} not found.")
        return

    content = path.read_text(encoding='utf-8')

    # 预扫描：查找文件中使用的最小标题级别
    # 注意：pattern 必须在调用 findall 前定义
    pattern = re.compile(r'^(#{1,6})\s+(.*)', re.MULTILINE)
    headings = pattern.findall(content)
    min_level = min([len(h[0]) for h in headings]) if headings else 1
    # 如果 min_level > 1，则偏移量为 min_level - 1，使得最小级别变为 1
    level_offset = min_level - 1

    # 转义内容中的 [ 和 ] (使用原始字符串字面量)
    content = content.replace('[', r'\[').replace(']', r'\]')


    index_stack = [0] * 6
    titles_stack = [""] * 6

    # 确定输出目录
    if output_dir_path:
        base_output_dir = Path(output_dir_path)
    else:
        base_output_dir = path.parent

    output_dir = base_output_dir / path.stem
    os.makedirs(output_dir, exist_ok=True)

    current_content = []
    current_indices = []
    current_titles = []

    lines = content.splitlines()

    def save_section(indices, titles, content):
        if not content: return

        # 命名格式: [name].[level1.level2].[title1.title2]
        # 对标题中的字符进行处理
        formatted_indices = '.'.join(map(str, indices))
        formatted_titles = '.'.join([re.sub(r'[\\/:*?"<>|]', '_', t) for t in titles])

        file_name = f"[{path.stem}].[{formatted_indices}].[{formatted_titles}].md"
        file_path = output_dir / file_name

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content))
        print(f"Created: {file_path}")

    for line in lines:
        match = pattern.match(line)
        if match:
            h_mark, h_title = match.groups()
            h_level = len(h_mark)

            # 应用偏移量，使最小级别变为 1
            logical_level = h_level - level_offset

            if logical_level <= max_level:
                if current_titles:
                    save_section(current_indices, current_titles, current_content)

                # 使用逻辑层级更新索引栈
                index_stack[logical_level-1] += 1
                for i in range(logical_level, 6):
                    index_stack[i] = 0

                titles_stack[logical_level-1] = h_title

                current_indices = index_stack[:logical_level]
                current_titles = titles_stack[:logical_level]
                current_content = [line]
            else:
                current_content.append(line)
        else:
            current_content.append(line)

    if current_titles:
        save_section(current_indices, current_titles, current_content)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Split markdown by heading level.")
    parser.add_argument("file", help="Path to the markdown file")
    parser.add_argument("--output", help="Output directory (default: same dir as md file)")
    parser.add_argument("--level", type=int, default=2, help="Heading level to split by (default: 2)")

    args = parser.parse_args()
    split_markdown(args.file, args.output, args.level)
