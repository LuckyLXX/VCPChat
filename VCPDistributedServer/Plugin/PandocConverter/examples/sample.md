# PandocConverter 示例文档

这是一个用于测试 PandocConverter 插件功能的示例文档。

## 目录

- [基本格式](#基本格式)
- [代码高亮](#代码高亮)
- [数学公式](#数学公式)
- [表格](#表格)
- [引用](#引用)
- [列表](#列表)

## 基本格式

这里展示了一些基本的文本格式：

- **粗体文本**
- *斜体文本*
- ***粗斜体文本***
- ~~删除线文本~~
- `行内代码`

这是一个[链接](https://pandoc.org)示例。

## 代码高亮

### Python 示例

```python
def fibonacci(n):
    """计算斐波那契数列"""
    if n <= 1:
        return n
    else:
        return fibonacci(n-1) + fibonacci(n-2)

# 测试
for i in range(10):
    print(f"F({i}) = {fibonacci(i)}")
```

### JavaScript 示例

```javascript
// 计算阶乘
function factorial(n) {
    if (n === 0 || n === 1) {
        return 1;
    } else {
        return n * factorial(n - 1);
    }
}

// 测试
for (let i = 1; i <= 10; i++) {
    console.log(`${i}! = ${factorial(i)}`);
}
```

## 数学公式

### 行内公式

爱因斯坦质能方程：$E = mc^2$

二次方程求根公式：$x = \frac{-b \pm \sqrt{b^2-4ac}}{2a}$

### 块级公式

#### 高斯积分

$$\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}$$

#### 欧拉恒等式

$$e^{i\pi} + 1 = 0$$

#### 泰勒级数

$$f(x) = \sum_{n=0}^{\infty} \frac{f^{(n)}(a)}{n!}(x-a)^n$$

## 表格

### 学生成绩表

| 姓名 | 语文 | 数学 | 英语 | 总分 |
|------|------|------|------|------|
| 张三 | 85 | 92 | 78 | 255 |
| 李四 | 90 | 88 | 95 | 273 |
| 王五 | 78 | 85 | 82 | 245 |

### 技术对比

| 特性 | Markdown | HTML | LaTeX |
|------|----------|------|-------|
| 易学性 | 高 | 中 | 低 |
| 表现力 | 中 | 高 | 高 |
| 适用场景 | 文档 | 网页 | 论文 |

## 引用

> 这是一个引用示例。
> 
> 引用可以包含多个段落，
> 甚至包含其他格式如**粗体**和`代码`。

> — 作者，来源

## 列表

### 无序列表

- 第一项
- 第二项
  - 子项 1
  - 子项 2
- 第三项

### 有序列表

1. 第一步
2. 第二步
   1. 子步骤 1
   2. 子步骤 2
3. 第三步

### 任务列表

- [x] 已完成任务
- [ ] 待完成任务
- [ ] 另一个待完成任务

## 图片

![示例图片](https://via.placeholder.com/300x200/4287f5/ffffff?text=示例图片)

## 分隔线

---

## 脚注

这里有一个脚注的示例[^1]。

[^1]: 这是脚注的内容。

## 总结

这个示例文档展示了 Pandoc 支持的各种格式和元素。使用 PandocConverter 插件，可以将此文档转换为多种其他格式，如 HTML、PDF、Word 等。

转换命令示例：

```bash
# 转换为 HTML
pandoc sample.md -o sample.html

# 转换为 PDF
pandoc sample.md -o sample.pdf --pdf-engine=xelatex

# 转换为 Word
pandoc sample.md -o sample.docx