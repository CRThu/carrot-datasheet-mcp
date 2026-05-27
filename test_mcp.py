# /// script
# dependencies = [
#   "mcp",
# ]
# ///

import asyncio
import os
import sys
import json
from mcp_server import list_datasheets, list_chapters, read_datasheet, read_chapters, search_in_datasheet

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
    content_res = await read_datasheet(target, start_line=1, line_limit=5)
    print(f"内容预览: {content_res.get('content', '')[:50]}...")
    print(f"分页信息: {content_res.get('page_info')}")

    # 尝试测试第一个手册的第二个章节（如果存在）
    if chapters and len(chapters) >= 1:
        # 使用索引 0 测试（单个章节）
        print(f"\n--- 测试 read_chapters (index 0) ---")
        chap_res = await read_chapters(target, "0", start_line=1, line_limit=5)
        # 结果现在是一个字典，Key 是章节名
        first_key = list(chap_res.keys())[0]
        chap_data = chap_res[first_key]
        print(f"内容预览: {chap_data.get('content', '')[:50]}...")
        print(f"分页信息: {chap_data.get('page_info')}")
        
        # 测试 search_in_datasheet
        print(f"\n--- 测试 search_in_datasheet (查询第一章的内容) ---")
        # 简单取一下第一章的一小部分文本进行测试
        chap_content = chap_data.get('content', '')
        search_query = chap_content[10:20].strip()
        if search_query:
            print(f"搜索查询: '{search_query}'")
            # 新的接口返回 dict
            search_result = await search_in_datasheet(target, search_query, page=1, page_size=20)
            print(f"搜索结果 (JSON):\n{json.dumps(search_result, indent=2, ensure_ascii=False)}")
        else:
            print("搜索查询为空，跳过测试。")

        # 测试批量读取 read_chapters (index 0,1)
        if len(chapters) >= 2:
            print(f"\n--- 测试 read_chapters (batch: 0,1) ---")
            batch_res = await read_chapters(target, "0,1", start_line=1, line_limit=5)
            print(f"读取到的章节: {list(batch_res.keys())}")
            for key, val in batch_res.items():
                print(f"章节 '{key}' 预览: {val.get('content', '')[:30]}...")
    else:
        print("\n跳过 read_chapters 测试 (未找到分章节目录或手册无章节)")

if __name__ == "__main__":
    # 强制将 stdout 重新配置为 utf-8，以支持中文和特殊符号显示
    sys.stdout.reconfigure(encoding='utf-8')
    asyncio.run(test())
