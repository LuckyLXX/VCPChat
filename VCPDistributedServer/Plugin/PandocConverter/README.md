# PandocConverter 插件

强大的文档格式转换插件，支持Markdown与多种格式（HTML、PDF、Word、LaTeX、EPUB等）的双向转换，保留代码高亮、数学公式、表格和图片等元素。

## 功能特性

- **多格式支持**：支持Markdown、HTML、PDF、Word(docx)、LaTeX、reStructuredText、EPUB等格式的双向转换
- **代码高亮**：保留代码块的语法高亮
- **数学公式**：支持MathJax、KaTeX等数学公式渲染
- **表格和图片**：完整保留表格结构和图片引用
- **批量转换**：支持一次性转换多个文件
- **分布式文件访问**：支持通过file://协议访问分布式环境中的文件
- **自定义样式**：支持自定义CSS样式和LaTeX模板
- **格式检测**：自动检测输入文件格式

## 安装要求

### 系统依赖

1. **Python 3.7+**
2. **Pandoc** - 必须在系统上安装Pandoc

#### 安装Pandoc

**Windows:**
```bash
# 使用 Chocolatey
choco install pandoc

# 或使用 Scoop
scoop install pandoc

# 或从官网下载安装包
# https://pandoc.org/installing.html
```

**macOS:**
```bash
# 使用 Homebrew
brew install pandoc

# 或使用 MacPorts
sudo port install pandoc
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install pandoc
```

**Linux (CentOS/RHEL):**
```bash
sudo yum install pandoc
```

### Python依赖

插件使用了Python内置模块，无需额外安装依赖。如果需要增强功能，可以安装可选依赖：

```bash
pip install requests beautifulsoup4 markdown jinja2 pygments
```

## 配置

1. 复制 `config.env.example` 为 `config.env`
2. 根据需要修改配置文件

主要配置项：

- `PANDOC_PATH`: Pandoc可执行文件路径
- `OUTPUT_DIR`: 输出文件目录
- `TEMP_DIR`: 临时文件目录
- `ENABLE_MATHJAX`: 是否启用数学公式支持
- `ENABLE_SYNTAX_HIGHLIGHTING`: 是否启用代码语法高亮
- `DEFAULT_PDF_ENGINE`: 默认PDF生成引擎（推荐xelatex以支持中文）
- `MAX_FILE_SIZE_MB`: 最大文件大小限制

## 使用方法

### 1. 单文件转换

将Markdown文件转换为PDF：

```
<<<[TOOL_REQUEST]>>>
maid:「始」Nova「末」,
tool_name:「始」PandocConverter「末」,
command:「始」ConvertFile「末」,
inputFile:「始」file:///C:/Users/用户名/docs/report.md「末」,
outputFormat:「始」pdf「末」,
options:「始」{"title":"技术报告","author":"张三","toc":true,"pdfEngine":"xelatex"}「末」
<<<[END_TOOL_REQUEST]>>>
```

### 2. 批量转换

批量转换多个Markdown文件为HTML：

