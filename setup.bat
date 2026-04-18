@echo off
chcp 65001 >nul
echo ========================================
echo PPT Logo Remover v5.0 - 环境搭建
echo ========================================

set SKILL_DIR=%~dp0
set VENV_DIR=%SKILL_DIR%.venv

if exist "%VENV_DIR%\Scripts\python.exe" (
    echo 虚拟环境已存在: %VENV_DIR%
    echo 如需重建，请先删除 .venv 目录
    goto :install_deps
)

echo 正在创建虚拟环境...
python -m venv "%VENV_DIR%"
if errorlevel 1 (
    echo 错误：创建虚拟环境失败
    pause
    exit /b 1
)
echo 虚拟环境创建成功

:install_deps
echo 正在升级 pip...
"%VENV_DIR%\Scripts\python.exe" -m pip install --upgrade pip -q

echo 正在安装基础依赖 (Pillow, numpy, opencv-python)...
"%VENV_DIR%\Scripts\pip.exe" install Pillow numpy opencv-python -i https://pypi.tuna.tsinghua.edu.cn/simple

echo.
echo 正在安装 LaMa AI 依赖 (simple-lama-inpainting, torch)...
echo （首次安装可能需要几分钟，约2GB）
"%VENV_DIR%\Scripts\pip.exe" install simple-lama-inpainting -i https://pypi.tuna.tsinghua.edu.cn/simple

echo.
echo ========================================
echo 环境搭建完成！
echo.
echo 虚拟环境: %VENV_DIR%
echo 主脚本会自动检测并使用此环境。
echo ========================================
pause
