#!/usr/bin/env python3
"""
修复 04-chapter4-prompt-engineering.md 中的语法错误
"""

# 读取文件
with open('/home/liunix/workspace/Agent-Framework-Book/04-chapter4-prompt-engineering.md', 'r', encoding='utf-8') as f:
    content = f.read()

# 替换 `...\)` 为 `)`
content = content.replace('...\)', ')')

# 写回文件
with open('/home/liunix/workspace/Agent-Framework-Book/04-chapter4-prompt-engineering.md', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 已修复 04-chapter4-prompt-engineering.md")
