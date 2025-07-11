# Docker构建配置修改记录

## 修改背景
Graphiti MCP服务的Docker构建最初只包含`mcp_server`目录中的文件，但修复阿里云API兼容性需要修改`graphiti_core`目录中的代码。

## 关键修改

### 1. docker-compose.yml
```yaml
# 修改前
build:
  context: .
  dockerfile: Dockerfile

# 修改后  
build:
  context: ..
  dockerfile: mcp_server/Dockerfile
```

### 2. Dockerfile
```dockerfile
# 修改前
COPY pyproject.toml uv.lock ./
COPY graphiti_mcp_server.py ./

# 修改后
COPY mcp_server/pyproject.toml mcp_server/uv.lock ./
COPY mcp_server/graphiti_mcp_server.py ./
COPY graphiti_core ./graphiti_core
```

## 构建上下文变更
- **原构建上下文**: `mcp_server/` 目录
- **新构建上下文**: 项目根目录 (`graphiti/`)
- **影响**: 现在可以访问和复制`graphiti_core`目录到容器中

## 重要性
这个修改确保了对`graphiti_core`中Pydantic模型的修复能够被包含在Docker镜像中，是修复阿里云API兼容性问题的关键步骤。