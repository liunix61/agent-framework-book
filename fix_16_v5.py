#!/usr/bin/env python3
"""
修复 16-chapter16-applications.md 中的 await 错误
"""

with open('16-chapter16-applications.md', 'r', encoding='utf-8') as f:
    content = f.read()

# 修复代码块 2：删除错误的外部 await 调用
# 找到代码块 2 的结束位置
block2_start = content.find('```python\n', content.find('```python\n', content.find('```python\n', content.find('```python\n') + 1) + 1) + 7
block2_end = content.find('\n```', block2_start)

block2 = content[block2_start:block2_end]

# 替换错误的外部 await 调用为测试代码
block2 = block2.replace(
    '''# 使用
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
asyncio.run(test_writing())''',
    '''# 测试
async def test_writing():
    system = WritingSystem()
    article = await system.write_article("AI Agent 的发展趋势")
    print(f"\\n最终结果：{article}")

# 运行测试
import asyncio
asyncio.run(test_writing())'''
)

# 替换代码块
content = content[:block2_start] + block2 + content[block2_end:]

# 修复代码块 4
block4_start = content.find('```python\n', content.find('```python\n', content.find('```python\n', content.find('```python\n') + 1) + 1) + 7
block4_end = content.find('\n```', block4_start)

block4 = content[block4_start:block4_end]

block4 = block4.replace(
    '''# 使用
system = QuantTradingSystem()

# 模拟市场数据
data = pd.DataFrame({
    'open': [100, 101, 102, 103, 104, 105],
    'high': [101, 102, 103, 104, 105, 106],
    'low': [99, 100, 101, 102, 103, 104],
    'close': [100, 101, 102, 103, 104, 105]
})

# 执行交易
result = await system.trade(data)
print(f"\\n最终结果：{result}")

# 测试
async def test_trading():
    result = await system.trade(data)
    print(f"\\n最终结果：{result}")

# 运行测试
import asyncio
asyncio.run(test_trading())''',
    '''# 测试
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
asyncio.run(test_trading())'''
)

content = content[:block4_start] + block4 + content[block4_end:]

# 修复代码块 6
block6_start = content.find('```python\n', content.find('```python\n', content.find('```python\n', content.find('```python\n') + 1) + 1) + 7
block6_end = content.find('\n```', block6_start)

block6 = content[block6_start:block6_end]

block6 = block6.replace(
    '''# 使用
system = CodeReviewSystem()
code = "print('hello')"
result = await system.review_code(code)
print(f"\\n最终结果：{result}")

# 测试
async def test_code_review():
    result = await system.review_code(code)
    print(f"\\n最终结果：{result}")

# 运行测试
import asyncio
asyncio.run(test_code_review())''',
    '''# 测试
async def test_code_review():
    system = CodeReviewSystem()
    code = "print('hello')"
    result = await system.review_code(code)
    print(f"\\n最终结果：{result}")

# 运行测试
import asyncio
asyncio.run(test_code_review())'''
)

content = content[:block6_start] + block6 + content[block6_end:]

# 写回文件
with open('16-chapter16-applications.md', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ 已修复 16-chapter16-applications.md')
