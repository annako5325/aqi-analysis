#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用從aqi_map.html提取的完整85個AQI測站資料建立疊圖地圖
Layer A: AQI Stations (三色分類: 0-50綠色, 51-100黃色, 101+紅色)
Layer B: Evacuation Shelters (已清理邊界異常點)
"""

import pandas as pd
import folium
import numpy as np
from folium import plugins
import re
from datetime import datetime
import os

class Correct85AQIShelterMap:
    """使用完整85個AQI測站資料建立疊圖地圖生成器"""
    
    def __init__(self):
        self.aqi_data = None
        self.shelter_data = None
        self.map = None
        
        # 台灣中心座標
        self.taiwan_center = [23.8, 121.0]
        
        # 簡化版AQI 三色對應
        self.aqi_colors = {
            'good': '#00E400',      # 綠色 (0-50)
            'moderate': '#FFFF00',   # 黃色 (51-100)
            'poor': '#FF0000'        # 紅色 (101+)
        }
    
    def extract_aqi_stations_from_html(self, html_file):
        """從aqi_map.html提取完整85個AQI測站資料"""
        print(f"從 {html_file} 提取 AQI 測站資料...")
        
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 尋找所有circleMarker的座標和顏色
        pattern = r'L\.circleMarker\(\s*\[([0-9.-]+),\s*([0-9.-]+)\],[^}]*"fillColor":\s*"([^"]+)"'
        matches = re.findall(pattern, content)
        
        print(f"找到 {len(matches)} 個測站")
        
        stations = []
        for i, (lat, lon, color) in enumerate(matches):
            station = {
                'SiteName': f'測站{i+1}',
                'County': '未知',
                'AQI': 0,
                'PM25': 0,
                'lat': float(lat),
                'lon': float(lon),
                'Color': color
            }
            stations.append(station)
        
        return stations
    
    def get_aqi_level(self, color):
        """根據顏色判斷AQI等級"""
        if color == self.aqi_colors['good']:
            return 'good'
        elif color == self.aqi_colors['moderate']:
            return 'moderate'
        elif color == self.aqi_colors['poor']:
            return 'poor'
        else:
            return 'unknown'
    
    def load_shelter_data(self):
        """載入避難收容處所資料"""
        shelter_file = "避難收容處所點位檔案v9_boundary_cleaned.csv"
        try:
            self.shelter_data = pd.read_csv(shelter_file, encoding='utf-8')
            print(f"載入避難收容處所: {len(self.shelter_data)} 筆")
            return True
        except Exception as e:
            print(f"載入避難收容處所失敗: {e}")
            return False
    
    def create_map(self):
        """建立地圖"""
        print("建立地圖...")
        
        # 建立基礎地圖
        self.map = folium.Map(
            location=self.taiwan_center,
            zoom_start=7,
            tiles='OpenStreetMap'
        )
        
        # 建立圖層群組
        aqi_layer = folium.FeatureGroup(name='AQI 測站')
        shelter_layer = folium.FeatureGroup(name='避難收容處所')
        
        # 新增AQI測站
        if self.aqi_data is not None:
            for station in self.aqi_data:
                lat = station['lat']
                lon = station['lon']
                color = station['Color']
                level = self.get_aqi_level(color)
                
                # 根據AQI等級決定圖標大小
                if level == 'good':
                    radius = 8
                elif level == 'moderate':
                    radius = 10
                else:
                    radius = 12
                
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=radius,
                    popup=f"""
                    <b>{station['SiteName']}</b><br>
                    AQI等級: {level}<br>
                    座標: ({lat:.4f}, {lon:.4f})
                    """,
                    color=color,
                    fillColor=color,
                    fillOpacity=0.7,
                    weight=2
                ).add_to(aqi_layer)
        
        # 新增避難收容處所
        if self.shelter_data is not None:
            indoor_count = 0
            outdoor_count = 0
            
            for _, shelter in self.shelter_data.iterrows():
                try:
                    lat = float(shelter['緯度'])
                    lon = float(shelter['經度'])
                    name = shelter['避難收容處所名稱']
                    is_indoor = shelter.get('is_indoor', True)
                    county = shelter.get('縣市及鄉鎮市區', '未知')
                    
                    # 根據室內外決定圖標
                    if is_indoor:
                        icon_color = 'blue'
                        icon_symbol = 'building'
                        indoor_count += 1
                    else:
                        icon_color = 'green'
                        icon_symbol = 'tree'
                        outdoor_count += 1
                    
                    folium.Marker(
                        location=[lat, lon],
                        popup=f"""
                        <b>{name}</b><br>
                        類型: {'室內設施' if is_indoor else '戶外設施'}<br>
                        位置: {county}<br>
                        座標: ({lat:.4f}, {lon:.4f})
                        """,
                        icon=folium.Icon(
                            color=icon_color,
                            icon=icon_symbol,
                            prefix='fa'
                        )
                    ).add_to(shelter_layer)
                    
                except (ValueError, TypeError) as e:
                    print(f"跳過無效座標的避難所: {shelter.get('避難收容處所名稱', '未知')}")
                    continue
        
        # 新增圖層到地圖
        aqi_layer.add_to(self.map)
        shelter_layer.add_to(self.map)
        
        # 新增圖層控制
        folium.LayerControl().add_to(self.map)
        
        # 新增全螢幕按鈕
        plugins.Fullscreen().add_to(self.map)
        
        # 新增小地圖
        plugins.MiniMap(toggle_display=True).add_to(self.map)
        
        # 新增統計面板
        self.add_statistics_panel()
        
        # 新增圖例
        self.add_legend()
    
    def add_statistics_panel(self):
        """新增統計面板"""
        if self.aqi_data is not None and self.shelter_data is not None:
            # 統計AQI測站
            aqi_stats = {}
            for station in self.aqi_data:
                level = self.get_aqi_level(station['Color'])
                aqi_stats[level] = aqi_stats.get(level, 0) + 1
            
            # 統計避難收容處所
            indoor_count = len(self.shelter_data[self.shelter_data.get('is_indoor', True) == True])
            outdoor_count = len(self.shelter_data[self.shelter_data.get('is_indoor', True) == False])
            
            stats_html = f"""
            <div style="position: fixed; 
                        top: 10px; right: 10px; width: 250px; height: auto; 
                        background-color: white; border: 2px solid grey; 
                        z-index: 9999; font-size: 14px; padding: 10px;
                        border-radius: 5px;">
            <h4>統計資訊</h4>
            <b>AQI 測站:</b><br>
            &nbsp;&nbsp;🟢 良好 (0-50): {aqi_stats.get('good', 0)} 個<br>
            &nbsp;&nbsp;🟡 普通 (51-100): {aqi_stats.get('moderate', 0)} 個<br>
            &nbsp;&nbsp;🔴 不佳 (101+): {aqi_stats.get('poor', 0)} 個<br>
            <br>
            <b>避難收容處所:</b><br>
            &nbsp;&nbsp;🏢 室內設施: {indoor_count} 筆<br>
            &nbsp;&nbsp;🌳 戶外設施: {outdoor_count} 筆<br>
            <br>
            <b>總計:</b> {len(self.shelter_data)} 筆避難收容處所<br>
            <b>測站數:</b> {len(self.aqi_data)} 個AQI測站
            </div>
            """
            
            self.map.get_root().html.add_child(folium.Element(stats_html))
    
    def add_legend(self):
        """新增圖例"""
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 200px; height: auto; 
                    background-color: white; border: 2px solid grey; 
                    z-index: 9999; font-size: 12px; padding: 10px;
                    border-radius: 5px;">
        <h4>圖例</h4>
        <b>AQI 測站:</b><br>
        &nbsp;<span style="color: #00E400;">●</span> 良好 (0-50)<br>
        &nbsp;<span style="color: #FFFF00;">●</span> 普通 (51-100)<br>
        &nbsp;<span style="color: #FF0000;">●</span> 不佳 (101+)<br>
        <br>
        <b>避難收容處所:</b><br>
        &nbsp;<i class="fa fa-building" style="color: blue;"></i> 室內設施<br>
        &nbsp;<i class="fa fa-tree" style="color: green;"></i> 戶外設施
        </div>
        '''
        
        self.map.get_root().html.add_child(folium.Element(legend_html))
    
    def save_map(self, filename="correct_85_aqi_shelter_map.html"):
        """儲存地圖"""
        if self.map is not None:
            self.map.save(filename)
            print(f"地圖已儲存至: {filename}")
        else:
            print("地圖尚未建立")
    
    def run(self):
        """執行完整流程"""
        print("=" * 70)
        print("創建完整85個AQI測站的疊圖地圖")
        print("AQI 三色分類: 0-50綠色, 51-100黃色, 101+紅色")
        print("避難收容處所: 已清理邊界異常點")
        print("=" * 70)
        
        # 提取AQI測站資料
        html_file = "outputs/aqi_map.html"
        if os.path.exists(html_file):
            self.aqi_data = self.extract_aqi_stations_from_html(html_file)
            # 保存提取的資料
            aqi_df = pd.DataFrame(self.aqi_data)
            aqi_df.to_csv('extracted_85_aqi_stations.csv', index=False, encoding='utf-8-sig')
            print("AQI測站數據已保存至 extracted_85_aqi_stations.csv")
        else:
            print(f"找不到 {html_file}，使用模擬資料")
            self.aqi_data = self._create_sample_aqi_data()
        
        # 載入避難收容處所資料
        if not self.load_shelter_data():
            return
        
        # 建立地圖
        self.create_map()
        
        # 儲存地圖
        self.save_map()
        
        print("\n" + "=" * 70)
        print("📁 輸出檔案: correct_85_aqi_shelter_map.html")
        print("🌐 請用瀏覽器開啟檔案查看地圖")
        print("🎯 AQI 三色分類:")
        print("   🟢 0-50: 良好 (綠色)")
        print("   🟡 51-100: 普通 (黃色)")
        print("   🔴 101+: 不佳 (紅色)")
        print("🏢 避難收容處所:")
        print("   🏢 室內設施 (藍色建築物圖標)")
        print("   🌳 戶外設施 (綠色樹木圖標)")
        print("✅ 已移除界線外異常點位")
        print("📊 完整85個AQI測站")
        print("=" * 70)

def main():
    """主程式"""
    map_creator = Correct85AQIShelterMap()
    map_creator.run()

if __name__ == "__main__":
    main()
