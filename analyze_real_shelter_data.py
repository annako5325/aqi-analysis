#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析真實避難收容處所數據的座標品質
檢查 WGS84 和 TWD97 混用問題
"""

import pandas as pd
import numpy as np
from typing import List, Tuple, Dict

class RealShelterAnalyzer:
    """真實避難收容處所數據分析器"""
    
    def __init__(self):
        # 台灣邊界定義（WGS84）
        self.taiwan_bounds_wgs84 = {
            'min_lat': 21.8, 'max_lat': 25.3,
            'min_lon': 119.8, 'max_lon': 122.2
        }
        
        # TWD97 範圍
        self.twd97_bounds = {
            'min_x': 170000, 'max_x': 340000,
            'min_y': 2400000, 'max_y': 2780000
        }
    
    def analyze_real_data(self, file_path: str) -> Dict:
        """分析真實避難收容處所數據"""
        print("=" * 60)
        print("真實避難收容處所數據分析")
        print("=" * 60)
        
        # 讀取數據
        try:
            df = pd.read_csv(file_path)
            print(f"成功載入數據: {file_path}")
            print(f"總記錄數: {len(df)}")
        except Exception as e:
            print(f"載入數據失敗: {e}")
            return {}
        
        # 檢查座標欄位
        if '經度' not in df.columns or '緯度' not in df.columns:
            print("錯誤: 找不到經度或緯度欄位")
            return {}
        
        # 移除空值
        df_clean = df.dropna(subset=['經度', '緯度'])
        print(f"有效座標記錄: {len(df_clean)}")
        
        # 分析座標
        coordinates = list(zip(df_clean['緯度'], df_clean['經度']))
        analysis_result = self._analyze_coordinates(coordinates, df_clean)
        
        # 顯示結果
        self._print_analysis_results(analysis_result)
        
        # 儲存分析結果
        self._save_analysis_results(df_clean, analysis_result)
        
        return analysis_result
    
    def _analyze_coordinates(self, coordinates: List[Tuple[float, float]], df: pd.DataFrame) -> Dict:
        """分析座標品質"""
        results = {
            'total_points': len(coordinates),
            'crs_classification': {'WGS84': 0, 'TWD97': 0, 'UNKNOWN': 0},
            'outliers': {'zero_coords': [], 'outside_taiwan': [], 'extreme_values': []},
            'quality_score': 0,
            'coordinate_ranges': {},
            'issues_found': []
        }
        
        # 分類座標
        for i, (lat, lon) in enumerate(coordinates):
            crs_type = self._classify_coordinate(lat, lon)
            results['crs_classification'][crs_type] += 1
            
            # 檢查問題
            if lat == 0 and lon == 0:
                results['outliers']['zero_coords'].append(i)
                results['issues_found'].append(f"第 {i+1} 行: (0,0) 座標")
            elif not self._is_in_taiwan_wgs84(lat, lon):
                results['outliers']['outside_taiwan'].append(i)
                results['issues_found'].append(f"第 {i+1} 行: 座標 ({lat}, {lon}) 在台灣範圍外")
        
        # 計算座標範圍
        lats = [coord[0] for coord in coordinates]
        lons = [coord[1] for coord in coordinates]
        
        results['coordinate_ranges'] = {
            'lat_min': min(lats), 'lat_max': max(lats),
            'lon_min': min(lons), 'lon_max': max(lons)
        }
        
        # 計算品質分數
        valid_points = len(coordinates) - len(results['outliers']['zero_coords']) - len(results['outliers']['outside_taiwan'])
        results['quality_score'] = (valid_points / len(coordinates)) * 100 if len(coordinates) > 0 else 0
        
        return results
    
    def _classify_coordinate(self, lat: float, lon: float) -> str:
        """分類座標系統"""
        if lat == 0 and lon == 0:
            return 'UNKNOWN'
        
        # 檢查是否在 WGS84 台灣範圍內
        if self._is_in_taiwan_wgs84(lat, lon):
            return 'WGS84'
        
        # 檢查是否在 TWD97 範圍內
        if self._is_in_twd97_range(lat, lon):
            return 'TWD97'
        
        return 'UNKNOWN'
    
    def _is_in_taiwan_wgs84(self, lat: float, lon: float) -> bool:
        """檢查是否在台灣 WGS84 範圍內"""
        return (self.taiwan_bounds_wgs84['min_lat'] <= lat <= self.taiwan_bounds_wgs84['max_lat'] and
                self.taiwan_bounds_wgs84['min_lon'] <= lon <= self.taiwan_bounds_wgs84['max_lon'])
    
    def _is_in_twd97_range(self, lat: float, lon: float) -> bool:
        """檢查是否在 TWD97 範圍內"""
        return (self.twd97_bounds['min_x'] <= lat <= self.twd97_bounds['max_x'] and
                self.twd97_bounds['min_y'] <= lon <= self.twd97_bounds['max_y'])
    
    def _print_analysis_results(self, result: Dict) -> None:
        """列印分析結果"""
        print("\n" + "=" * 50)
        print("分析結果")
        print("=" * 50)
        
        print(f"總點位數: {result['total_points']}")
        print(f"品質分數: {result['quality_score']:.1f}/100")
        
        print("\n座標系統分類:")
        crs_data = result['crs_classification']
        total = sum(crs_data.values())
        for crs_type, count in crs_data.items():
            percentage = (count / total * 100) if total > 0 else 0
            print(f"  {crs_type}: {count} ({percentage:.1f}%)")
        
        print("\n問題統計:")
        outliers = result['outliers']
        print(f"  (0,0) 座標: {len(outliers['zero_coords'])}")
        print(f"  台灣範圍外: {len(outliers['outside_taiwan'])}")
        
        if result['issues_found']:
            print(f"\n發現的問題 (前10個):")
            for issue in result['issues_found'][:10]:
                print(f"  ❌ {issue}")
            if len(result['issues_found']) > 10:
                print(f"  ... 還有 {len(result['issues_found'])-10} 個問題")
        
        print("\n座標範圍:")
        ranges = result['coordinate_ranges']
        print(f"  緯度: {ranges['lat_min']:.6f} 到 {ranges['lat_max']:.6f}")
        print(f"  經度: {ranges['lon_min']:.6f} 到 {ranges['lon_max']:.6f}")
    
    def _save_analysis_results(self, df: pd.DataFrame, analysis_result: Dict) -> None:
        """儲存分析結果"""
        # 添加分析結果到原始數據
        df_result = df.copy()
        df_result['crs_type'] = ''
        df_result['quality_status'] = '正常'
        
        for i, (lat, lon) in enumerate(zip(df_result['緯度'], df_result['經度'])):
            crs_type = self._classify_coordinate(lat, lon)
            df_result.loc[i, 'crs_type'] = crs_type
            
            # 標記問題
            if lat == 0 and lon == 0:
                df_result.loc[i, 'quality_status'] = '(0,0)座標'
            elif not self._is_in_taiwan_wgs84(lat, lon):
                df_result.loc[i, 'quality_status'] = '台灣範圍外'
        
        # 儲存結果
        output_file = 'real_shelter_quality_analysis.csv'
        df_result.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\n詳細分析結果已儲存至: {output_file}")
        
        # 生成問題清單
        if analysis_result['issues_found']:
            issues_file = 'shelter_issues_found.txt'
            with open(issues_file, 'w', encoding='utf-8') as f:
                f.write("避難收容處所座標問題清單\n")
                f.write("=" * 40 + "\n")
                for i, issue in enumerate(analysis_result['issues_found'], 1):
                    f.write(f"{i}. {issue}\n")
            print(f"問題清單已儲存至: {issues_file}")

def main():
    """主程式"""
    # 真實數據檔案路徑
    data_file = "data/避難收容處所點位檔案v9.csv"
    
    # 創建分析器
    analyzer = RealShelterAnalyzer()
    
    # 執行分析
    result = analyzer.analyze_real_data(data_file)
    
    print("\n" + "=" * 60)
    print("分析完成！")
    print("=" * 60)
    
    # 總結建議
    crs_data = result.get('crs_classification', {})
    has_wgs84 = crs_data.get('WGS84', 0) > 0
    has_twd97 = crs_data.get('TWD97', 0) > 0
    
    print("\n🎯 改善建議:")
    if has_wgs84 and has_twd97:
        print("  1. 發現混合座標系統問題！")
        print("  2. 建議統一轉換為 WGS84 格式")
        print("  3. 使用專業座標轉換工具確保精度")
    elif result['quality_score'] < 80:
        print("  1. 座標品質需要改善")
        print("  2. 檢查並修正問題座標")
        print("  3. 建立座標驗證機制")
    else:
        print("  1. 座標品質良好")
        print("  2. 繼續維護數據品質")

if __name__ == "__main__":
    main()
