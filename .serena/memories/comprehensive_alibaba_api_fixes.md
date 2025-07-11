# 阿里云DashScope API兼容性修复完整记录

## 修复的所有Pydantic模型

### 1. ExtractedEntities (`graphiti_core/prompts/extract_nodes.py`)
- **问题**: 字段映射和缺失字段
- **修复**: 处理`entity_name`→`name`映射，处理`entities`→`extracted_entities`映射

### 2. NodeResolutions (`graphiti_core/prompts/dedupe_nodes.py`)
- **问题**: API返回列表而非对象，缺少`duplicates`字段
- **修复**: 处理列表响应，添加默认`duplicates`字段

### 3. ExtractedEdges (`graphiti_core/prompts/extract_edges.py`)
- **问题**: 字段映射和缺失`fact`字段
- **修复**: 处理`subject_id`→`source_entity_id`映射，自动生成`fact`字段

### 4. EdgeDuplicate (`graphiti_core/prompts/dedupe_edges.py`)
- **问题**: 缺少必需字段
- **修复**: 为`duplicate_facts`、`contradicted_facts`、`fact_type`提供默认值

## 通用修复模式
所有模型都使用相同的修复模式：
```python
@model_validator(mode='before')
@classmethod
def handle_field_mapping(cls, values):
    # 1. 处理API直接返回列表的情况
    # 2. 处理字段名映射
    # 3. 为缺失字段提供默认值
    return values
```

## JSON格式要求修复
在所有相关提示函数中添加：
- 系统提示: "Please respond in JSON format"
- 用户提示末尾: "Please respond in JSON format"

## 修复文件清单
1. `graphiti_core/prompts/extract_nodes.py` ✓
2. `graphiti_core/prompts/dedupe_nodes.py` ✓
3. `graphiti_core/prompts/extract_edges.py` ✓
4. `graphiti_core/prompts/dedupe_edges.py` ✓
5. `mcp_server/Dockerfile` ✓
6. `mcp_server/docker-compose.yml` ✓