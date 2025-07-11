# 阿里云DashScope API特殊要求

## JSON响应格式要求
阿里云DashScope API有一个特殊要求：当使用`response_format: {type: "json_object"}`时，**消息内容中必须包含"json"关键词**。

### 错误示例
```
Error: 'messages' must contain the word 'json' in some form, to use 'response_format' of type 'json_object'
```

### 解决方案
在所有系统提示和用户提示中添加"json"关键词：
- 系统提示: "Please respond in JSON format"
- 用户提示末尾: "Please respond in JSON format"

## 字段映射差异
阿里云API返回的JSON结构与OpenAI API略有不同：

### 实体提取
- **阿里云返回**: `entity_name` 字段
- **Graphiti期望**: `name` 字段
- **解决**: Pydantic验证器中添加字段映射

### 边提取  
- **阿里云返回**: `subject_id`, `object_id` 字段
- **Graphiti期望**: `source_entity_id`, `target_entity_id` 字段
- **解决**: Pydantic验证器中添加字段映射

## 响应结构差异
阿里云API有时直接返回列表，而不是包含列表的对象：
- **标准格式**: `{"extracted_entities": [...]}`
- **阿里云格式**: `[...]` 或 `{"entities": [...]}`

## 嵌入模型
- **支持的模型**: `text-embedding-v4`, `text-embedding-v1`
- **不支持**: OpenAI的`text-embedding-3-small`