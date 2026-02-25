# 🔧 手動 Git 和 GitHub 部署命令

## 📋 前置檢查

### 1. 檢查 Git 安裝
```bash
git --version
```

### 2. 檢查 GitHub CLI 登入
```bash
gh auth status
```

---

## 🚀 完整部署命令

### 步驟 1：開啟命令提示字元

**方法一：使用 PowerShell**
1. 按 `Win + X`
2. 選擇 "Windows PowerShell (管理員)"
3. 或搜尋 "PowerShell" 並以管理員身份執行

**方法二：使用命令提示字元**
1. 按 `Win + R`
2. 輸入 `cmd`
3. 按 `Ctrl + Shift + Enter` 以管理員身份執行

### 步驟 2：切換到專案目錄
```bash
cd C:\Users\User\CascadeProjects\python_project
```

### 步驟 3：初始化 Git 倉庫
```bash
git init
git add .
git commit -m "Initial commit: AQI Analysis Project with TWD97"
git branch -M main
```

### 步驟 4：創建 GitHub 倉庫並推送
```bash
gh repo create aqi-analysis --public --source=. --remote=origin --push
```

---

## 🔍 如果 Git 未安裝

### 下載 Git
1. 前往：https://git-scm.com/download/win
2. 下載 64-bit Git for Windows Setup
3. 執行安裝程式
4. 使用預設設定完成安裝

### 驗證安裝
```bash
# 重新開啟命令提示字元後執行
git --version
```

---

## 🛠 故障排除

### 如果找不到 git 命令：

**方法一：檢查 PATH**
```bash
echo $PATH
```

**方法二：使用完整路徑**
```bash
# 如果 Git 安裝在預設位置
"C:\Program Files\Git\bin\git.exe" init
"C:\Program Files\Git\bin\git.exe" add .
"C:\Program Files\Git\bin\git.exe" commit -m "Initial commit: AQI Analysis Project with TWD97"
"C:\Program Files\Git\bin\git.exe" branch -M main
```

**方法三：重新安裝 Git**
1. 解除現有 Git
2. 重新下載並安裝
3. 確保勾選 "Add Git to PATH"

### 如果 GitHub CLI 命令失敗：

**重新登入**
```bash
gh auth logout
gh auth login
```

**檢查網路連線**
```bash
ping github.com
```

---

## 📱 一鍵部署腳本

創建 `deploy_now.bat` 檔案：

```batch
@echo off
echo ========================================
echo AQI Analysis 自動部署
echo ========================================
echo.

cd /d "C:\Users\User\CascadeProjects\python_project"

echo 步驟 1: 初始化 Git 倉庫...
git init
git add .
git commit -m "Initial commit: AQI Analysis Project with TWD97"
git branch -M main

echo.
echo 步驟 2: 創建 GitHub 倉庫...
gh repo create aqi-analysis --public --source=. --remote=origin --push

echo.
echo ========================================
echo 部署完成！
echo ========================================
echo GitHub 倉庫: https://github.com/YOUR_USERNAME/aqi-analysis
echo.
pause
```

使用方式：
1. 儲存為 `deploy_now.bat`
2. 雙擊執行
3. 按照提示操作

---

## 🎯 預期結果

### 成功後會看到：
```
Initialized empty Git repository in C:/Users/User/CascadeProjects/python_project/.git/
[master (root-commit) 1234567] Initial commit: AQI Analysis Project with TWD97
 87 files changed, 12345 insertions(+)
Created repository 'https://github.com/YOUR_USERNAME/aqi-analysis'
✓ Added repository https://github.com/YOUR_USERNAME/aqi-analysis
✓ Merged default branch into main
✓ Pushed files to repository
```

### GitHub 倉庫地址：
```
https://github.com/YOUR_USERNAME/aqi-analysis
```

---

## 📞 後續操作

### 檢查遠端倉庫
```bash
git remote -v
```

### 查看倉庫資訊
```bash
gh repo view aqi-analysis
```

### 推送更新
```bash
git add .
git commit -m "Update: 描述變更內容"
git push origin main
```

---

**按照上述步驟手動執行即可完成部署！** 🚀✨
