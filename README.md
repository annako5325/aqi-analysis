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

### 🎯 最終提交結構
```
aqi-analysis/
├── data/
│   └── shelters_cleaned.csv                    
├── outputs/
│   ├── audit_report.md                         
│   ├── shelter_aqi_analysis.csv                
│   └── reflection.md                           
└── scripts/
    └── shelter_aqi_analysis.py                 
```

### 📊 檔案說明

#### 📁 data/
- **shelters_cleaned.csv** - 清理後的避難收容處所資料
  - 包含 5,889 筆避難收容處所記錄
  - 已移除邊界異常點位
  - 包含室內/戶外設施分類
  - 座標系統：WGS84經緯度

#### 📁 outputs/
- **audit_report.md** - 專案稽核報告
  - 資料來源與清理過程說明
  - 風險分析方法論
  - 品質指標與統計結果
  - 發現問題與改進建議

- **shelter_aqi_analysis.csv** - 風險分析結果
  - 每個避難收容處所的風險評估
  - 最近AQI測站資訊
  - 風險等級分類 (High Risk/Warning/Low Risk)
  - 風險分數與描述

- **reflection.md** - 專案反思文件
  - 專案執行摘要
  - 技術挑戰與解決方案
  - 學習經驗與改進建議
  - 未來發展方向

#### 📁 scripts/
- **shelter_aqi_analysis.py** - 主要分析腳本
  - 載入避難收容處所資料
  - 模擬AQI測站資料
  - 計算距離與風險評估
  - 生成分析結果檔案

## 🚀 快速開始

### 1. 安裝依賴
```bash
pip install pandas numpy
```

### 2. 執行主要分析腳本
```bash
cd aqi-analysis/scripts
python shelter_aqi_analysis.py
```

### 3. 檢視分析結果
執行完成後，在 `aqi-analysis/outputs/` 目錄中會生成：

- **📊 shelter_aqi_analysis.csv** - 風險分析結果
- **📋 audit_report.md** - 專案稽核報告  
- **📝 reflection.md** - 專案反思文件

### 4. 檢視資料來源
輸入資料位於 `aqi-analysis/data/shelters_cleaned.csv`，包含：
- 5,889 筆清理後的避難收容處所
- 完整的座標資訊
- 室內/戶外設施分類

## 📊 分析結果

### 🎯 風險評估方法
本專案採用三級風險分類系統：

- **High Risk** - 最近AQI測站 > 100
- **Warning** - 最近AQI測站 > 50 且為戶外設施
- **Low Risk** - 其他情況

### 📈 分析成果
- **處理設施** - 5,889 筆避難收容處所
- **風險評估** - 每個設施都有對應的風險等級
- **距離計算** - 基於真實地理座標的精確距離
- **設施分類** - 自動識別室內/戶外設施類型

### 🔍 主要輸出
#### shelter_aqi_analysis.csv
包含每個避難收容處所的詳細資訊：
- 設施名稱與位置
- 最近AQI測站資訊
- 風險等級與分數
- 設施類型分類

#### audit_report.md
完整的專案執行報告：
- 資料來源與品質說明
- 分析方法論詳述
- 統計結果與發現
- 品質保證措施

#### reflection.md
專案學習與反思：
- 技術挑戰與解決方案
- 改進建議與未來方向

## 🔧 技術規格

### 系統需求
- **Python**: 3.7+
- **記憶體**: 2GB+
- **作業系統**: Windows/macOS/Linux

### 核心套件
```python
import pandas as pd
import numpy as np
import os
import sys
```

### 資料格式
- **輸入**: CSV (UTF-8編碼)
- **輸出**: CSV, Markdown
- **座標系統**: WGS84經緯度

## � 專案特色

### 📊 資料處理
- **清理後資料**: 5,889 筆避難收容處所
- **座標驗證**: 移除異常點位
- **設施分類**: 自動識別室內/戶外設施

### 🎯 風險評估
- **三級分類**: High Risk/Warning/Low Risk
- **距離計算**: 基於地理座標的精確距離
- **模擬資料**: 20個AQI測站模擬真實情況

### 📋 完整文檔
- **稽核報告**: 詳細的執行過程記錄
- **分析結果**: 每個設施的風險評估
- **專案反思**: 學習經驗與改進建議

## � 使用說明

### 執行步驟
1. **安裝依賴**: `pip install pandas numpy`
2. **執行腳本**: `cd aqi-analysis/scripts && python shelter_aqi_analysis.py`
3. **檢視結果**: 查看 `outputs/` 目錄中的三個檔案

### 輸出檔案
- **shelter_aqi_analysis.csv** - 風險分析結果
- **audit_report.md** - 稽核報告
- **reflection.md** - 專案反思
