#!/usr/bin/env python3
"""
修复 25-chapter25-applications.md 中的 await 错误
"""

with open('25-chapter25-applications.md', 'r', encoding='utf-8') as f:
    content = f.read()

# 替换方法定义为 async
old_code = '''    def trade(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        执行交易

        Args:
            data: 市场数据

        Returns:
            交易结果
        """'''

new_code = '''    async def trade(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        执行交易

        Args:
            data: 市场数据

        Returns:
            交易结果
        """'''

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
