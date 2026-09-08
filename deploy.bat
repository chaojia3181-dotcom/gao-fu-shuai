@echo off
chcp 65001 >nul
echo ==========================================
echo  期货八种形态网站 - 一键部署助手
echo ==========================================
echo.

REM 检查 git
where git >nul 2>nul
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Git，请先安装 Git
    echo 下载地址: https://git-scm.com/download/win
    pause
    exit /b 1
)

REM 进入项目目录
cd /d "%~dp0"

set /p USERNAME="请输入你的 GitHub 用户名: "

if "%USERNAME%"=="" (
    echo [错误] 用户名不能为空
    pause
    exit /b 1
)

echo.
echo [1/3] 正在添加远程仓库...
git remote add origin https://github.com/%USERNAME%/gao-fu-shuai.git 2>nul
git branch -M main

echo [2/3] 正在推送代码到 GitHub...
git push -u origin main

if %errorlevel% neq 0 (
    echo.
    echo [提示] 推送失败，可能需要输入 GitHub 用户名和密码
    echo 如果提示输入密码，请使用 GitHub Personal Access Token
    echo 获取方式: GitHub 头像 → Settings → Developer settings → Personal access tokens
    pause
    exit /b 1
)

echo.
echo ==========================================
echo  ✅ 代码推送成功！
echo ==========================================
echo.
echo 下一步：部署到 Vercel（国内访问快）
echo.
echo 1. 打开浏览器访问: https://vercel.com
echo 2. 点击 Sign Up → Continue with GitHub
echo 3. 点击 Add New Project
echo 4. 找到 gao-fu-shuai 仓库，点击 Import
echo 5. Framework Preset 选 Other，点击 Deploy
echo.
echo 部署完成后，你会得到一个网址：
echo https://gao-fu-shuai-%USERNAME%.vercel.app
echo.
echo 网站每天 15:35 自动更新期货数据！
echo.
pause
