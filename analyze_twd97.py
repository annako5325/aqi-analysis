#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析 TWD97 座標數量
"""

import pandas as pd

def analyze_twd97():
    """分析 TWD97 座標"""
    df = pd.read_csv('shelter_quality_quick_check.csv')
    
    print("=" * 50)
    print("TWD97 座標分析報告")
    print("=" * 50)
    
    print(f"總筆數: {len(df)}")
    print()
    
    # 座標範圍
    print("座標範圍檢查:")
    print(f"緯度範圍: {df['latitude'].min():.2f} 到 {df['latitude'].max():.2f}")
    print(f"經度範圍: {df['longitude'].min():.2f} 到 {df['longitude'].max():.2f}")
    print()
    
    # 識別 TWD97 座標（大於 100000 的值）
    twd97_mask = (df['latitude'] > 100000) | (df['longitude'] > 100000)
    twd97_coords = df[twd97_mask]
    
    print(f"可能的 TWD97 座標 (大於100000的值):")
    print(f"TWD97 筆數: {len(twd97_coords)}")
    print()
    
    if len(twd97_coords) > 0:
        print("TWD97 座標明細:")
        for idx, row in twd97_coords.iterrows():
            print(f"  {row['id']}: {row['name']} - ({row['latitude']:.0f}, {row['longitude']:.0f})")
        print()
        
        # TWD97 統計
        print("TWD97 座標統計:")
        print(f"  X 座標範圍: {twd97_coords['latitude'].min():.0f} 到 {twd97_coords['latitude'].max():.0f}")
        print(f"  Y 座標範圍: {twd97_coords['longitude'].min():.0f} 到 {twd97_coords['longitude'].max():.0f}")
        print()
    
    # WGS84 座標
    wgs84_coords = df[~twd97_mask]
    print(f"WGS84 座標筆數: {len(wgs84_coords)}")
    
    if len(wgs84_coords) > 0:
        print("WGS84 座標範例:")
        for idx, row in wgs84_coords.head(3).iterrows():
            print(f"  {row['id']}: {row['name']} - ({row['latitude']:.6f}, {row['longitude']:.6f})")
    
    print()
    print("=" * 50)
    print("分析完成")
    print("=" * 50)

if __name__ == "__main__":
    analyze_twd97()
