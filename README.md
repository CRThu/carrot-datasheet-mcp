# Carrot Datasheet MCP

**Carrot Datasheet MCP** 是一套轻量级、本地优先的硬件文档处理方案。它通过将手册结构化，让 AI 能够像工程师一样通过“目录直达”的方式精准获取信息，彻底告别了传统模糊检索带来的检索偏差。

**为什么选择 Carrot Datasheet MCP？**

*   **告别模糊检索**：摒弃传统 RAG 的概率性搜索，通过 MCP 协议直接定位章节。AI 获取的是该章节的“完整原文”，彻底解决了“断章取义”和“读不懂寄存器表”的常见问题。
*   **本地轻量运行**：无需部署复杂的向量数据库，无需外部云端索引。本地文件夹即是知识库，安全、快速且无额外依赖。
*   **专注硬件细节**：内置的多模态解析能力，能深度还原手册中的关键图表（原理图、寄存器表等），让 AI 不仅能读懂文字，更能准确解析关键的技术逻辑。

## 核心功能

*   **全自动流水线**：从原始 DOCX 到最终切分好的 Markdown 的标准化处理流程。
*   **智能图片解析**：利用多模态大模型（Gemini）自动识别并解析硬件文档中的原理图、时序图、引脚图。
*   **EMF 兼容支持**：自动将文档中常见的 EMF 矢量图转换为 Web 友好的 PNG 格式。
*   **文档结构化切分**：自动按标题层级拆分超长文档，适合 LLM 上下文检索。
*   **MCP 原生支持**：内置 MCP Server，允许 AI 助手直接读取、检索并理解 datasheets。

---

## 核心流水线流程

本项目构建了一套“转换 -> 解析 -> 合并 -> 切分”的完整工作流：

1.  **Pandoc 转换**：提取文本与媒体资源。
2.  **图像预处理**：将 EMF 格式统一转换为 PNG。
3.  **多模态增强**：通过 `analyze_image.py` 调用 Gemini 深度分析图片中的技术参数（寄存器、逻辑图等），并将结果以 Markdown 格式“逆向翻译”回原文。
4.  **内容切分**：通过 `split_md.py` 将长文档拆解为原子化的章节文件。
5.  **MCP 服务**：通过 `mcp_server.py` 提供统一接口，供开发环境调用。

---

## 🛠 前置要求

在开始之前，请确保系统已安装以下工具：

*   **Python**: 建议 3.10+
*   **uv**: [快速安装指南](https://github.com/astral-sh/uv) (项目依赖管理工具)
*   **Pandoc**: 必须安装，用于文档转换。([官网下载](https://pandoc.org/installing.html))
*   **Google API Key**: 用于多模态图片解析 (Gemini)。

---

## 文档构建工作流

本项目通过一系列脚本处理文档。对于每个新的 datasheet（以 `YourDoc.docx` 为例），请按照以下标准流程在项目根目录下操作：

### 1. 准备工作区
在 `build/` 目录下创建一个文件夹，放入您的 `.docx` 文件：
```bash
mkdir build/your-project-name
# 将 your-doc.docx 放入 build/your-project-name/
cd build/your-project-name
```

### 2. 执行标准处理流程
请在 `build/your-project-name/` 目录下依次执行以下命令（假设您已配置好环境变量）：

1.  **转换为 Markdown 并提取图片**：
    ```bash
    pandoc "your-doc.docx" -t markdown -o "pandoc.md" --wrap=none --extract-media="."
    ```
2.  **处理图片（EMF 转 PNG）**：
    ```bash
    uv run ../../convert_emf.py
    ```
3.  **多模态图片解析**（此步会调用 Gemini，请确保 `.env` 配置正确）：
    ```bash
    uv run ../../analyze_image.py
    ```
4.  **合并解析结果到主文档**：
    ```bash
    uv run ../../merge_images.py --input_md="pandoc.md" --info_md="media_info.md" --output_md="../../ds/final_doc.md"
    ```
5.  **按标题层级切分文档**（生成可被 MCP 读取的碎片化章节）：
    ```bash
    uv run ../../split_md.py ../../ds/final_doc.md --level 2
    ```

---

## MCP 服务配置

为了让您的 IDE 能够调用此工具，请按照以下路径配置 MCP。

### 1. Claude Code 配置
配置文件路径：`~\.claude.json`

### 2. Antigravity IDE 配置
配置文件路径：`~\.gemini\config\mcp_config.json`

**配置内容模板：**

```json
{
  "mcpServers": {
    "carrot-datasheet-mcp": {
      "command": "uv",
      "args":[
        "run",
        "--directory",
        "YOUR_PROJECT_PATH\\carrot-datasheet-mcp",
        "mcp_server.py"
      ]
    }
  }
}
```
*请务必将 `YOUR_PROJECT_PATH\\carrot-datasheet-mcp` 替换为本地项目的真实绝对路径。*

---

### 可用 MCP 工具 (Tools)
配置生效后，AI 可调用以下接口：
*   `list_datasheets()`: 获取所有已索引的手册列表。
*   `list_chapters(datasheet_name)`: 查看特定手册的所有章节。
*   `read_datasheet(datasheet_name)`: 获取全文内容。
*   `read_chapter(datasheet_name, chapter_name)`: **精准读取特定章节**（推荐用于长文档检索）。

---

## 工具脚本及参数详解

本项目包含多个处理脚本，您可以直接通过 `uv run` 调用。

### 1. `convert_emf.py`
将 `media/` 目录下的所有 EMF 矢量图批量转换为 PNG。
*   **参数**：无（自动处理当前目录下的 `media` 文件夹）。
*   **用法**：`uv run convert_emf.py`

### 2. `analyze_image.py`
遍历媒体目录，调用 Gemini 对硬件图片进行结构化解析。
*   `--media_dir` (默认 `media`): 图片存放目录。
*   `--output_md` (默认 `media_info.md`): 解析结果的输出文件。
*   **用法**：`uv run analyze_image.py --media_dir "media" --output_md "output.md"`

### 3. `merge_images.py`
将解析好的图片 Markdown 片段合并回主文档。
*   `--input_md` (默认 `pandoc.md`): 原始 Markdown 文档路径。
*   `--info_md` (默认 `media_info.md`): 由 `analyze_image.py` 生成的解析信息文件。
*   `--output_md` (默认 `../../ds/pandoc_final.md`): 合并后的最终输出路径。
*   **用法**：`uv run merge_images.py --input_md "doc.md" --info_md "info.md" --output_md "final.md"`

### 4. `split_md.py`
将合并后的 Markdown 文件按标题层级切分为碎片化的小文件，提升检索命中率。
*   `file` (位置参数): 待切分的 Markdown 文件路径。
*   `--output` (可选): 指定输出目录。
*   `--level` (默认 `2`): 按几级标题进行切分（例如：2 表示按 H2 标题切分）。
*   **用法**：`uv run split_md.py path/to/doc.md --level 2`

## 目录结构
*   `/ds/`: 存放切分好的 Markdown 章节，MCP 服务直接读取该目录。
*   `/build/`: 工作空间，每个子目录对应一个待处理文档。
*   `/media/`: 构建过程中产生的图片缓存。

## 许可说明
本项目遵循开源协议 Apache 2.0。