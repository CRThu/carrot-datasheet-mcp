# /// script
# dependencies = [
#   "mcp",
# ]
# ///

import asyncio
import os
from mcp_server import list_datasheets, list_chapters, read_datasheet, read_chapter

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

    if chapters and isinstance(chapters, list) and len(chapters) > 0 and "提示" not in chapters[0]:
        chapter_target = chapters[0]
        print(f"\n--- 测试 read_chapter ({target} -> {chapter_target}) ---")
        chap_content = await read_chapter(target, chapter_target)
        print(f"内容预览: {chap_content[:50]}...")
    else:
        print("\n跳过 read_chapter 测试 (未找到分章节目录或手册无章节)")

if __name__ == "__main__":
    asyncio.run(test())
