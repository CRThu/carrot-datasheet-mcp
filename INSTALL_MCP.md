# 安装配置指南

若要将 `carrot-datasheet-mcp` 配置为 Claude Code 的全局 MCP 服务，请按照以下步骤操作：

## 1. 定位配置文件
Claude Code 的全局配置文件位于：
`~\.claude.json`

## 2. 修改配置
请确保该文件中的 `mcpServers` 部分包含以下内容。如果该文件不存在或缺少 `mcpServers` 字段，请创建并添加如下配置：

```json
{
  "mcpServers": {
    "carrot-datasheet-mcp": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "D:\\Projects\\carrot-datasheet-mcp",
        "--script",
        "mcp_server.py"
      ]
    }
  }
}
```

## 3. 注意事项
- **路径检查**：请确认 `D:\\Projects\\carrot-datasheet-mcp` 路径正确指向了项目所在的物理目录。
- **依赖环境**：确保系统中已安装并配置好 `uv` 工具，且该目录下的 Python 环境能够正常运行 `mcp_server.py`。
- **生效方式**：修改完成后，重启 Claude Code CLI 或相关的 IDE 插件即可生效。

## 4. 验证安装
重启 Claude Code 后，直接使用 `/mcp` 指令即可验证服务是否已成功加载并查看可用的工具。
