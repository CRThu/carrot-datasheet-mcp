# /// script
# dependencies = [
#   "mcp",
# ]
# ///

import os
from mcp.server.fastmcp import FastMCP

# 初始化 MCP 服务器
mcp = FastMCP("fm434-server")

# 配置数据表存放目录
DATA_DIR = "datasheets"

# 确保目录存在
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

@mcp.tool()
async def list_datasheets() -> list[str]:
    """列出所有可用的 datasheet 文件"""
    return [f for f in os.listdir(DATA_DIR) if f.endswith(".md")]

@mcp.tool()
async def read_datasheet(filename: str) -> str:
    """读取指定 datasheet 的内容 (例如: 'fm434_final.md')"""
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        return f"错误：文件 {filename} 不存在"
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"读取文件时发生错误：{str(e)}"

if __name__ == "__main__":
    mcp.run()
