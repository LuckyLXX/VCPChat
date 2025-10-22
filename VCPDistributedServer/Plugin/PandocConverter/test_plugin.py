#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PandocConverter 插件测试脚本
用于验证插件的各项功能是否正常工作
"""

import json
import os
import subprocess
import tempfile
import sys
from pathlib import Path

def run_plugin_command(command_data):
    """运行插件命令并返回结果"""
    try:
        # 将命令数据转换为JSON字符串
        command_json = json.dumps(command_data, ensure_ascii=False)
        
        # 运行插件脚本
        result = subprocess.run(
            [sys.executable, "pandoc_converter.py"],
            input=command_json,
            text=True,
            capture_output=True,
            timeout=60
        )
        
        # 解析输出
        try:
            output = json.loads(result.stdout)
        except json.JSONDecodeError:
            output = {
                "status": "error",
                "error": "插件输出格式无效",
                "raw_output": result.stdout
            }
        
        # 如果有错误输出，添加到结果中
        if result.stderr:
            output["stderr"] = result.stderr
        
        return output
        
    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "error": "插件执行超时"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"执行插件命令时发生错误: {str(e)}"
        }

def test_get_supported_formats():
    """测试获取支持格式命令"""
    print("测试获取支持格式...")
    
    command = {
        "command": "GetSupportedFormats"
    }
    
    result = run_plugin_command(command)
    
    if result.get("status") == "success":
        print("✓ 获取支持格式成功")
        formats = result.get("result", {})
        print(f"  输入格式数量: {len(formats.get('input_formats', []))}")
        print(f"  输出格式数量: {len(formats.get('output_formats', []))}")
        return True
    else:
        print(f"✗ 获取支持格式失败: {result.get('error')}")
        return False

def test_detect_format():
    """测试格式检测命令"""
    print("\n测试格式检测...")
    
    # 创建临时Markdown文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as temp_file:
        temp_file.write("# 测试文档\n\n这是一个测试文档。")
        temp_file_path = temp_file.name
    
    try:
        command = {
            "command": "DetectFormat",
            "inputFile": temp_file_path
        }
        
        result = run_plugin_command(command)
        
        if result.get("status") == "success":
            print("✓ 格式检测成功")
            detected_format = result.get("result", {}).get("detected_format")
            print(f"  检测到的格式: {detected_format}")
            return True
        else:
            print(f"✗ 格式检测失败: {result.get('error')}")
            return False
    finally:
        # 清理临时文件
        try:
            os.unlink(temp_file_path)
        except:
            pass

def test_convert_from_content():
    """测试从内容转换命令"""
    print("\n测试从内容转换...")
    
    command = {
        "command": "ConvertFromContent",
        "content": "# 测试文档\n\n这是一个**Markdown**测试文档。\n\n## 代码示例\n\n```python\nprint('Hello, World!')\n``",
        "inputFormat": "markdown",
        "outputFormat": "html",
        "options": {
            "title": "测试文档",
            "toc": True
        }
    }
    
    result = run_plugin_command(command)
    
    if result.get("status") == "success":
        print("✓ 从内容转换成功")
        output_file = result.get("result", {}).get("output_file")
        print(f"  输出文件: {output_file}")
        
        # 检查输出文件是否存在
        if os.path.exists(output_file):
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if "测试文档" in content and "Hello, World!" in content:
                    print("  输出文件内容验证成功")
                    return True
                else:
                    print("✗ 输出文件内容验证失败")
                    return False
        else:
            print("✗ 输出文件不存在")
            return False
    else:
        print(f"✗ 从内容转换失败: {result.get('error')}")
        return False

def test_convert_file():
    """测试文件转换命令"""
    print("\n测试文件转换...")
    
    # 创建临时Markdown文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as temp_file:
        temp_file.write("# 数学公式测试\n\n当 $a \\ne 0$ 时，方程 $ax^2 + bx + c = 0$ 的解为：\n\n$$x = {-b \\pm \\sqrt{b^2-4ac} \\over 2a}$$")
        temp_file_path = temp_file.name
    
    try:
        command = {
            "command": "ConvertFile",
            "inputFile": temp_file_path,
            "outputFormat": "html",
            "options": {
                "title": "数学公式测试",
                "mathMethod": "mathjax"
            }
        }
        
        result = run_plugin_command(command)
        
        if result.get("status") == "success":
            print("✓ 文件转换成功")
            output_file = result.get("result", {}).get("output_file")
            print(f"  输出文件: {output_file}")
            
            # 检查输出文件是否存在
            if os.path.exists(output_file):
                with open(output_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if "数学公式测试" in content:
                        print("  输出文件内容验证成功")
                        return True
                    else:
                        print("✗ 输出文件内容验证失败")
                        return False
            else:
                print("✗ 输出文件不存在")
                return False
        else:
            print(f"✗ 文件转换失败: {result.get('error')}")
            return False
    finally:
        # 清理临时文件
        try:
            os.unlink(temp_file_path)
        except:
            pass

def test_batch_convert():
    """测试批量转换命令"""
    print("\n测试批量转换...")
    
    # 创建临时文件
    temp_files = []
    try:
        for i in range(2):
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as temp_file:
                temp_file.write(f"# 章节 {i+1}\n\n这是第 {i+1} 章的内容。")
                temp_files.append(temp_file.name)
        
        command = {
            "command": "BatchConvert",
            "inputFiles": temp_files,
            "outputFormat": "html",
            "options": {
                "title": "测试文档集"
            }
        }
        
        result = run_plugin_command(command)
        
        if result.get("status") == "success":
            print("✓ 批量转换成功")
            batch_result = result.get("result", {})
            success_count = batch_result.get("success_count", 0)
            total_files = batch_result.get("total_files", 0)
            print(f"  成功转换: {success_count}/{total_files}")
            
            if success_count == total_files:
                return True
            else:
                print("✗ 部分文件转换失败")
                return False
        else:
            print(f"✗ 批量转换失败: {result.get('error')}")
            return False
    finally:
        # 清理临时文件
        for temp_file in temp_files:
            try:
                os.unlink(temp_file)
            except:
                pass

def main():
    """主函数"""
    print("PandocConverter 插件测试开始...\n")
    
    # 检查当前目录
    if not os.path.exists("pandoc_converter.py"):
        print("错误: 未找到 pandoc_converter.py 文件，请在插件目录中运行此测试脚本")
        return 1
    
    # 运行测试
    tests = [
        test_get_supported_formats,
        test_detect_format,
        test_convert_from_content,
        test_convert_file,
        test_batch_convert
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ 测试执行异常: {str(e)}")
    
    print(f"\n测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("✓ 所有测试通过，插件功能正常")
        return 0
    else:
        print("✗ 部分测试失败，请检查插件配置和依赖")
        return 1

if __name__ == "__main__":
    sys.exit(main())