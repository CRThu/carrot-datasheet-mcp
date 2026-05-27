# /// script
# dependencies = [
#   "mcp",
# ]
# ///

import asyncio
import os
from mcp_server import list_datasheets, list_chapters, read_datasheet, read_chapter, search_in_datasheet

async def test():
    print("--- 测试 list_datasheets ---")
    sheets = await list_datasheets()
    print(f"找到手册: {sheets}")

    if not sheets:
        print("未找到任何手册，无法继续测试。")
        return

    target = sheets[0]

    print(f"\n--- 测试 list_chapters ({target}) ---")
    chapters = await list_chapters(target)
    print(f"章节列表: {chapters}")

    print(f"\n--- 测试 read_datasheet ({target}) ---")
    content = await read_datasheet(target)
    # 只打印前 50 个字符避免输出过长
    print(f"内容预览: {content[:50]}...")

    # 尝试测试第一个手册的第二个章节（如果存在）
    if chapters and len(chapters) >= 1:
        # 使用索引 0 测试
        print(f"\n--- 测试 read_chapter (index 0) ---")
        chap_content = await read_chapter(target, 0)
        print(f"内容预览: {chap_content[:50]}...")
        
        # 测试 search_in_datasheet
        print(f"\n--- 测试 search_in_datasheet (查询第一章的内容) ---")
        # 简单取一下第一章的一小部分文本进行测试
        search_query = chap_content[10:20].strip()
        if search_query:
            print(f"搜索查询: '{search_query}'")
            # 新的接口返回 dict
            search_result = await search_in_datasheet(target, search_query, page=1, page_size=20)
            import json
            print(f"搜索结果 (JSON):\n{json.dumps(search_result, indent=2, ensure_ascii=False)}")
        else:
            print("搜索查询为空，跳过测试。")
    else:
        print("\n跳过 read_chapter 测试 (未找到分章节目录或手册无章节)")

if __name__ == "__main__":
    asyncio.run(test())
