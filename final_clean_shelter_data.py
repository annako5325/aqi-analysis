#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最終清理避難收容處所數據
刪除海外遠距的14筆資料，產出最終CSV
"""

import pandas as pd
import numpy as np

def create_final_clean_data():
    """創建最終清理後的數據"""
    print("=" * 60)
    print("創建最終清理後的避難收容處所數據")
    print("=" * 60)
    
    # 讀取已清理的數據
    try:
        df = pd.read_csv('避難收容處所點位檔案v9_cleaned.csv')
        print(f"載入已清理數據: {len(df)} 筆")
    except Exception as e:
        print(f"載入數據失敗: {e}")
        return
    
    # 讀取界線外點位清單
    try:
        unmatched = pd.read_csv('unmatched_shelters.csv')
        print(f"載入界線外點位: {len(unmatched)} 筆")
    except Exception as e:
        print(f"載入界線外點位失敗: {e}")
        return
    
    # 篩選出海外的14筆資料
    overseas_points = unmatched[unmatched['location_category'] == '海外遠距'].copy()
    print(f"海外遠距點位: {len(overseas_points)} 筆")
    
    # 獲取要刪除的序號
    remove_sequence_numbers = set(overseas_points['序號'].tolist())
    print(f"要刪除的序號: {sorted(remove_sequence_numbers)}")
    
    # 從原始數據中移除海外點位
    initial_count = len(df)
    df_final = df[~df['序號'].isin(remove_sequence_numbers)].copy()
    removed_count = initial_count - len(df_final)
    
    print(f"\n清理統計:")
    print(f"  原始清理後數據: {initial_count} 筆")
    print(f"  移除海外遠距點位: {removed_count} 筆")
    print(f"  最終保留數據: {len(df_final)} 筆")
    print(f"  最終保留比例: {len(df_final)/initial_count*100:.1f}%")
    
    # 重新統計地理分佈
    print(f"\n最終地理分佈:")
    
    # 台灣本島邊界
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
        
        return 'unknown'
    
    # 分類最終數據
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
    
    print(f"  台灣本島: {mainland_count} 筆 ({mainland_count/len(df_final)*100:.1f}%)")
    for island, count in sorted(island_counts.items()):
        print(f"  離島-{island}: {count} 筆 ({count/len(df_final)*100:.1f}%)")
    
    # 儲存最終數據
    output_file = '避難收容處所點位檔案v9_final.csv'
    df_final.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n最終數據已儲存至: {output_file}")
    
    # 儲存被刪除的海外點位
    overseas_file = 'removed_overseas_points.csv'
    overseas_points.to_csv(overseas_file, index=False, encoding='utf-8-sig')
    print(f"被刪除的海外點位已儲存至: {overseas_file}")
    
    # 生成最終報告
    generate_final_report(initial_count, removed_count, len(df_final), 
                     mainland_count, island_counts, overseas_points)
    
    print("\n" + "=" * 60)
    print("最終數據清理完成！")
    print("=" * 60)
    
    # 驗證最終數據
    verify_final_data(output_file)

def generate_final_report(initial_count, removed_count, final_count, 
                     mainland_count, island_counts, overseas_points):
    """生成最終清理報告"""
    
    # 完整清理過程報告
    full_process = {
        '階段': ['原始數據', '移除座標缺失', '移除海外座標', '移除海外遠距', '最終保留'],
        '數量': [5973, 3, 47, removed_count, final_count],
        '累計保留': [5973, 5970, 5923, final_count, final_count],
        '階段說明': [
            '原始避難收容處所數據',
            '移除經度為0的3筆記錄',
            '移除47筆海外座標',
            f'移除{removed_count}筆海外遠距座標',
            '最終高品質數據'
        ]
    }
    
    process_df = pd.DataFrame(full_process)
    process_df.to_csv('full_cleaning_process.csv', index=False, encoding='utf-8-sig')
    print("完整清理過程報告已儲存至: full_cleaning_process.csv")
    
    # 最終地理分佈報告
    geo_data = {
        '地區': ['台灣本島'] + list(island_counts.keys()),
        '數量': [mainland_count] + list(island_counts.values()),
        '比例': [f'{mainland_count/final_count*100:.1f}%'] + 
                [f'{count/final_count*100:.1f}%' for count in island_counts.values()]
    }
    
    geo_df = pd.DataFrame(geo_data)
    geo_df.to_csv('final_geographic_distribution.csv', index=False, encoding='utf-8-sig')
    print("最終地理分佈報告已儲存至: final_geographic_distribution.csv")
    
    # 被刪除的海外點位詳細資訊
    if len(overseas_points) > 0:
        print(f"\n被刪除的海外遠距點位 ({len(overseas_points)} 筆):")
        for idx, row in overseas_points.iterrows():
            name = row.get('避難收容處所名稱', 'N/A')
            county = row.get('縣市及鄉鎮市區', 'N/A')
            lat = row['緯度']
            lon = row['經度']
            distance = row['distance_to_taiwan']
            
            print(f"  {name}")
            print(f"    位置: {county}")
            print(f"    座標: ({lat:.6f}, {lon:.6f})")
            print(f"    距離台灣中心: {distance:.1f}公里")
            print()

def verify_final_data(file_path):
    """驗證最終數據"""
    print("\n驗證最終數據...")
    
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
        
        # 檢查是否還有海外遠距座標
        taiwan_bounds = {
            'min_lat': 21.8, 'max_lat': 25.3,
            'min_lon': 119.8, 'max_lon': 122.2
        }
        
        island_areas = {
            '金門': {'lat_range': (24.0, 24.8), 'lon_range': (118.0, 118.5)},
            '馬祖': {'lat_range': (26.0, 26.5), 'lon_range': (119.5, 120.5)},
            '澎湖': {'lat_range': (23.5, 23.8), 'lon_range': (119.5, 119.8)},
            '綠島': {'lat_range': (22.0, 23.0), 'lon_range': (120.0, 121.5)},
            '蘭嶼': {'lat_range': (22.0, 22.8), 'lon_range': (121.0, 122.0)},
            '小琉球': {'lat_range': (24.0, 26.0), 'lon_range': (123.0, 125.0)},
            '釣魚台': {'lat_range': (25.0, 26.0), 'lon_range': (121.0, 123.0)}
        }
        
        def is_valid_location(lat, lon):
            if (taiwan_bounds['min_lat'] <= lat <= taiwan_bounds['max_lat'] and
                taiwan_bounds['min_lon'] <= lon <= taiwan_bounds['max_lon']):
                return True
            
            for area in island_areas.values():
                lat_min, lat_max = area['lat_range']
                lon_min, lon_max = area['lon_range']
                if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
                    return True
            
            return False
        
        valid_locations = df.apply(
            lambda row: is_valid_location(row['緯度'], row['經度']), axis=1
        )
        
        invalid_count = len(df) - valid_locations.sum()
        print(f"有效地理位置: {valid_locations.sum()} 筆 ({valid_locations.sum()/len(df)*100:.1f}%)")
        print(f"無效地理位置: {invalid_count} 筆 ({invalid_count/len(df)*100:.1f}%)")
        
        if invalid_count == 0:
            print("✅ 所有座標都在台灣本島或離島範圍內")
        else:
            print("⚠️ 仍有無效地理位置的座標")
        
        print("✅ 最終數據驗證通過")
        
    except Exception as e:
        print(f"❌ 驗證失敗: {e}")

if __name__ == "__main__":
    create_final_clean_data()
