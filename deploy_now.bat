@echo off
chcp 65001 >nul
echo ========================================
echo AQI Analysis 自動部署
echo ========================================
echo.

cd /d "C:\Users\User\CascadeProjects\python_project"

echo 步驟 1: 檢查 Git 安裝...
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 錯誤: Git 未安裝或未在 PATH 中
    echo.
    echo 請按照以下步驟安裝 Git:
    echo 1. 前往 https://git-scm.com/download/win
    echo 2. 下載 Git for Windows Setup
    echo 3. 安裝時務必勾選 "Add Git to PATH"
    echo 4. 重新開啟命令提示字元
    echo.
    echo 安裝完成後請重新執行此批次檔
    echo.
    pause
    exit /b 1
)

echo Git 已安裝: 
git --version
echo.

echo 步驟 2: 檢查 GitHub CLI 登入...
gh auth status >nul 2>&1
if %errorlevel% neq 0 (
    echo 錯誤: GitHub CLI 未登入
    echo 請先執行: gh auth login
    echo.
    pause
    exit /b 1
)

echo GitHub CLI 已登入
echo.

echo 步驟 3: 初始化 Git 倉庫...
git init
git add .
git commit -m "Initial commit: AQI Analysis Project with TWD97"
git branch -M main

echo.
echo 步驟 4: 創建 GitHub 倉庫...
gh repo create aqi-analysis --public --source=. --remote=origin --push

echo.
echo ========================================
echo 部署完成！
echo ========================================
echo.
echo 專案檔案:
echo - aqi_map.py (主程式)
echo - aqi_twd97_results.csv (TWD97 計算結果)
echo - outputs/aqi_map.html (互動式地圖)
echo - outputs/aqi_analysis.csv (數據分析)
echo.
echo GitHub 倉庫: https://github.com/YOUR_USERNAME/aqi-analysis
echo.
echo 按任意鍵開啟 GitHub 倉庫...
pause >nul
start https://github.com/YOUR_USERNAME/aqi-analysis
