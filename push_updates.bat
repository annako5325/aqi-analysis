@echo off
chcp 65001 >nul
echo ========================================
echo AQI Analysis 重新推送
echo ========================================
echo.

cd /d "C:\Users\User\CascadeProjects\python_project"

echo 步驟 1: 檢查 Git 狀態...
git status

echo.
echo 步驟 2: 添加所有變更...
git add .
git add .gitignore
git add outputs/
git add aqi_twd97_results.csv

echo.
echo 步驟 3: 提交變更...
git commit -m "Update: Add outputs and TWD97 results to repository"

echo.
echo 步驟 4: 推送到 GitHub...
git push origin main

echo.
echo ========================================
echo 重新推送完成！
echo ========================================
echo.
echo 更新內容:
echo - .gitignore (移除 outputs/ 忽略)
echo - outputs/ (包含地圖和數據檔案)
echo - aqi_twd97_results.csv (TWD97 計算結果)
echo.
echo GitHub 倉庫: https://github.com/YOUR_USERNAME/aqi-analysis
echo.
echo 按任意鍵開啟 GitHub 倉庫...
pause >nul
start https://github.com/YOUR_USERNAME/aqi-analysis
