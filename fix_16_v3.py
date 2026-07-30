#!/usr/bin/env python3
"""
修复 16-chapter16-applications.md 中的 await 错误（暴力修复）
"""

with open('16-chapter16-applications.md', 'r', encoding='utf-8') as f:
    content = f.read()

# 查找所有代码块
import re
python_blocks = re.findall(r'\`\`\`python\n(.*?)\`\`\`', content, re.DOTALL)

# 修复代码块 2
block2 = python_blocks[1]

# 在代码块末尾添加测试代码
test_code = '''

# 测试
async def test_writing():
    system = WritingSystem()
    article = await system.write_article("AI Agent 的发展趋势")
    print(f"\\n最终结果：{article}")

# 运行测试
import asyncio
asyncio.run(test_writing())
'''

# 在代码块末尾添加测试代码
block2 = block2.rstrip() + test_code + '\n'

# 替换代码块
python_blocks[1] = block2

# 修复代码块 4
block4 = python_blocks[3]

test_code = '''

# 测试
async def test_trading():
    system = QuantTradingSystem()
    data = pd.DataFrame({
        'open': [100, 101, 102, 103, 104, 105],
        'high': [101, 102, 103, 104, 105, 106],
        'low': [99, 100, 101, 102, 103, 104],
        'close': [100, 101, 102, 103, 104, 105]
    })
    result = await system.trade(data)
    print(f"\\n最终结果：{result}")

# 运行测试
import asyncio
asyncio.run(test_trading())
'''

block4 = block4.rstrip() + test_code + '\n'
python_blocks[3] = block4

# 修复代码块 6
block6 = python_blocks[5]

test_code = '''

# 测试
async def test_code_review():
    system = CodeReviewSystem()
    code = "print('hello')"
    result = await system.review_code(code)
    print(f"\\n最终结果：{result}")

# 运行测试
import asyncio
asyncio.run(test_code_review())
'''

block6 = block6.rstrip() + test_code + '\n'
python_blocks[5] = block6

# 重新组合内容
new_content = ''
for i, block in enumerate(python_blocks):
    new_content += '```python\n' + block + '\n```'

# 写回文件
with open('16-chapter16-applications.md', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('✅ 已修复 16-chapter16-applications.md')
