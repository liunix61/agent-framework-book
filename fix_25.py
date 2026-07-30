#!/usr/bin/env python3
"""
修复 25-chapter25-applications.md 中的 await 错误
"""

with open('25-chapter25-applications.md', 'r', encoding='utf-8') as f:
    content = f.read()

# 修复代码块 1：将末尾的 await 调用包装在 async 函数中
block1_end = content.find('```', content.find('```python', content.find('```python', content.find('```python') + 1) + 1) + 1) + 3
block1_start = content.rfind('```python', 0, block1_end)

block1 = content[block1_start:block1_end]

# 在代码块末尾添加 async 函数包装
wrapper = '''

# 测试
async def test_strategy():
    strategy_agent = StrategyAgent(llm_tool=None)
    data = pd.DataFrame({
        'open': [100, 101, 102, 103, 104, 105],
        'high': [101, 102, 103, 104, 105, 106],
        'low': [99, 100, 101, 102, 103, 104],
        'close': [100, 101, 102, 103, 104, 105]
    })
    result = await strategy_agent.generate_strategy(data)
    print(f"\\n最终结果：{result}")

# 运行测试
import asyncio
asyncio.run(test_strategy())
'''

# 替换代码块 1
content = content[:block1_end] + wrapper + content[block1_end:]

# 写回文件
with open('25-chapter25-applications.md', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ 已修复 25-chapter25-applications.md')
