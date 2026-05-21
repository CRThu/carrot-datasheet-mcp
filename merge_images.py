import os
import re
import sys
import argparse

def insert_image_info(md_file, info_file, output_file):
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()

    with open(info_file, 'r', encoding='utf-8') as f:
        info_content = f.read()

    # 将生成的图片信息按图片名分割
    # 假设每个块以 <!-- REVERSE TRANSLATION: media/XXX.png --> 开头
    # 且以 <!-- END OF REVERSE TRANSLATION: media/XXX.png --> 结尾
    pattern = re.compile(r'<!-- REVERSE TRANSLATION: (media/.*?) -->(.*?)<!-- END OF REVERSE TRANSLATION: \1 -->', re.DOTALL)
    blocks = {match.group(1): match.group(0) for match in pattern.finditer(info_content)}

    # 替换 markdown 中的 ![](./media/***.emf)
    # 替换规则：寻找 ./media/ 之后的文件名，并在 info_file 中寻找对应的块
    def replace_func(match):
        image_path = match.group(1) # 获取 media/xxx.png
        # emf 格式转 png 格式的查找
        if image_path.endswith('.emf'):
            image_path = image_path.replace('.emf', '.png')

        if image_path in blocks:
            print(f"Replacing {match.group(0)} with block for {image_path}")
            return blocks[image_path]
        else:
            print(f"No info found for {image_path}")
            return match.group(0)

    # 匹配 ![](./media/***.emf) 或 ![](./media/***.png)
    new_md_content = re.sub(r'!\[.*?\]\(\./(media/.*?)\)', replace_func, md_content)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(new_md_content)
    print(f"Done! Saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_md', default='fm434_all.md')
    parser.add_argument('--info_md', default='fm434_image_info.md')
    parser.add_argument('--output_md', default='fm434_final.md')
    args = parser.parse_args()

    insert_image_info(args.input_md, args.info_md, args.output_md)
