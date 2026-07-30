#!/usr/bin/env python3
"""
测试代码块 5 的编译错误
"""

import re

with open('04-chapter4-prompt-engineering.md', 'r', encoding='utf-8') as f:
    content = f.read()

python_blocks = re.findall(r'\`\`\`python\n(.*?)\`\`\`', content, re.DOTALL)
block5 = python_blocks[4]

# 查找 create 调用
lines = block5.split('\n')
for i, line in enumerate(lines, 1):
    if 'create(' in line:
        print(f'行 {i}: {line}')
        # 打印前后几行
        for j in range(max(0, i-2), min(i+3, len(lines))):
            print(f'{j+1}: {lines[j]}')
