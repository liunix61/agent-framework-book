#!/usr/bin/env python3
"""
修复 28-chapter28-knowledge-graph.md 中的重复参数错误（直接替换）
"""

with open('28-chapter28-knowledge-graph.md', 'r', encoding='utf-8') as f:
    content = f.read()

# 直接删除重复的 edge_id 参数行
content = content.replace(
    '''        edge_id: Optional[str] = None,\n        created_at: Optional[datetime] = None''',
    '''        created_at: Optional[datetime] = None'''
)

# 写回文件
with open('28-chapter28-knowledge-graph.md', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ 已修复 28-chapter28-knowledge-graph.md')
