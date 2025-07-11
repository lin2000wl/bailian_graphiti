# Graphiti与阿里云DashScope API兼容性修复总结

## 问题背景
用户使用Docker部署Graphiti MCP服务，配置阿里云DashScope API时遇到多个兼容性问题：

1. **JSON格式要求错误**: 阿里云API要求消息中必须包含"json"关键词才能使用JSON响应格式
2. **Pydantic验证错误**: API返回的JSON结构与Graphiti期望的不匹配
3. **字段映射问题**: API返回`entity_name`字段，但Graphiti期望`name`字段
4. **嵌入模型配置问题**: 默认使用OpenAI的`text-embedding-3-small`，需要改为阿里云的`text-embedding-v4`

## 已实施的修复

### 1. 环境配置修复
- **文件**: `mcp_server/.env`
- **修复**: 配置正确的阿里云API参数
  - `EMBEDDING_MODEL=text-embedding-v4`
  - `OPENAI_API_KEY=sk-5e0e2df5e99b45edb9cd27b136b235df`
  - `OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1`

### 2. Docker构建修复
- **文件**: `mcp_server/Dockerfile`, `mcp_server/docker-compose.yml`
- **修复**: 修改构建上下文以包含`graphiti_core`目录
  - 构建上下文从`.`改为`..`
  - Dockerfile路径更新为`mcp_server/Dockerfile`
  - 复制`graphiti_core`目录到容器中

### 3. 实体提取模型修复
- **文件**: `graphiti_core/prompts/extract_nodes.py`
- **修复内容**:
  - 在所有系统提示中添加"json"关键词
  - 为`ExtractedEntities`模型添加`@model_validator`装饰器
  - 处理API返回列表而非对象的情况
  - 处理`entity_name` → `name`字段映射
  - 处理`entities` → `extracted_entities`字段映射

### 4. 节点去重模型修复
- **文件**: `graphiti_core/prompts/dedupe_nodes.py`
- **修复内容**:
  - 添加`@model_validator`装饰器到`NodeResolutions`模型
  - 处理API返回列表的情况
  - 自动添加缺失的`duplicates`字段
  - 在系统提示中添加"json"关键词

### 5. 边提取模型修复
- **文件**: `graphiti_core/prompts/extract_edges.py`
- **修复内容**:
  - 添加`@model_validator`装饰器到`ExtractedEdges`模型
  - 处理API返回列表的情况
  - 处理`subject_id` → `source_entity_id`字段映射
  - 处理`object_id` → `target_entity_id`字段映射
  - 在系统提示中添加"json"关键词

## 修复策略模式

### Pydantic验证器模式
```python
@model_validator(mode='before')
@classmethod
def handle_field_mapping(cls, values):
    # 1. 处理API直接返回列表的情况
    if isinstance(values, list):
        return {'expected_field': processed_list}
    
    # 2. 处理字段名映射
    if isinstance(values, dict):
        # 字段重命名逻辑
        # 缺失字段补充逻辑
    
    return values
```

### 系统提示模式
- 在所有系统提示中添加"Please respond in JSON format"
- 在用户提示末尾添加"Please respond in JSON format"

## 当前状态
- 所有代码修复已完成并被用户接受
- Docker容器构建配置已更新
- 准备重新构建和测试修复效果

## 下一步
1. 重新构建Docker容器
2. 测试修复是否完全解决兼容性问题
3. 验证数据能否正常写入和检索