#!/bin/bash

# GAL-SIM 依赖检查和安装脚本
# 此脚本帮助检查和安装必要的依赖

set -e

echo "========================================"
echo "  GAL-SIM 依赖检查脚本"
echo "========================================"
echo ""

# 检查 Python 是否安装
echo "1. 检查 Python 安装..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    echo "✓ Python 版本: $($PYTHON_CMD --version)"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    echo "✓ Python 版本: $($PYTHON_CMD --version)"
else
    echo "❌ Python 未安装"
    echo "   请安装 Python 3.8+"
    exit 1
fi

# 检查 pip 是否可用
echo ""
echo "2. 检查 pip 安装..."
if $PYTHON_CMD -m pip --version > /dev/null 2>&1; then
    echo "✓ pip 可用"
else
    echo "❌ pip 未安装或不可用"
    echo "   请安装 pip: $PYTHON_CMD -m ensurepip --upgrade"
    exit 1
fi

# 安装 Python 依赖
echo ""
echo "3. 安装 Python 依赖包..."
if [ -f "requirements.txt" ]; then
    echo "   正在安装依赖包..."
    $PYTHON_CMD -m pip install -r requirements.txt || {
        echo "❌ 依赖安装失败"
        echo "   尝试使用国内镜像源安装..."
        $PYTHON_CMD -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
    }
else
    echo "❌ 未找到 requirements.txt 文件"
    echo "   请确保在正确的安装目录中运行此脚本"
    exit 1
fi

# 检查 .env 文件
echo ""
echo "4. 检查 .env 配置文件..."
if [ ! -f ".env" ]; then
    echo "⚠️  .env 文件不存在，正在从 .env.example 创建..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ 已创建 .env 文件"
        echo "   请编辑 .env 文件并添加您的 API 密钥"
    else
        echo "❌ 未找到 .env.example 文件"
    fi
else
    echo "✅ .env 文件已存在"
fi

# 测试 Python 环境
echo ""
echo "5. 测试 Python 环境..."
$PYTHON_CMD -c "import fastapi,uvicorn,dotenv; print('✓ Python 依赖测试通过')" 2>/dev/null || {
    echo "❌ Python 依赖测试失败"
    echo "   部分依赖可能未正确安装"
    exit 1
}
echo "✓ Python 依赖测试通过"

echo ""
echo "========================================"
echo "  依赖检查完成!"
echo "========================================"
echo ""
echo "✅ 您的系统已准备好运行 GAL-SIM"
echo ""
echo "提示:"
echo "  - 请确保 .env 文件中已配置正确的 API 密钥"
echo "  - 如需启动应用，请运行 start_electron.sh 或直接启动 GAL-SIM"
echo ""