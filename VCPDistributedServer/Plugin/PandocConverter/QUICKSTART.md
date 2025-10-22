# PandocConverter 快速开始指南

本指南将帮助您快速安装和使用 PandocConverter 插件。

## 安装步骤

### 1. 系统要求

- Python 3.7 或更高版本
- Pandoc (必须安装)
- LaTeX 发行版 (可选，用于PDF生成)

### 2. 安装 Pandoc

**Windows:**
```bash
# 使用 Chocolatey
choco install pandoc

# 或从官网下载安装包
# https://pandoc.org/installing.html
```

**macOS:**
```bash
# 使用 Homebrew
brew install pandoc
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install pandoc
```

### 3. 安装 LaTeX (可选，用于PDF生成)

**Windows:**
- 安装 MiKTeX: https://miktex.org/download

**macOS:**
- 安装 MacTeX: https://www.tug.org/mactex/

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install texlive-full
```

### 4. 配置插件

1. 进入插件目录：
```bash
cd VCPChat/VCPDistributedServer/Plugin/PandocConverter
```

2. 运行安装脚本：
```bash
python install.py
```

3. 根据提示完成配置

## 基本使用

### 1. 转换单个文件

将 Markdown 文件转换为 PDF：

```
<<<[TOOL_REQUEST]>>>
maid:「始」Nova「末」,
tool_name:「始」PandocConverter「末」,
command:「始」ConvertFile「末」,
inputFile:「始」file:///C:/Users/用户名/docs/report.md「末」,
outputFormat:「始」pdf「末」,
options:「始」{"title":"技术报告","author":"张三","toc":true}「末」
<<<[END_TOOL_REQUEST]>>>
```

### 2. 批量转换文件

批量转换多个 Markdown 文件为 HTML：

```
<<<[TOOL_REQUEST]>>>
maid:「始」Nova「末」,
tool_name:「始」PandocConverter「末」,
command:「始」BatchConvert「末」,
inputFiles:「始」["file:///C:/docs/chapter1.md", "file:///C:/docs/chapter2.md"]「末」,
outputFormat:「始」html「末」,
options:「始」{"title":"完整文档","toc":true}「末」
<<<[END_TOOL_REQUEST]>>>
```

### 3. 从内容转换（推荐用于分布式环境）

直接从文本内容转换：

```
<<<[TOOL_REQUEST]>>>
maid:「始」Nova「末」,
tool_name:「始」PandocConverter「末」,
command:「始」ConvertFromContent「末」,
content:「始」# 标题\n\n这是一个**Markdown**文档。「末」,
inputFormat:「始」markdown「末」,
outputFormat:「始」html「末」,
options:「始」{"title":"转换测试"}「末」
<<<[END_TOOL_REQUEST]>>>
```

## 常见转换场景

### Markdown 转 PDF（中文支持）

```
<<<[TOOL_REQUEST]>>>
maid:「始」Nova「末」,
tool_name:「始」PandocConverter「末」,
command:「始」ConvertFile「末」,
inputFile:「始」file:///C:/docs/report.md「末」,
outputFormat:「始」pdf「末」,
options:「始」{"pdfEngine":"xelatex","fontSize":"12pt","margin":"1in"}「末」
<<<[END_TOOL_REQUEST]>>>
```

### Markdown 转 HTML（带代码高亮）

```
<<<[TOOL_REQUEST]>>>
maid:「始」Nova「末」,
tool_name:「始」PandocConverter「末」,
command:「始」ConvertFile「末」,
inputFile:「始」file:///C:/docs/tutorial.md「末」,
outputFormat:「始」html「末」,
options:「始」{"highlightStyle":"github"}「末」
<<<[END_TOOL_REQUEST]>>>
```

### HTML 转 Word

```
<<<[TOOL_REQUEST]>>>
maid:「始」Nova「末」,
tool_name:「始」PandocConverter「末」,
command:「始」ConvertFile「末」,
inputFile:「始」https://example.com/page.html「末」,
outputFormat:「始」docx「末」,
options:「始」{"enableRawHTML":true}「末」
<<<[END_TOOL_REQUEST]>>>
```

## 支持的格式

### 输入格式
- Markdown (.md, .markdown)
- HTML (.html, .htm)
- LaTeX (.tex, .latex)
- reStructuredText (.rst)
- EPUB (.epub)
- Word (.docx, .doc)
- PDF (.pdf)
- 纯文本 (.txt)
- 更多格式...

### 输出格式
- HTML (.html)
- PDF (.pdf)
- Word (.docx)
- LaTeX (.tex)
- reStructuredText (.rst)
- EPUB (.epub)
- 纯文本 (.txt)
- 更多格式...

## 转换选项

### 基本选项
- `title`: 文档标题
- `author`: 文档作者
- `toc`: 是否生成目录 (true/false)
- `tocDepth`: 目录深度 (数字)

### 样式选项
- `cssFile`: CSS样式文件路径
- `highlightStyle`: 代码高亮样式
- `fontSize`: 字体大小 (如 "12pt")
- `margin`: 页边距 (如 "1in")

### PDF选项
- `pdfEngine`: PDF引擎 (pdflatex/xelatex/lualatex)
- `papersize`: 纸张大小 (a4/letter)
- `landscape`: 是否横向 (true/false)

## 分布式环境使用

### 文件访问方式

在分布式环境中，请使用以下方式指定文件：

1. **file:// 协议**（推荐）：
```
inputFile:「始」file:///C:/Users/用户名/docs/report.md「末」
```

2. **HTTP/HTTPS URL**：
```
inputFile:「始」https://example.com/document.md「末」
```

3. **直接传递内容**（最可靠）：
```
command:「始」ConvertFromContent「末」,
content:「始」# 文档内容...「末」,
inputFormat:「始」markdown「末」,
outputFormat:「始」pdf「末」
```

### 路径转换

如果用户提供了相对路径，AI应将其转换为绝对路径或file://格式：

```
用户输入：./docs/report.md
AI应转换为：file:///C:/Users/用户名/project/docs/report.md
```

## 故障排除

### 常见问题

1. **Pandoc不可用**
   - 确保已正确安装Pandoc
   - 检查PANDOC_PATH配置

2. **PDF生成失败**
   - 确保已安装LaTeX发行版
   - 尝试使用xelatex引擎

3. **中文显示问题**
   - 使用xelatex作为PDF引擎
   - 确保系统已安装中文字体

### 测试插件

运行测试脚本验证插件功能：

```bash
python test_plugin.py
```

## 进阶使用

### 自定义模板

1. 将自定义模板放在 `templates/` 目录
2. 在转换选项中指定模板路径：
```
options:「始」{"template":"./templates/custom_template.html"}「末」
```

### 批量处理

使用 BatchConvert 命令处理多个文件：

```
<<<[TOOL_REQUEST]>>>
maid:「始」Nova「末」,
tool_name:「始」PandocConverter「末」,
command:「始」BatchConvert「末」,
inputFiles:「始」["doc1.md", "doc2.md", "doc3.md"]「末」,
outputFormat:「始」pdf「末」,
preserveStructure:「始」true「末」
<<<[END_TOOL_REQUEST]>>>
```

## 更多信息

- 详细文档：README.md
- 配置选项：config.env.example
- 示例文档：examples/sample.md

如有问题，请参考完整文档或提交Issue。