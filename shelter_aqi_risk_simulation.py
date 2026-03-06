#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
避難收容處所 AQI 風險分析與情境模擬
模擬高 AQI 情境以驗證風險標籤邏輯
"""

import pandas as pd
import numpy as np
from scipy.spatial import cKDTree
import math

class ShelterAQIRiskAnalysis:
    """避難收容處所 AQI 風險分析器"""
    
    def __init__(self):
        self.shelter_data = None
        self.aqi_data = None
        self.risk_analysis = None
        
    def load_data(self):
        """載入數據"""
        print("載入數據...")
        
        # 載入避難收容處所數據
        try:
            self.shelter_data = pd.read_csv('避難收容處所點位檔案v9_boundary_cleaned.csv')
            print(f"載入避難收容處所: {len(self.shelter_data)} 筆")
        except Exception as e:
            print(f"載入避難收容處所失敗: {e}")
            return False
        
        # 載入 AQI 測站數據
        try:
            self.aqi_data = pd.read_csv('extracted_85_aqi_stations.csv')
            print(f"載入 AQI 測站: {len(self.aqi_data)} 筆")
        except Exception as e:
            print(f"載入 AQI 測站失敗: {e}")
            return False
        
        return True
    
    def simulate_high_aqi_scenario(self):
        """模擬高 AQI 情境"""
        print("\n進行情境模擬...")
        
        # 檢查原始 AQI 分佈
        original_stats = {
            'mean': self.aqi_data['AQI'].mean(),
            'max': self.aqi_data['AQI'].max(),
            'min': self.aqi_data['AQI'].min(),
            'good_count': len(self.aqi_data[self.aqi_data['AQI'] <= 50]),
            'moderate_count': len(self.aqi_data[(self.aqi_data['AQI'] > 50) & (self.aqi_data['AQI'] <= 100)]),
            'poor_count': len(self.aqi_data[self.aqi_data['AQI'] > 100])
        }
        
        print(f"原始 AQI 統計:")
        print(f"  平均值: {original_stats['mean']:.1f}")
        print(f"  最大值: {original_stats['max']}")
        print(f"  最小值: {original_stats['min']}")
        print(f"  良好 (≤50): {original_stats['good_count']} 個")
        print(f"  普通 (51-100): {original_stats['moderate_count']} 個")
        print(f"  不佳 (>100): {original_stats['poor_count']} 個")
        
        # 模擬情境：將高雄測站的 AQI 設為 150
        print(f"\n🚨 情境模擬：將高雄測站 AQI 設為 150")
        
        # 找到高雄測站
        kaohsiung_stations = self.aqi_data[self.aqi_data['County'].str.contains('高雄', na=False)]
        if len(kaohsiung_stations) > 0:
            # 將第一個高雄測站的 AQI 設為 150
            target_idx = kaohsiung_stations.index[0]
            original_aqi = self.aqi_data.loc[target_idx, 'AQI']
            self.aqi_data.loc[target_idx, 'AQI'] = 150
            self.aqi_data.loc[target_idx, 'PM25'] = 42.0  # 對應的 PM2.5
            
            print(f"  將 {self.aqi_data.loc[target_idx, 'SiteName']} 測站")
            print(f"  AQI 從 {original_aqi} 調整為 150")
            print(f"  PM2.5 調整為 42.0 μg/m³")
        else:
            # 如果沒有找到高雄測站，選擇南部地區的測站
            southern_stations = self.aqi_data[
                (self.aqi_data['lat'] < 23.5) & 
                (self.aqi_data['lon'] > 120.0)
            ]
            if len(southern_stations) > 0:
                target_idx = southern_stations.index[0]
                original_aqi = self.aqi_data.loc[target_idx, 'AQI']
                self.aqi_data.loc[target_idx, 'AQI'] = 150
                self.aqi_data.loc[target_idx, 'PM25'] = 42.0
                
                print(f"  將 {self.aqi_data.loc[target_idx, 'SiteName']} 測站")
                print(f"  AQI 從 {original_aqi} 調整為 150")
                print(f"  PM2.5 調整為 42.0 μg/m³")
        
        # 顯示模擬後的統計
        simulated_stats = {
            'mean': self.aqi_data['AQI'].mean(),
            'max': self.aqi_data['AQI'].max(),
            'min': self.aqi_data['AQI'].min(),
            'good_count': len(self.aqi_data[self.aqi_data['AQI'] <= 50]),
            'moderate_count': len(self.aqi_data[(self.aqi_data['AQI'] > 50) & (self.aqi_data['AQI'] <= 100)]),
            'poor_count': len(self.aqi_data[self.aqi_data['AQI'] > 100])
        }
        
        print(f"\n模擬後 AQI 統計:")
        print(f"  平均值: {simulated_stats['mean']:.1f}")
        print(f"  最大值: {simulated_stats['max']}")
        print(f"  最小值: {simulated_stats['min']}")
        print(f"  良好 (≤50): {simulated_stats['good_count']} 個")
        print(f"  普通 (51-100): {simulated_stats['moderate_count']} 個")
        print(f"  不佳 (>100): {simulated_stats['poor_count']} 個")
    
    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """計算兩點間的距離（公里）"""
        # 使用 Haversine 公式
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
        print("\n執行風險分析...")
        
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
                
                # 距離懲罰（距離越遠，不確定性越高）
                if distance > 20:
                    risk_score += 10
                elif distance > 10:
                    risk_score += 5
                
                risk_score = min(100, risk_score)  # 限制最大值為100
                
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
                    '風險分數': risk_score,
                    '模擬情境': '高AQI情境模擬'
                }
                
                risk_results.append(result)
        
        self.risk_analysis = pd.DataFrame(risk_results)
        print(f"完成 {len(risk_results)} 個避難收容處所的風險分析")
        
        return self.risk_analysis
    
    def generate_statistics(self):
        """生成統計報告"""
        print("\n生成風險分析統計...")
        
        if self.risk_analysis is None:
            print("請先執行風險分析")
            return
        
        # 風險等級統計
        risk_counts = self.risk_analysis['風險等級'].value_counts()
        print(f"\n風險等級分佈:")
        for risk_level, count in risk_counts.items():
            percentage = count / len(self.risk_analysis) * 100
            print(f"  {risk_level}: {count:,} 筆 ({percentage:.1f}%)")
        
        # 設施類型統計
        facility_counts = self.risk_analysis['設施類型'].value_counts()
        print(f"\n設施類型分佈:")
        for facility_type, count in facility_counts.items():
            percentage = count / len(self.risk_analysis) * 100
            print(f"  {facility_type}: {count:,} 筆 ({percentage:.1f}%)")
        
        # 高風險設施詳情
        high_risk = self.risk_analysis[self.risk_analysis['風險等級'] == 'High Risk']
        if len(high_risk) > 0:
            print(f"\n高風險設施 (前10個):")
            for _, row in high_risk.head(10).iterrows():
                print(f"  {row['避難收容處所名稱']} ({row['設施類型']})")
                print(f"    位置: {row['縣市及鄉鎮市區']}")
                print(f"    最近測站: {row['最近AQI測站']} (AQI: {row['最近測站AQI']})")
                print(f"    距離: {row['距離測站(km)']} km")
                print(f"    風險分數: {row['風險分數']}")
                print()
        
        # 警告設施詳情
        warning_risk = self.risk_analysis[self.risk_analysis['風險等級'] == 'Warning']
        if len(warning_risk) > 0:
            print(f"\n警告風險設施 (前5個):")
            for _, row in warning_risk.head(5).iterrows():
                print(f"  {row['避難收容處所名稱']} ({row['設施類型']})")
                print(f"    位置: {row['縣市及鄉鎮市區']}")
                print(f"    最近測站: {row['最近AQI測站']} (AQI: {row['最近測站AQI']})")
                print(f"    距離: {row['距離測站(km)']} km")
                print(f"    風險分數: {row['風險分數']}")
                print()
    
    def save_results(self):
        """儲存分析結果"""
        if self.risk_analysis is None:
            print("請先執行風險分析")
            return
        
        # 確保 outputs 目錄存在
        import os
        os.makedirs('outputs', exist_ok=True)
        
        # 儲存主要分析結果
        output_file = 'outputs/shelter_aqi_analysis.csv'
        self.risk_analysis.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\n風險分析結果已儲存至: {output_file}")
        
        # 儲存統計摘要
        summary_stats = {
            '項目': [
                '總避難收容處所數量',
                '高風險設施數量',
                '警告風險設施數量', 
                '低風險設施數量',
                '室內設施數量',
                '戶外設施數量',
                '平均風險分數',
                '最高風險分數',
                '模擬情境說明'
            ],
            '數值': [
                len(self.risk_analysis),
                len(self.risk_analysis[self.risk_analysis['風險等級'] == 'High Risk']),
                len(self.risk_analysis[self.risk_analysis['風險等級'] == 'Warning']),
                len(self.risk_analysis[self.risk_analysis['風險等級'] == 'Low Risk']),
                len(self.risk_analysis[self.risk_analysis['is_indoor'] == True]),
                len(self.risk_analysis[self.risk_analysis['is_indoor'] == False]),
                self.risk_analysis['風險分數'].mean(),
                self.risk_analysis['風險分數'].max(),
                '將南部測站AQI設為150進行情境模擬'
            ]
        }
        
        summary_df = pd.DataFrame(summary_stats)
        summary_file = 'outputs/shelter_aqi_analysis_summary.csv'
        summary_df.to_csv(summary_file, index=False, encoding='utf-8-sig')
        print(f"統計摘要已儲存至: {summary_file}")
        
        # 儲存模擬後的 AQI 數據
        simulation_file = 'outputs/simulated_aqi_stations.csv'
        self.aqi_data.to_csv(simulation_file, index=False, encoding='utf-8-sig')
        print(f"模擬後 AQI 測站數據已儲存至: {simulation_file}")
    
    def run_analysis(self):
        """執行完整分析流程"""
        print("=" * 80)
        print("避難收容處所 AQI 風險分析與情境模擬")
        print("=" * 80)
        
        # 載入數據
        if not self.load_data():
            print("載入數據失敗")
            return
        
        # 情境模擬
        self.simulate_high_aqi_scenario()
        
        # 執行風險分析
        self.perform_risk_analysis()
        
        # 生成統計
        self.generate_statistics()
        
        # 儲存結果
        self.save_results()
        
        print("\n" + "=" * 80)
        print("風險分析與情境模擬完成！")
        print("=" * 80)
        print("📁 輸出檔案:")
        print("   outputs/shelter_aqi_analysis.csv - 詳細風險分析結果")
        print("   outputs/shelter_aqi_analysis_summary.csv - 統計摘要")
        print("   outputs/simulated_aqi_stations.csv - 模擬後的AQI測站數據")
        print("\n🚨 情境模擬說明:")
        print("   已將南部測站 AQI 設為 150")
        print("   驗證風險標籤邏輯是否正確觸發")
        print("   確保能看到 'High Risk' 標籤")

def main():
    """主程式"""
    analyzer = ShelterAQIRiskAnalysis()
    analyzer.run_analysis()

if __name__ == "__main__":
    main()
