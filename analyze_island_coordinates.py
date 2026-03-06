#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析離島和海上座標點位
"""

import pandas as pd

def analyze_island_coordinates():
    """分析離島和海上座標"""
    print("=" * 60)
    print("離島和海上座標分析")
    print("=" * 60)
    
    # 讀取問題清單
    try:
        with open('shelter_issues_found.txt', 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except:
        print("無法讀取問題清單")
        return
    
    # 離島地區定義
    island_areas = {
        '金門': {'lat_range': (24.0, 24.8), 'lon_range': (118.0, 118.5)},
        '馬祖': {'lat_range': (26.0, 26.5), 'lon_range': (119.5, 120.5)},
        '澎湖': {'lat_range': (23.5, 23.8), 'lon_range': (119.5, 119.8)},
        '綠島': {'lat_range': (22.0, 23.0), 'lon_range': (120.0, 121.5)},
        '蘭嶼': {'lat_range': (22.0, 22.8), 'lon_range': (121.0, 122.0)},
        '小琉球': {'lat_range': (24.0, 26.0), 'lon_range': (123.0, 125.0)},
        '釣魚台': {'lat_range': (25.0, 26.0), 'lon_range': (121.0, 123.0)}
    }
    
    # 分析每個問題座標
    island_coords = []
    sea_coords = []
    mainland_coords = []
    
    print("分析問題座標的地理位置:")
    print()
    
    for line in lines[2:]:  # 跳過標題行
        if '第' in line and '行:' in line:
            # 提取座標資訊
            try:
                # 解析座標
                coord_part = line.split('(')[1].split(')')[0]
                lat = float(coord_part.split(',')[0])
                lon = float(coord_part.split(',')[1])
                
                # 判斷地理位置
                location = classify_location(lat, lon, island_areas)
                
                if location['type'] == 'island':
                    island_coords.append({
                        'line': line.strip(),
                        'lat': lat,
                        'lon': lon,
                        'location': location
                    })
                elif location['type'] == 'sea':
                    sea_coords.append({
                        'line': line.strip(),
                        'lat': lat,
                        'lon': lon,
                        'location': location
                    })
                else:
                    mainland_coords.append({
                        'line': line.strip(),
                        'lat': lat,
                        'lon': lon,
                        'location': location
                    })
                    
                print(f"  {line.strip()}")
                print(f"    座標: ({lat:.6f}, {lon:.6f})")
                print(f"    位置: {location['description']}")
                print(f"    離島距離: {location.get('distance_to_mainland', 'N/A')}")
                print()
                
            except:
                print(f"  無法解析: {line.strip()}")
                print()
    
    # 統計結果
    print("=" * 60)
    print("統計結果")
    print("=" * 60)
    
    print(f"總問題座標: {len(island_coords) + len(sea_coords) + len(mainland_coords)}")
    print(f"離島座標: {len(island_coords)}")
    print(f"海上座標: {len(sea_coords)}")
    print(f"本島座標: {len(mainland_coords)}")
    print()
    
    # 離島分佈
    if island_coords:
        print("離島分佈:")
        island_count = {}
        for coord in island_coords:
            island_name = coord['location']['island']
            island_count[island_name] = island_count.get(island_name, 0) + 1
        
        for island, count in sorted(island_count.items(), key=lambda x: x[1], reverse=True):
            print(f"  {island}: {count} 個座標")
        print()
    
    # 海上座標分析
    if sea_coords:
        print("海上座標分析:")
        for i, coord in enumerate(sea_coords):
            print(f"  {i+1}. {coord['location']['description']}")
            print(f"     座標: ({coord['lat']:.6f}, {coord['lon']:.6f})")
        print()
    
    # 儲存分類結果
    save_classification_results(island_coords, sea_coords, mainland_coords)
    
    print("=" * 60)
    print("分析完成！")
    print("=" * 60)

def classify_location(lat: float, lon: float, island_areas: dict) -> dict:
    """分類座標的地理位置"""
    
    # 檢查各個離島地區
    for island_name, area in island_areas.items():
        lat_min, lat_max = area['lat_range']
        lon_min, lon_max = area['lon_range']
        
        if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
            # 計算到台灣本島的概略距離
            taiwan_center = (23.8, 120.8)  # 台灣中心點
            distance = calculate_distance(lat, lon, taiwan_center[0], taiwan_center[1])
            
            return {
                'type': 'island',
                'island': island_name,
                'description': f'{island_name}地區',
                'distance_to_mainland': f'{distance:.1f}公里'
            }
    
    # 檢查是否為海上座標（遠離所有陸地）
    mainland_points = [
        (25.3, 121.6),   # 台灣北端
        (21.8, 120.8),   # 台灣南端
        (119.8, 121.0),  # 台灣西端
        (122.2, 121.0)   # 台灣東端
    ]
    
    min_distance_to_mainland = float('inf')
    for mainland_lat, mainland_lon in mainland_points:
        distance = calculate_distance(lat, lon, mainland_lat, mainland_lon)
        min_distance_to_mainland = min(min_distance_to_mainland, distance)
    
    # 如果距離台灣本島超過 50 公里，視為海上座標
    if min_distance_to_mainland > 50:
        return {
            'type': 'sea',
            'description': '海上遠離陸地',
            'distance_to_mainland': f'{min_distance_to_mainland:.1f}公里'
        }
    
    # 否則視為本島座標
    return {
        'type': 'mainland',
        'description': '台灣本島',
        'distance_to_mainland': 'N/A'
    }

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """計算兩點間的距離（公里）"""
    import math
    
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return 6371 * c  # 地球半徑

def save_classification_results(island_coords: list, sea_coords: list, mainland_coords: list):
    """儲存分類結果"""
    all_coords = island_coords + sea_coords + mainland_coords
    
    with open('coordinate_classification.csv', 'w', encoding='utf-8-sig') as f:
        f.write('類型,行號,緯度,經度,位置描述,距離本島\n')
        
        for coord in island_coords:
            f.write(f"離島,{coord['line']},{coord['lat']:.6f},{coord['lon']:.6f},{coord['location']['description']},{coord['location']['distance_to_mainland']}\n")
        
        for coord in sea_coords:
            f.write(f"海上,{coord['line']},{coord['lat']:.6f},{coord['lon']:.6f},{coord['location']['description']},{coord['location']['distance_to_mainland']}\n")
        
        for coord in mainland_coords:
            f.write(f"本島,{coord['line']},{coord['lat']:.6f},{coord['lon']:.6f},{coord['location']['description']},{coord['location']['distance_to_mainland']}\n")
    
    print("分類結果已儲存至: coordinate_classification.csv")

if __name__ == "__main__":
    import math
    analyze_island_coordinates()
