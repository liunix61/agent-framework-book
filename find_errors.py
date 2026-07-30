#!/usr/bin/env python3
"""
查找代码错误
"""

import re

# 读取文件
with open('/home/liunix/workspace/Agent-Framework-Book/04-chapter4-prompt-engineering.md', 'r', encoding='utf-8') as f:
    content = f.read()

# 查找所有 Python 代码块
python_blocks = re.findall(r'```python\n(.*?)```', content, re.DOTALL)

# 查找包含 "def.*await" 的代码块
for i, block in enumerate(python_blocks):
    if 'def' in block and 'await' in block:
        lines = block.split('\n')
        for j, line in enumerate(lines):
            if 'def' in line and 'await' in line:
                print(f"代码块 {i+1}, 行 {j+1}:")
                print(line)
                print()

# 查找包含 "await" 在非 async 函数中的代码
print("\n" + "=" * 80)
print("查找 await 在非 async 函数中的使用")
print("=" * 80)

for i, block in enumerate(python_blocks):
    lines = block.split('\n')

    # 找到所有 async 函数定义
    async_functions = set()
    for j, line in enumerate(lines):
        if re.search(r'def\s+\w+\(.*\):\s*$', line):
            # 检查前面几行是否有 async
            func_start = max(0, j - 10)
            func_section = '\n'.join(lines[func_start:j+1])
            if 'async' in func_section:
                # 提取函数名
                func_match = re.search(r'def\s+(\w+)\(', line)
                if func_match:
                    async_functions.add(func_match.group(1))

    # 检查 await 是否在非 async 函数中
    for j, line in enumerate(lines):
        if 'await' in line and 'def' not in line:
            # 检查是否在函数内部
            if re.search(r'^\s+return\s+await', line):
                print(f"\n代码块 {i+1}, 行 {j+1}:")
                print(f"  await 在 return 语句中")
                print(f"  上下文:")
                start = max(0, j - 5)
                for k in range(start, min(j + 1, len(lines))):
                    print(f"    {k+1}: {lines[k]}")
