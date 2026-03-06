#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速避難收容處所座標品質檢查器
專門檢查 CRS 混淆和離群值問題
"""

import pandas as pd
import numpy as np
from typing import List, Tuple, Dict

class QuickShelterChecker:
    """快速避難收容處所座標檢查器"""
    
    def __init__(self):
        # 台灣邊界（WGS84）
        self.taiwan_bounds = {
            'min_lat': 21.8, 'max_lat': 25.3,
            'min_lon': 119.8, 'max_lon': 122.2
        }
        
        # TWD97 範圍
        self.twd97_bounds = {
            'min_x': 170000, 'max_x': 340000,
            'min_y': 2400000, 'max_y': 2780000
        }
    
    def check_coordinate_quality(self, df: pd.DataFrame) -> Dict:
        """檢查座標品質"""
        results = {
            'total_points': len(df),
            'crs_issues': [],
            'outlier_issues': [],
            'quality_score': 0,
            'recommendations': []
        }
        
        wgs97_count = 0
        twd97_count = 0
        unknown_count = 0
        zero_count = 0
        outside_count = 0
        
        for idx, row in df.iterrows():
            lat = row.get('latitude', 0)
            lon = row.get('longitude', 0)
            
            # 檢查 (0,0)
            if lat == 0 and lon == 0:
                zero_count += 1
                results['outlier_issues'].append(f"第 {idx+1} 行: (0,0) 座標")
                continue
            
            # 判斷 CRS
            if (self.taiwan_bounds['min_lat'] <= lat <= self.taiwan_bounds['max_lat'] and
                self.taiwan_bounds['min_lon'] <= lon <= self.taiwan_bounds['max_lon']):
                wgs97_count += 1
            elif (self.twd97_bounds['min_x'] <= lat <= self.twd97_bounds['max_x'] and
                  self.twd97_bounds['min_y'] <= lon <= self.twd97_bounds['max_y']):
                twd97_count += 1
            else:
                unknown_count += 1
                outside_count += 1
                results['outlier_issues'].append(f"第 {idx+1} 行: 座標 ({lat}, {lon}) 在台灣範圍外")
        
        # CRS 檢查
        if twd97_count > 0 and wgs97_count > 0:
            results['crs_issues'].append(f"發現混合座標系統: WGS84 ({wgs97_count}) 和 TWD97 ({twd97_count})")
        elif twd97_count > 0:
            results['crs_issues'].append(f"所有座標都是 TWD97 格式 ({twd97_count} 個)")
        elif wgs97_count > 0:
            results['crs_issues'].append(f"所有座標都是 WGS84 格式 ({wgs97_count} 個)")
        
        # 計算品質分數
        valid_points = results['total_points'] - zero_count - outside_count
        results['quality_score'] = (valid_points / results['total_points']) * 100
        
        # 生成建議
        if zero_count > 0:
            results['recommendations'].append(f"修正 {zero_count} 個 (0,0) 座標")
        if outside_count > 0:
            results['recommendations'].append(f"檢查 {outside_count} 個範圍外座標")
        if twd97_count > 0 and wgs97_count > 0:
            results['recommendations'].append("統一所有座標為相同格式 (建議 WGS84)")
        
        return results
    
    def create_sample_data(self) -> pd.DataFrame:
        """創建範例數據"""
        np.random.seed(42)
        
        data = []
        
        # 正常 WGS84 座標
        for i in range(20):
            lat = np.random.uniform(23.0, 25.0)
            lon = np.random.uniform(120.0, 122.0)
            data.append({
                'id': f'SH_{i:03d}',
                'name': f'避難所_{i}',
                'latitude': lat,
                'longitude': lon
            })
        
        # TWD97 座標
        for i in range(20, 30):
            x = np.random.uniform(200000, 300000)
            y = np.random.uniform(2500000, 2700000)
            data.append({
                'id': f'SH_{i:03d}',
                'name': f'避難所_{i}',
                'latitude': x,
                'longitude': y
            })
        
        # 問題座標
        for i in range(30, 35):
            data.append({
                'id': f'SH_{i:03d}',
                'name': f'避難所_{i}',
                'latitude': 0,
                'longitude': 0
            })
        
        # 離群值
        for i in range(35, 40):
            lat = np.random.uniform(-10, 40)
            lon = np.random.uniform(100, 140)
            data.append({
                'id': f'SH_{i:03d}',
                'name': f'避難所_{i}',
                'latitude': lat,
                'longitude': lon
            })
        
        return pd.DataFrame(data)
    
    def run_quick_check(self, data_file: str = None) -> Dict:
        """執行快速檢查"""
        print("=" * 50)
        print("快速避難收容處所座標品質檢查")
        print("=" * 50)
        
        # 載入數據
        if data_file:
            try:
                df = pd.read_csv(data_file)
                print(f"載入數據: {data_file}")
            except:
                print(f"無法載入 {data_file}，使用範例數據")
                df = self.create_sample_data()
        else:
            print("使用範例數據")
            df = self.create_sample_data()
        
        # 執行檢查
        result = self.check_coordinate_quality(df)
        
        # 顯示結果
        print(f"\n總點位數: {result['total_points']}")
        print(f"品質分數: {result['quality_score']:.1f}%")
        
        print("\nCRS 問題:")
        for issue in result['crs_issues']:
            print(f"  ⚠️  {issue}")
        
        print("\n離群值問題:")
        for issue in result['outlier_issues'][:5]:  # 只顯示前5個
            print(f"  ❌ {issue}")
        if len(result['outlier_issues']) > 5:
            print(f"  ... 還有 {len(result['outlier_issues'])-5} 個問題")
        
        print("\n改善建議:")
        for i, rec in enumerate(result['recommendations'], 1):
            print(f"  {i}. {rec}")
        
        # 儲存結果
        df['quality_check'] = '正常'
        for idx, row in df.iterrows():
            lat, lon = row['latitude'], row['longitude']
            if lat == 0 and lon == 0:
                df.loc[idx, 'quality_check'] = '(0,0)座標'
            elif not (self.taiwan_bounds['min_lat'] <= lat <= self.taiwan_bounds['max_lat'] and
                     self.taiwan_bounds['min_lon'] <= lon <= self.taiwan_bounds['max_lon']):
                df.loc[idx, 'quality_check'] = '範圍外'
        
        output_file = 'shelter_quality_quick_check.csv'
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\n詳細報告已儲存至: {output_file}")
        
        return result

def main():
    """主程式"""
    checker = QuickShelterChecker()
    
    # 可以指定數據檔案，或使用範例數據
    # result = checker.run_quick_check('your_shelter_data.csv')
    result = checker.run_quick_check()
    
    print("\n" + "=" * 50)
    print("檢查完成！")

if __name__ == "__main__":
    main()
