# 台灣 AQI 即時數據地圖生成器

這個程式可以串接環境部 API 獲取全台即時 AQI 數據，並使用 folium 在地圖上標示所有測站位置。

## 功能特色

- 串接環境部 API (aqx_p_432) 獲取即時空氣品質數據
- 使用不同顏色標示 AQI 等級（綠色良好到紅色危害）
- 顯示詳細的空氣品質資訊（PM2.5、PM10、NO₂、SO₂、CO、O₃）
- 互動式地圖，可點擊測站查看詳細資訊
- 自動處理環境安裝

## 安裝與設定

### 1. 安裝 Python 套件

```bash
pip install -r requirements.txt
```

### 2. 設定 API Key

在專案根目錄的 `.env` 檔案中新增環境部 API Key：

```
EPA_API_KEY=你的API金鑰
```

**如何取得 API Key：**
1. 前往 [環境部資料開放平台](https://data.epa.gov.tw/)
2. 註冊帳號並登入
3. 申請 API Key
4. 將 API Key 加入 `.env` 檔案

## 使用方法

執行程式：

```bash
python aqi_map.py
```

程式會：
1. 自動獲取最新的 AQI 數據
2. 生成互動式地圖
3. 將地圖保存為 `outputs/aqi_map.html`
4. 在瀏覽器中開啟地圖檔案即可查看結果

## AQI 顏色對應

| AQI 數值 | 等級 | 顏色 |
|---------|------|------|
| 0-50 | 良好 | 綠色 |
| 51-100 | 普通 | 黃色 |
| 101-150 | 對敏感族群不健康 | 橙色 |
| 151-200 | 對所有族群不健康 | 紅色 |
| 201-300 | 非常不健康 | 紫色 |
| 300+ | 危害 | 褐紅色 |

## 檔案結構

```
python_project/
├── aqi_map.py          # 主程式
├── requirements.txt    # Python 套件依賴
├── .env               # 環境變數設定（需自行建立）
├── outputs/           # 輸出目錄
│   └── aqi_map.html   # 生成的地圖檔案
└── README.md          # 說明文件
```

## 錯誤排除

### 常見問題

1. **API Key 錯誤**
   - 確認 `.env` 檔案中的 API Key 正確
   - 確認 API Key 仍有效且未超過使用限制

2. **網路連線問題**
   - 確認網路連線正常
   - 檢查防火牆設定

3. **套件安裝失敗**
   - 嘗試使用 `pip install --upgrade pip` 更新 pip
   - 確認 Python 版本為 3.7 或以上

## 技術規格

- Python 3.7+
- 主要套件：
  - `requests`: HTTP 請求
  - `folium`: 地圖視覺化
  - `python-dotenv`: 環境變數管理
  - `pandas`: 資料處理

## 授權

本專案僅供教育與研究使用，API 數據版權歸屬環境部所有。
