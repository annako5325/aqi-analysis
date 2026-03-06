#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檢查避難收容處所數據的座標缺失值
"""

import pandas as pd
import numpy as np

def check_missing_coordinates():
    """檢查座標缺失值"""
    print("=" * 60)
    print("避難收容處所座標缺失值檢查")
    print("=" * 60)
    
    # 讀取原始數據
    try:
        df = pd.read_csv('data/避難收容處所點位檔案v9.csv')
        print(f"成功載入數據: data/避難收容處所點位檔案v9.csv")
        print(f"總記錄數: {len(df)}")
    except Exception as e:
        print(f"載入數據失敗: {e}")
        return
    
    print("\n" + "=" * 40)
    print("欄位檢查")
    print("=" * 40)
    
    # 檢查所有欄位
    print(f"總欄位數: {len(df.columns)}")
    print("欄位列表:")
    for i, col in enumerate(df.columns, 1):
        print(f"  {i:2d}. {col}")
    
    print("\n" + "=" * 40)
    print("座標欄位缺失值分析")
    print("=" * 40)
    
    # 檢查座標相關欄位
    coordinate_fields = ['經度', '緯度', '序號', '縣市及鄉鎮市區', '村里', '避難收容處所地址', '避難收容處所名稱']
    
    for field in coordinate_fields:
        if field in df.columns:
            missing_count = df[field].isna().sum()
            empty_count = (df[field] == '').sum()
            zero_count = (df[field] == 0).sum()
            total_missing = missing_count + empty_count + zero_count
            
            print(f"\n{field}:")
            print(f"  總記錄: {len(df)}")
            print(f"  NaN 值: {missing_count}")
            print(f"  空字串: {empty_count}")
            print(f"  零值: {zero_count}")
            print(f"  總缺失: {total_missing} ({total_missing/len(df)*100:.1f}%)")
        else:
            print(f"\n{field}: 欄位不存在")
    
    print("\n" + "=" * 40)
    print("座標缺失值詳細分析")
    print("=" * 40)
    
    # 詳細座標分析
    if '經度' in df.columns and '緯度' in df.columns:
        # 各種缺失情況
        missing_lat = df['緯度'].isna() | (df['緯度'] == '') | (df['緯度'] == 0)
        missing_lon = df['經度'].isna() | (df['經度'] == '') | (df['經度'] == 0)
        
        # 完全缺失座標的記錄
        missing_both = missing_lat & missing_lon
        
        # 部分缺失座標的記錄
        missing_lat_only = missing_lat & ~missing_lon
        missing_lon_only = missing_lon & ~missing_lat
        
        # 有效座標的記錄
        valid_coords = ~missing_lat & ~missing_lon
        
        print(f"完全缺失座標 (經度&緯度都缺失): {missing_both.sum()} 筆")
        print(f"僅缺失緯度: {missing_lat_only.sum()} 筆")
        print(f"僅缺失經度: {missing_lon_only.sum()} 筆")
        print(f"有效座標: {valid_coords.sum()} 筆")
        
        # 計算有效座標比例
        valid_percentage = valid_coords.sum() / len(df) * 100
        print(f"有效座標比例: {valid_percentage:.1f}%")
        
        print("\n缺失座標的記錄樣本:")
        missing_records = df[missing_both].head(10)
        for idx, row in missing_records.iterrows():
            print(f"  第 {idx+1} 行: {row.get('避難收容處所名稱', 'N/A')} - {row.get('縣市及鄉鎮市區', 'N/A')}")
        
        # 儲存缺失座標記錄
        if missing_both.sum() > 0:
            missing_df = df[missing_both].copy()
            output_file = 'missing_coordinates_records.csv'
            missing_df.to_csv(output_file, index=False, encoding='utf-8-sig')
            print(f"\n缺失座標記錄已儲存至: {output_file}")
    
    print("\n" + "=" * 40)
    print("其他欄位缺失值統計")
    print("=" * 40)
    
    # 統計所有欄位的缺失值
    missing_stats = []
    for col in df.columns:
        missing_count = df[col].isna().sum()
        empty_count = (df[col] == '').sum()
        total_missing = missing_count + empty_count
        
        if total_missing > 0:
            missing_stats.append({
                '欄位': col,
                '缺失數': total_missing,
                '缺失比例': total_missing/len(df)*100
            })
    
    # 按缺失數排序
    missing_stats.sort(key=lambda x: x['缺失數'], reverse=True)
    
    print("缺失值最多的前10個欄位:")
    for i, stat in enumerate(missing_stats[:10], 1):
        print(f"  {i:2d}. {stat['欄位']}: {stat['缺失數']} ({stat['缺失比例']:.1f}%)")
    
    # 儲存完整缺失值統計
    if missing_stats:
        missing_df = pd.DataFrame(missing_stats)
        stats_file = 'missing_values_statistics.csv'
        missing_df.to_csv(stats_file, index=False, encoding='utf-8-sig')
        print(f"\n缺失值統計已儲存至: {stats_file}")
    
    print("\n" + "=" * 60)
    print("檢查完成！")
    print("=" * 60)
    
    # 總結
    if '經度' in df.columns and '緯度' in df.columns:
        total_records = len(df)
        valid_coords = (~(df['緯度'].isna() | (df['緯度'] == '') | (df['緯度'] == 0) | 
                        df['經度'].isna() | (df['經度'] == '') | (df['經度'] == 0))).sum()
        
        print(f"\n📊 座標數據品質總結:")
        print(f"  總記錄數: {total_records}")
        print(f"  有效座標: {valid_coords} ({valid_coords/total_records*100:.1f}%)")
        print(f"  缺失座標: {total_records - valid_coords} ({(total_records - valid_coords)/total_records*100:.1f}%)")
        
        if valid_coords/total_records >= 0.95:
            print("  ✅ 座標完整性優秀")
        elif valid_coords/total_records >= 0.90:
            print("  ⚠️ 座標完整性良好")
        else:
            print("  ❌ 座標完整性需要改善")

if __name__ == "__main__":
    check_missing_coordinates()
