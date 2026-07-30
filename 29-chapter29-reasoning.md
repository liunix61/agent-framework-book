# 第29章：Agent 知识推理

## 本章目标

通过实战项目，掌握 Agent 知识推理的实现方法。

## 前置知识

- **基础 图理论**: 图遍历、路径查询
- **基础 逻辑**: 逻辑推理、规则推理
- **基础 项目**: 项目结构、代码组织

## 29.1 知识推理概述

### 29.1.1 知识推理概述

**1. 知识推理类型**

| 推理类型 | 说明 | 用途 |
|---------|------|------|
| **演绎推理** | 从一般到特殊的推理 | 规则推理 |
| **归纳推理** | 从特殊到一般的推理 | 模式识别 |
| **类比推理** | 从一个领域到另一个领域的推理 | 知识迁移 |
| **因果推理** | 推断因果关系 | 因果分析 |

**2. 知识推理流程**

```
┌─────────────────────────────────────────────────────────┐
│                    知识推理流程                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │                  知识表示                          │  │
│  │  - 知识图谱                                        │  │
│  │  - 规则库                                          │  │
│  │  - 事实库                                          │  │
│  └───────────────────────────────────────────────────┘  │
│                        ↓                                 │
│  ┌───────────────────────────────────────────────────┐  │
│  │                  推理引擎                          │  │
│  │  - 前向推理                                        │  │
│  │  - 后向推理                                        │  │
│  │  - 混合推理                                        │  │
│  └───────────────────────────────────────────────────┘  │
│                        ↓                                 │
│  ┌───────────────────────────────────────────────────┐  │
│  │                  推理结果                          │  │
│  │  - 新事实                                          │  │
│  │  - 新规则                                          │  │
│  │  - 结论                                            │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 29.1.2 知识推理接口

```python
# knowledge_reasoning/interface.py
from typing import Dict, Any, List, Optional

