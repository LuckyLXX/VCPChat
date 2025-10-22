#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PandocConverter - 强大的文档格式转换插件
支持Markdown与多种格式的双向转换，保留代码高亮、数学公式、表格和图片等元素
"""

import sys
import json
import os
import subprocess
import tempfile
import shutil
import logging
import mimetypes
import urllib.parse
import urllib.request
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PandocConverter:
    """Pandoc文档转换器主类"""
    
    def __init__(self):
        """初始化转换器，读取配置"""
        self.config = self._load_config()
        self.temp_files = []  # 跟踪临时文件以便清理
        
    def _load_config(self) -> Dict[str, Any]:
        """从环境变量加载配置"""
        config = {
            'pandoc_path': os.getenv('PANDOC_PATH', 'pandoc'),
            'output_dir': os.getenv('OUTPUT_DIR', './outputs'),
            'temp_dir': os.getenv('TEMP_DIR', './temp'),
            'enable_mathjax': os.getenv('ENABLE_MATHJAX', 'true').lower() == 'true',
            'enable_syntax_highlighting': os.getenv('ENABLE_SYNTAX_HIGHLIGHTING', 'true').lower() == 'true',
            'default_pdf_engine': os.getenv('DEFAULT_PDF_ENGINE', 'xelatex'),
            'cleanup_temp_files': os.getenv('CLEANUP_TEMP_FILES', 'true').lower() == 'true',
            'max_file_size_mb': int(os.getenv('MAX_FILE_SIZE_MB', '50'))
        }
        
        # 确保目录存在
        os.makedirs(config['output_dir'], exist_ok=True)
        os.makedirs(config['temp_dir'], exist_ok=True)
        
        return config
    
    def _check_pandoc_availability(self) -> Tuple[bool, str]:
        """检查Pandoc是否可用"""
        try:
            result = subprocess.run(
                [self.config['pandoc_path'], '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                version_info = result.stdout.split('\n')[0]
                return True, version_info
            else:
                return False, "Pandoc执行失败"
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            return False, f"Pandoc不可用: {str(e)}"
    
    def _detect_file_format(self, file_path: str) -> Optional[str]:
        """检测文件格式"""
        # 首先从文件扩展名判断
        ext = Path(file_path).suffix.lower()
        format_map = {
            '.md': 'markdown',
            '.markdown': 'markdown',
            '.html': 'html',
            '.htm': 'html',
            '.pdf': 'pdf',
            '.docx': 'docx',
            '.doc': 'doc',
            '.tex': 'latex',
            '.latex': 'latex',
            '.rst': 'rst',
            '.rest': 'rst',
            '.epub': 'epub',
            '.txt': 'plain',
            '.text': 'plain',
            '.rtf': 'rtf',
            '.odt': 'odt',
            '.org': 'org',
            '.wiki': 'mediawiki',
            '.ipynb': 'ipynb',
            '.csv': 'csv',
            '.json': 'json',
            '.xml': 'xml'
        }
        
        if ext in format_map:
            return format_map[ext]
        
        # 如果扩展名不明确，尝试使用mimetypes
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type:
            mime_format_map = {
                'text/html': 'html',
                'text/markdown': 'markdown',
                'text/plain': 'plain',
                'application/pdf': 'pdf',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
                'application/msword': 'doc',
                'application/x-latex': 'latex',
                'text/x-rst': 'rst',
                'application/epub+zip': 'epub',
                'text/rtf': 'rtf',
                'application/vnd.oasis.opendocument.text': 'odt'
            }
            if mime_type in mime_format_map:
                return mime_format_map[mime_type]
        
        return None
    
    def _download_file(self, url: str) -> str:
        """下载文件到临时目录"""
        try:
            parsed_url = urllib.parse.urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                raise ValueError("无效的URL")
            
            # 生成临时文件名
            filename = os.path.basename(parsed_url.path) or f"download_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            temp_path = os.path.join(self.config['temp_dir'], filename)
            
            # 下载文件
            urllib.request.urlretrieve(url, temp_path)
            self.temp_files.append(temp_path)
            logger.info(f"文件下载成功: {url} -> {temp_path}")
            return temp_path
            
        except Exception as e:
            raise RuntimeError(f"下载文件失败 {url}: {str(e)}")
    
    def _prepare_input_file(self, input_file: str) -> str:
        """准备输入文件，处理URL、本地文件和分布式文件"""
        if input_file.startswith(('http://', 'https://')):
            return self._download_file(input_file)
        elif input_file.startswith('file://'):
            # 处理file://协议的分布式文件
            return self._handle_distributed_file(input_file)
        else:
            # 处理本地文件路径
            if not os.path.exists(input_file):
                # 如果本地文件不存在，抛出特殊错误让FileFetcherServer处理
                error = FileNotFoundError(f"本地文件未找到: {input_file}")
                error.code = 'FILE_NOT_FOUND_LOCALLY'
                error.fileUrl = f"file://{os.path.abspath(input_file)}"
                raise error
            
            # 检查文件大小
            file_size_mb = os.path.getsize(input_file) / (1024 * 1024)
            if file_size_mb > self.config['max_file_size_mb']:
                raise ValueError(f"文件大小超过限制: {file_size_mb:.2f}MB > {self.config['max_file_size_mb']}MB")
            
            return input_file
    
    def _handle_distributed_file(self, file_url: str) -> str:
        """处理分布式文件（file://协议）"""
        try:
            # 转换file://为本地路径
            parsed_url = urllib.parse.urlparse(file_url)
            local_path = parsed_url.path
            
            # 在Windows上需要处理路径格式
            if os.name == 'nt' and local_path.startswith('/'):
                local_path = local_path[1:].replace('/', '\\')
            
            # 检查文件是否存在
            if os.path.exists(local_path):
                return local_path
            else:
                # 文件不存在，抛出特殊错误
                error = FileNotFoundError(f"分布式文件未找到: {file_url}")
                error.code = 'FILE_NOT_FOUND_LOCALLY'
                error.fileUrl = file_url
                raise error
            
        except Exception as e:
            if isinstance(e, FileNotFoundError):
                raise
            else:
                raise RuntimeError(f"处理分布式文件失败 {file_url}: {str(e)}")
    
    def _build_pandoc_command(self, input_file: str, output_file: str, 
                            input_format: Optional[str], output_format: str,
                            options: Dict[str, Any]) -> List[str]:
        """构建Pandoc命令"""
        cmd = [self.config['pandoc_path']]
        
        # 输入文件
        cmd.append(input_file)
        
        # 输出文件
        cmd.append('-o')
        cmd.append(output_file)
        
        # 输入格式
        if input_format:
            cmd.extend(['-f', input_format])
        
        # 输出格式
        cmd.extend(['-t', output_format])
        
        # 处理选项
        if options.get('title'):
            cmd.extend(['--metadata', f"title={options['title']}"])
        
        if options.get('author'):
            cmd.extend(['--metadata', f"author={options['author']}"])
        
        if options.get('cssFile'):
            cmd.extend(['--css', options['cssFile']])
        
        if options.get('template'):
            cmd.extend(['--template', options['template']])
        
        if options.get('toc', False):
            cmd.append('--toc')
            if options.get('tocDepth'):
                cmd.extend(['--toc-depth', str(options['tocDepth'])])
        
        if self.config['enable_syntax_highlighting'] and options.get('highlightStyle'):
            cmd.extend(['--highlight-style', options['highlightStyle']])
        elif self.config['enable_syntax_highlighting']:
            cmd.extend(['--highlight-style', 'pygments'])
        
        if options.get('mathMethod'):
            math_options = {
                'mathjax': ['--webtex'],
                'katex': ['--katex'],
                'webtex': ['--webtex'],
                'mathml': ['--mathml'],
                'latex': ['--latexmathml']
            }
            if options['mathMethod'] in math_options:
                cmd.extend(math_options[options['mathMethod']])
        elif self.config['enable_mathjax']:
            cmd.extend(['--webtex'])
        
        if output_format == 'pdf':
            pdf_engine = options.get('pdfEngine', self.config['default_pdf_engine'])
            cmd.extend(['--pdf-engine', pdf_engine])
        
        if options.get('fontSize'):
            cmd.extend(['--variable', f"fontsize={options['fontSize']}"])
        
        if options.get('margin'):
            cmd.extend(['--variable', f"geometry:margin={options['margin']}"])
        
        if options.get('lineSpacing'):
            cmd.extend(['--variable', f"linespread={options['lineSpacing']}"])
        
        if options.get('columns', 1) > 1:
            cmd.extend(['--variable', f"columns={options['columns']}"])
        
        if options.get('papersize'):
            cmd.extend(['--variable', f"papersize={options['papersize']}"])
        
        if options.get('landscape', False):
            cmd.append('--variable=landscape')
        
        if not options.get('enableRawHTML', True):
            cmd.append('--raw-html')
        
        if options.get('preserveTabs', False):
            cmd.append('--preserve-tabs')
            if options.get('tabStop'):
                cmd.extend(['--tab-stop', str(options['tabStop'])])
        
        # 添加自变量
        cmd.extend(['--standalone'])
        
        return cmd
    
    def _generate_output_filename(self, input_file: str, output_format: str, 
                                 output_dir: Optional[str] = None) -> str:
        """生成输出文件名"""
        input_path = Path(input_file)
        output_dir = output_dir or self.config['output_dir']
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成文件名
        base_name = input_path.stem
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 根据输出格式确定扩展名
        ext_map = {
            'html': 'html',
            'pdf': 'pdf',
            'docx': 'docx',
            'latex': 'tex',
            'rst': 'rst',
            'epub': 'epub',
            'txt': 'txt',
            'plain': 'txt',
            'rtf': 'rtf',
            'odt': 'odt',
            'json': 'json',
            'xml': 'xml'
        }
        
        ext = ext_map.get(output_format, output_format)
        filename = f"{base_name}_converted_{timestamp}.{ext}"
        
        return os.path.join(output_dir, filename)
    
    def convert_file(self, input_file: str, output_format: str, 
                    input_format: Optional[str] = None,
                    output_file: Optional[str] = None,
                    options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """转换单个文件"""
        try:
            # 准备选项
            options = options or {}
            
            # 准备输入文件
            actual_input_file = self._prepare_input_file(input_file)
            
            # 检测输入格式
            if not input_format:
                input_format = self._detect_file_format(actual_input_file)
                if not input_format:
                    raise ValueError("无法检测输入文件格式，请手动指定")
            
            # 生成输出文件路径
            if not output_file:
                output_file = self._generate_output_filename(actual_input_file, output_format)
            
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            # 构建命令
            cmd = self._build_pandoc_command(
                actual_input_file, output_file, input_format, output_format, options
            )
            
            # 执行转换
            logger.info(f"开始转换: {actual_input_file} -> {output_file}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )
            
            if result.returncode != 0:
                error_msg = result.stderr or result.stdout
                raise RuntimeError(f"Pandoc转换失败: {error_msg}")
            
            # 检查输出文件
            if not os.path.exists(output_file):
                raise RuntimeError("转换完成但输出文件不存在")
            
            # 获取文件信息
            file_size = os.path.getsize(output_file)
            abs_path = os.path.abspath(output_file)
            
            logger.info(f"转换成功: {output_file} ({file_size} bytes)")
            
            return {
                'success': True,
                'input_file': actual_input_file,
                'output_file': output_file,
                'absolute_path': abs_path,
                'file_size': file_size,
                'input_format': input_format,
                'output_format': output_format,
                'options_used': options
            }
            
        except Exception as e:
            logger.error(f"文件转换失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'input_file': input_file,
                'output_format': output_format
            }
    
    def batch_convert(self, input_files: List[str], output_format: str,
                     input_format: Optional[str] = None,
                     output_dir: Optional[str] = None,
                     options: Optional[Dict[str, Any]] = None,
                     preserve_structure: bool = False) -> Dict[str, Any]:
        """批量转换文件"""
        results = []
        success_count = 0
        error_count = 0
        
        try:
            options = options or {}
            
            for i, input_file in enumerate(input_files):
                try:
                    # 如果保持目录结构，调整输出路径
                    current_output_file = None
                    if preserve_structure and output_dir:
                        input_path = Path(input_file)
                        relative_path = input_path.parent.name if input_path.parent else '.'
                        specific_output_dir = os.path.join(output_dir, relative_path)
                        os.makedirs(specific_output_dir, exist_ok=True)
                        current_output_file = self._generate_output_filename(
                            input_file, output_format, specific_output_dir
                        )
                    
                    # 转换单个文件
                    result = self.convert_file(
                        input_file=input_file,
                        output_format=output_format,
                        input_format=input_format,
                        output_file=current_output_file,
                        options=options
                    )
                    
                    if result['success']:
                        success_count += 1
                    else:
                        error_count += 1
                    
                    results.append(result)
                    
                except Exception as e:
                    error_count += 1
                    results.append({
                        'success': False,
                        'error': str(e),
                        'input_file': input_file,
                        'output_format': output_format
                    })
            
            return {
                'success': error_count == 0,
                'total_files': len(input_files),
                'success_count': success_count,
                'error_count': error_count,
                'results': results,
                'output_format': output_format,
                'preserve_structure': preserve_structure
            }
            
        except Exception as e:
            logger.error(f"批量转换失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'total_files': len(input_files),
                'success_count': success_count,
                'error_count': error_count,
                'results': results
            }
    
    def convert_from_content(self, content: str, input_format: str, 
                           output_format: str, options: Optional[Dict[str, Any]] = None,
                           output_file: Optional[str] = None) -> Dict[str, Any]:
        """从文本内容进行转换"""
        try:
            # 创建临时输入文件
            with tempfile.NamedTemporaryFile(
                mode='w', 
                suffix=self._get_file_extension(input_format),
                dir=self.config['temp_dir'],
                delete=False,
                encoding='utf-8'
            ) as temp_file:
                temp_file.write(content)
                temp_input_file = temp_file.name
            
            self.temp_files.append(temp_input_file)
            
            # 转换文件
            result = self.convert_file(
                input_file=temp_input_file,
                output_format=output_format,
                input_format=input_format,
                output_file=output_file,
                options=options
            )
            
            # 如果成功，读取输出文件内容（如果是文本格式）
            if result['success'] and output_format in ['html', 'txt', 'plain', 'rst', 'markdown', 'json', 'xml']:
                try:
                    with open(result['output_file'], 'r', encoding='utf-8') as f:
                        result['output_content'] = f.read()
                except Exception as e:
                    logger.warning(f"读取输出文件内容失败: {str(e)}")
            
            return result
            
        except Exception as e:
            logger.error(f"内容转换失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'input_format': input_format,
                'output_format': output_format
            }
    
    def _get_file_extension(self, format_name: str) -> str:
        """根据格式名获取文件扩展名"""
        ext_map = {
            'markdown': '.md',
            'html': '.html',
            'plain': '.txt',
            'txt': '.txt',
            'latex': '.tex',
            'rst': '.rst',
            'json': '.json',
            'xml': '.xml'
        }
        return ext_map.get(format_name, '.txt')
    
    def get_supported_formats(self) -> Dict[str, Any]:
        """获取支持的格式列表"""
        try:
            # 调用pandoc --list-input-formats和--list-output-formats
            input_result = subprocess.run(
                [self.config['pandoc_path'], '--list-input-formats'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            output_result = subprocess.run(
                [self.config['pandoc_path'], '--list-output-formats'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            input_formats = []
            output_formats = []
            
            if input_result.returncode == 0:
                input_formats = [line.strip() for line in input_result.stdout.split('\n') if line.strip()]
            
            if output_result.returncode == 0:
                output_formats = [line.strip() for line in output_result.stdout.split('\n') if line.strip()]
            
            return {
                'success': True,
                'input_formats': input_formats,
                'output_formats': output_formats,
                'common_formats': {
                    'markdown': 'markdown',
                    'html': 'html',
                    'pdf': 'pdf',
                    'docx': 'docx',
                    'latex': 'latex',
                    'rst': 'rst',
                    'epub': 'epub',
                    'txt': 'plain',
                    'rtf': 'rtf',
                    'odt': 'odt'
                }
            }
            
        except Exception as e:
            logger.error(f"获取支持格式失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'common_formats': {
                    'markdown': 'markdown',
                    'html': 'html',
                    'pdf': 'pdf',
                    'docx': 'docx',
                    'latex': 'latex',
                    'rst': 'rst',
                    'epub': 'epub',
                    'txt': 'plain',
                    'rtf': 'rtf',
                    'odt': 'odt'
                }
            }
    
    def detect_format(self, file_path: str) -> Dict[str, Any]:
        """检测文件格式"""
        try:
            # 准备文件
            actual_file_path = self._prepare_input_file(file_path)
            
            # 检测格式
            detected_format = self._detect_file_format(actual_file_path)
            
            if detected_format:
                return {
                    'success': True,
                    'file_path': actual_file_path,
                    'detected_format': detected_format,
                    'file_extension': Path(actual_file_path).suffix,
                    'file_size': os.path.getsize(actual_file_path)
                }
            else:
                return {
                    'success': False,
                    'error': '无法检测文件格式',
                    'file_path': actual_file_path,
                    'file_extension': Path(actual_file_path).suffix
                }
                
        except Exception as e:
            logger.error(f"格式检测失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'file_path': file_path
            }
    
    def cleanup(self):
        """清理临时文件"""
        if self.config['cleanup_temp_files']:
            for temp_file in self.temp_files:
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                        logger.debug(f"清理临时文件: {temp_file}")
                except Exception as e:
                    logger.warning(f"清理临时文件失败 {temp_file}: {str(e)}")
            self.temp_files.clear()

def main():
    """主函数"""
    converter = None
    
    try:
        # 读取输入
        input_data = sys.stdin.readline().strip()
        if not input_data:
            raise ValueError("未收到输入数据")
        
        # 解析JSON
        try:
            params = json.loads(input_data)
        except json.JSONDecodeError:
            raise ValueError("输入数据格式无效")
        
        # 检查必要参数
        if 'command' not in params:
            raise ValueError("缺少必要参数: command")
        
        command = params['command']
        
        # 初始化转换器
        converter = PandocConverter()
        
        # 检查Pandoc可用性
        pandoc_ok, pandoc_info = converter._check_pandoc_availability()
        if not pandoc_ok:
            raise RuntimeError(f"Pandoc不可用: {pandoc_info}")
        
        logger.info(f"Pandoc可用: {pandoc_info}")
        
        result = None
        
        # 执行命令时需要处理分布式文件错误
        try:
            if command == 'ConvertFile':
                # 单文件转换
                required_params = ['inputFile', 'outputFormat']
                for param in required_params:
                    if param not in params:
                        raise ValueError(f"ConvertFile需要{param}参数")
                
                result = converter.convert_file(
                    input_file=params['inputFile'],
                    output_format=params['outputFormat'],
                    input_format=params.get('inputFormat'),
                    output_file=params.get('outputFile'),
                    options=params.get('options')
                )
                
            elif command == 'BatchConvert':
                # 批量转换
                required_params = ['inputFiles', 'outputFormat']
                for param in required_params:
                    if param not in params:
                        raise ValueError(f"BatchConvert需要{param}参数")
                
                input_files = params['inputFiles']
                if isinstance(input_files, str):
                    try:
                        input_files = json.loads(input_files)
                    except json.JSONDecodeError:
                        raise ValueError("inputFiles参数必须是有效的JSON数组")
                
                result = converter.batch_convert(
                    input_files=input_files,
                    output_format=params['outputFormat'],
                    input_format=params.get('inputFormat'),
                    output_dir=params.get('outputDir'),
                    options=params.get('options'),
                    preserve_structure=params.get('preserveStructure', False)
                )
                
            elif command == 'ConvertFromContent':
                # 从内容转换
                required_params = ['content', 'inputFormat', 'outputFormat']
                for param in required_params:
                    if param not in params:
                        raise ValueError(f"ConvertFromContent需要{param}参数")
                
                result = converter.convert_from_content(
                    content=params['content'],
                    input_format=params['inputFormat'],
                    output_format=params['outputFormat'],
                    options=params.get('options'),
                    output_file=params.get('outputFile')
                )
                
            elif command == 'DetectFormat':
                # 检测格式
                if 'inputFile' not in params:
                    raise ValueError("DetectFormat需要inputFile参数")
                
                result = converter.detect_format(params['inputFile'])
                
            elif command == 'GetSupportedFormats':
                # 获取支持格式
                result = converter.get_supported_formats()
                
            else:
                raise ValueError(f"不支持的命令: {command}")
        
        except Exception as e:
            # 检查是否是分布式文件未找到错误
            if hasattr(e, 'code') and e.code == 'FILE_NOT_FOUND_LOCALLY':
                # 返回特殊错误结构，让主服务器处理文件获取
                error_response = {
                    "status": "error",
                    "code": "FILE_NOT_FOUND_LOCALLY",
                    "error": str(e),
                    "fileUrl": e.fileUrl
                }
                print(json.dumps(error_response, ensure_ascii=False))
                sys.exit(1)
            else:
                # 其他错误正常处理
                raise
        
        # 构建响应
        if result.get('success', False):
            response = {
                "status": "success",
                "result": result
            }
        else:
            response = {
                "status": "error",
                "error": result.get('error', '未知错误'),
                "details": result
            }
        
        # 输出结果
        print(json.dumps(response, ensure_ascii=False, indent=2))
        
    except Exception as e:
        # 输出错误
        logger.error(f"执行失败: {str(e)}")
        print(json.dumps({
            "status": "error",
            "error": str(e)
        }, ensure_ascii=False))
        sys.exit(1)
    
    finally:
        # 清理资源
        if converter:
            converter.cleanup()

if __name__ == "__main__":
    main()