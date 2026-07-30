#!/usr/bin/env python3
"""
修复 04-chapter4-prompt-engineering.md 中的语法错误
"""

# 读取文件
with open('/home/liunix/workspace/Agent-Framework-Book/04-chapter4-prompt-engineering.md', 'r', encoding='utf-8') as f:
    content = f.read()

# 打印原始内容
print("原始内容（前 50 行）:")
print(content[:500])
print("\n" + "=" * 80 + "\n")

# 查找 `...\)`
count = content.count('...\)')
print(f"找到 {count} 个 `...\)`")
print("\n" + "=" * 80 + "\n")

# 替换 `...\)` 为 `)`
content = content.replace('...\)', ')')

# 打印替换后的内容
print("替换后内容（前 50 行）:")
print(content[:500])
print("\n" + "=" * 80 + "\n")

# 查找 `...` 后面跟着 `)` 的情况
import re
matches = re.findall(r'...\)', content)
print(f"替换后找到 {len(matches)} 个 `...\)`")

# 写回文件
with open('/home/liunix/workspace/Agent-Framework-Book/04-chapter4-prompt-engineering.md', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✅ 已修复 04-chapter4-prompt-engineering.md")
