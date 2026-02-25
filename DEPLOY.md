# GitHub 部署指南

## 🚀 將 AQI Analysis 專案部署到 GitHub

### 前置需求

1. **安裝 Git**
   - 下載地址: https://git-scm.com/download/win
   - 安裝時使用預設設定即可

2. **安裝 GitHub CLI**
   - 下載地址: https://cli.github.com/
   - 或使用 Chocolatey: `choco install gh`

### 部署步驟

#### 方法一：自動部署（推薦）

```bash
# 執行自動部署腳本
python deploy.py
```

#### 方法二：手動部署

1. **登入 GitHub**
   ```bash
   gh auth login
   ```
   - 選擇 `GitHub.com`
   - 選擇 `HTTPS`
   - 選擇 `Use web browser to sign in`
   - 複製並貼上認證碼

2. **初始化 Git 倉庫**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: AQI Analysis Project"
   git branch -M main
   ```

3. **創建 GitHub 倉庫**
   ```bash
   gh repo create aqi-analysis --public --source=. --remote=origin --push
   ```

### 📁 專案結構

部署完成後，您的 GitHub 倉庫將包含：

```
aqi-analysis/
├── aqi_map.py          # 主程式
├── deploy.py           # 部署腳本
├── requirements.txt    # Python 依賴
├── README.md          # 專案說明
├── DEPLOY.md          # 部署指南
├── .env               # 環境變數（已 gitignore）
├── .gitignore         # Git 忽略檔案
└── outputs/           # 輸出目錄
    ├── aqi_map.html   # 互動式地圖
    └── aqi_analysis.csv # 數據分析
```

### 🔗 部署完成後

- **GitHub 倉庫**: https://github.com/YOUR_USERNAME/aqi-analysis
- **線上地圖**: 可直接在瀏覽器開啟 `outputs/aqi_map.html`
- **數據下載**: 可下載 `outputs/aqi_analysis.csv` 查看分析結果

### 🎯 專案特色

- ✅ **即時數據**: 串接環境部 API 獲取真實 AQI 數據
- ✅ **空間分析**: 計算測站到台北車站的距離
- ✅ **視覺化**: 互動式地圖顯示空氣品質分佈
- ✅ **數據導出**: CSV 格式的分析結果
- ✅ **雲端備份**: GitHub 版本控制與協作

### 🛠 故障排除

#### Git 未找到
```bash
# 確認 Git 安裝路徑
where git

# 如果未安裝，請下載安裝
# https://git-scm.com/download/win
```

#### GitHub CLI 未登入
```bash
# 重新登入
gh auth login

# 檢查登入狀態
gh auth status
```

#### 權限問題
```bash
# 如果遇到權限問題，可能需要以管理員身份執行
# 或檢查 PowerShell 執行政策
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 📞 技術支援

如遇到問題，請檢查：
1. 網路連線是否正常
2. Git 和 GitHub CLI 是否正確安裝
3. GitHub 登入是否有效
4. 專案目錄權限是否正確

---

**部署完成後，您就擁有一個完整的 AQI 空氣品質分析系統！** 🌍✨
