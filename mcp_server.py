# /// script
# dependencies = [
#   "mcp",
# ]
# ///

import os
from mcp.server.fastmcp import FastMCP

# 初始化 MCP 服务器
mcp = FastMCP("fm-datasheet-server")

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
        return [f"提示：该手册没有分章节目录，可以直接使用 read_datasheet 读取 {datasheet_name}"]

    return [f.rsplit('.', 1)[0] for f in os.listdir(subdir) if f.endswith(".md")]

@mcp.tool()
async def read_datasheet(datasheet_name: str) -> str:
    """读取指定 datasheet 的内容"""
    filepath = os.path.join(DATA_DIR, f"{datasheet_name}.md")
    if not os.path.exists(filepath):
        return f"错误：手册文件 {datasheet_name}.md 不存在"
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"读取文件时发生错误：{str(e)}"

@mcp.tool()
async def read_chapter(datasheet_name: str, chapter_name: str) -> str:
    """读取指定手册的特定章节内容"""
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
