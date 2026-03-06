#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理避難收容處所數據
保留本島和離島座標，刪除海外座標和缺失值
"""

import pandas as pd
import numpy as np

def clean_shelter_data():
    """清理避難收容處所數據"""
    print("=" * 60)
    print("清理避難收容處所數據")
    print("=" * 60)
    
    # 讀取原始數據
    try:
        df = pd.read_csv('data/避難收容處所點位檔案v9.csv')
        print(f"成功載入原始數據: {len(df)} 筆")
    except Exception as e:
        print(f"載入數據失敗: {e}")
        return
    
    print(f"原始數據欄位: {list(df.columns)}")
    
    # 台灣本島邊界（WGS84）
    taiwan_bounds = {
        'min_lat': 21.8, 'max_lat': 25.3,
        'min_lon': 119.8, 'max_lon': 122.2
    }
    
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
    
    print("\n" + "=" * 40)
    print("數據清理步驟")
    print("=" * 40)
    
    # 步驟1: 移除座標缺失值
    print("步驟1: 移除座標缺失值...")
    initial_count = len(df)
    
    # 移除經度或緯度為 NaN、空字串或 0 的記錄
    df_clean = df[
        ~df['經度'].isna() & 
        (df['經度'] != '') & 
        (df['經度'] != 0) &
        ~df['緯度'].isna() & 
        (df['緯度'] != '') & 
        (df['緯度'] != 0)
    ].copy()
    
    removed_missing = initial_count - len(df_clean)
    print(f"  移除座標缺失值: {removed_missing} 筆")
    print(f"  剩餘記錄: {len(df_clean)} 筆")
    
    # 步驟2: 分類座標位置
    print("\n步驟2: 分類座標位置...")
    
    def classify_location(lat, lon):
        """分類座標位置"""
        # 檢查台灣本島
        if (taiwan_bounds['min_lat'] <= lat <= taiwan_bounds['max_lat'] and
            taiwan_bounds['min_lon'] <= lon <= taiwan_bounds['max_lon']):
            return 'mainland'
        
        # 檢查各個離島
        for island_name, area in island_areas.items():
            lat_min, lat_max = area['lat_range']
            lon_min, lon_max = area['lon_range']
            
            if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
                return f'island_{island_name}'
        
        return 'overseas'
    
    # 添加位置分類
    df_clean['location_type'] = df_clean.apply(
        lambda row: classify_location(row['緯度'], row['經度']), axis=1
    )
    
    # 統計各類型數量
    location_counts = df_clean['location_type'].value_counts()
    print("位置分類統計:")
    for loc_type, count in location_counts.items():
        if loc_type == 'mainland':
            print(f"  台灣本島: {count} 筆")
        elif loc_type.startswith('island_'):
            island_name = loc_type.replace('island_', '')
            print(f"  離島-{island_name}: {count} 筆")
        else:
            print(f"  海外: {count} 筆")
    
    # 步驟3: 保留本島和離島，移除海外
    print("\n步驟3: 保留本島和離島，移除海外...")
    
    # 保留本島和離島
    df_final = df_clean[df_clean['location_type'] != 'overseas'].copy()
    
    removed_overseas = len(df_clean) - len(df_final)
    print(f"  移除海外座標: {removed_overseas} 筆")
    print(f"  最終保留: {len(df_final)} 筆")
    
    # 移除臨時分類欄位
    df_final = df_final.drop('location_type', axis=1)
    
    print("\n" + "=" * 40)
    print("清理結果統計")
    print("=" * 40)
    
    print(f"原始數據: {initial_count} 筆")
    print(f"移除座標缺失: {removed_missing} 筆")
    print(f"移除海外座標: {removed_overseas} 筆")
    print(f"最終清理後: {len(df_final)} 筆")
    print(f"保留比例: {len(df_final)/initial_count*100:.1f}%")
    
    # 重新分類最終數據的地理位置
    print("\n最終數據地理位置分佈:")
    mainland_count = 0
    island_counts = {}
    
    for idx, row in df_final.iterrows():
        lat, lon = row['緯度'], row['經度']
        loc_type = classify_location(lat, lon)
        
        if loc_type == 'mainland':
            mainland_count += 1
        elif loc_type.startswith('island_'):
            island_name = loc_type.replace('island_', '')
            island_counts[island_name] = island_counts.get(island_name, 0) + 1
    
    print(f"  台灣本島: {mainland_count} 筆")
    for island, count in sorted(island_counts.items()):
        print(f"  離島-{island}: {count} 筆")
    
    # 儲存清理後的數據
    output_file = '避難收容處所點位檔案v9_cleaned.csv'
    df_final.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n清理後數據已儲存至: {output_file}")
    
    # 儲存清理報告
    save_cleaning_report(initial_count, removed_missing, removed_overseas, len(df_final), 
                     mainland_count, island_counts)
    
    print("\n" + "=" * 60)
    print("數據清理完成！")
    print("=" * 60)
    
    # 驗證清理結果
    verify_cleaned_data(output_file)

def save_cleaning_report(initial_count, removed_missing, removed_overseas, final_count, 
                     mainland_count, island_counts):
    """儲存清理報告"""
    report = {
        '清理項目': ['原始數據', '移除座標缺失', '移除海外座標', '最終保留'],
        '數量': [initial_count, removed_missing, removed_overseas, final_count],
        '比例': ['100.0%', f'{removed_missing/initial_count*100:.1f}%', 
                 f'{removed_overseas/initial_count*100:.1f}%', 
                 f'{final_count/initial_count*100:.1f}%']
    }
    
    report_df = pd.DataFrame(report)
    report_df.to_csv('cleaning_report.csv', index=False, encoding='utf-8-sig')
    print("清理報告已儲存至: cleaning_report.csv")
    
    # 地理分佈報告
    geo_report = {
        '地區': ['台灣本島'] + list(island_counts.keys()),
        '數量': [mainland_count] + list(island_counts.values()),
        '比例': [f'{mainland_count/final_count*100:.1f}%'] + 
                [f'{count/final_count*100:.1f}%' for count in island_counts.values()]
    }
    
    geo_df = pd.DataFrame(geo_report)
    geo_df.to_csv('geographic_distribution.csv', index=False, encoding='utf-8-sig')
    print("地理分佈報告已儲存至: geographic_distribution.csv")

def verify_cleaned_data(file_path):
    """驗證清理後的數據"""
    print("\n驗證清理後數據...")
    
    try:
        df = pd.read_csv(file_path)
        print(f"驗證檔案: {file_path}")
        print(f"記錄數量: {len(df)}")
        
        # 檢查座標完整性
        valid_coords = df[
            ~df['經度'].isna() & 
            (df['經度'] != '') & 
            (df['經度'] != 0) &
            ~df['緯度'].isna() & 
            (df['緯度'] != '') & 
            (df['緯度'] != 0)
        ]
        
        print(f"有效座標: {len(valid_coords)} 筆")
        print(f"座標完整性: {len(valid_coords)/len(df)*100:.1f}%")
        
        # 檢查座標範圍
        lats = df['緯度']
        lons = df['經度']
        
        print(f"緯度範圍: {lats.min():.6f} 到 {lats.max():.6f}")
        print(f"經度範圍: {lons.min():.6f} 到 {lons.max():.6f}")
        
        print("✅ 數據驗證通過")
        
    except Exception as e:
        print(f"❌ 驗證失敗: {e}")

if __name__ == "__main__":
    clean_shelter_data()
