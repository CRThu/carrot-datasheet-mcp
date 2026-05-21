# /// script
# dependencies = [
#   "google-genai",
#   "python-dotenv",
#   "pillow",
# ]
# ///

import os
import glob
import time
import argparse
from google import genai
from google.genai import types
from PIL import Image
from dotenv import load_dotenv

# 加载 .env 文件并配置 API Key
load_dotenv(dotenv_path=".env")

# 自动从环境变量设置代理（如果 .env 中定义了代理）
proxy = os.getenv("HTTP_PROXY")
if proxy:
    os.environ["HTTP_PROXY"] = proxy
    os.environ["HTTPS_PROXY"] = proxy

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("未在 .env 文件中找到 GOOGLE_API_KEY")
client = genai.Client(api_key=api_key)

def analyze_image(image_path, max_retries=10):
    img = Image.open(image_path)

    # 动态获取文件名以填入模板
    filename = os.path.basename(image_path)

    prompt = f"""
    你是一位资深的硬件工程师。请根据以下规范分析这张硬件图片，解析结果必须严格遵守下面的 Markdown 格式。

    #### 图片解析规范：结构优先策略
    凡是可以通过表格或图表表达的信息，严禁仅用文字描述。请优先采用：
    - **Markdown 表格**：用于寄存器映射、引脚定义、时序参数表、逻辑真值表。
    - **Mermaid/ASCII 图表**：用于状态机（FSM）路径、模块连接关系、数据流转逻辑。
    - **层级列表**：用于描述模块间的拓扑结构或嵌套层级。

    若图片逻辑无法通过结构化方式表达，必须使用严谨的硬件工程术语（如 `posedge clk`, `[X:0]`, `Hi-Z`, `Valid/Ready`）描述，且必须具备 Spec 级的准确性，禁止使用“大约”、“可能”等模糊词汇。图中未标明的信息一律标记为“未标明”。

    #### 图片解析输出格式 (必须严格执行)

    1. 【总览信息】：一句话定义图片核心功能。
    2. 【核心组成部件】
    3. 【数据流向与交互】（放置对应的表格、Mermaid 或 ASCII 图表）
    4. 【功能总结性陈述】（补充无法通过表/图表达的细节，以及专业级的硬件行为总结）
    """


    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model='gemini-3.1-flash-lite',
                #model='gemma-4-31b-it',
                contents=[prompt, img]
            )
            return response.text
        except Exception as e:
            if attempt < max_retries - 1:
                wait = min(30, (attempt + 1) * 5)
                print(f"遇到错误: {e}，正在重试 ({attempt + 1}/{max_retries})... 等待 {wait} 秒")
                time.sleep(wait)
                continue
            raise e

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--media_dir', default='media')
    parser.add_argument('--output_md', default='media_info.md')
    args = parser.parse_args()

    # 批量处理 media 目录下的所有 png 文件
    image_files = glob.glob(os.path.join(args.media_dir, "*.png"))

    if not image_files:
        print("未找到 media 目录下的 png 文件")
    else:
        for img_file in image_files:
            print(f"正在解析: {img_file}")
            try:
                result = analyze_image(img_file)

                # 追加写入汇总文档
                with open(args.output_md, "a", encoding="utf-8") as f:
                    f.write(f"<!-- REVERSE TRANSLATION: {img_file.replace(os.path.sep, '/')} -->\n")
                    f.write(result + "\n\n")
                    f.write(f"<!-- END OF REVERSE TRANSLATION: {img_file.replace(os.path.sep, '/')} -->\n\n")
                print(f"已完成: {img_file}")
            except Exception as e:
                print(f"解析 {img_file} 出错: {e}")