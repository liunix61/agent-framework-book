#!/usr/bin/env python3
"""
修复 25-chapter25-applications.md 中的 await 错误
"""

with open('25-chapter25-applications.md', 'r', encoding='utf-8') as f:
    content = f.read()

# 替换错误的外部 await 调用为测试代码
old_code = '''# 使用
strategy_agent = StrategyAgent(llm_tool=None)
data = pd.DataFrame({
    'open': [100, 101, 102, 103, 104, 105],
    'high': [101, 102, 103, 104, 105, 106],
    'low': [99, 100, 101, 102, 103, 104],
    'close': [100, 101, 102, 103, 104, 105]
})
result = await strategy_agent.generate_strategy(data)
print(f"\\n最终结果：{result}")'''

new_code = '''# 测试
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
asyncio.run(test_strategy())'''

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
with open('25-chapter25-applications.md', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('✅ 已修复 25-chapter25-applications.md')
