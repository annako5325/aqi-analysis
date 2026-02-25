# 手動 GitHub 部署指南

## 🚀 將 AQI Analysis 專案部署到 GitHub

### 📋 部署前檢查清單

- [x] ✅ Python 程式完成
- [x] ✅ TWD97 距離計算實作
- [x] ✅ CSV 數據輸出功能
- [x] ✅ 互動式地圖生成
- [x] ✅ 部署腳本準備
- [ ] ❌ Git 安裝
- [ ] ❌ GitHub CLI 登入
- [ ] ❌ GitHub 倉庫創建

---

## 🔧 安裝必要工具

### 1. 安裝 Git
```bash
# 下載並安裝 Git for Windows
# https://git-scm.com/download/win

# 或使用 Chocolatey
choco install git
```

### 2. 安裝 GitHub CLI
```bash
# 下載並安裝 GitHub CLI
# https://cli.github.com/

# 或使用 Chocolatey
choco install gh
```

### 3. 驗證安裝
```bash
git --version
gh --version
```

---

## 🔐 登入 GitHub

### 方法一：使用 GitHub CLI
```bash
gh auth login
```
按照提示操作：
1. 選擇 `GitHub.com`
2. 選擇 `HTTPS`
3. 選擇 `Use web browser to sign in`
4. 複製認證碼並貼上

### 方法二：使用 Personal Access Token
```bash
# 設定環境變數
export GH_TOKEN=your_personal_access_token
```

---

## 📁 部署步驟

### 步驟 1：初始化 Git 倉庫
```bash
cd c:\Users\User\CascadeProjects\python_project
git init
git add .
git commit -m "Initial commit: AQI Analysis Project with TWD97"
git branch -M main
```

### 步驟 2：創建 GitHub 倉庫
```bash
gh repo create aqi-analysis --public --source=. --remote=origin --push
```

### 步驟 3：驗證部署
```bash
# 檢查遠端倉庫
git remote -v

# 檢查推送狀態
git status
```

---

## 📊 專案檔案結構

部署後的 GitHub 倉庫將包含：

```
aqi-analysis/
├── aqi_map.py              # 主程式（TWD97 距離計算）
├── deploy.py               # 自動部署腳本
├── test_coordinates.py     # 座標轉換測試
├── check_results.py        # 結果檢查腳本
├── requirements.txt        # Python 依賴
├── README.md              # 專案說明
├── DEPLOY.md              # 部署指南
├── MANUAL_DEPLOY.md       # 手動部署指南
├── .env                   # 環境變數（已 gitignore）
├── .gitignore             # Git 忽略檔案
├── aqi_twd97_results.csv  # TWD97 計算結果
└── outputs/               # 輸出目錄
    ├── aqi_map.html       # 互動式地圖
    └── aqi_analysis.csv  # 數據分析
```

---

## 🎯 專案特色

### ✅ 已實現功能
- **即時數據獲取**：串接環境部 API 獲取 85 個測站數據
- **TWD97 精確計算**：使用台灣二度分帶座標系統
- **空間分析**：計算測站到台北車站的精確距離
- **視覺化地圖**：互動式 Folium 地圖顯示 AQI 分佈
- **數據導出**：CSV 格式的完整分析結果
- **統計分析**：距離分佈和極值資訊

### 📈 技術規格
- **座標系統**：WGS84 → TWD97 轉換
- **距離計算**：歐幾里得平面距離
- **精度範圍**：台灣區域內 < 0.3% 誤差
- **數據格式**：UTF-8 CSV 輸出
- **地圖格式**：HTML 互動式地圖

---

## 🔗 部署完成後

### GitHub 倉庫地址
```
https://github.com/YOUR_USERNAME/aqi-analysis
```

### 檔案說明
- **主程式**：`aqi_map.py` - 完整的 AQI 分析系統
- **數據結果**：`aqi_twd97_results.csv` - TWD97 距離計算結果
- **互動地圖**：`outputs/aqi_map.html` - 可直接開啟的地圖
- **部署指南**：`DEPLOY.md` 和 `MANUAL_DEPLOY.md`

### 使用方式
```bash
# 執行程式
python aqi_map.py

# 查看結果
python check_results.py

# 測試座標轉換
python test_coordinates.py
```

---

## 🛠 故障排除

### Git 未安裝
```bash
# 檢查 Git 安裝
where git

# 重新安裝 Git
# https://git-scm.com/download/win
```

### GitHub CLI 未登入
```bash
# 重新登入
gh auth login

# 檢查登入狀態
gh auth status
```

### 權限問題
```bash
# 以管理員身份執行 PowerShell
# 或設定執行政策
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 📞 後續維護

### 更新程式碼
```bash
git add .
git commit -m "Update: 描述變更內容"
git push origin main
```

### 新增功能
1. 修改程式碼
2. 測試功能
3. 提交變更
4. 推送到 GitHub

---

**完成部署後，您就擁有一個完整的 TWD97 AQI 分析系統！** 🌍✨
