#!/usr/bin/env python3
"""
修复 28-chapter28-knowledge-graph.md 中的重复参数错误
"""

with open('28-chapter28-knowledge-graph.md', 'r', encoding='utf-8') as f:
    content = f.read()

# 修复代码块 2：删除重复的 edge_id 参数
block2_end = content.find('```', content.find('```python', content.find('```python', content.find('```python') + 1) + 1) + 1) + 3
block2_start = content.rfind('```python', 0, block2_end)

block2 = content[block2_start:block2_end]

# 删除重复的 edge_id 参数
block2 = block2.replace(
    '''    def __init__(
        self,
        edge_id: str,
        source_node_id: str,
        target_node_id: str,
        relationship_type: str,
        properties: Optional[Dict[str, Any]] = None,
        edge_id: Optional[str] = None,
        created_at: Optional[datetime] = None
    ):''',
    '''    def __init__(
        self,
        edge_id: str,
        source_node_id: str,
        target_node_id: str,
        relationship_type: str,
        properties: Optional[Dict[str, Any]] = None,
        created_at: Optional[datetime] = None
    ):'''
)

# 替换代码块 2
content = content[:block2_start] + block2 + content[block2_end:]

# 写回文件
with open('28-chapter28-knowledge-graph.md', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ 已修复 28-chapter28-knowledge-graph.md')
