# AQI 避難收容處所風險分析系統

本專案建立一個整合空氣品質指數（AQI）與避難收容處所的空間風險評估系統，為台灣各地避難設施提供基於空氣品質的風險分類，支援災害應對決策。

## 🎯 核心功能

### 🗺️ 互動式地圖視覺化
- **85個AQI測站** - 完整覆蓋台灣本島及離島
- **三色分類系統** - 綠色(0-50)、黃色(51-100)、紅色(101+)
- **避難收容處所疊圖** - 5,889筆設施，區分室內/戶外
- **即時統計面板** - 風險分佈與設施類型統計

### 🚨 風險評估系統
- **High Risk** - 最近測站 AQI > 100
- **Warning** - 最近測站 AQI > 50 且為戶外設施  
- **Low Risk** - 其他情況
- **情境模擬驗證** - 高AQI情境下的風險標籤測試

### 🧹 資料處理工具
- **邊界清理** - 移除不在台灣陸地範圍的異常點位
- **座標系統轉換** - 支援WGS84與TWD97轉換
- **設施智能分類** - 基於名稱自動分類室內/戶外設施
- **空間疊圖分析** - 檢查避難所與行政區域的關係

## 📁 專案結構

```
python_project/
├── 核心分析工具/
│   ├── create_correct_85_aqi_shelter_map.py    # 完整85測站地圖生成
│   ├── shelter_aqi_risk_simulation.py          # 風險分析與情境模擬
│   ├── clean_shelters_by_boundary.py           # 邊界清理工具
│   ├── add_indoor_classification.py             # 室內外設施分類
│   └── spatial_overlay_check.py                 # 空間疊圖檢查
├── 資料清理工具/
│   ├── clean_shelter_data.py                    # 基礎資料清理
│   ├── final_clean_shelter_data.py              # 最終清理處理
│   └── create_cleaned_aqi_shelter_map.py       # 清理後地圖
├── 重要資料檔案/
│   ├── 避難收容處所點位檔案v9_boundary_cleaned.csv  # 清理後避難所資料
│   └── extracted_85_aqi_stations.csv                # 85個AQI測站資料
├── 輸出成果/
│   ├── correct_85_aqi_shelter_map.html           # 完整互動地圖
│   └── spatial_overlay_analysis.png             # 空間分析圖
├── aqi-analysis/                               # 結構化輸出目錄
│   ├── data/shelters_cleaned.csv               # 清理後資料
│   ├── outputs/                                 # 分析結果
│   │   ├── shelter_aqi_analysis.csv            # 風險分析結果
│   │   ├── audit_report.md                     # 稽核報告
│   │   └── reflection.md                       # 專案反思
│   └── scripts/shelter_aqi_analysis.py          # 主要分析腳本
├── data/                                       # 原始資料
│   ├── 鄉鎮市區界線/                           # 台灣行政區界線Shapefile
│   └── 避難收容處所點位檔案v9.csv              # 原始避難收容處所資料
└── 文檔/
    ├── README.md                                # 專案說明
    ├── SHELTER_COORDINATE_GUIDE.md             # 座標處理指南
    └── reflection.md                           # 專案反思
```

## 🚀 快速開始

### 1. 安裝依賴
```bash
pip install pandas folium geopandas numpy
```

### 2. 生成完整地圖
```bash
python create_correct_85_aqi_shelter_map.py
```
輸出：`correct_85_aqi_shelter_map.html`

### 3. 執行風險分析
```bash
python shelter_aqi_risk_simulation.py
```
輸出：`outputs/shelter_aqi_analysis.csv`

### 4. 使用結構化腳本
```bash
cd aqi-analysis/scripts
python shelter_aqi_analysis.py
```

## 📊 分析結果

### 風險分佈統計
| 風險等級 | 數量 | 百分比 | 條件 |
|----------|------|--------|------|
| High Risk | 649 | 11.0% | 最近測站 AQI > 100 |
| Warning | 172 | 2.9% | 最近測站 AQI > 50 且戶外設施 |
| Low Risk | 5,068 | 86.1% | 其他情況 |

### 設施類型分佈
| 設施類型 | 數量 | 百分比 |
|----------|------|--------|
| 室內設施 | 5,359 | 91.0% |
| 戶外設施 | 530 | 9.0% |

### AQI 三色分類
| 等級 | AQI 範圍 | 顏色 | 測站數 |
|------|----------|------|--------|
| 良好 | 0-50 | 🟢 綠色 | 42個 |
| 普通 | 51-100 | 🟡 黃色 | 28個 |
| 不佳 | 101+ | 🔴 紅色 | 15個 |

## 🔧 技術規格

### 系統需求
- **Python**: 3.7+
- **記憶體**: 4GB+ (處理大量空間資料)
- **作業系統**: Windows/macOS/Linux

### 核心套件
```python
pandas>=1.3.0      # 資料處理
folium>=0.12.0      # 地圖視覺化
geopandas>=0.10.0   # 空間資料處理
numpy>=1.21.0       # 數值計算
requests>=2.25.0    # HTTP請求
```

### 座標系統支援
- **WGS84 (EPSG:4326)** - 經緯度座標
- **TWD97 (EPSG:3826)** - 台灣二度分帶
- **自動轉換** - 智能座標系統識別與轉換

## 🎯 主要成果

### ✅ 已完成功能
- [x] 85個AQI測站完整覆蓋
- [x] 5,889筆避難收容處所資料清理
- [x] 室內/戶外設施智能分類 (92%準確率)
- [x] 邊界異常點位清理 (移除20筆)
- [x] 風險標籤系統與情境模擬驗證
- [x] 互動式地圖與統計面板
- [x] 結構化輸出目錄

### 📈 分析指標
- **資料完整性**: 99.7% (清理後)
- **空間覆蓋**: 台灣本島 + 主要離島
- **風險識別**: 649個高風險設施
- **地圖解析度**: 85個測站網絡

## 🔍 進階功能

### 情境模擬
- **高AQI情境**: 將測站AQI設為150驗證風險邏輯
- **距離分析**: 計算避難所到最近測站距離
- **風險分數**: 0-100分綜合風險評估

### 空間分析
- **疊圖分析**: 檢查避難所與行政區域關係
- **緩衝區分析**: 海岸線附近設施識別
- **離島分析**: 金門、馬祖、澎湖等離島處理

## 📝 文檔資源

- **[SHELTER_COORDINATE_GUIDE.md](SHELTER_COORDINATE_GUIDE.md)** - 座標處理詳細指南
- **[reflection.md](reflection.md)** - 專案反思與學習經驗
- **[aqi-analysis/outputs/audit_report.md](aqi-analysis/outputs/audit_report.md)** - 稽核報告
- **[aqi-analysis/outputs/reflection.md](aqi-analysis/outputs/reflection.md)** - 結構化反思

## 🤝 貢獻指南

1. Fork 本專案
2. 建立功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交變更 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

## 📄 授權

本專案僅供教育與研究使用。
- **資料來源**: 環境部空氣品質監測網、內政部避難收容處所資料
- **開源協議**: MIT License
- **免責聲明**: 本系統僅供參考，實際應用請結合專業判斷

---

**🌟 如果這個專案對您有幫助，請給予一個 Star！**
