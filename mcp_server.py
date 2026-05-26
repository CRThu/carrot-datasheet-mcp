# /// script
# dependencies = [
#   "mcp",
# ]
# ///

import os
import itertools
from mcp.server.fastmcp import FastMCP

# 初始化 MCP 服务器
VERSION = "1.1.0"
mcp = FastMCP(f"carrot-datasheet-mcp")

@mcp.tool()
async def get_version() -> str:
    """获取当前 MCP 服务器版本号"""
    return VERSION

# 配置数据表存放目录
DATA_DIR = "ds"

# 确保目录存在
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

@mcp.tool()
async def list_datasheets() -> list[str]:
    """列出所有可用的 datasheet 名称 (不包含文件后缀)"""
    names = set()
    for f in os.listdir(DATA_DIR):
        if f.endswith(".md"):
            names.add(f.rsplit('.', 1)[0])
        elif os.path.isdir(os.path.join(DATA_DIR, f)):
            names.add(f)
    return sorted(list(names))

@mcp.tool()
async def list_chapters(datasheet_name: str) -> list[str]:
    """列出指定 datasheet 的所有分章节文件"""
    subdir = os.path.join(DATA_DIR, datasheet_name)
    if not os.path.exists(subdir) or not os.path.isdir(subdir):
        return []
    return sorted([f.rsplit('.', 1)[0] for f in os.listdir(subdir) if f.endswith(".md")])

@mcp.tool()
async def read_datasheet(datasheet_name: str, start_line: int = 1, line_limit: int = 1000) -> str:
    """读取指定 datasheet 的内容。支持按行读取以避免过长。start_line 从1开始。"""
    filepath = os.path.join(DATA_DIR, f"{datasheet_name}.md")
    if not os.path.exists(filepath):
        return f"错误：手册文件 {datasheet_name}.md 不存在"
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            # 创建一个从 start_line 开始的迭代器
            it = itertools.islice(f, start_line - 1, None)
            # 从该迭代器中读取需要的行
            selected_lines = list(itertools.islice(it, line_limit))
            result = "".join(selected_lines)
            
            # 检查是否还有更多内容 (尝试从迭代器中读取下一行)
            has_more = len(list(itertools.islice(it, 1))) > 0
            
            if has_more:
                result += f"\n\n--- 已读取第 {start_line} 到 {start_line + len(selected_lines) - 1} 行。如需继续，请调用 read_datasheet(datasheet_name='{datasheet_name}', start_line={start_line + line_limit}) ---"
            else:
                result += f"\n\n--- 文件已读取完毕。 ---"
            return result
    except Exception as e:
        return f"读取文件时发生错误：{str(e)}"

@mcp.tool()
async def read_chapter(datasheet_name: str, index: int) -> str:
    """通过章节索引(从0开始)读取指定手册的特定章节内容。请先调用 list_chapters 获取列表，然后使用索引读取。"""
    # 获取所有章节列表
    chapters = await list_chapters(datasheet_name)
    
    if not chapters:
        return f"错误：该手册 {datasheet_name} 没有分章节目录，或无法找到。"
    
    # 检查索引是否有效
    if 0 <= index < len(chapters):
        chapter_name = chapters[index]
    else:
        return f"错误：索引 {index} 超出范围 (0-{len(chapters)-1})"

    filepath = os.path.join(DATA_DIR, datasheet_name, f"{chapter_name}.md")

    if not os.path.exists(filepath):
        return f"错误：章节文件 {chapter_name}.md 不存在"
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"读取文件时发生错误：{str(e)}"

if __name__ == "__main__":
    mcp.run()
