#!/usr/bin/env python3

with open('04-chapter4-prompt-engineering.md', 'r', encoding='utf-8') as f:
    content = f.read()

# 替换 `...` 为空字符串
content = content.replace('...', '')

with open('04-chapter4-prompt-engineering.md', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ 已替换所有 `...` 为空字符串')
