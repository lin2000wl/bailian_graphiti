# EdgeDuplicate模型修复记录

## 新发现的问题
在测试过程中发现了另一个Pydantic验证错误：`EdgeDuplicate`模型缺少必需字段。

## 错误信息
```
2 validation errors for EdgeDuplicate
duplicate_facts: Field required
contradicted_facts: Field required
```

## 修复方案
1. **文件**: `graphiti_core/prompts/dedupe_edges.py`
2. **修复内容**:
   - 添加`@model_validator`装饰器到`EdgeDuplicate`模型
   - 处理缺失字段，提供默认值：
     - `duplicate_facts`: 默认为空列表`[]`
     - `contradicted_facts`: 默认为空列表`[]`
     - `fact_type`: 默认为`'DEFAULT'`
   - 在所有系统提示中添加"Please respond in JSON format"

## 修复模式
与其他模型修复一致，使用`@model_validator(mode='before')`来预处理API响应：
- 检查必需字段是否存在
- 为缺失字段提供合理的默认值
- 确保阿里云API的JSON格式要求得到满足

## 当前状态
- 代码修复已完成并被用户接受
- 准备重新构建Docker容器进行测试