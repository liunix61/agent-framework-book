#!/usr/bin/env python3
"""
查看代码块 5 的内容
"""

import re

# 读取文件
with open('/home/liunix/workspace/Agent-Framework-Book/04-chapter4-prompt-engineering.md', 'r', encoding='utf-8') as f:
    content = f.read()

# 查找所有 Python 代码块
python_blocks = re.findall(r'```python\n(.*?)```', content, re.DOTALL)

# 打印代码块 5
print("代码块 5:")
print("=" * 80)
print(python_blocks[4])
print("\n" + "=" * 80)
print(f"代码块长度: {len(python_blocks[4])}")
print(f"包含 '...': {'...' in python_blocks[4]}")
print(f"包含 '...\\)': {'...\\)' in python_blocks[4]}")
