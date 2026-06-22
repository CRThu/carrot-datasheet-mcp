# Carrot Datasheet MCP

轻量级、本地优先的硬件文档处理方案。通过将手册结构化，让 AI 通过"目录直达"方式精准获取信息，告别模糊检索。

*   **告别模糊检索**：通过 MCP 协议直接定位章节，获取完整原文，解决"断章取义"问题。
*   **本地轻量运行**：无需向量数据库，本地文件夹即知识库。
*   **智能图片解析**：多模态大模型自动解析原理图、时序图、寄存器表等关键图表。

---

## 快速开始

### 前置要求

*   **Python** 3.10+
*   **uv** — [安装指南](https://github.com/astral-sh/uv)
*   **Pandoc** — [官网下载](https://pandoc.org/installing.html)
*   **Google API Key**（可选）— 用于多模态图片解析，未配置时自动跳过

### 一键构建（推荐）

```powershell
.\build_v2.ps1 "datasheet.pdf"
```

自动完成：PDF → Markdown → EMF 转 PNG → 多模态图片解析 → 合并 → 切分。每次构建前自动清理旧文件。

**参数：**

| 参数 | 别名 | 默认值 | 说明 |
|------|------|--------|------|
| `-releaseDir` | `-r` | `ds` | 最终发布目录 |
| `-outputName` | `-o` | 输入文件名 | 项目名称 |
| `-level` | `-l` | `2` | 切分的标题层级 |
| `-buildDir` | `-b` | `build` | 构建临时目录 |
| `-method` | `-m` | `pymupdf` | 转换引擎：`pymupdf` 或 `markitdown` |

```powershell
.\build_v2.ps1 "datasheet.pdf" -r "my_release" -l 3
```

---

## 手动构建

如需逐步控制构建过程，可按以下步骤操作。

### 1. 准备工作区

```bash
mkdir build/your-project-name
cp your-doc.pdf build/your-project-name/
cd build/your-project-name
```

### 2. PDF 转 Markdown

**方案 A：直接转换（推荐）**

```bash
uv run ../../pdf2md_pymupdf4llm.py "your-doc.pdf" "pandoc.md" "media"
```

**方案 B：经 DOCX 中转（排版还原度更高，需 Acrobat + Pandoc）**

```bash
uv run ../../pdf2docx_acrobat.py "your-doc.pdf" "your-doc.docx"
pandoc "your-doc.docx" -t markdown -o "pandoc.md" --wrap=none --extract-media="."
```

> 无需 Acrobat 的替代方案：`uv run ../../pdf2docx_pdf2docx.py`（排版还原度可能较低）

### 3. 处理图片

```bash
uv run ../../convert_emf.py --media_dir "media"
```

### 4. 多模态图片解析（可选）

需配置 `.env` 中的 `GOOGLE_API_KEY`。未配置或服务不可用时自动跳过。

```bash
uv run ../../analyze_image.py --media_dir "media"
```

### 5. 合并结果

```bash
uv run ../../merge_images.py --input_md="pandoc.md" --info_md="media_info.md" --output_md="../../ds/final_doc.md"
```

### 6. 按标题切分

```bash
uv run ../../split_md.py ../../ds/final_doc.md --level 2
```

---

## MCP 集成

配置后 AI 助手可直接读取和检索 datasheets。

### 配置文件

| IDE | 路径 |
|-----|------|
| Claude Code | `~\.claude.json` |
| Antigravity IDE | `~\.gemini\config\mcp_config.json` |

```json
{
  "mcpServers": {
    "carrot-datasheet-mcp": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "YOUR_PROJECT_PATH\\carrot-datasheet-mcp",
        "mcp_server.py"
      ]
    }
  }
}
```

> 将 `YOUR_PROJECT_PATH\\carrot-datasheet-mcp` 替换为本地项目绝对路径。

### 可用工具

| 工具 | 说明 |
|------|------|
| `list_datasheets()` | 获取所有已索引的手册列表 |
| `list_chapters(datasheet_name)` | 查看特定手册的章节 |
| `read_datasheet(datasheet_name)` | 获取全文内容 |
| `read_chapter(datasheet_name, chapter_name)` | 精准读取特定章节（推荐） |

---

## 脚本参考

| 脚本 | 说明 | 用法 |
|------|------|------|
| `pdf2md_pymupdf4llm.py` | PDF 直转 Markdown，提取媒体资源（默认） | `uv run pdf2md_pymupdf4llm.py <input.pdf> <output.md> <media_dir>` |
| `pdf2md_markitdown.py` | PDF 转 Markdown（MarkItDown 引擎，备选） | `uv run pdf2md_markitdown.py <input.pdf> <output.md> <media_dir>` |
| `pdf2docx_acrobat.py` | PDF 转 DOCX（需 Acrobat） | `uv run pdf2docx_acrobat.py <input.pdf> <output.docx>` |
| `pdf2docx_pdf2docx.py` | PDF 转 DOCX（无需 Acrobat） | `uv run pdf2docx_pdf2docx.py <input.pdf> <output.docx>` |
| `convert_emf.py` | EMF 批量转 PNG | `uv run convert_emf.py --media_dir "media"` |
| `analyze_image.py` | 多模态图片解析（可选，需 API Key） | `uv run analyze_image.py --media_dir "media" --output_md "output.md"` |
| `merge_images.py` | 合并图片解析结果到主文档 | `uv run merge_images.py --input_md "doc.md" --info_md "info.md" --output_md "final.md"` |
| `split_md.py` | 按标题层级切分文档 | `uv run split_md.py path/to/doc.md --level 2` |
| `get_toc.py` | 解析文件目录结构 | `uv run get_toc.py <文件路径> [-l level]` |

**容错说明：**
- `analyze_image.py`：无 API Key 时跳过；连接失败自动重试（最多 10 次），单张失败不影响后续处理
- `merge_images.py`：`info_md` 不存在或为空时，直接复制原始文档，不报错

---

## 项目结构

```
carrot-datasheet-mcp/
├── build/                    # 构建临时目录（每个子目录对应一个文档）
├── ds/                       # 切分后的 Markdown 章节，MCP 服务读取此目录
├── pdf2md_pymupdf4llm.py     # PDF 转 Markdown（默认引擎）
├── pdf2md_markitdown.py      # PDF 转 Markdown（MarkItDown 引擎）
├── convert_emf.py            # EMF 转 PNG
├── analyze_image.py          # 多模态图片解析
├── merge_images.py           # 合并图片解析结果
├── split_md.py               # 文档切分
├── mcp_server.py             # MCP Server 入口
└── build_v2.ps1              # 一键构建脚本
```

---

## 许可

Apache License 2.0
