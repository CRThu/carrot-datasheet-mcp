# /// script
# dependencies = [
#   "emf-to-png-convertor",
#   "pillow",
#   "pywin32",
# ]
# ///

import os
import sys
import argparse
from pathlib import Path

# 尝试导入必要的库，如果不存在则提示安装
try:
    from emf_to_png import EMFToPNGConverter
except ImportError:
    print("错误: 缺少必要的库。请使用以下命令安装:")
    print("uv pip install emf-to-png-convertor pillow pywin32")
    sys.exit(1)

def convert_media_folder(folder_path):
    """
    遍历文件夹，将所有的 .emf 文件转换为 .png 格式
    """
    media_dir = Path(folder_path)
    if not media_dir.exists() or not media_dir.is_dir():
        print(f"错误: 找不到目录 {folder_path}")
        return

    # 初始化转换器
    converter = EMFToPNGConverter()
    
    emf_files = list(media_dir.glob("*.emf"))
    if not emf_files:
        print("未发现 .emf 文件。")
        return

    print(f"开始转换 {len(emf_files)} 个文件...")
    
    success_count = 0
    fail_count = 0

    for emf_path in emf_files:
        png_path = emf_path.with_suffix(".png")
        
        # 如果已经存在同名的 png，可以选择跳过或覆盖
        # 这里默认如果 png 已存在且比 emf 新，则跳过
        if png_path.exists() and png_path.stat().st_mtime > emf_path.stat().st_mtime:
            # print(f"跳过: {png_path.name} 已存在且较新")
            success_count += 1
            continue

        try:
            # 执行转换
            converter.emf_file_to_png_file(str(emf_path), str(png_path))
            print(f"成功: {emf_path.name} -> {png_path.name}")
            success_count += 1
        except Exception as e:
            print(f"失败: {emf_path.name}, 错误: {e}")
            fail_count += 1

    print("\n转换完成!")
    print(f"成功: {success_count}")
    print(f"失败: {fail_count}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--media_dir', default='media')
    args = parser.parse_args()
    
    convert_media_folder(args.media_dir)
