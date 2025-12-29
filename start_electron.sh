#!/bin/bash

# 检查是否安装了Node.js
if ! command -v node &> /dev/null; then
    echo "错误: Node.js 未安装，请先安装 Node.js"
    exit 1
fi

# 检查是否安装了npm
if ! command -v npm &> /dev/null; then
    echo "错误: npm 未安装，请先安装 npm"
    exit 1
fi

# 进入electron目录
cd electron

# 安装依赖
echo "正在安装Electron依赖..."
npm install

# 启动Electron应用
echo "正在启动Electron应用..."
npm start