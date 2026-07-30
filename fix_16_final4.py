#!/usr/bin/env python3
"""
修复 16-chapter16-applications.md 中的所有 await 错误（最终版本）
"""

with open('16-chapter16-applications.md', 'r', encoding='utf-8') as f:
    content = f.read()

# 替换方法定义为 async（代码块 6）
old_code = '''    def review_code(self, code: str) -> Dict[str, Any]:
        """
        审查代码

        Args:
            code: 代码

        Returns:
            审查结果
        """'''

new_code = '''    async def review_code(self, code: str) -> Dict[str, Any]:
        """
        审查代码

        Args:
            code: 代码

        Returns:
            审查结果
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
with open('16-chapter16-applications.md', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('✅ 已修复 16-chapter16-applications.md')