```
<<<[TOOL_REQUEST]>>>
maid:「始」Nova「末」,
tool_name:「始」PandocConverter「末」,
command:「始」BatchConvert「末」,
inputFiles:「始」["file:///C:/docs/chapter1.md", "file:///C:/docs/chapter2.md"]「末」,
outputFormat:「始」html「末」,
options:「始」{"title":"完整文档","toc":true}「末」,
preserveStructure:「始」true「末」
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

### 4. 格式检测

检测文件格式：

```
<<<[TOOL_REQUEST]>>>
maid:「始」Nova「末」,
tool_name:「始」PandocConverter「末」,
command:「始」DetectFormat「末」,
inputFile:「始」file:///C:/Users/用户名/docs/unknown_file「末」
<<<[END_TOOL_REQUEST]>>>
```

### 5. 获取支持格式

获取所有支持的格式：

```
<<<[TOOL_REQUEST]>>>
maid:「始」Nova「末」,
tool_name:「始」PandocConverter「末」,
command:「始」GetSupportedFormats「末」
<<<[END_TOOL_REQUEST]>>>
```

## 分布式环境使用

在分布式环境中，文件访问需要特殊处理：

### 使用file://协议

```
inputFile:「始」file:///C:/Users/用户名/docs/report.md「末」
```

### 使用ConvertFromContent命令

对于分布式环境，最可靠的方式是直接传递内容：

```
command:「始」ConvertFromContent「末」,
content:「始」# 文档内容...「末」,
inputFormat:「始」markdown「末」,
outputFormat:「始」pdf「末」
```

## 转换选项详解

### 基本文档选项

- `title`: 文档标题
- `author`: 文档作者
- `date`: 文档日期
- `keywords`: 文档关键词

### 格式选项

- `toc`: 是否生成目录（true/false）
- `tocDepth`: 目录深度（数字）
- `fontSize`: 字体大小（如"12pt"）
- `margin`: 页边距（如"1in"）
- `lineSpacing`: 行间距（如"1.5"）
- `columns`: 分栏数量（数字）
- `papersize`: 纸张大小（如"a4", "letter"）
- `landscape`: 是否横向（true/false）

### 样式选项

- `cssFile`: CSS样式文件路径
- `template`: 模板文件路径
- `highlightStyle`: 代码高亮样式
- `mathMethod`: 数学公式渲染方法

### 高级选项

- `enableRawHTML`: 是否允许原始HTML
- `preserveTabs`: 是否保留制表符
- `tabStop`: 制表符宽度
- `pdfEngine`: PDF生成引擎

## 常见转换场景

### 1. Markdown转PDF（中文支持）

```
<<<[TOOL_REQUEST]>>>
maid:「始」Nova「末」,
tool_name:「始」PandocConverter「末」,
command:「始」ConvertFile「末」,
inputFile:「始」file:///C:/docs/report.md「末」,
outputFormat:「始」pdf「末」,
options:「始」{"title":"技术报告","pdfEngine":"xelatex","fontSize":"12pt","margin":"1in"}「末」
<<<[END_TOOL_REQUEST]>>>
```

### 2. Markdown转HTML（带代码高亮）

```
<<<[TOOL_REQUEST]>>>
maid:「始」Nova「末」,
tool_name:「始」PandocConverter「末」,
command:「始」ConvertFile「末」,
inputFile:「始」file:///C:/docs/tutorial.md「末」,
outputFormat:「始」html「末」,
options:「始」{"title":"教程","highlightStyle":"github","cssFile":"./styles/custom.css"}「末」
<<<[END_TOOL_REQUEST]>>>
```

### 3. HTML转Word

```
<<<[TOOL_REQUEST]>>>
maid:「始」Nova「末」,
tool_name:「始」PandocConverter「末」,
command:「始」ConvertFile「末」,
inputFile:「始」https://example.com/page.html「末」,
outputFormat:「始」docx「末」,
options:「始」{"title":"网页文档","enableRawHTML":true}「末」
<<<[END_TOOL_REQUEST]>>>
```

### 4. LaTeX转PDF

```
<<<[TOOL_REQUEST]>>>
maid:「始」Nova「末」,
tool_name:「始」PandocConverter「末」,
command:「始」ConvertFile「末」,
inputFile:「始」file:///C:/docs/paper.tex「末」,
outputFormat:「始」pdf「末」,
options:「始」{"pdfEngine":"xelatex"}「末」
<<<[END_TOOL_REQUEST]>>>
```

## 故障排除

### 常见问题

1. **Pandoc不可用**
   - 确保已正确安装Pandoc
   - 检查PANDOC_PATH配置是否正确

2. **PDF生成失败**
   - 确保已安装LaTeX发行版（如TeX Live、MiKTeX）
   - 尝试使用不同的PDF引擎（pdflatex、xelatex、lualatex）

3. **中文显示问题**
   - 使用xelatex或lualatex作为PDF引擎
   - 确保系统已安装中文字体

4. **数学公式不显示**
   - 启用ENABLE_MATHJAX配置
   - 尝试不同的数学公式渲染方法

5. **分布式文件访问失败**
   - 使用file://协议指定完整路径
   - 优先使用ConvertFromContent命令

### 日志调试

启用调试模式：

1. 在config.env中设置 `DEBUG_MODE=true`
2. 检查插件输出的日志信息

## 性能优化

1. **批量处理**：使用BatchConvert命令一次性处理多个文件
2. **缓存利用**：启用临时文件缓存以提高重复转换的性能
3. **文件大小限制**：合理设置MAX_FILE_SIZE_MB以避免内存问题

## 扩展开发

如需扩展插件功能，可以：

1. 修改`pandoc_converter.py`中的转换逻辑
2. 添加新的命令和参数
3. 自定义模板和样式文件

## 许可证

本插件遵循MIT许可证。

## 贡献

欢迎提交Issue和Pull Request来改进此插件。

## 更新日志

### v1.0.0
- 初始版本发布
- 支持基本的文档格式转换
- 支持分布式文件访问
- 支持批量转换
- 支持多种自定义选项