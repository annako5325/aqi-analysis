#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
從原始 aqi_map.html 提取所有 85 個 AQI 測站數據
"""

import re
import json

def extract_aqi_stations_from_html(html_file):
    """從 HTML 檔案提取 AQI 測站數據"""
    
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取所有 circle_marker 的數據
    stations = []
    
    # 正則表達式匹配 circle_marker 的座標和彈出視窗內容
    circle_pattern = r'var circle_marker_[a-f0-9]+ = L\.circleMarker\(\s*\[([0-9.-]+), ([0-9.-]+)\],\s*\{[^}]*fillColor": "([^"]+)"[^}]*\}\s*\)'
    
    # 找出所有 circle_marker
    matches = re.findall(circle_pattern, content)
    
    print(f"找到 {len(matches)} 個測站")
    
    # 提取彈出視窗內容來獲取測站名稱和 AQI 值
    popup_pattern = r'var popup_[a-f0-9]+ = L\.popup\(\{"maxWidth": 250\}\);\s*[^<]*<div[^>]*>.*?<h4[^>]*>([^<]+)</h4>.*?AQI[^>]*>([^<]+)</span>.*?</div>'
    
    popup_matches = re.findall(popup_pattern, content, re.DOTALL)
    
    print(f"找到 {len(popup_matches)} 個彈出視窗")
    
    # 組合數據
    for i, (lat, lon, color) in enumerate(matches):
        if i < len(popup_matches):
            site_name, aqi_value = popup_matches[i]
            
            # 清理數據
            site_name = site_name.strip()
            aqi_value = aqi_value.strip()
            
            # 嘗試提取 AQI 數值
            aqi_match = re.search(r'(\d+)', aqi_value)
            aqi_num = int(aqi_match.group(1)) if aqi_match else 0
            
            station = {
                'SiteName': site_name,
                'lat': float(lat),
                'lon': float(lon),
                'AQI': aqi_num,
                'Color': color
            }
            
            stations.append(station)
    
    return stations

def get_county_from_coordinates(lat, lon):
    """根據座標推斷縣市"""
    # 簡單的座標範圍判斷
    if 25.0 <= lat <= 25.3 and 121.3 <= lon <= 121.8:
        return "台北市"
    elif 24.9 <= lat <= 25.2 and 121.2 <= lon <= 121.7:
        return "新北市"
    elif 24.8 <= lat <= 25.1 and 121.0 <= lon <= 121.4:
        return "桃園市"
    elif 24.5 <= lat <= 24.9 and 120.8 <= lon <= 121.2:
        return "新竹市"
    elif 24.2 <= lat <= 24.6 and 120.6 <= lon <= 121.0:
        return "苗栗市"
    elif 24.0 <= lat <= 24.3 and 120.5 <= lon <= 120.9:
        return "台中市"
    elif 23.8 <= lat <= 24.2 and 120.3 <= lon <= 120.7:
        return "彰化市"
    elif 23.6 <= lat <= 24.0 and 120.4 <= lon <= 120.8:
        return "南投市"
    elif 23.4 <= lat <= 23.8 and 120.2 <= lon <= 120.6:
        return "雲林市"
    elif 23.2 <= lat <= 23.6 and 120.3 <= lon <= 120.7:
        return "嘉義市"
    elif 22.8 <= lat <= 23.2 and 120.1 <= lon <= 120.5:
        return "台南市"
    elif 22.4 <= lat <= 22.8 and 120.3 <= lon <= 120.7:
        return "高雄市"
    elif 22.2 <= lat <= 22.6 and 120.4 <= lon <= 120.8:
        return "屏東市"
    elif 23.8 <= lat <= 24.2 and 121.4 <= lon <= 121.8:
        return "宜蘭市"
    elif 22.6 <= lat <= 23.0 and 121.0 <= lon <= 121.4:
        return "花蓮市"
    elif 22.6 <= lat <= 23.0 and 120.9 <= lon <= 121.3:
        return "台東市"
    elif 23.5 <= lat <= 23.7 and 119.5 <= lon <= 119.7:
        return "澎湖縣"
    elif 26.1 <= lat <= 26.2 and 119.9 <= lon <= 120.0:
        return "連江縣"
    else:
        return "未知地區"

def main():
    """主程式"""
    print("從 aqi_map.html 提取 AQI 測站數據...")
    
    # 提取測站數據
    stations = extract_aqi_stations_from_html("outputs/aqi_map.html")
    
    # 添加縣市資訊和 PM2.5 估算值
    for station in stations:
        station['County'] = get_county_from_coordinates(station['lat'], station['lon'])
        
        # 根據 AQI 估算 PM2.5 (簡化公式)
        aqi = station['AQI']
        if aqi <= 50:
            station['PM25'] = round(aqi * 0.3, 1)
        elif aqi <= 100:
            station['PM25'] = round(15 + (aqi - 50) * 0.5, 1)
        else:
            station['PM25'] = round(40 + (aqi - 100) * 0.7, 1)
    
    # 保存數據
    import pandas as pd
    df = pd.DataFrame(stations)
    df.to_csv('extracted_aqi_stations.csv', index=False, encoding='utf-8-sig')
    
    print(f"成功提取 {len(stations)} 個 AQI 測站")
    print("數據已保存至 extracted_aqi_stations.csv")
    
    # 顯示統計
    print("\n測站統計:")
    print(f"總測站數: {len(stations)}")
    
    # 按 AQI 等級統計
    good_count = len([s for s in stations if s['AQI'] <= 50])
    moderate_count = len([s for s in stations if 51 <= s['AQI'] <= 100])
    poor_count = len([s for s in stations if s['AQI'] > 100])
    
    print(f"良好 (0-50): {good_count} 個")
    print(f"普通 (51-100): {moderate_count} 個")
    print(f"不佳 (101+): {poor_count} 個")
    
    # 按縣市統計
    county_stats = {}
    for station in stations:
        county = station['County']
        if county not in county_stats:
            county_stats[county] = 0
        county_stats[county] += 1
    
    print("\n按縣市分佈:")
    for county, count in sorted(county_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"{county}: {count} 個")
    
    return stations

if __name__ == "__main__":
    stations = main()