class KnowledgeReasoner:
    """知识推理器接口"""

    def infer(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        推理

        Args:
            query: 查询
            context: 上下文

        Returns:
            推理结果列表
        """
        raise NotImplementedError

    def query(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        查询

        Args:
            query: 查询
            context: 上下文

        Returns:
            查询结果列表
        """
        raise NotImplementedError

    def learn(
        self,
        examples: List[Dict[str, Any]]
    ) -> None:
        """
        学习

        Args:
            examples: 示例列表
        """
        raise NotImplementedError

    def explain(
        self,
        query: str,
        result: Dict[str, Any]
    ) -> List[str]:
        """
        解释

        Args:
            query: 查询
            result: 结果

        Returns:
            解释列表
        """
        raise NotImplementedError
```

## 29.2 知识推理算法

### 29.2.1 前向推理

**1. 前向推理算法**

```python
# knowledge_reasoning/forward_chaining.py
from typing import Dict, Any, List, Optional
from knowledge_reasoning.interface import KnowledgeReasoner

class ForwardChainingReasoner(KnowledgeReasoner):
    """前向推理器"""

    def __init__(self, rules: List[Dict[str, Any]]):
        """
        初始化前向推理器

        Args:
            rules: 规则列表
        """
        self.rules = rules
        self.facts = set()

    def infer(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        推理

        Args:
            query: 查询
            context: 上下文

        Returns:
            推理结果列表
        """
        # 添加查询到事实
        self.facts.add(query)

        # 前向推理
        results = []

        # 循环推理，直到没有新事实产生
        while True:
            new_facts = set()

            # 遍历所有规则
            for rule in self.rules:
                # 检查规则前提是否满足
                if self._rule_precondition_met(rule, self.facts):
                    # 推导新事实
                    new_fact = rule["conclusion"]

                    if new_fact not in self.facts:
                        new_facts.add(new_fact)
                        results.append({
                            "rule": rule,
                            "fact": new_fact,
                            "reason": "rule"
                        })

            # 如果没有新事实产生，停止推理
            if not new_facts:
                break

            # 添加新事实
            self.facts.update(new_facts)

        return results

    def _rule_precondition_met(
        self,
        rule: Dict[str, Any],
        facts: set
    ) -> bool:
        """
        检查规则前提是否满足

        Args:
            rule: 规则
            facts: 事实集合

        Returns:
            是否满足
        """
        # 检查所有前提是否都在事实中
        for precondition in rule["preconditions"]:
            if precondition not in facts:
                return False

        return True

    def query(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        查询

        Args:
            query: 查询
            context: 上下文

        Returns:
            查询结果列表
        """
        # 检查查询是否在事实中
        if query in self.facts:
            return [{
                "query": query,
                "status": "true",
                "reason": "fact"
            }]

        # 否则返回空结果
        return [{
            "query": query,
            "status": "false",
            "reason": "not_found"
        }]

    def learn(
        self,
        examples: List[Dict[str, Any]]
    ) -> None:
        """
        学习

        Args:
            examples: 示例列表
        """
        # 从示例中提取规则
        for example in examples:
            # 简单的规则提取
            if "preconditions" in example and "conclusion" in example:
                rule = {
                    "preconditions": example["preconditions"],
                    "conclusion": example["conclusion"]
                }

                self.rules.append(rule)

    def explain(
        self,
        query: str,
        result: Dict[str, Any]
    ) -> List[str]:
        """
        解释

        Args:
            query: 查询
            result: 结果

        Returns:
            解释列表
        """
        explanations = []

        if result["reason"] == "rule":
            explanations.append(f"根据规则推导出结论：{query}")

            # 添加规则前提
            for rule in self.rules:
                if rule["conclusion"] == query:
                    explanations.append("规则前提：")
                    for precondition in rule["preconditions"]:
                        explanations.append(f"- {precondition}")

        elif result["reason"] == "fact":
            explanations.append(f"查询在事实中找到：{query}")

        return explanations


# 使用
rules = [
    {
        "preconditions": ["AI Agent", "Python"],
        "conclusion": "AI Agent 可以使用 Python 实现"
    },
    {
        "preconditions": ["LLM", "大语言模型"],
        "conclusion": "LLM 是大语言模型"
    },
    {
        "preconditions": ["AI Agent", "LLM"],
        "conclusion": "AI Agent 可以使用 LLM"
    }
]

reasoner = ForwardChainingReasoner(rules)

# 推理
results = reasoner.infer("AI Agent 可以使用 LLM")

print(f"推理结果：")
for result in results:
    print(f"结论：{result['fact']}")
    print(f"原因：{result['reason']}")
    print()

# 查询
query_results = reasoner.query("AI Agent 可以使用 Python")

print(f"查询结果：")
for result in query_results:
    print(f"查询：{result['query']}")
    print(f"状态：{result['status']}")
    print(f"原因：{result['reason']}")
    print()

# 解释
explanations = reasoner.explain("AI Agent 可以使用 Python", query_results[0])

print(f"解释：")
for explanation in explanations:
    print(f"- {explanation}")
```

**2. 前向推理示例**

```python
# 前向推理示例
rules = [
    {
        "preconditions": ["猫", "喵喵叫"],
        "conclusion": "这是猫"
    },
    {
        "preconditions": ["狗", "汪汪叫"],
        "conclusion": "这是狗"
    },
    {
        "preconditions": ["这是猫", "猫吃鱼"],
        "conclusion": "猫吃鱼"
    },
    {
        "preconditions": ["这是狗", "狗吃肉"],
        "conclusion": "狗吃肉"
    }
]

reasoner = ForwardChainingReasoner(rules)

# 推理
results = reasoner.infer("猫吃鱼")

print(f"推理结果：")
for result in results:
    print(f"结论：{result['fact']}")
```

### 29.2.2 后向推理

**1. 后向推理算法**

```python
# knowledge_reasoning/backward_chaining.py
from typing import Dict, Any, List, Optional
from knowledge_reasoning.interface import KnowledgeReasoner

class BackwardChainingReasoner(KnowledgeReasoner):
    """后向推理器"""

    def __init__(self, rules: List[Dict[str, Any]]):
        """
        初始化后向推理器

        Args:
            rules: 规则列表
        """
        self.rules = rules
        self.facts = set()

    def infer(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        推理

        Args:
            query: 查询
            context: 上下文

        Returns:
            推理结果列表
        """
        # 后向推理
        results = []

        # 检查查询是否在事实中
        if query in self.facts:
            return [{
                "query": query,
                "status": "true",
                "reason": "fact"
            }]

        # 否则尝试从规则推导
        for rule in self.rules:
            # 检查规则结论是否匹配查询
            if rule["conclusion"] == query:
                # 检查规则前提是否满足
                if self._rule_precondition_met(rule):
                    # 添加新事实
                    self.facts.add(query)
                    results.append({
                        "query": query,
                        "status": "true",
                        "reason": "rule",
                        "rule": rule
                    })

                    # 递归检查前提
                    for precondition in rule["preconditions"]:
                        sub_results = self.infer(precondition)
                        results.extend(sub_results)

                    return results

        # 无法推导
        results.append({
            "query": query,
            "status": "false",
            "reason": "not_found"
        })

        return results

    def _rule_precondition_met(self, rule: Dict[str, Any]) -> bool:
        """
        检查规则前提是否满足

        Args:
            rule: 规则

        Returns:
            是否满足
        """
        # 检查所有前提是否在事实中
        for precondition in rule["preconditions"]:
            if precondition not in self.facts:
                return False

        return True

    def query(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        查询

        Args:
            query: 查询
            context: 上下文

        Returns:
            查询结果列表
        """
        # 后向推理
        return self.infer(query)

    def learn(
        self,
        examples: List[Dict[str, Any]]
    ) -> None:
        """
        学习

        Args:
            examples: 示例列表
        """
        # 从示例中提取规则
        for example in examples:
            # 简单的规则提取
            if "preconditions" in example and "conclusion" in example:
                rule = {
                    "preconditions": example["preconditions"],
                    "conclusion": example["conclusion"]
                }

                self.rules.append(rule)

    def explain(
        self,
        query: str,
        result: Dict[str, Any]
    ) -> List[str]:
        """
        解释

        Args:
            query: 查询
            result: 结果

        Returns:
            解释列表
        """
        explanations = []

        if result["reason"] == "rule":
            explanations.append(f"根据规则推导出结论：{query}")

            # 添加规则前提
            if "rule" in result:
                rule = result["rule"]
                explanations.append("规则前提：")
                for precondition in rule["preconditions"]:
                    explanations.append(f"- {precondition}")

        elif result["reason"] == "fact":
            explanations.append(f"查询在事实中找到：{query}")

        return explanations


# 使用
rules = [
    {
        "preconditions": ["猫", "喵喵叫"],
        "conclusion": "这是猫"
    },
    {
        "preconditions": ["这是猫", "猫吃鱼"],
        "conclusion": "猫吃鱼"
    },
    {
        "preconditions": ["狗", "汪汪叫"],
        "conclusion": "这是狗"
    },
    {
        "preconditions": ["这是狗", "狗吃肉"],
        "conclusion": "狗吃肉"
    }
]

reasoner = BackwardChainingReasoner(rules)

# 推理
results = reasoner.infer("猫吃鱼")

print(f"推理结果：")
for result in results:
    print(f"查询：{result['query']}")
    print(f"状态：{result['status']}")
    print(f"原因：{result['reason']}")
    print()

# 查询
query_results = reasoner.query("猫吃鱼")

print(f"查询结果：")
for result in query_results:
    print(f"查询：{result['query']}")
    print(f"状态：{result['status']}")
    print(f"原因：{result['reason']}")
    print()

# 解释
explanations = reasoner.explain("猫吃鱼", query_results[0])

print(f"解释：")
for explanation in explanations:
    print(f"- {explanation}")
```

## 29.3 知识推理应用

### 29.3.1 医疗诊断推理

**1. 医疗诊断推理器**

```python
# knowledge_reasoning/medical_diagnosis.py
from typing import Dict, Any, List, Optional
from knowledge_reasoning.interface import KnowledgeReasoner

class MedicalDiagnosisReasoner(KnowledgeReasoner):
    """医疗诊断推理器"""

    def __init__(self, symptoms_rules: List[Dict[str, Any]], diseases_rules: List[Dict[str, Any]]):
        """
        初始化医疗诊断推理器

        Args:
            symptoms_rules: 症状规则
            diseases_rules: 疾病规则
        """
        self.symptoms_rules = symptoms_rules
        self.diseases_rules = diseases_rules
        self.facts = set()

    def infer(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        推理

        Args:
            query: 查询
            context: 上下文

        Returns:
            推理结果列表
        """
        # 添加查询到事实
        self.facts.add(query)

        # 推理
        results = []

        # 遍历所有疾病规则
        for rule in self.diseases_rules:
            # 检查规则前提是否满足
            if self._rule_precondition_met(rule, self.facts):
                # 推导新结论
                disease = rule["conclusion"]

                if disease not in self.facts:
                    self.facts.add(disease)
                    results.append({
                        "disease": disease,
                        "confidence": rule.get("confidence", 1.0),
                        "reason": "symptoms"
                    })

        return results

    def _rule_precondition_met(
        self,
        rule: Dict[str, Any],
        facts: set
    ) -> bool:
        """
        检查规则前提是否满足

        Args:
            rule: 规则
            facts: 事实集合

        Returns:
            是否满足
        """
        # 检查所有前提是否都在事实中
        for precondition in rule["preconditions"]:
            if precondition not in facts:
                return False

        return True

    def query(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        查询

        Args:
            query: 查询
            context: 上下文

        Returns:
            查询结果列表
        """
        # 检查查询是否在事实中
        if query in self.facts:
            return [{
                "query": query,
                "status": "true",
                "reason": "fact"
            }]

        # 否则返回空结果
        return [{
            "query": query,
            "status": "false",
            "reason": "not_found"
        }]

    def learn(
        self,
        examples: List[Dict[str, Any]]
    ) -> None:
        """
        学习

        Args:
            examples: 示例列表
        """
        # 从示例中提取规则
        for example in examples:
            # 简单的规则提取
            if "preconditions" in example and "conclusion" in example:
                rule = {
                    "preconditions": example["preconditions"],
                    "conclusion": example["conclusion"]
                }

                self.diseases_rules.append(rule)

    def explain(
        self,
        query: str,
        result: Dict[str, Any]
    ) -> List[str]:
        """
        解释

        Args:
            query: 查询
            result: 结果

        Returns:
            解释列表
        """
        explanations = []

        if result["reason"] == "symptoms":
            explanations.append(f"根据症状 {query} 推断出可能的疾病")

            # 添加症状
            for rule in self.diseases_rules:
                if rule["conclusion"] == query:
                    explanations.append("症状：")
                    for precondition in rule["preconditions"]:
                        explanations.append(f"- {precondition}")

        elif result["reason"] == "fact":
            explanations.append(f"查询在事实中找到：{query}")

        return explanations


# 使用
symptoms_rules = [
    {
        "preconditions": ["发烧", "咳嗽"],
        "conclusion": "感冒"
    },
    {
        "preconditions": ["发烧", "咳嗽", "喉咙痛"],
        "conclusion": "流感"
    },
    {
        "preconditions": ["发烧", "胸痛", "呼吸困难"],
        "conclusion": "肺炎"
    },
    {
        "preconditions": ["咳嗽", "咳痰", "喘息", "胸闷"],
        "conclusion": "支气管炎"
    }
]

diseases_rules = [
    {
        "preconditions": ["感冒", "咳嗽"],
        "conclusion": "感冒"
    },
    {
        "preconditions": ["感冒", "发烧"],
        "conclusion": "感冒"
    },
    {
        "preconditions": ["流感", "发烧", "咳嗽", "喉咙痛"],
        "conclusion": "流感"
    },
    {
        "preconditions": ["肺炎", "发烧", "咳嗽", "胸痛", "呼吸困难"],
        "conclusion": "肺炎"
    },
    {
        "preconditions": ["支气管炎", "咳嗽", "咳痰", "喘息", "胸闷"],
        "conclusion": "支气管炎"
    }
]

reasoner = MedicalDiagnosisReasoner(symptoms_rules, diseases_rules)

# 推理
results = reasoner.infer("感冒")

print(f"推理结果：")
for result in results:
    print(f"疾病：{result['disease']}")
    print(f"置信度：{result['confidence']}")
    print(f"原因：{result['reason']}")
    print()

# 查询
query_results = reasoner.query("感冒")

print(f"查询结果：")
for result in query_results:
    print(f"查询：{result['query']}")
    print(f"状态：{result['status']}")
    print(f"原因：{result['reason']}")
    print()

# 解释
explanations = reasoner.explain("感冒", query_results[0])

print(f"解释：")
for explanation in explanations:
    print(f"- {explanation}")
```

## 29.4 本章总结

### 核心要点

1. **知识推理概述**: 知识推理类型、知识推理流程
2. **前向推理算法**: 前向推理算法实现
3. **后向推理算法**: 后向推理算法实现
4. **知识推理应用**: 医疗诊断推理应用

### 实战技巧

- **前向推理**: 从已知事实出发，应用规则推导新事实
- **后向推理**: 从目标出发，反向推导所需前提
- **医疗诊断**: 使用症状和疾病规则进行诊断推理
- **规则提取**: 从示例中提取规则

### 练习题

1. 实现前向推理算法
2. 实现后向推理算法
3. 实现医疗诊断推理器
4. 实现金融诊断推理器

### 下章预告

第30章将介绍 **Agent 系统评估**，包括：
- 系统评估概述
- 系统评估指标
- 系统评估方法

---

**本章完**

**下一章**: [第30章：Agent 系统评估](./30-chapter29-reasoning.md)
