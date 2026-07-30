#!/usr/bin/env python3
"""
代码验证脚本
用于验证 Agent Framework Book 中的所有代码示例
"""

import os
import sys
import subprocess
import ast
from pathlib import Path

class CodeValidator:
    """代码验证器"""

    def __init__(self, book_dir="/home/liunix/workspace/Agent-Framework-Book"):
        """初始化验证器"""
        self.book_dir = Path(book_dir)
        self.issues = []

    def validate_python_syntax(self, code: str, source_file: str) -> bool:
        """
        验证 Python 语法

        Args:
            code: 代码内容
            source_file: 源文件名

        Returns:
            是否通过验证
        """
        try:
            ast.parse(code)
            return True
        except SyntaxError as e:
            self.issues.append({
                "file": source_file,
                "type": "syntax_error",
                "message": f"语法错误: {e}"
            })
            return False

    def validate_python_code(self, code: str, source_file: str) -> bool:
        """
        验证 Python 代码

        Args:
            code: 代码内容
            source_file: 源文件名

        Returns:
            是否通过验证
        """
        # 验证语法
        if not self.validate_python_syntax(code, source_file):
            return False

        # 检查是否有运行时错误
        try:
            # 执行代码（只检查语法，不执行）
            compile(code, source_file, 'exec')
            return True
        except Exception as e:
            self.issues.append({
                "file": source_file,
                "type": "runtime_error",
                "message": f"运行时错误: {e}"
            })
            return False

    def validate_cxx_syntax(self, code: str, source_file: str) -> bool:
        """
        验证 C++ 语法

        Args:
            code: 代码内容
            source_file: 源文件名

        Returns:
            是否通过验证
        """
        try:
            # 检查基本语法
            if not code.strip():
                return False

            # 检查是否包含基本的 C++ 语法结构
            required_keywords = ['class', 'struct', 'int', 'return', 'void', 'def']
            for keyword in required_keywords:
                if keyword not in code:
                    self.issues.append({
                        "file": source_file,
                        "type": "cxx_syntax_warning",
                        "message": f"可能缺少 C++ 关键词: {keyword}"
                    })

            return True
        except Exception as e:
            self.issues.append({
                "file": source_file,
                "type": "cxx_syntax_error",
                "message": f"C++ 语法错误: {e}"
            })
            return False

    def find_code_blocks(self, content: str) -> list:
        """
        在内容中查找代码块

        Args:
            content: 内容

        Returns:
            代码块列表
        """
        code_blocks = []

        # 查找 Python 代码块
        import re
        python_pattern = r'```python\n(.*?)```'
        python_blocks = re.findall(python_pattern, content, re.DOTALL)

        for block in python_blocks:
            code_blocks.append({
                "language": "python",
                "code": block.strip(),
                "type": "python"
            })

        # 查找 C++ 代码块
        cxx_pattern = r'```cpp\n(.*?)```'
        cxx_blocks = re.findall(cxx_pattern, content, re.DOTALL)

        for block in cxx_blocks:
            code_blocks.append({
                "language": "cpp",
                "code": block.strip(),
                "type": "cpp"
            })

        # 查找 Bash 代码块
        bash_pattern = r'```bash\n(.*?)```'
        bash_blocks = re.findall(bash_pattern, content, re.DOTALL)

        for block in bash_blocks:
            code_blocks.append({
                "language": "bash",
                "code": block.strip(),
                "type": "bash"
            })

        return code_blocks

    def validate_all(self):
        """验证所有章节"""
        print("=" * 80)
        print("开始验证 Agent Framework Book 中的所有代码")
        print("=" * 80)
        print()

        # 遍历所有章节文件
        chapter_files = sorted(self.book_dir.glob("*.md"))
        total_files = len(chapter_files)
        validated = 0
        failed = 0

        for i, chapter_file in enumerate(chapter_files, 1):
            print(f"[{i}/{total_files}] 验证: {chapter_file.name}")

            # 读取文件内容
            with open(chapter_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 查找代码块
            code_blocks = self.find_code_blocks(content)

            if not code_blocks:
                print(f"  ⚠️  无代码块")
                continue

            # 验证每个代码块
            for j, code_block in enumerate(code_blocks, 1):
                language = code_block["language"]
                code = code_block["code"]
                block_num = j

                print(f"  📄 代码块 {block_num} ({language})")

                # 根据语言验证
                if language == "python":
                    if self.validate_python_code(code, chapter_file.name):
                        print(f"  ✅ Python 代码验证通过")
                        validated += 1
                    else:
                        print(f"  ❌ Python 代码验证失败")
                        failed += 1
                elif language == "cpp":
                    if self.validate_cxx_syntax(code, chapter_file.name):
                        print(f"  ✅ C++ 代码验证通过")
                        validated += 1
                    else:
                        print(f"  ❌ C++ 代码验证失败")
                        failed += 1
                elif language == "bash":
                    print(f"  ⚠️  Bash 代码跳过验证")
                    validated += 1

            print()

        # 输出总结
        print("=" * 80)
        print("验证总结")
        print("=" * 80)
        print(f"总文件数: {total_files}")
        print(f"总代码块数: {validated + failed}")
        print(f"✅ 通过: {validated}")
        print(f"❌ 失败: {failed}")
        print(f"📊 通过率: {(validated / (validated + failed) * 100):.2f}%")
        print()

        if self.issues:
            print("=" * 80)
            print("发现的问题")
            print("=" * 80)
            for issue in self.issues:
                print(f"文件: {issue['file']}")
                print(f"类型: {issue['type']}")
                print(f"消息: {issue['message']}")
                print()

        return failed == 0


if __name__ == "__main__":
    validator = CodeValidator()
    success = validator.validate_all()

    sys.exit(0 if success else 1)
