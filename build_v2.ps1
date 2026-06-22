<#
.SYNOPSIS
    构建文档项目脚本。用于将 PDF 文档转换为切分好的 Markdown 项目。

.DESCRIPTION
    本脚本自动化执行以下流程：
    1. PDF 转 Markdown
    2. EMF 转 PNG
    3. 多模态图片内容解析
    4. 合并图片解析内容到主 Markdown
    5. 将合并后的文档按标题层级切分

.PARAMETER inputFile
    输入的 PDF 文件路径（可选，因为可以通过 -h 查看帮助）。

.PARAMETER buildDir
    构建过程的临时工作目录（默认：build）。

.PARAMETER releaseDir
    最终发布目录（默认：ds，别名 -r）。

.PARAMETER outputName
    项目名称，默认使用输入文件名（别名 -o）。

.PARAMETER level
    Markdown 切分的标题层级（默认：2，别名 -l）。

.EXAMPLE
    .\build_v2.ps1 "datasheet.pdf"
    .\build_v2.ps1 -h
    .\build_v2.ps1 "datasheet.pdf" -r "my_release" -l 3
#>
param(
    [Parameter(Position=0)]
    [Alias('i')]
    [string]$inputFile,

    [Alias('b')]
    [string]$buildDir = "build",

    [Alias('r')]
    [string]$releaseDir = "ds",

    [Alias('o')]
    [string]$outputName = "",

    [Alias('l')]
    [int]$level = 2,

    [Alias('m')]
    [ValidateSet("pymupdf", "markitdown")]
    [string]$method = "pymupdf",

    # 添加帮助开关
    [Alias('h', '?')]
    [Switch]$Help
)

# 处理帮助请求
if ($Help) {
    Get-Help $MyInvocation.MyCommand.Path -Full
    exit
}

# 手动检查输入文件是否为空
if (-not $inputFile) {
    Write-Host "错误: 必须提供输入文件路径。" -ForegroundColor Red
    Write-Host "使用 -h 或 -? 查看帮助。" -ForegroundColor Yellow
    exit 1
}

# 前置环境检查
if (-not (Get-Command "uv" -ErrorAction SilentlyContinue)) {
    Write-Host "错误: 未找到 'uv' 命令。请确保已安装 uv 并将其添加到系统 PATH 中。" -ForegroundColor Red
    exit 1
}

# 获取输入文件名（不带扩展名）作为项目名
$inputFileInfo = Get-Item $inputFile
$projectName = if ($outputName) { $outputName } else { $inputFileInfo.BaseName }

# 创建构建目录（已存在则先清理，确保干净构建）
$projectBuildDir = Join-Path $buildDir $projectName
if (Test-Path $projectBuildDir) {
    Write-Host "构建目录已存在，清理旧文件: $projectBuildDir" -ForegroundColor Yellow
    Remove-Item -Recurse -Force $projectBuildDir
}
New-Item -ItemType Directory -Path $projectBuildDir | Out-Null

# 构建路径变量
$mediaDir = Join-Path $projectBuildDir "media"
$intermediateMdPath = Join-Path $projectBuildDir "$projectName.md"
$mediaInfoPath = Join-Path $projectBuildDir "media_info.md"

# 复制输入文件到构建目录
$targetFilePath = Join-Path $projectBuildDir $inputFileInfo.Name
Copy-Item $inputFile -Destination $targetFilePath

Write-Host "开始构建项目: $projectName" -ForegroundColor Cyan
Write-Host "工作目录: $projectBuildDir"

# 转换流程
Write-Host "1. 转换为 Markdown (引擎: $method)..." -ForegroundColor Yellow
$converterScript = switch ($method) {
    "markitdown" { "pdf2md_markitdown.py" }
    default { "pdf2md_pymupdf4llm.py" }
}
uv run $converterScript $targetFilePath $intermediateMdPath $mediaDir
if ($LASTEXITCODE -ne 0) { Write-Host "错误: 转换 Markdown 失败" -ForegroundColor Red; exit 1 }

Write-Host "2. 处理 EMF 图片..." -ForegroundColor Yellow
uv run convert_emf.py --media_dir $mediaDir
if ($LASTEXITCODE -ne 0) { Write-Host "错误: EMF 图片处理失败" -ForegroundColor Red; exit 1 }

Write-Host "3. 多模态图片解析..." -ForegroundColor Yellow
uv run analyze_image.py --media_dir $mediaDir --output_md $mediaInfoPath
if ($LASTEXITCODE -ne 0) { Write-Host "错误: 多模态解析失败" -ForegroundColor Red; exit 1 }

Write-Host "4. 合并结果到主文档..." -ForegroundColor Yellow
# 确保输出目录存在
$fullReleaseDir = Join-Path $PSScriptRoot $releaseDir
if (-not (Test-Path $fullReleaseDir)) { New-Item -ItemType Directory -Path $fullReleaseDir | Out-Null }

# 清理当前项目旧的输出文件（主 md + 切分目录）
$finalMdPath = Join-Path $fullReleaseDir "$projectName.md"
$splitDir = Join-Path $fullReleaseDir $projectName
if (Test-Path $finalMdPath) { Remove-Item -Force $finalMdPath }
if (Test-Path $splitDir) { Remove-Item -Recurse -Force $splitDir }

uv run merge_images.py --input_md $intermediateMdPath --info_md $mediaInfoPath --output_md $finalMdPath
if ($LASTEXITCODE -ne 0) { Write-Host "错误: 文档合并失败" -ForegroundColor Red; exit 1 }

Write-Host "5. 切分文档..." -ForegroundColor Yellow
uv run split_md.py $finalMdPath --level $level
if ($LASTEXITCODE -ne 0) { Write-Host "错误: 文档切分失败" -ForegroundColor Red; exit 1 }

Write-Host "构建完成！文件已输出到 $releaseDir" -ForegroundColor Green
