# /// script
# dependencies = [
#   "mcp",
# ]
# ///

import os
import itertools
import re
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

@mcp.tool()
async def search_in_datasheet(
    datasheet_name: str,
    query: str,
    page: int = 1,
    page_size: int = 20,
    context_length: int = 200
) -> dict:
    """在指定 datasheet 中搜索关键字。返回包含分页信息和匹配结果的 JSON 结构。"""
    
    all_matches = []
    
    # 确定搜索路径
    dir_path = os.path.join(DATA_DIR, datasheet_name)
    file_path = os.path.join(DATA_DIR, f"{datasheet_name}.md")
    
    files_to_search = []
    if os.path.isdir(dir_path):
        # It's a directory, search all .md files
        for f in sorted(os.listdir(dir_path)):
            if f.endswith(".md"):
                files_to_search.append((f.rsplit('.', 1)[0], os.path.join(dir_path, f)))
    elif os.path.exists(file_path):
        # It's a single file
        files_to_search.append((datasheet_name, file_path))
    else:
        return {"error": f"手册 {datasheet_name} 不存在。"}
    
    # 执行搜索并收集所有匹配
    for name, path in files_to_search:
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                
            for match in re.finditer(re.escape(query), content, re.IGNORECASE):
                start = max(0, match.start() - context_length)
                end = min(len(content), match.end() + context_length)
                
                context = content[start:end].replace('\n', ' ')
                
                all_matches.append({
                    "chapter": name,
                    "context": f"...{context}..."
                })
        except Exception as e:
            continue
            
    # 计算分页
    total_matches = len(all_matches)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paged_results = all_matches[start_idx:end_idx]
    
    return {
        "query": query,
        "total_matches": total_matches,
        "page": page,
        "page_size": page_size,
        "returned_matches": len(paged_results),
        "results": paged_results
    }

if __name__ == "__main__":
    mcp.run()
