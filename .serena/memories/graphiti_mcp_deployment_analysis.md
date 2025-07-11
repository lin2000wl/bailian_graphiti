# Graphiti MCP部署分析

## 问题识别
用户遇到的问题是embedding模型配置不匹配：
- 代码中默认使用 `text-embedding-3-small` (OpenAI模型)
- 但用户配置的是阿里云DashScope API
- 阿里云API不支持OpenAI的embedding模型

## 默认配置分析
```python
DEFAULT_LLM_MODEL = 'gpt-4.1-mini'          # 正确 - 用户已配置为qwen-max-latest
DEFAULT_EMBEDDER_MODEL = 'text-embedding-3-small'  # 问题所在 - 需要改为阿里云支持的模型
```

## Docker配置分析
- Docker Compose使用环境变量覆盖
- .env文件是可选的，但用户已创建
- 需要正确配置embedding模型环境变量

## 解决方案
1. 更新环境变量配置支持阿里云embedding模型
2. 修改Docker部署以使用正确的模型配置
3. 确保所有API调用使用统一的服务提供商