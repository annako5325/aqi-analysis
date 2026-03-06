#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
建立簡化版 Folium 地圖，視覺化 AQI 測站和避難收容處所
Layer A: AQI Stations (三色分類: 0-50綠色, 51-100黃色, 101+紅色)
Layer B: Evacuation Shelters (Distinct icons for Indoor vs. Outdoor)
"""

import pandas as pd
import folium
import numpy as np
from folium import plugins
import requests
from datetime import datetime

class SimpleAQIShelterMap:
    """簡化版 AQI 和避難收容處所地圖生成器"""
    
    def __init__(self):
        self.aqi_data = None
        self.shelter_data = None
        self.map = None
        
        # 台灣中心點
        self.taiwan_center = [23.8, 121.0]
        
        # 簡化的 AQI 三色對應
        self.aqi_colors = {
            'good': '#00E400',      # 綠色 (0-50)
            'moderate': '#FFFF00',   # 黃色 (51-100)
            'poor': '#FF0000'        # 紅色 (101+)
        }
        
        # 簡化的 AQI 等級對應
        self.aqi_levels = {
            'good': (0, 50),
            'moderate': (51, 100),
            'poor': (101, 500)
        }
    
    def load_aqi_data(self, use_sample=True):
        """載入 AQI 數據"""
        print("載入 AQI 數據...")
        
        if use_sample:
            # 使用包含各種 AQI 等級的範例數據
            self.aqi_data = self._get_comprehensive_sample_aqi_data()
            print(f"使用範例 AQI 數據: {len(self.aqi_data)} 個測站")
        else:
            # 嘗試從 API 獲取數據
            try:
                self.aqi_data = self._fetch_aqi_from_api()
                print(f"從 API 獲取 AQI 數據: {len(self.aqi_data)} 個測站")
            except Exception as e:
                print(f"API 獲取失敗，使用範例數據: {e}")
                self.aqi_data = self._get_comprehensive_sample_aqi_data()
                print(f"使用範例 AQI 數據: {len(self.aqi_data)} 個測站")
    
    def _get_comprehensive_sample_aqi_data(self):
        """獲取包含各種 AQI 等級的範例數據"""
        return [
            # 0-50 綠色等級
            {'SiteName': '基隆', 'County': '基隆市', 'AQI': 25, 'PM25': 8.3, 'lat': 25.1276, 'lon': 121.7392},
            {'SiteName': '花蓮', 'County': '花蓮市', 'AQI': 35, 'PM25': 9.8, 'lat': 23.9759, 'lon': 121.6034},
            {'SiteName': '台東', 'County': '台東市', 'AQI': 42, 'PM25': 10.5, 'lat': 22.7553, 'lon': 121.1506},
            {'SiteName': '澎湖', 'County': '澎湖縣', 'AQI': 38, 'PM25': 9.2, 'lat': 23.5697, 'lon': 119.5665},
            {'SiteName': '馬祖', 'County': '連江縣', 'AQI': 31, 'PM25': 8.7, 'lat': 26.1616, 'lon': 119.9368},
            {'SiteName': '蘭嶼', 'County': '台東縣', 'AQI': 28, 'PM25': 7.5, 'lat': 22.0346, 'lon': 121.5142},
            {'SiteName': '綠島', 'County': '台東縣', 'AQI': 33, 'PM25': 9.1, 'lat': 22.6735, 'lon': 121.4623},
            
            # 51-100 黃色等級
            {'SiteName': '台北', 'County': '台北市', 'AQI': 78, 'PM25': 23.1, 'lat': 25.0330, 'lon': 121.5654},
            {'SiteName': '新北', 'County': '新北市', 'AQI': 92, 'PM25': 28.7, 'lat': 25.0173, 'lon': 121.4625},
            {'SiteName': '桃園', 'County': '桃園市', 'AQI': 65, 'PM25': 18.9, 'lat': 24.9936, 'lon': 121.3010},
            {'SiteName': '新竹', 'County': '新竹市', 'AQI': 58, 'PM25': 15.2, 'lat': 24.8138, 'lon': 120.9675},
            {'SiteName': '苗栗', 'County': '苗栗市', 'AQI': 72, 'PM25': 21.3, 'lat': 24.5646, 'lon': 120.8214},
            {'SiteName': '台中', 'County': '台中市', 'AQI': 85, 'PM25': 25.4, 'lat': 24.1477, 'lon': 120.6736},
            {'SiteName': '彰化', 'County': '彰化市', 'AQI': 69, 'PM25': 19.8, 'lat': 24.0771, 'lon': 120.5428},
            {'SiteName': '南投', 'County': '南投市', 'AQI': 55, 'PM25': 16.1, 'lat': 23.9096, 'lon': 120.6838},
            {'SiteName': '雲林', 'County': '雲林市', 'AQI': 61, 'PM25': 17.9, 'lat': 23.6990, 'lon': 120.4329},
            {'SiteName': '嘉義', 'County': '嘉義市', 'AQI': 74, 'PM25': 22.1, 'lat': 23.4801, 'lon': 120.4491},
            {'SiteName': '台南', 'County': '台南市', 'AQI': 67, 'PM25': 19.5, 'lat': 22.9999, 'lon': 120.2269},
            {'SiteName': '屏東', 'County': '屏東市', 'AQI': 56, 'PM25': 16.8, 'lat': 22.6697, 'lon': 120.4859},
            {'SiteName': '宜蘭', 'County': '宜蘭市', 'AQI': 48, 'PM25': 13.2, 'lat': 24.6929, 'lon': 121.7216},
            
            # 101+ 紅色等級
            {'SiteName': '高雄', 'County': '高雄市', 'AQI': 125, 'PM25': 35.2, 'lat': 22.6273, 'lon': 120.3014},
            {'SiteName': '屏東(枋寮)', 'County': '屏東縣', 'AQI': 118, 'PM25': 33.8, 'lat': 22.3767, 'lon': 120.6955},
            {'SiteName': '嘉義(布袋)', 'County': '嘉義縣', 'AQI': 112, 'PM25': 31.5, 'lat': 23.3809, 'lon': 120.1656},
            {'SiteName': '台中(沙鹿)', 'County': '台中市', 'AQI': 135, 'PM25': 38.7, 'lat': 24.2334, 'lon': 120.5627},
            {'SiteName': '新竹(竹東)', 'County': '新竹縣', 'AQI': 108, 'PM25': 30.1, 'lat': 24.7338, 'lon': 121.0845}
        ]
    
    def _fetch_aqi_from_api(self):
        """從 API 獲取 AQI 數據"""
        url = "https://data.moenv.gov.tw/api/v2/aqx_p_432"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if isinstance(data, dict) and 'records' in data:
                records = data['records']
            elif isinstance(data, list):
                records = data
            else:
                records = []
            
            # 處理數據
            processed_data = []
            for record in records:
                if isinstance(record, dict):
                    try:
                        site_data = {
                            'SiteName': record.get('sitename', 'Unknown'),
                            'County': record.get('county', 'Unknown'),
                            'AQI': int(record.get('aqi', 0)),
                            'PM25': float(record.get('pm2.5', 0)),
                            'lat': float(record.get('latitude', 0)),
                            'lon': float(record.get('longitude', 0))
                        }
                        
                        # 過濾有效座標
                        if site_data['lat'] != 0 and site_data['lon'] != 0:
                            processed_data.append(site_data)
                    except (ValueError, TypeError):
                        continue
            
            return processed_data
            
        except Exception as e:
            raise Exception(f"API 獲取失敗: {e}")
    
    def load_shelter_data(self):
        """載入避難收容處所數據"""
        print("載入避難收容處所數據...")
        
        try:
            # 載入有 is_indoor 欄位的檔案
            self.shelter_data = pd.read_csv('避難收容處所點位檔案v9_with_indoor.csv')
            print(f"載入避難收容處所數據: {len(self.shelter_data)} 筆")
            
            # 檢查必要欄位
            required_cols = ['經度', '緯度', '避難收容處所名稱', 'is_indoor']
            missing_cols = [col for col in required_cols if col not in self.shelter_data.columns]
            if missing_cols:
                print(f"缺少必要欄位: {missing_cols}")
                return False
            
            # 移除座標缺失值
            initial_count = len(self.shelter_data)
            self.shelter_data = self.shelter_data.dropna(subset=['經度', '緯度'])
            self.shelter_data = self.shelter_data[(self.shelter_data['經度'] != 0) & (self.shelter_data['緯度'] != 0)]
            
            print(f"移除座標缺失值後: {len(self.shelter_data)} 筆")
            return True
            
        except Exception as e:
            print(f"載入避難收容處所數據失敗: {e}")
            return False
    
    def get_simple_aqi_color_and_level(self, aqi_value):
        """根據簡化的 AQI 三色分類獲取顏色和等級"""
        if pd.isna(aqi_value) or aqi_value == 0:
            return '#808080', 'Unknown', '未知'
        
        aqi_value = int(aqi_value)
        
        if 0 <= aqi_value <= 50:
            return self.aqi_colors['good'], 'good', '良好 (0-50)'
        elif 51 <= aqi_value <= 100:
            return self.aqi_colors['moderate'], 'moderate', '普通 (51-100)'
        else:  # 101+
            return self.aqi_colors['poor'], 'poor', '不佳 (101+)'
    
    def create_base_map(self):
        """創建基礎地圖"""
        print("創建基礎地圖...")
        
        self.map = folium.Map(
            location=self.taiwan_center,
            zoom_start=8,
            tiles='OpenStreetMap'
        )
        
        # 添加圖層控制
        folium.TileLayer('OpenStreetMap').add_to(self.map)
        folium.TileLayer('CartoDB positron').add_to(self.map)
        folium.TileLayer('CartoDB dark_matter').add_to(self.map)
    
    def add_aqi_stations_layer(self):
        """添加 AQI 測站圖層"""
        print("添加 AQI 測站圖層...")
        
        # 創建 AQI 測站圖層組
        aqi_feature_group = folium.FeatureGroup(name='AQI 測站', show=True)
        
        for station in self.aqi_data:
            lat, lon = station['lat'], station['lon']
            aqi = station['AQI']
            color, level, level_name = self.get_simple_aqi_color_and_level(aqi)
            
            # 創建圓形標記
            circle_marker = folium.CircleMarker(
                location=[lat, lon],
                radius=10,  # 固定大小
                popup=folium.Popup(
                    f"""
                    <div style="font-family: Arial, sans-serif;">
                        <h4 style="margin: 0; color: {color};">{station['SiteName']}</h4>
                        <p><strong>縣市:</strong> {station['County']}</p>
                        <p><strong>AQI:</strong> <span style="color: {color}; font-weight: bold; font-size: 16px;">{aqi}</span></p>
                        <p><strong>PM2.5:</strong> {station['PM25']} μg/m³</p>
                        <p><strong>空氣品質:</strong> <span style="color: {color}; font-weight: bold;">{level_name}</span></p>
                    </div>
                    """,
                    max_width=300
                ),
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.8,
                weight=2
            )
            
            circle_marker.add_to(aqi_feature_group)
        
        aqi_feature_group.add_to(self.map)
        
        # 添加簡化的 AQI 圖例
        self._add_simple_aqi_legend()
    
    def _add_simple_aqi_legend(self):
        """添加簡化的 AQI 圖例"""
        legend_html = '''
        <div style="position: fixed; 
                    top: 10px; right: 10px; width: 200px; height: 140px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px; box-shadow: 0 0 15px rgba(0,0,0,0.2);">
        <h4 style="margin: 0 0 10px 0; color: #333;">AQI 空氣品質指標</h4>
        <p style="margin: 5px 0;"><i class="fa fa-circle" style="color: #00E400;"></i> 0-50 良好</p>
        <p style="margin: 5px 0;"><i class="fa fa-circle" style="color: #FFFF00;"></i> 51-100 普通</p>
        <p style="margin: 5px 0;"><i class="fa fa-circle" style="color: #FF0000;"></i> 101+ 不佳</p>
        </div>
        '''
        self.map.get_root().html.add_child(folium.Element(legend_html))
    
    def add_shelter_layer(self):
        """添加避難收容處所圖層"""
        print("添加避難收容處所圖層...")
        
        # 分離室內和戶外設施
        indoor_shelters = self.shelter_data[self.shelter_data['is_indoor'] == True]
        outdoor_shelters = self.shelter_data[self.shelter_data['is_indoor'] == False]
        
        print(f"  室內設施: {len(indoor_shelters)} 筆")
        print(f"  戶外設施: {len(outdoor_shelters)} 筆")
        
        # 創建避難收容處所圖層組
        shelter_feature_group = folium.FeatureGroup(name='避難收容處所', show=True)
        
        # 添加室內設施
        indoor_group = folium.FeatureGroup(name='室內設施', show=True)
        for idx, shelter in indoor_shelters.iterrows():
            lat, lon = shelter['緯度'], shelter['經度']
            name = shelter['避難收容處所名稱']
            county = shelter.get('縣市及鄉鎮市區', '未知')
            capacity = shelter.get('預計收容人數', '未知')
            
            # 室內設施使用藍色建築物圖標
            icon = folium.Icon(
                icon='home',
                color='blue',
                prefix='fa'
            )
            
            marker = folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(
                    f"""
                    <div style="font-family: Arial, sans-serif;">
                        <h4 style="margin: 0; color: #2196F3;">🏢 {name}</h4>
                        <p><strong>類型:</strong> 室內設施</p>
                        <p><strong>位置:</strong> {county}</p>
                        <p><strong>收容人數:</strong> {capacity} 人</p>
                        <p><strong>座標:</strong> ({lat:.6f}, {lon:.6f})</p>
                    </div>
                    """,
                    max_width=300
                ),
                icon=icon,
                tooltip=name
            )
            
            marker.add_to(indoor_group)
        
        indoor_group.add_to(shelter_feature_group)
        
        # 添加戶外設施
        outdoor_group = folium.FeatureGroup(name='戶外設施', show=True)
        for idx, shelter in outdoor_shelters.iterrows():
            lat, lon = shelter['緯度'], shelter['經度']
            name = shelter['避難收容處所名稱']
            county = shelter.get('縣市及鄉鎮市區', '未知')
            capacity = shelter.get('預計收容人數', '未知')
            
            # 戶外設施使用綠色樹木圖標
            icon = folium.Icon(
                icon='tree',
                color='green',
                prefix='fa'
            )
            
            marker = folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(
                    f"""
                    <div style="font-family: Arial, sans-serif;">
                        <h4 style="margin: 0; color: #27AE60;">🌳 {name}</h4>
                        <p><strong>類型:</strong> 戶外設施</p>
                        <p><strong>位置:</strong> {county}</p>
                        <p><strong>收容人數:</strong> {capacity} 人</p>
                        <p><strong>座標:</strong> ({lat:.6f}, {lon:.6f})</p>
                    </div>
                    """,
                    max_width=300
                ),
                icon=icon,
                tooltip=name
            )
            
            marker.add_to(outdoor_group)
        
        outdoor_group.add_to(shelter_feature_group)
        shelter_feature_group.add_to(self.map)
        
        # 添加避難收容處所圖例
        self._add_shelter_legend()
    
    def _add_shelter_legend(self):
        """添加避難收容處所圖例"""
        legend_html = '''
        <div style="position: fixed; 
                    top: 160px; right: 10px; width: 200px; height: 120px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px; box-shadow: 0 0 15px rgba(0,0,0,0.2);">
        <h4 style="margin: 0 0 10px 0; color: #333;">避難收容處所</h4>
        <p style="margin: 5px 0;"><i class="fa fa-home" style="color: #2196F3;"></i> 室內設施</p>
        <p style="margin: 5px 0;"><i class="fa fa-tree" style="color: #27AE60;"></i> 戶外設施</p>
        </div>
        '''
        self.map.get_root().html.add_child(folium.Element(legend_html))
    
    def add_layer_control(self):
        """添加圖層控制"""
        # 添加圖層控制
        folium.LayerControl().add_to(self.map)
        
        # 添加全螢幕控制按鈕
        plugins.Fullscreen(
            position='topright',
            title='全螢幕',
            force_separate_button=True
        ).add_to(self.map)
        
        # 添加小地圖
        plugins.MiniMap(toggle_display=True).add_to(self.map)
    
    def add_statistics_panel(self):
        """添加統計面板"""
        # 計算統計資訊
        total_shelters = len(self.shelter_data)
        indoor_count = len(self.shelter_data[self.shelter_data['is_indoor'] == True])
        outdoor_count = len(self.shelter_data[self.shelter_data['is_indoor'] == False])
        
        total_aqi_stations = len(self.aqi_data)
        
        # 計算簡化的 AQI 統計
        aqi_values = [station['AQI'] for station in self.aqi_data if station['AQI'] > 0]
        avg_aqi = np.mean(aqi_values) if aqi_values else 0
        max_aqi = max(aqi_values) if aqi_values else 0
        min_aqi = min(aqi_values) if aqi_values else 0
        
        # 計算三色分類數量
        level_counts = {'good': 0, 'moderate': 0, 'poor': 0}
        for station in self.aqi_data:
            _, level, _ = self.get_simple_aqi_color_and_level(station['AQI'])
            if level in level_counts:
                level_counts[level] += 1
        
        # 創建統計面板
        stats_html = f'''
        <div style="position: fixed; 
                    bottom: 10px; left: 10px; width: 280px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:12px; padding: 15px; box-shadow: 0 0 15px rgba(0,0,0,0.2);">
        <h4 style="margin: 0 0 10px 0; color: #333;">📊 統計資訊</h4>
        
        <h5 style="margin: 10px 0 5px 0; color: #2196F3;">🏢 避難收容處所</h5>
        <p style="margin: 3px 0;">總數: <strong>{total_shelters:,}</strong> 筆</p>
        <p style="margin: 3px 0;">室內: <strong>{indoor_count:,}</strong> 筆 ({indoor_count/total_shelters*100:.1f}%)</p>
        <p style="margin: 3px 0;">戶外: <strong>{outdoor_count:,}</strong> 筆 ({outdoor_count/total_shelters*100:.1f}%)</p>
        
        <h5 style="margin: 10px 0 5px 0; color: #FF6B6B;">🌡️ AQI 測站 (三色分類)</h5>
        <p style="margin: 3px 0;">測站數: <strong>{total_aqi_stations}</strong> 個</p>
        <p style="margin: 3px 0;">平均 AQI: <strong>{avg_aqi:.1f}</strong></p>
        <p style="margin: 3px 0;">良好 (0-50): <strong>{level_counts['good']}</strong> 個</p>
        <p style="margin: 3px 0;">普通 (51-100): <strong>{level_counts['moderate']}</strong> 個</p>
        <p style="margin: 3px 0;">不佳 (101+): <strong>{level_counts['poor']}</strong> 個</p>
        
        <p style="margin: 10px 0 5px 0; font-size: 10px; color: #666;">
        更新時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </p>
        </div>
        '''
        
        self.map.get_root().html.add_child(folium.Element(stats_html))
    
    def save_map(self, filename='simple_aqi_shelter_map.html'):
        """儲存地圖"""
        print(f"儲存地圖至: {filename}")
        self.map.save(filename)
        print(f"地圖已儲存: {filename}")
    
    def create_map(self, use_sample_aqi=True):
        """創建完整地圖"""
        print("=" * 60)
        print("創建簡化版 AQI 和避難收容處所地圖")
        print("AQI 三色分類: 0-50綠色, 51-100黃色, 101+紅色")
        print("=" * 60)
        
        # 載入數據
        self.load_aqi_data(use_sample_aqi)
        
        if not self.load_shelter_data():
            print("載入避難收容處所數據失敗")
            return
        
        # 創建地圖
        self.create_base_map()
        self.add_aqi_stations_layer()
        self.add_shelter_layer()
        self.add_layer_control()
        self.add_statistics_panel()
        
        # 儲存地圖
        self.save_map()
        
        print("\n" + "=" * 60)
        print("簡化版地圖創建完成！")
        print("=" * 60)
        print("📁 輸出檔案: simple_aqi_shelter_map.html")
        print("🌐 請用瀏覽器開啟檔案查看地圖")
        print("🎯 AQI 三色分類:")
        print("   🟢 0-50: 良好 (綠色)")
        print("   🟡 51-100: 普通 (黃色)")
        print("   🔴 101+: 不佳 (紅色)")
        print("🏢 避難收容處所:")
        print("   🏢 室內設施 (藍色建築物圖標)")
        print("   🌳 戶外設施 (綠色樹木圖標)")

def main():
    """主程式"""
    map_creator = SimpleAQIShelterMap()
    
    # 創建地圖（使用範例 AQI 數據）
    map_creator.create_map(use_sample_aqi=True)

if __name__ == "__main__":
    main()
