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
from pathlib import Path
from dotenv import load_dotenv

# 加载项目根目录下的 .env 文件
base_path = Path(__file__).resolve().parent
load_dotenv(dotenv_path=base_path / ".env")

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
    你是一位资深硬件工程师。请精准分析这张硬件图片，解析结果必须严格遵循下述规范：

    #### 解析策略：事实与推论分离
    1. **事实挖掘（必须严格遵循原图）**：
       - 凡是图中明确的逻辑、数值、时序、引脚，严禁曲解。
       - 所有结构化数据（如时序参数、帧格式）必须采用以下一个或多个：
        - **Markdown 表格**：用于寄存器映射、引脚定义、时序参数表、逻辑真值表。
        - **Mermaid/ASCII 图表**：用于状态机（FSM）路径、模块连接关系、数据流转逻辑。
        - **层级列表**：用于描述模块间的拓扑结构或嵌套层级。
    
       - 若图中未标注，一律标记为“未标明”。
       - 若图片仅为简单符号或置信度过低，直接返回“无详细有效信息”。

    2. **工程推理（允许适度专业推论）**：
       - 在【功能总结性陈述】中，允许基于 Spec 级经验对硬件行为进行逻辑推论。
       - **核心约束**：推理必须显式标记为“[工程推论]”。例如：[工程推论] 此 4.8ms 延迟时间显著长于总线传输周期，极大概率对应非易失性存储单元的页写入周期。
       - 禁止在表格或事实描述中混入任何推论。

    #### 图片解析输出格式 (必须严格执行)
    1. 【总览信息】：一句话定义图片核心功能。
    2. 【核心组成部件】：清晰列出部件及功能。
    3. 【数据流向与交互】：(Markdown 表格、Mermaid、ASCII 图表)
    4. 【功能总结性陈述】：
       - **事实描述**：总结原图明确表达的技术特征。
       - **工程推论**：(以 [工程推论] 开头) 基于经验对硬件行为的专业分析，必须严谨，禁止无根据的联想。
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