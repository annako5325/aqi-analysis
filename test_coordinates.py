#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試座標轉換和距離計算差異
"""

import math

def haversine_distance(lat1, lon1, lat2, lon2):
    """Haversine 公式計算球面距離"""
    lat1, lon1 = math.radians(lat1), math.radians(lon1)
    lat2, lon2 = math.radians(lat2), math.radians(lon2)
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    r = 6371  # 地球半徑（公里）
    return c * r

def wgs84_to_twd97_simple(lat, lon):
    """簡化的 TWD97 轉換"""
    a = 6378137.0
    f = 1/298.257222101
    e2 = f * (2 - f)
    
    lon0 = math.radians(121)
    k0 = 0.9999
    
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    
    N = a / math.sqrt(1 - e2 * math.sin(lat_rad)**2)
    
    # 子午線弧長
    M = a * (1 - e2/4 - 3*e2**2/64 - 5*e2**3/256) * lat_rad
    M += a * (3*e2/8 + 3*e2**2/32 + 45*e2**3/1024) * math.sin(2*lat_rad)
    M += a * (15*e2**2/256 + 45*e2**3/1024) * math.sin(4*lat_rad)
    M += a * 35*e2**3/3072 * math.sin(6*lat_rad)
    
    dl = lon_rad - lon0
    
    t = math.tan(lat_rad)
    t2 = t * t
    cos_lat = math.cos(lat_rad)
    cos2_lat = cos_lat * cos_lat
    
    x = k0 * N * cos_lat * (dl + (1/6) * (1 - t2 + cos2_lat) * dl**3)
    y = k0 * (M + N * t * (0.5*dl**2 + (1/24)*(5 - t2 + 9*cos2_lat)*dl**4))
    
    return x, y

def euclidean_distance_tw97(lat1, lon1, lat2, lon2):
    """TWD97 平面距離"""
    x1, y1 = wgs84_to_twd97_simple(lat1, lon1)
    x2, y2 = wgs84_to_twd97_simple(lat2, lon2)
    
    dx = x2 - x1
    dy = y2 - y1
    return math.sqrt(dx**2 + dy**2) / 1000  # 轉換為公里

def main():
    # 台北車站座標
    taipei_lat, taipei_lon = 25.0478, 121.5170
    
    # 測試幾個測站
    test_stations = [
        ("萬華", 25.046503, 121.507972),
        ("三重", 25.072611, 121.493806),
        ("板橋", 25.012972, 121.458667),
        ("桃園", 24.9947107, 121.30500531),
        ("台中", 24.151958, 120.641092),
        ("台南", 22.999972, 120.226917),
        ("高雄", 22.627279, 120.301444),
        ("恆春", 21.958069, 120.788928)
    ]
    
    print("=" * 80)
    print("座標轉換和距離計算比較")
    print("=" * 80)
    print(f"{'測站':<8} {'Haversine':<12} {'TWD97':<12} {'差異':<10} {'差異%':<8}")
    print("-" * 80)
    
    for name, lat, lon in test_stations:
        # Haversine 距離
        haversine = haversine_distance(taipei_lat, taipei_lon, lat, lon)
        
        # TWD97 距離
        twd97 = euclidean_distance_tw97(taipei_lat, taipei_lon, lat, lon)
        
        # 差異計算
        diff = abs(haversine - twd97)
        diff_percent = (diff / haversine) * 100 if haversine > 0 else 0
        
        print(f"{name:<8} {haversine:<12.2f} {twd97:<12.2f} {diff:<10.3f} {diff_percent:<8.3f}")
    
    print("-" * 80)
    
    # 顯示 TWD97 座標轉換結果
    print("\nTWD97 座標轉換結果（台北車站為原點）:")
    print(f"台北車站 WGS84: ({taipei_lat}, {taipei_lon})")
    taipei_x, taipei_y = wgs84_to_twd97_simple(taipei_lat, taipei_lon)
    print(f"台北車站 TWD97: ({taipei_x:.2f}, {taipei_y:.2f})")
    
    print("\n其他測站 TWD97 座標:")
    for name, lat, lon in test_stations[:3]:
        x, y = wgs84_to_twd97_simple(lat, lon)
        print(f"{name}: ({x:.2f}, {y:.2f})")

if __name__ == "__main__":
    main()
