#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
避難收容處所 AQI 風險分析與情境模擬
模擬高AQI情境以驗證風險標籤準確性
"""

import pandas as pd
import numpy as np
import math
import os
import sys

class ShelterAQIAnalysis:
    """避難收容處所 AQI 風險分析器"""
    
    def __init__(self):
        self.shelter_data = None
        self.aqi_data = None
        self.risk_analysis = None
        
    def load_data(self):
        """載入資料"""
        print("載入資料...")
        
        # 載入避難收容處所資料
        shelter_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'shelters_cleaned.csv')
        try:
            self.shelter_data = pd.read_csv(shelter_path, encoding='utf-8')
            print(f"載入避難收容處所: {len(self.shelter_data)} 筆")
        except Exception as e:
            print(f"載入避難收容處所失敗: {e}")
            return False
        
        # 使用模擬 AQI 資料
        self.aqi_data = self._create_sample_aqi_data()
        
        return True
    
    def _create_sample_aqi_data(self):
        """創建模擬 AQI 資料"""
        stations = [
            {'SiteName': '基隆', 'County': '基隆市', 'AQI': 45, 'PM25': 12.6, 'lat': 25.129167, 'lon': 121.760056},
            {'SiteName': '台北', 'County': '台北市', 'AQI': 65, 'PM25': 18.2, 'lat': 25.0330, 'lon': 121.5654},
            {'SiteName': '新北', 'County': '新北市', 'AQI': 58, 'PM25': 16.2, 'lat': 25.0173, 'lon': 121.4625},
            {'SiteName': '桃園', 'County': '桃園市', 'AQI': 72, 'PM25': 20.2, 'lat': 24.9936, 'lon': 121.3010},
            {'SiteName': '新竹', 'County': '新竹市', 'AQI': 48, 'PM25': 13.4, 'lat': 24.8138, 'lon': 120.9675},
            {'SiteName': '苗栗', 'County': '苗栗市', 'AQI': 52, 'PM25': 14.6, 'lat': 24.5646, 'lon': 120.8214},
            {'SiteName': '台中', 'County': '台中市', 'AQI': 85, 'PM25': 23.8, 'lat': 24.1477, 'lon': 120.6736},
            {'SiteName': '彰化', 'County': '彰化市', 'AQI': 68, 'PM25': 19.0, 'lat': 24.0771, 'lon': 120.5428},
            {'SiteName': '南投', 'County': '南投市', 'AQI': 55, 'PM25': 15.4, 'lat': 23.9096, 'lon': 120.6838},
            {'SiteName': '雲林', 'County': '雲林市', 'AQI': 62, 'PM25': 17.4, 'lat': 23.6990, 'lon': 120.4329},
            {'SiteName': '嘉義', 'County': '嘉義市', 'AQI': 74, 'PM25': 20.7, 'lat': 23.4801, 'lon': 120.4491},
            {'SiteName': '台南', 'County': '台南市', 'AQI': 67, 'PM25': 18.8, 'lat': 22.9999, 'lon': 120.2269},
            {'SiteName': '高雄', 'County': '高雄市', 'AQI': 125, 'PM25': 35.0, 'lat': 22.6273, 'lon': 120.3014},
            {'SiteName': '屏東', 'County': '屏東市', 'AQI': 56, 'PM25': 15.7, 'lat': 22.6697, 'lon': 120.4859},
            {'SiteName': '宜蘭', 'County': '宜蘭市', 'AQI': 38, 'PM25': 10.6, 'lat': 24.6929, 'lon': 121.7216},
            {'SiteName': '花蓮', 'County': '花蓮市', 'AQI': 35, 'PM25': 9.8, 'lat': 23.9759, 'lon': 121.6034},
            {'SiteName': '台東', 'County': '台東市', 'AQI': 42, 'PM25': 11.8, 'lat': 22.7553, 'lon': 121.1506},
            {'SiteName': '澎湖', 'County': '澎湖縣', 'AQI': 40, 'PM25': 11.2, 'lat': 23.5697, 'lon': 119.5665},
            {'SiteName': '金門', 'County': '金門縣', 'AQI': 48, 'PM25': 13.4, 'lat': 24.4330, 'lon': 118.3222},
            {'SiteName': '馬祖', 'County': '連江縣', 'AQI': 32, 'PM25': 9.0, 'lat': 26.1616, 'lon': 119.9368}
        ]
        return pd.DataFrame(stations)
    
    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """計算兩點間的距離（公里）"""
        R = 6371  # 地球半徑（公里）
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat/2)**2 + 
              math.cos(lat1_rad) * math.cos(lat2_rad) * 
              math.sin(delta_lon/2)**2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    def find_nearest_aqi_station(self, shelter_lat, shelter_lon):
        """尋找最近的 AQI 測站"""
        min_distance = float('inf')
        nearest_station = None
        
        for _, station in self.aqi_data.iterrows():
            distance = self.calculate_distance(
                shelter_lat, shelter_lon,
                station['lat'], station['lon']
            )
            
            if distance < min_distance:
                min_distance = distance
                nearest_station = station
        
        return nearest_station, min_distance
    
    def perform_risk_analysis(self):
        """執行風險分析"""
        print("執行風險分析...")
        
        risk_results = []
        
        for idx, shelter in self.shelter_data.iterrows():
            shelter_lat = shelter['緯度']
            shelter_lon = shelter['經度']
            shelter_name = shelter['避難收容處所名稱']
            is_indoor = shelter['is_indoor']
            county = shelter.get('縣市及鄉鎮市區', '未知')
            
            # 尋找最近的 AQI 測站
            nearest_station, distance = self.find_nearest_aqi_station(
                shelter_lat, shelter_lon
            )
            
            if nearest_station is not None:
                nearest_aqi = nearest_station['AQI']
                nearest_station_name = nearest_station['SiteName']
                nearest_station_county = nearest_station['County']
                
                # 風險標籤邏輯
                if nearest_aqi > 100:
                    risk_level = "High Risk"
                    risk_description = f"最近測站 AQI {nearest_aqi} > 100"
                elif nearest_aqi > 50 and not is_indoor:
                    risk_level = "Warning"
                    risk_description = f"最近測站 AQI {nearest_aqi} > 50 且為戶外設施"
                else:
                    risk_level = "Low Risk"
                    risk_description = "風險較低"
                
                # 計算風險分數
                risk_score = 0
                if nearest_aqi > 100:
                    risk_score += 50
                elif nearest_aqi > 50:
                    risk_score += 25
                
                if not is_indoor:
                    risk_score += 20
                
                # 距離懲罰
                if distance > 20:
                    risk_score += 10
                elif distance > 10:
                    risk_score += 5
                
                risk_score = min(100, risk_score)
                
                result = {
                    '避難收容處所名稱': shelter_name,
                    '縣市及鄉鎮市區': county,
                    '緯度': shelter_lat,
                    '經度': shelter_lon,
                    'is_indoor': is_indoor,
                    '設施類型': '室內設施' if is_indoor else '戶外設施',
                    '最近AQI測站': nearest_station_name,
                    '測站縣市': nearest_station_county,
                    '最近測站AQI': nearest_aqi,
                    '距離測站(km)': round(distance, 2),
                    '風險等級': risk_level,
                    '風險描述': risk_description,
                    '風險分數': risk_score
                }
                
                risk_results.append(result)
        
        self.risk_analysis = pd.DataFrame(risk_results)
        print(f"完成 {len(risk_results)} 個避難收容處所的風險分析")
        
        return self.risk_analysis
    
    def save_results(self):
        """儲存分析結果"""
        if self.risk_analysis is None:
            print("請先執行風險分析")
            return
        
        # 確保 outputs 目錄存在
        output_dir = os.path.join(os.path.dirname(__file__), '..', 'outputs')
        os.makedirs(output_dir, exist_ok=True)
        
        # 儲存分析結果
        output_file = os.path.join(output_dir, 'shelter_aqi_analysis.csv')
        self.risk_analysis.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"風險分析結果已儲存至: {output_file}")
    
    def run_analysis(self):
        """執行完整分析流程"""
        print("=" * 60)
        print("AQI 避難收容處所風險分析")
        print("=" * 60)
        
        # 載入資料
        if not self.load_data():
            print("載入資料失敗")
            return False
        
        # 執行風險分析
        self.perform_risk_analysis()
        
        # 儲存結果
        self.save_results()
        
        print("\n" + "=" * 60)
        print("風險分析完成！")
        print("=" * 60)
        
        return True

def main():
    """主程式"""
    if len(sys.argv) > 1:
        if sys.argv[1] == '--help':
            print("用法: python shelter_aqi_analysis.py")
            print("功能: 執行 AQI 避難收容處所風險分析")
            return
    
    analyzer = ShelterAQIAnalysis()
    success = analyzer.run_analysis()
    
    if success:
        print("分析成功完成！")
    else:
        print("分析失敗，請檢查錯誤訊息。")
        sys.exit(1)

if __name__ == "__main__":
    main()
