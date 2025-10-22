#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PandocConverter 插件安装脚本
用于检查依赖、配置环境并初始化插件
"""

import os
import sys
import subprocess
import json
import shutil
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    print("检查Python版本...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("✗ Python版本过低: {}.{}".format(version.major, version.minor))
        print("  需要Python 3.7或更高版本")
        return False
    else:
        print("✓ Python版本: {}.{}.{}".format(version.major, version.minor, version.micro))
        return True

def check_pandoc():
    """检查Pandoc是否安装"""
    print("\n检查Pandoc...")
    try:
        result = subprocess.run(
            ["pandoc", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print("✓ Pandoc已安装: {}".format(version_line))
            return True
        else:
            print("✗ Pandoc未正确安装")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("✗ Pandoc未安装或不在PATH中")
        print("  请从 https://pandoc.org/installing.html 下载安装")
        return False

def check_latex():
    """检查LaTeX发行版（PDF生成需要）"""
    print("\n检查LaTeX发行版...")
    engines = ["xelatex", "pdflatex", "lualatex"]
    found_engines = []
    
    for engine in engines:
        try:
            result = subprocess.run(
                [engine, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                found_engines.append(engine)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
    
    if found_engines:
        print("✓ 找到LaTeX引擎: {}".format(', '.join(found_engines)))
        return True
    else:
        print("⚠ 未找到LaTeX引擎，PDF生成功能可能不可用")
        print("  建议安装TeX Live、MiKTeX或其他LaTeX发行版")
        return False

def create_config():
    """创建配置文件"""
    print("\n创建配置文件...")
    
    config_file = "config.env"
    config_example = "config.env.example"
    
    if os.path.exists(config_file):
        try:
            overwrite = input("  {} 已存在，是否覆盖? (y/N): ".format(config_file)).strip().lower()
            if overwrite != 'y':
                print("  跳过配置文件创建")
                return True
        except:
            # 在非交互环境中，默认不覆盖
            print("  跳过配置文件创建（非交互环境）")
            return True
    
    if os.path.exists(config_example):
        try:
            shutil.copy(config_example, config_file)
            print("✓ 已从 {} 创建 {}".format(config_example, config_file))
            return True
        except Exception as e:
            print("✗ 创建配置文件失败: {}".format(str(e)))
            return False
    else:
        print("✗ 配置示例文件 {} 不存在".format(config_example))
        return False

def create_directories():
    """创建必要的目录"""
    print("\n创建目录...")
    
    directories = ["outputs", "temp", "logs"]
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            print("✓ 创建目录: {}".format(directory))
        except Exception as e:
            print("✗ 创建目录 {} 失败: {}".format(directory, str(e)))
            return False
    
    return True

def run_tests():
    """运行测试"""
    print("\n运行插件测试...")
    
    test_file = "test_plugin.py"
    
    if not os.path.exists(test_file):
        print("✗ 测试文件 {} 不存在".format(test_file))
        return False
    
    try:
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            print("✓ 所有测试通过")
            return True
        else:
            print("✗ 部分测试失败")
            print(result.stdout)
            return False
    except subprocess.TimeoutExpired:
        print("✗ 测试超时")
        return False
    except Exception as e:
        print("✗ 运行测试失败: {}".format(str(e)))
        return False

def print_usage_info():
    """打印使用信息"""
    print("\n" + "="*50)
    print("安装完成！")
    print("="*50)
    print("\n使用说明:")
    print("1. 确保分布式服务器已启动")
    print("2. 插件将自动注册到VCP系统")
    print("3. AI可以使用以下命令调用插件:")
    print("   - ConvertFile: 转换单个文件")
    print("   - BatchConvert: 批量转换文件")
    print("   - ConvertFromContent: 从内容转换")
    print("   - DetectFormat: 检测文件格式")
    print("   - GetSupportedFormats: 获取支持格式")
    print("\n配置文件: config.env")
    print("输出目录: outputs/")
    print("临时文件: temp/")
    print("\n更多信息请参考 README.md")

def main():
    """主函数"""
    print("PandocConverter 插件安装程序")
    print("="*50)
    
    # 检查Python版本
    if not check_python_version():
        return 1
    
    # 检查Pandoc
    if not check_pandoc():
        return 1
    
    # 检查LaTeX（可选）
    check_latex()
    
    # 创建配置文件
    if not create_config():
        return 1
    
    # 创建目录
    if not create_directories():
        return 1
    
    # 运行测试
    try:
        run_test = input("\n是否运行插件测试? (Y/n): ").strip().lower()
        if run_test != 'n':
            if not run_tests():
                print("⚠ 测试未完全通过，插件可能无法正常工作")
    except:
        # 在非交互环境中，默认不运行测试
        print("\n跳过测试（非交互环境）")
    
    # 打印使用信息
    print_usage_info()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())