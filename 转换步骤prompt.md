# 硬件文档自动转换与解析指南

## 变量定义
在执行前，请根据实际工程环境修改以下占位符：
- `INPUT_DOCX`: "fm434.docx" (待转换的原始文档)
- `OUTPUT_MD`: "fm434_all.md" (转换后的主文档)
- `IMAGE_INFO_MD`: "fm434_image_info.md" (解析结果汇总文档)

---

## 任务目标
将 `INPUT_DOCX` 转换为高质量、结构化的 `markdown`，以便 MCP 环境进行纯文本读取与检索。核心工作流包括：Pandoc 文档转换、媒体文件（特别是 EMF）处理、基于多模态的图片内容深度解析，以及将解析结果精准植入 `OUTPUT_MD`。

## 工程执行流水线

### 第一步：文档格式转换
在 Shell 中执行以下命令，将文档转换为 Markdown 并导出图片资源：
```bash
pandoc "$INPUT_DOCX" -t markdown -o "$OUTPUT_MD" --wrap=none --extract-media="."
```

### 第二步：资源预处理
1. **EMF 转换**：检查 `media/` 目录下是否存在 `.emf` 文件。若存在，立即执行 `uv run convert_emf.py`，将所有 EMF 转换为同名的 PNG 文件。
2. **清单梳理**：遍历 `media/` 目录，建立所有图片资源文件的列表。

### 第三步：图片内容自动逆向解析
使用 `analyze_image.py` 脚本遍历 `media/` 目录下的所有图片资源，调用多模态大模型进行深入解读。
用法：
```bash
python analyze_image.py --media_dir "media" --output_md "解析结果文件名.md"
```

### 第四步：主文档精准回填
解析完成后，执行 `merge_images.py` 脚本，该脚本会自动读取解析结果文档，并将其结构化内容植入主 Markdown 文档中。
用法：
```bash
python merge_images.py --input_md "主文档.md" --info_md "解析结果.md" --output_md "最终文档.md"
```
脚本会自动定位 `![](media/文件名.xxx)` 引用，并将其替换为如下精准格式：

```markdown
<!-- START OF REVERSE TRANSLATION: media/文件名.xxx -->
【此处填充对应的结构化呈现及逻辑总结】
<!-- END OF REVERSE TRANSLATION: media/文件名.xxx -->
```
