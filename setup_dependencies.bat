@echo off
REM GAL-SIM 依赖检查和安装脚本
REM 此脚本帮助检查和安装必要的依赖

echo ========================================
echo   GAL-SIM 依赖检查脚本
echo ========================================
echo.

REM 检查 Python 是否安装
echo 1. 检查 Python 安装...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python 未安装或未添加到 PATH
    echo    请访问 https://www.python.org/ 下载并安装 Python 3.8+
    echo    安装时请务必勾选 "Add Python to PATH" 选项
    pause
    exit /b 1
) else (
    for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
    echo ✓ Python 版本: %PYTHON_VERSION%
)

REM 检查 pip 是否可用
echo.
echo 2. 检查 pip 安装...
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ pip 未安装或不可用
    echo    请重新安装 Python 并确保包含 pip
    pause
    exit /b 1
) else (
    echo ✓ pip 可用
)

REM 安装 Python 依赖
echo.
echo 3. 安装 Python 依赖包...
if exist "requirements.txt" (
    echo    正在安装依赖包...
    python -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ❌ 依赖安装失败
        echo    尝试使用国内镜像源安装...
        python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
    )
) else (
    echo ❌ 未找到 requirements.txt 文件
    echo    请确保在正确的安装目录中运行此脚本
    pause
    exit /b 1
)

REM 检查 .env 文件
echo.
echo 4. 检查 .env 配置文件...
if not exist ".env" (
    echo ⚠️  .env 文件不存在，正在从 .env.example 创建...
    if exist ".env.example" (
        copy ".env.example" ".env"
        echo ✅ 已创建 .env 文件
        echo    请编辑 .env 文件并添加您的 API 密钥
    ) else (
        echo ❌ 未找到 .env.example 文件
    )
) else (
    echo ✅ .env 文件已存在
)

REM 测试 Python 环境
echo.
echo 5. 测试 Python 环境...
python -c "import fastapi,uvicorn,dotenv; print('✓ Python 依赖测试通过')" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python 依赖测试失败
    echo    部分依赖可能未正确安装
    pause
    exit /b 1
) else (
    echo ✓ Python 依赖测试通过
)

echo.
echo ========================================
echo   依赖检查完成!
echo ========================================
echo.
echo ✅ 您的系统已准备好运行 GAL-SIM
echo.
echo 提示:
echo   - 请确保 .env 文件中已配置正确的 API 密钥
echo   - 如需启动应用，请运行 start_electron.sh 或直接启动 GAL-SIM
echo.
pause