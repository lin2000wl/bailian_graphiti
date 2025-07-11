# Cursor MCP服务配置脚本
# 此脚本将自动配置Cursor以连接到Graphiti MCP服务

Write-Host "🔧 开始配置Cursor MCP服务..." -ForegroundColor Green

# 定义配置文件路径
$configPath = "$env:APPDATA\Cursor\User\globalStorage\cursor.mcp"
$configFile = "$configPath\config.json"

# 创建配置目录（如果不存在）
if (-not (Test-Path $configPath)) {
    Write-Host "📁 创建配置目录: $configPath" -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $configPath -Force | Out-Null
}

# MCP配置内容
$mcpConfig = @{
    mcpServers = @{
        graphiti = @{
            transport = "sse"
            url = "http://localhost:8000/sse"
        }
    }
} | ConvertTo-Json -Depth 3

# 检查配置文件是否已存在
if (Test-Path $configFile) {
    Write-Host "⚠️  配置文件已存在: $configFile" -ForegroundColor Yellow
    Write-Host "📄 当前配置内容:" -ForegroundColor Cyan
    Get-Content $configFile | Write-Host
    
    $overwrite = Read-Host "是否覆盖现有配置？(y/n)"
    if ($overwrite.ToLower() -ne 'y') {
        Write-Host "❌ 配置已取消" -ForegroundColor Red
        exit
    }
}

# 写入配置文件
try {
    $mcpConfig | Out-File -FilePath $configFile -Encoding UTF8
    Write-Host "✅ 配置文件已创建: $configFile" -ForegroundColor Green
    
    Write-Host "📄 配置内容:" -ForegroundColor Cyan
    Write-Host $mcpConfig -ForegroundColor White
    
} catch {
    Write-Host "❌ 创建配置文件失败: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 验证Docker服务状态
Write-Host "🐳 检查Docker服务状态..." -ForegroundColor Blue
try {
    $dockerStatus = docker compose ps --format json | ConvertFrom-Json
    $graphitiService = $dockerStatus | Where-Object { $_.Service -eq "graphiti-mcp" }
    
    if ($graphitiService -and $graphitiService.State -eq "running") {
        Write-Host "✅ Graphiti MCP服务运行正常" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Graphiti MCP服务未运行，请先启动Docker服务" -ForegroundColor Yellow
        Write-Host "   运行命令: docker compose up -d" -ForegroundColor Cyan
    }
} catch {
    Write-Host "⚠️  无法检查Docker状态，请确保Docker已安装并运行" -ForegroundColor Yellow
}

# 测试MCP服务连接
Write-Host "🌐 测试MCP服务连接..." -ForegroundColor Blue
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000" -Method Get -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ MCP服务连接正常" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  无法连接到MCP服务，请确保服务正在运行" -ForegroundColor Yellow
    Write-Host "   服务地址: http://localhost:8000" -ForegroundColor Cyan
}

Write-Host "`n🎉 配置完成！" -ForegroundColor Green
Write-Host "📋 下一步操作:" -ForegroundColor Cyan
Write-Host "   1. 重启Cursor应用" -ForegroundColor White
Write-Host "   2. 在Cursor中使用@graphiti调用MCP功能" -ForegroundColor White
Write-Host "   3. 验证知识图谱功能是否正常工作" -ForegroundColor White

Write-Host "`n📍 配置文件位置: $configFile" -ForegroundColor Cyan
Write-Host "🌐 MCP服务地址: http://localhost:8000/sse" -ForegroundColor Cyan
Write-Host "💾 Neo4j界面: http://localhost:7474" -ForegroundColor Cyan

Read-Host "`n按回车键退出" 