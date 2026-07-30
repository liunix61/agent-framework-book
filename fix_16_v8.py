#!/usr/bin/env python3
"""
修复 16-chapter16-applications.md 中的所有 await 错误
"""

with open('16-chapter16-applications.md', 'r', encoding='utf-8') as f:
    content = f.read()

# 查找代码块 2
import re
block2_match = re.search(r'```python\n(.*?)\n```', content, re.DOTALL)
if block2_match:
    block2 = block2_match.group(1)

    # 替换错误的外部 await 调用为测试代码
    old_code = '''# 使用
system = WritingSystem()

article = await system.write_article("AI Agent 的发展趋势")
print(f"\\n最终结果：{article}")

# 测试
async def test_writing():
    system = WritingSystem()
    article = await system.write_article("AI Agent 的发展趋势")
    print(f"\\n最终结果：{article}")

# 运行测试
import asyncio
asyncio.run(test_writing())'''

    new_code = '''# 测试
async def test_writing():
    system = WritingSystem()
    article = await system.write_article("AI Agent 的发展趋势")
    print(f"\\n最终结果：{article}")

# 运行测试
import asyncio
asyncio.run(test_writing())'''

    block2 = block2.replace(old_code, new_code)

    # 替换代码块
    content = content[:block2_match.start()] + '```python\n' + block2 + '\n```' + content[block2_match.end():]

# 查找代码块 4
block4_match = re.search(r'```python\n(.*?)\n```', content, re.DOTALL)
if block4_match:
    block4 = block4_match.group(1)

    # 替换错误的外部 await 调用为测试代码
    block4 = block4.replace(old_code, new_code)

    # 替换代码块
    content = content[:block4_match.start()] + '```python\n' + block4 + '\n```' + content[block4_match.end():]

# 查找代码块 6
block6_match = re.search(r'```python\n(.*?)\n```', content, re.DOTALL)
if block6_match:
    block6 = block6_match.group(1)

    # 替换错误的外部 await 调用为测试代码
    block6 = block6.replace(old_code, new_code)

    # 替换代码块
    content = content[:block6_match.start()] + '```python\n' + block6 + '\n```' + content[block6_match.end():]

# 写回文件
with open('16-chapter16-applications.md', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ 已修复 16-chapter16-applications.md')
