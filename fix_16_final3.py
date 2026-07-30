#!/usr/bin/env python3
"""
修复 16-chapter16-applications.md 中的所有 await 错误（最终版本）
"""

with open('16-chapter16-applications.md', 'r', encoding='utf-8') as f:
    content = f.read()

# 替换错误的外部 await 调用为测试代码（代码块 6）
old_code = '''# 使用
system = CodeReviewSystem()

# 代码
code = """
def calculate_sum(numbers):
    total = 0
    for i in range(len(numbers)):
        for j in range(len(numbers)):
            total += numbers[i] * numbers[j]
    return total
"""

# 审查代码
result = await system.review_code(code)
print(f"\\n最终结果：{result}")

# 测试
async def test_code_review():
    system = CodeReviewSystem()
    code = "print('hello')"
    result = await system.review_code(code)
    print(f"\\n最终结果：{result}")

# 运行测试
import asyncio
asyncio.run(test_code_review())'''

new_code = '''# 测试
async def test_code_review():
    system = CodeReviewSystem()
    code = "print('hello')"
    result = await system.review_code(code)
    print(f"\\n最终结果：{result}")

# 运行测试
import asyncio
asyncio.run(test_code_review())'''

# 查找所有代码块并替换
import re
python_blocks = re.findall(r'```python\n(.*?)\n```', content, re.DOTALL)

for i, block in enumerate(python_blocks):
    if old_code in block:
        python_blocks[i] = block.replace(old_code, new_code)

# 重新组合内容
new_content = ''
for i, block in enumerate(python_blocks):
    new_content += '```python\n' + block + '\n```'

# 写回文件
with open('16-chapter16-applications.md', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('✅ 已修复 16-chapter16-applications.md')
