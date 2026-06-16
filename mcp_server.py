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
VERSION = "1.3.3"
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
async def read_datasheet(datasheet_name: str, start_line: int = 1, line_limit: int = 1000) -> dict:
    """读取指定 datasheet 的全部或部分内容。警告：若文档体积巨大，建议仅在无TOC划分的文档中使用此方法，优先通过 search 或 read_chapter 获取具体片段。"""
    filepath = os.path.join(DATA_DIR, f"{datasheet_name}.md")
    if not os.path.exists(filepath):
        return {"error": f"手册文件 {datasheet_name}.md 不存在"}
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            # 创建迭代器以进行行读取
            all_lines = f.readlines()
            total_lines = len(all_lines)
            
            # 计算切片范围
            start = start_line - 1
            end = start + line_limit
            
            selected_lines = all_lines[start:end]
            has_more = end < total_lines
            
            return {
                "content": "".join(selected_lines),
                "page_info": {
                    "current_start_line": start_line,
                    "line_limit": line_limit,
                    "lines_read": len(selected_lines),
                    "has_more": has_more
                }
            }
    except Exception as e:
        return {"error": str(e)}

# 辅助函数，封装通用的读取逻辑
async def _read_chapter_file(datasheet_name: str, chapter_filename: str, start_line: int, line_limit: int) -> dict:
    """读取指定路径的章节文件内容"""
    filepath = os.path.join(DATA_DIR, datasheet_name, f"{chapter_filename}.md")
    
    if not os.path.exists(filepath):
        return {"error": f"章节文件 {chapter_filename}.md 不存在"}
        
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
            total_lines = len(lines)
            
            # 计算切片范围
            start = start_line - 1
            end = start + line_limit
            
            selected_lines = lines[start:end]
            has_more = end < total_lines
            
            return {
                "chapter_name": chapter_filename,
                "content": "".join(selected_lines),
                "page_info": {
                    "current_start_line": start_line,
                    "line_limit": line_limit,
                    "lines_read": len(selected_lines),
                    "has_more": has_more
                }
            }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def read_chapters(datasheet_name: str, indices_str: str, start_line: int = 1, line_limit: int = 50) -> dict:
    """通过章节号（如 '1' 或 '1.1'）读取指定手册的特定章节。支持逗号分隔批量查找，如 '1,1.1,1.2'。"""
    
    # 1. 获取所有章节名列表
    all_chapters = await list_chapters(datasheet_name)
    if not all_chapters:
        return {"error": f"手册 {datasheet_name} 没有找到分章节目录"}
    
    # 2. 解析用户传入的章节号字符串，仅支持逗号分隔
    requested_ids = [cid.strip() for cid in str(indices_str).split(',') if cid.strip()]
    
    results = {}
    
    # 3. 匹配并读取
    for cid in requested_ids:
        # 在章节列表中查找：章节名格式为 [datasheet].[id].[title]
        # 使用正则表达式精确匹配第二个方括号内的内容 cid
        match = None
        for ch in all_chapters:
            # 文件名结构: [datasheet].[id].[title]
            # 切分：['', 'datasheet', 'id', 'title', '']
            parts = re.split(r'\[|\]\.\[|\]', ch)
            if len(parts) >= 4 and parts[2] == cid:
                match = ch
                break
        
        if not match:
            results[f"error_{cid}"] = f"未找到章节号 {cid}"
            continue
            
        results[cid] = await _read_chapter_file(datasheet_name, match, start_line, line_limit)
        
    return results

def _get_chapter_info(filename):
    # Filename structure: [datasheet].[id].[title]
    # Example: [stm32f103].[1.1].[introduction]
    parts = re.split(r'\[|\]\.\[|\]', filename)
    # Result: ['', 'datasheet', 'id', 'title', '']
    
    if len(parts) >= 4:
        return {
            "id": parts[2],
            "title": parts[3]
        }
    return {"id": filename, "title": filename}

@mcp.tool()
async def search_in_datasheet(
    datasheet_name: str,
    query: str,
    page: int = 1,
    page_size: int = 20,
    context_length: int = 200
) -> dict:
    """在 datasheet 中通过精确字符串匹配工具对关键字进行Ctrl-F形式的搜索定位。用于初步查找寄存器名称、功能描述或协议细节(无法进行模糊搜索或启发式搜索，必须使用单词匹配: ARR, 6301, SPI, 不要使用多词匹配: TIM1_ARR, Timing, 0x6301, 6301h register info)，是在datasheet精确查找信息或术语的首选工具。"""
    
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
                
                info = _get_chapter_info(name)
                all_matches.append({
                    "chapter_id": info["id"],
                    "chapter_title": info["title"],
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
