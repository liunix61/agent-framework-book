#!/usr/bin/env python3
"""
编译 Python 代码块并查找错误
"""

import re

# 读取文件
with open('/home/liunix/workspace/Agent-Framework-Book/04-chapter4-prompt-engineering.md', 'r', encoding='utf-8') as f:
    content = f.read()

# 查找所有 Python 代码块
python_blocks = re.findall(r'```python\n(.*?)```', content, re.DOTALL)

# 编译每个代码块并查找错误
print("编译 Python 代码块并查找错误:")
print("=" * 80)

for i, block in enumerate(python_blocks):
    try:
        compile(block, f'block_{i+1}', 'exec')
        print(f"✅ 代码块 {i+1}: 编译成功")
    except SyntaxError as e:
        print(f"\n❌ 代码块 {i+1}: 语法错误")
        print(f"  行 {e.lineno}: {e.msg}")
        print(f"  代码: {e.text}")
        print(f"  上下文:")
        lines = block.split('\n')
        start = max(0, e.lineno - 3)
        for k in range(start, min(e.lineno + 2, len(lines))):
            print(f"    {k+1}: {lines[k]}")
