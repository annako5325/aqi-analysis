#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
環境部 AQI 即時數據地圖顯示程式
串接環境部 API (aqx_p_432) 獲取全台即時 AQI 數據
使用 folium 在地圖上標示所有測站位置
"""

import os
import requests
import folium
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime
import json
import math
import csv

# 載入環境變數
load_dotenv()

class AQIMapGenerator:
    def __init__(self):
        self.api_key = os.getenv('EPA_API_KEY')
        self.api_url = "https://data.moenv.gov.tw/api/v2/aqx_p_432"
        self.stations_data = []
        self.taipei_station = (25.0478, 121.5170)  # 台北車站座標
        
    def get_sample_data(self):
        """獲取範例數據用於測試"""
        print("使用範例數據進行測試...")
        
        sample_data = [
            # 北部地區
            {'sitename': '台北', 'county': '台北市', 'aqi': '45', 'latitude': '25.0330', 'longitude': '121.5654'},
            {'sitename': '中山', 'county': '台北市', 'aqi': '42', 'latitude': '25.0620', 'longitude': '121.5250'},
            {'sitename': '松山', 'county': '台北市', 'aqi': '48', 'latitude': '25.0500', 'longitude': '121.5800'},
            {'sitename': '古亭', 'county': '台北市', 'aqi': '46', 'latitude': '25.0200', 'longitude': '121.5300'},
            {'sitename': '萬華', 'county': '台北市', 'aqi': '51', 'latitude': '25.0300', 'longitude': '121.5000'},
            {'sitename': '大同', 'county': '台北市', 'aqi': '44', 'latitude': '25.0800', 'longitude': '121.5200'},
            {'sitename': '士林', 'county': '台北市', 'aqi': '43', 'latitude': '25.0800', 'longitude': '121.5300'},
            {'sitename': '內湖', 'county': '台北市', 'aqi': '47', 'latitude': '25.0700', 'longitude': '121.5800'},
            {'sitename': '南港', 'county': '台北市', 'aqi': '45', 'latitude': '25.0500', 'longitude': '121.6000'},
            {'sitename': '板橋', 'county': '新北市', 'aqi': '58', 'latitude': '25.0100', 'longitude': '121.4600'},
            {'sitename': '新莊', 'county': '新北市', 'aqi': '62', 'latitude': '25.0300', 'longitude': '121.4400'},
            {'sitename': '三重', 'county': '新北市', 'aqi': '65', 'latitude': '25.0800', 'longitude': '121.4900'},
            {'sitename': '中和', 'county': '新北市', 'aqi': '59', 'latitude': '25.0000', 'longitude': '121.4800'},
            {'sitename': '永和', 'county': '新北市', 'aqi': '61', 'latitude': '25.0100', 'longitude': '121.5000'},
            {'sitename': '樹林', 'county': '新北市', 'aqi': '55', 'latitude': '24.9900', 'longitude': '121.4200'},
            {'sitename': '新店', 'county': '新北市', 'aqi': '41', 'latitude': '24.9700', 'longitude': '121.5400'},
            {'sitename': '淡水', 'county': '新北市', 'aqi': '39', 'latitude': '25.1600', 'longitude': '121.4400'},
            {'sitename': '林口', 'county': '新北市', 'aqi': '52', 'latitude': '25.0800', 'longitude': '121.3800'},
            {'sitename': '三峽', 'county': '新北市', 'aqi': '48', 'latitude': '24.9300', 'longitude': '121.3700'},
            {'sitename': '鶯歌', 'county': '新北市', 'aqi': '56', 'latitude': '24.9500', 'longitude': '121.3500'},
            {'sitename': '桃園', 'county': '桃園市', 'aqi': '68', 'latitude': '24.9900', 'longitude': '121.3000'},
            {'sitename': '中壢', 'county': '桃園市', 'aqi': '72', 'latitude': '24.9500', 'longitude': '121.2200'},
            {'sitename': '大溪', 'county': '桃園市', 'aqi': '64', 'latitude': '24.8800', 'longitude': '121.2800'},
            {'sitename': '蘆竹', 'county': '桃園市', 'aqi': '70', 'latitude': '25.0300', 'longitude': '121.2900'},
            {'sitename': '龍潭', 'county': '桃園市', 'aqi': '58', 'latitude': '24.8600', 'longitude': '121.2100'},
            {'sitename': '平鎮', 'county': '桃園市', 'aqi': '66', 'latitude': '24.9500', 'longitude': '121.2000'},
            {'sitename': '楊梅', 'county': '桃園市', 'aqi': '63', 'latitude': '24.9100', 'longitude': '121.1500'},
            {'sitename': '新竹', 'county': '新竹市', 'aqi': '68', 'latitude': '24.8138', 'longitude': '120.9675'},
            {'sitename': '竹東', 'county': '新竹縣', 'aqi': '62', 'latitude': '24.7300', 'longitude': '121.0800'},
            {'sitename': '新埔', 'county': '新竹縣', 'aqi': '55', 'latitude': '24.8200', 'longitude': '121.0500'},
            {'sitename': '關西', 'county': '新竹縣', 'aqi': '48', 'latitude': '24.7800', 'longitude': '121.1700'},
            
            # 中部地區
            {'sitename': '台中', 'county': '台中市', 'aqi': '82', 'latitude': '24.1477', 'longitude': '120.6736'},
            {'sitename': '西屯', 'county': '台中市', 'aqi': '85', 'latitude': '24.1600', 'longitude': '120.6000'},
            {'sitename': '沙鹿', 'county': '台中市', 'aqi': '78', 'latitude': '24.2300', 'longitude': '120.5600'},
            {'sitename': '大里', 'county': '台中市', 'aqi': '80', 'latitude': '24.1000', 'longitude': '120.6800'},
            {'sitename': '豐原', 'county': '台中市', 'aqi': '75', 'latitude': '24.2400', 'longitude': '120.7200'},
            {'sitename': '太平', 'county': '台中市', 'aqi': '77', 'latitude': '24.1200', 'longitude': '120.7100'},
            {'sitename': '大甲', 'county': '台中市', 'aqi': '71', 'latitude': '24.3500', 'longitude': '120.6200'},
            {'sitename': '清水', 'county': '台中市', 'aqi': '73', 'latitude': '24.2700', 'longitude': '120.5800'},
            {'sitename': '梧棲', 'county': '台中市', 'aqi': '76', 'latitude': '24.2500', 'longitude': '120.5400'},
            {'sitename': '烏日', 'county': '台中市', 'aqi': '79', 'latitude': '24.0800', 'longitude': '120.6500'},
            {'sitename': '彰化', 'county': '彰化縣', 'aqi': '88', 'latitude': '24.0800', 'longitude': '120.5400'},
            {'sitename': '員林', 'county': '彰化縣', 'aqi': '84', 'latitude': '23.9600', 'longitude': '120.5700'},
            {'sitename': '溪湖', 'county': '彰化縣', 'aqi': '86', 'latitude': '23.9600', 'longitude': '120.4800'},
            {'sitename': '北斗', 'county': '彰化縣', 'aqi': '82', 'latitude': '23.8700', 'longitude': '120.5200'},
            {'sitename': '二林', 'county': '彰化縣', 'aqi': '85', 'latitude': '23.9000', 'longitude': '120.3700'},
            {'sitename': '南投', 'county': '南投縣', 'aqi': '52', 'latitude': '23.9100', 'longitude': '120.6800'},
            {'sitename': '埔里', 'county': '南投縣', 'aqi': '48', 'latitude': '23.9600', 'longitude': '120.9700'},
            {'sitename': '竹山', 'county': '南投縣', 'aqi': '55', 'latitude': '23.7600', 'longitude': '120.6800'},
            {'sitename': '集集', 'county': '南投縣', 'aqi': '45', 'latitude': '23.8300', 'longitude': '120.7800'},
            {'sitename': '雲林', 'county': '雲林縣', 'aqi': '92', 'latitude': '23.7000', 'longitude': '120.4300'},
            {'sitename': '斗六', 'county': '雲林縣', 'aqi': '89', 'latitude': '23.7000', 'longitude': '120.5400'},
            {'sitename': '虎尾', 'county': '雲林縣', 'aqi': '91', 'latitude': '23.7100', 'longitude': '120.4400'},
            {'sitename': '西螺', 'county': '雲林縣', 'aqi': '87', 'latitude': '23.8000', 'longitude': '120.4600'},
            {'sitename': '北港', 'county': '雲林縣', 'aqi': '85', 'latitude': '23.5600', 'longitude': '120.4000'},
            
            # 南部地區
            {'sitename': '嘉義', 'county': '嘉義市', 'aqi': '78', 'latitude': '23.4800', 'longitude': '120.4500'},
            {'sitename': '朴子', 'county': '嘉義縣', 'aqi': '81', 'latitude': '23.4600', 'longitude': '120.2500'},
            {'sitename': '布袋', 'county': '嘉義縣', 'aqi': '76', 'latitude': '23.3800', 'longitude': '120.1700'},
            {'sitename': '台南', 'county': '台南市', 'aqi': '55', 'latitude': '22.9999', 'longitude': '120.2269'},
            {'sitename': '安南', 'county': '台南市', 'aqi': '58', 'latitude': '23.0500', 'longitude': '120.2000'},
            {'sitename': '善化', 'county': '台南市', 'aqi': '61', 'latitude': '23.1300', 'longitude': '120.3000'},
            {'sitename': '新營', 'county': '台南市', 'aqi': '64', 'latitude': '23.3800', 'longitude': '120.3200'},
            {'sitename': '麻豆', 'county': '台南市', 'aqi': '59', 'latitude': '23.1800', 'longitude': '120.2500'},
            {'sitename': '佳里', 'county': '台南市', 'aqi': '62', 'latitude': '23.1600', 'longitude': '120.1800'},
            {'sitename': '新化', 'county': '台南市', 'aqi': '56', 'latitude': '23.0800', 'longitude': '120.3100'},
            {'sitename': '高雄', 'county': '高雄市', 'aqi': '72', 'latitude': '22.6273', 'longitude': '120.3014'},
            {'sitename': '左營', 'county': '高雄市', 'aqi': '75', 'latitude': '22.6900', 'longitude': '120.3000'},
            {'sitename': '楠梓', 'county': '高雄市', 'aqi': '78', 'latitude': '22.7300', 'longitude': '120.3200'},
            {'sitename': '三民', 'county': '高雄市', 'aqi': '74', 'latitude': '22.6400', 'longitude': '120.3200'},
            {'sitename': '前金', 'county': '高雄市', 'aqi': '71', 'latitude': '22.6300', 'longitude': '120.3000'},
            {'sitename': '鳳山', 'county': '高雄市', 'aqi': '76', 'latitude': '22.6300', 'longitude': '120.3600'},
            {'sitename': '林園', 'county': '高雄市', 'aqi': '79', 'latitude': '22.5000', 'longitude': '120.3900'},
            {'sitename': '大寮', 'county': '高雄市', 'aqi': '77', 'latitude': '22.6000', 'longitude': '120.4000'},
            {'sitename': '岡山', 'county': '高雄市', 'aqi': '73', 'latitude': '22.8000', 'longitude': '120.3000'},
            {'sitename': '橋頭', 'county': '高雄市', 'aqi': '70', 'latitude': '22.7600', 'longitude': '120.3100'},
            {'sitename': '屏東', 'county': '屏東縣', 'aqi': '65', 'latitude': '22.6800', 'longitude': '120.4900'},
            {'sitename': '潮州', 'county': '屏東縣', 'aqi': '68', 'latitude': '22.5500', 'longitude': '120.5600'},
            {'sitename': '東港', 'county': '屏東縣', 'aqi': '63', 'latitude': '22.4700', 'longitude': '120.4300'},
            {'sitename': '恆春', 'county': '屏東縣', 'aqi': '58', 'latitude': '22.0000', 'longitude': '120.7500'},
            
            # 東部地區
            {'sitename': '花蓮', 'county': '花蓮縣', 'aqi': '38', 'latitude': '23.7539', 'longitude': '121.6034'},
            {'sitename': '吉安', 'county': '花蓮縣', 'aqi': '41', 'latitude': '23.7800', 'longitude': '121.5800'},
            {'sitename': '玉里', 'county': '花蓮縣', 'aqi': '35', 'latitude': '23.3300', 'longitude': '121.3000'},
            {'sitename': '台東', 'county': '台東縣', 'aqi': '42', 'latitude': '22.7500', 'longitude': '121.1500'},
            {'sitename': '關山', 'county': '台東縣', 'aqi': '38', 'latitude': '23.0500', 'longitude': '121.1600'},
            {'sitename': '成功', 'county': '台東縣', 'aqi': '40', 'latitude': '23.1000', 'longitude': '121.3800'},
            {'sitename': '大武', 'county': '台東縣', 'aqi': '36', 'latitude': '22.3500', 'longitude': '120.9000'},
            
            # 離島地區
            {'sitename': '馬公', 'county': '澎湖縣', 'aqi': '45', 'latitude': '23.5700', 'longitude': '119.5800'},
            {'sitename': '金門', 'county': '金門縣', 'aqi': '48', 'latitude': '24.4300', 'longitude': '118.3200'},
            {'sitename': '烈嶼', 'county': '金門縣', 'aqi': '50', 'latitude': '24.4300', 'longitude': '118.2500'},
            {'sitename': '馬祖', 'county': '連江縣', 'aqi': '43', 'latitude': '26.1600', 'longitude': '119.9500'},
            {'sitename': '蘭嶼', 'county': '台東縣', 'aqi': '32', 'latitude': '22.0500', 'longitude': '121.5300'},
            {'sitename': '綠島', 'county': '台東縣', 'aqi': '35', 'latitude': '22.6700', 'longitude': '121.4800'}
        ]
        
        self.stations_data = sample_data
        print(f"載入 {len(self.stations_data)} 個範例測站數據")
        return True

    def get_aqi_data(self, use_sample=False):
        """從環境部 API 獲取 AQI 數據"""
        if use_sample:
            return self.get_sample_data()
            
        if not self.api_key:
            raise ValueError("請在 .env 檔案中設定 EPA_API_KEY")
        
        # 嘗試多個 API 端點
        api_urls = [
            "https://data.moenv.gov.tw/api/v2/aqx_p_432",
            "https://data.moenv.gov.tw/api/v1/aqx_p_432",
            "https://opendata.epa.gov.tw/api/v1/AQI"
        ]
        
        params = {
            'api_key': self.api_key,
            'format': 'JSON',
            'limit': 1000
        }
        
        for i, api_url in enumerate(api_urls):
            try:
                print(f"正在嘗試 API 端點 {i+1}/{len(api_urls)}: {api_url}")
                response = requests.get(api_url, params=params, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                
                # 處理不同的 API 回應格式
                if isinstance(data, list):
                    # 如果直接返回 list，就是記錄數據
                    self.stations_data = data
                    print(f"成功獲取 {len(self.stations_data)} 個測站數據")
                    return True
                elif isinstance(data, dict):
                    # 如果是 dict，檢查是否有數據欄位
                    if data.get('success') or 'records' in data or data.get('Data'):
                        # 處理不同 API 格式
                        if 'records' in data:
                            self.stations_data = data.get('records', [])
                        elif 'Data' in data:
                            self.stations_data = data.get('Data', [])
                        else:
                            self.stations_data = data
                            
                        print(f"成功獲取 {len(self.stations_data)} 個測站數據")
                        return True
                    else:
                        print(f"API 回傳錯誤: {data.get('message', '未知錯誤')}")
                else:
                    print(f"未知的數據格式: {type(data)}")
                    
            except requests.exceptions.RequestException as e:
                print(f"API 端點 {i+1} 請求失敗: {e}")
                if i < len(api_urls) - 1:
                    print("嘗試下一個 API 端點...")
                    continue
            except json.JSONDecodeError as e:
                print(f"JSON 解析失敗: {e}")
                if i < len(api_urls) - 1:
                    continue
        
        print("所有 API 端點都無法連接")
        print("建議：")
        print("1. 檢查網路連線")
        print("2. 確認防火牆設定")
        print("3. 嘗試使用範例數據：python aqi_map.py --sample")
        return False
    
    def calculate_distance_to_taipei(self, lat, lon):
        """計算測站到台北車站的距離（使用 TWD97 座標系統）"""
        # 將 WGS84 經緯度轉換為 TWD97 座標
        taipei_x, taipei_y = self.wgs84_to_twd97(self.taipei_station[0], self.taipei_station[1])
        station_x, station_y = self.wgs84_to_twd97(lat, lon)
        
        # 計算平面距離（歐幾里得距離）
        dx = station_x - taipei_x
        dy = station_y - taipei_y
        distance = math.sqrt(dx**2 + dy**2) / 1000  # 轉換為公里
        
        return round(distance, 2)
    
    def wgs84_to_twd97(self, lat, lon):
        """將 WGS84 經緯度轉換為 TWD97 平面座標（簡化版）"""
        # 使用簡化的 TWD97 轉換公式
        # 台灣二度分帶參數
        a = 6378137.0  # WGS84 半長軸
        f = 1/298.257222101  # WGS84 扁率
        e2 = f * (2 - f)
        
        # 中央經線和尺度比例
        lon0 = math.radians(121)  # 中央經線
        k0 = 0.9999  # 尺度比例
        
        # 轉換為弧度
        lat_rad = math.radians(lat)
        lon_rad = math.radians(lon)
        
        # 計算卯酉圈曲率半徑
        N = a / math.sqrt(1 - e2 * math.sin(lat_rad)**2)
        
        # 計算子午線弧長（簡化版）
        M = a * (1 - e2/4 - 3*e2**2/64 - 5*e2**3/256) * lat_rad
        M += a * (3*e2/8 + 3*e2**2/32 + 45*e2**3/1024) * math.sin(2*lat_rad)
        M += a * (15*e2**2/256 + 45*e2**3/1024) * math.sin(4*lat_rad)
        M += a * 35*e2**3/3072 * math.sin(6*lat_rad)
        
        # 計算經度差
        dl = lon_rad - lon0
        
        # 計算平面座標
        t = math.tan(lat_rad)
        t2 = t * t
        cos_lat = math.cos(lat_rad)
        cos2_lat = cos_lat * cos_lat
        
        # x 座標（東向）
        x = k0 * N * cos_lat * (dl + (1/6) * (1 - t2 + cos2_lat) * dl**3)
        
        # y 座標（北向）
        y = k0 * (M + N * t * (0.5*dl**2 + (1/24)*(5 - t2 + 9*cos2_lat)*dl**4))
        
        return x, y
    
    def calculate_all_distances(self):
        """計算所有測站到台北車站的距離（使用 TWD97 座標系統）"""
        print("正在計算測站到台北車站的距離（TWD97 座標系統）...")
        
        for station in self.stations_data:
            try:
                lat = float(station.get('latitude', 0))
                lon = float(station.get('longitude', 0))
                
                if lat != 0 and lon != 0:
                    distance = self.calculate_distance_to_taipei(lat, lon)
                    station['distance_to_taipei'] = distance
                else:
                    station['distance_to_taipei'] = None
                    
            except (ValueError, TypeError):
                station['distance_to_taipei'] = None
        
        print(f"已完成 {len(self.stations_data)} 個測站的 TWD97 距離計算")
        return True
    
    def get_aqi_color(self, aqi_value):
        """根據 AQI 數值返回對應的顏色（簡化三色分級）"""
        try:
            aqi = int(aqi_value)
        except (ValueError, TypeError):
            return '#808080'  # 灰色表示無效數值
        
        if aqi <= 50:
            return '#00E400'  # 綠色 - 良好
        elif aqi <= 100:
            return '#FFFF00'  # 黃色 - 普通
        else:
            return '#FF0000'  # 紅色 - 不健康
    
    def get_aqi_level(self, aqi_value):
        """根據 AQI 數值返回對應的等級（簡化三級）"""
        try:
            aqi = int(aqi_value)
        except (ValueError, TypeError):
            return '無數據'
        
        if aqi <= 50:
            return '良好'
        elif aqi <= 100:
            return '普通'
        else:
            return '不健康'
    
    def create_map(self):
        """創建 AQI 地圖"""
        if not self.stations_data:
            print("沒有測站數據，無法創建地圖")
            return None
        
        # 以台灣中心為地圖中心點
        taiwan_center = [23.8, 120.9]
        
        # 創建地圖
        m = folium.Map(
            location=taiwan_center,
            zoom_start=7,
            tiles='OpenStreetMap'
        )
        
        # 添加 AQI 圖例（簡化三色）
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 180px; height: 140px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px">
        <h4>AQI 空氣品質指標</h4>
        <p><i class="fa fa-circle" style="color:#00E400"></i> 0-50 良好</p>
        <p><i class="fa fa-circle" style="color:#FFFF00"></i> 51-100 普通</p>
        <p><i class="fa fa-circle" style="color:#FF0000"></i> 101+ 不健康</p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # 添加標題
        title_html = '''
        <div style="position: fixed; 
                    top: 10px; left: 50%; transform: translateX(-50%); 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:20px; font-weight:bold; padding: 10px">
        台灣即時 AQI 空氣品質地圖
        </div>
        '''
        m.get_root().html.add_child(folium.Element(title_html))
        
        # 添加測站標記
        for station in self.stations_data:
            try:
                # 獲取測站資訊
                site_name = station.get('sitename', '未知測站')
                county = station.get('county', station.get('area', '未知地區'))
                aqi = station.get('aqi', 'N/A')
                
                # 獲取座標
                latitude = float(station.get('latitude', 0))
                longitude = float(station.get('longitude', 0))
                
                if latitude == 0 or longitude == 0:
                    continue
                
                # 獲取 AQI 顏色和等級
                color = self.get_aqi_color(aqi)
                level = self.get_aqi_level(aqi)
                
                # 創建簡潔的彈出視窗內容
                popup_content = f"""
                <div style="font-family: Arial, sans-serif; min-width: 200px;">
                    <h4 style="margin: 5px 0; color: #333;">{site_name}</h4>
                    <p style="margin: 3px 0; color: #666;"><b>所在地：</b>{county}</p>
                    <p style="margin: 3px 0; font-size: 16px;">
                        <b>AQI：</b>
                        <span style="color: {color}; font-weight: bold;">{aqi}</span>
                        <span style="color: #666;">({level})</span>
                    </p>
                    <p style="margin: 5px 0 0 0; font-size: 12px; color: #999;">
                        更新時間: {datetime.now().strftime('%H:%M')}
                    </p>
                </div>
                """
                
                # 創建圓形標記
                folium.CircleMarker(
                    location=[latitude, longitude],
                    radius=10,
                    popup=folium.Popup(popup_content, max_width=250),
                    tooltip=f"{site_name} - AQI: {aqi}",
                    color='black',
                    weight=2,
                    fillColor=color,
                    fillOpacity=0.9
                ).add_to(m)
                
            except (ValueError, KeyError) as e:
                print(f"處理測站 {station.get('sitename', '未知')} 時發生錯誤: {e}")
                continue
        
        return m
    
    def save_map(self, map_obj, filename='outputs/aqi_map.html'):
        """保存地圖到檔案"""
        try:
            # 確保輸出目錄存在
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            map_obj.save(filename)
            print(f"地圖已保存至: {filename}")
            return True
        except Exception as e:
            print(f"保存地圖時發生錯誤: {e}")
            return False
    
    def export_to_csv(self, filename='outputs/aqi_analysis.csv'):
        """將測站數據和距離計算結果匯出為 CSV 檔案"""
        try:
            # 確保輸出目錄存在
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            # 準備 CSV 數據
            csv_data = []
            for station in self.stations_data:
                csv_data.append({
                    '測站名稱': station.get('sitename', '未知'),
                    '所在地': station.get('county', station.get('area', '未知')),
                    'AQI數值': station.get('aqi', 'N/A'),
                    '經度': station.get('longitude', 'N/A'),
                    '緯度': station.get('latitude', 'N/A'),
                    '距離台北車站(公里)': station.get('distance_to_taipei', 'N/A'),
                    '空氣品質等級': self.get_aqi_level(station.get('aqi', 'N/A'))
                })
            
            # 按距離排序
            csv_data.sort(key=lambda x: x['距離台北車站(公里)'] if x['距離台北車站(公里)'] != 'N/A' else float('inf'))
            
            # 寫入 CSV 檔案
            with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
                fieldnames = ['測站名稱', '所在地', 'AQI數值', '經度', '緯度', '距離台北車站(公里)', '空氣品質等級']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                writer.writerows(csv_data)
            
            print(f"數據已匯出至: {filename}")
            
            # 顯示統計資訊
            valid_distances = [s for s in csv_data if s['距離台北車站(公里)'] != 'N/A']
            if valid_distances:
                nearest = valid_distances[0]
                farthest = valid_distances[-1]
                print(f"最近測站: {nearest['測站名稱']} ({nearest['距離台北車站(公里)']} 公里)")
                print(f"最遠測站: {farthest['測站名稱']} ({farthest['距離台北車站(公里)']} 公里)")
            
            return True
            
        except Exception as e:
            print(f"匯出 CSV 時發生錯誤: {e}")
            return False
    
    def run(self, use_sample=False):
        """執行完整流程"""
        print("=" * 50)
        print("台灣 AQI 即時數據地圖生成器")
        print("=" * 50)
        
        # 獲取數據
        if not self.get_aqi_data(use_sample=use_sample):
            print("無法獲取 AQI 數據，程式終止")
            return False
        
        # 計算距離
        if not self.calculate_all_distances():
            print("距離計算失敗")
            return False
        
        # 創建地圖
        print("正在創建地圖...")
        map_obj = self.create_map()
        
        if not map_obj:
            print("無法創建地圖")
            return False
        
        # 保存地圖
        if self.save_map(map_obj):
            print("地圖生成完成！")
        
        # 匯出 CSV
        if self.export_to_csv():
            print("數據分析完成！")
        
        print("\n所有任務完成！")
        print("- 地圖檔案: outputs/aqi_map.html")
        print("- 數據檔案: outputs/aqi_analysis.csv")
        return True

def main():
    """主程式"""
    import sys
    
    use_sample = False
    if len(sys.argv) > 1 and sys.argv[1] == '--sample':
        use_sample = True
        print("使用範例數據模式")
    
    generator = AQIMapGenerator()
    success = generator.run(use_sample=use_sample)
    
    if success:
        print("\n程式執行成功！")
    else:
        print("\n程式執行失敗，請檢查錯誤訊息")

if __name__ == "__main__":
    main()
