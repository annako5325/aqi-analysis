#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
避難收容處所點位座標品質檢查器
CRS Confusion: 檢查座標是 TWD97 (EPSG:3826) 還是 WGS84 (EPSG:4326)
Outliers: 偵測位在台灣邊界外或為 (0,0) 的異常點位
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Tuple, List, Dict
import warnings
warnings.filterwarnings('ignore')

# 設定中文字體
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

class ShelterCoordinateQualityChecker:
    """避難收容處所座標品質檢查器"""
    
    def __init__(self):
        # 台灣邊界定義（WGS84）
        self.taiwan_bounds_wgs84 = {
            'min_lat': 21.8,   # 南端
            'max_lat': 25.3,   # 北端
            'min_lon': 119.8,  # 西端
            'max_lon': 122.2   # 東端
        }
        
        # 台灣邊界定義（TWD97）
        self.taiwan_bounds_twd97 = {
            'min_x': 170000,   # 西端
            'max_x': 340000,   # 東端
            'min_y': 2400000,  # 南端
            'max_y': 2780000   # 北端
        }
        
        # 台灣主要城市中心點（WGS84）
        self.city_centers = {
            '台北': (25.0478, 121.5170),
            '新北': (25.0173, 121.4663),
            '桃園': (24.9936, 121.3009),
            '台中': (24.1477, 120.6736),
            '台南': (22.9999, 120.2269),
            '高雄': (22.6273, 120.3014),
            '基隆': (25.1276, 121.7392),
            '新竹': (24.8138, 120.9675),
            '嘉義': (23.4801, 120.4491),
            '宜蘭': (24.7577, 121.7623),
            '花蓮': (23.7569, 121.6063),
            '台東': (22.7518, 121.1525)
        }
    
    def detect_crs(self, coordinates: List[Tuple[float, float]]) -> Dict[str, int]:
        """偵測座標參考系統 (CRS)"""
        crs_counts = {'WGS84': 0, 'TWD97': 0, 'UNKNOWN': 0}
        
        for lat, lon in coordinates:
            crs_type = self._classify_single_coordinate(lat, lon)
            crs_counts[crs_type] += 1
        
        return crs_counts
    
    def _classify_single_coordinate(self, lat: float, lon: float) -> str:
        """分類單一點位的座標系統"""
        # 檢查是否為 (0,0) 或無效值
        if lat == 0 and lon == 0:
            return 'UNKNOWN'
        
        # 檢查是否在 WGS84 台灣範圍內
        if (self.taiwan_bounds_wgs84['min_lat'] <= lat <= self.taiwan_bounds_wgs84['max_lat'] and
            self.taiwan_bounds_wgs84['min_lon'] <= lon <= self.taiwan_bounds_wgs84['max_lon']):
            return 'WGS84'
        
        # 檢查是否在 TWD97 台灣範圍內
        if (self.taiwan_bounds_twd97['min_x'] <= lat <= self.taiwan_bounds_twd97['max_x'] and
            self.taiwan_bounds_twd97['min_y'] <= lon <= self.taiwan_bounds_twd97['max_y']):
            return 'TWD97'
        
        return 'UNKNOWN'
    
    def detect_outliers(self, coordinates: List[Tuple[float, float]]) -> Dict:
        """偵測離群值"""
        outliers = {
            'zero_coordinates': [],
            'outside_taiwan_wgs84': [],
            'outside_taiwan_twd97': [],
            'extreme_values': []
        }
        
        for i, (lat, lon) in enumerate(coordinates):
            # 檢查 (0,0) 座標
            if lat == 0 and lon == 0:
                outliers['zero_coordinates'].append(i)
                continue
            
            # 檢查是否在 WGS84 台灣範圍外
            if not (self.taiwan_bounds_wgs84['min_lat'] <= lat <= self.taiwan_bounds_wgs84['max_lat'] and
                    self.taiwan_bounds_wgs84['min_lon'] <= lon <= self.taiwan_bounds_wgs84['max_lon']):
                outliers['outside_taiwan_wgs84'].append(i)
            
            # 檢查是否在 TWD97 台灣範圍外
            if not (self.taiwan_bounds_twd97['min_x'] <= lat <= self.taiwan_bounds_twd97['max_x'] and
                    self.taiwan_bounds_twd97['min_y'] <= lon <= self.taiwan_bounds_twd97['max_y']):
                outliers['outside_taiwan_twd97'].append(i)
            
            # 檢查極端值（遠離所有城市中心）
            min_distance_to_city = float('inf')
            for city_name, (city_lat, city_lon) in self.city_centers.items():
                distance = self._haversine_distance(lat, lon, city_lat, city_lon)
                min_distance_to_city = min(min_distance_to_city, distance)
            
            # 如果距離最近城市超過 200 公里，視為極端值
            if min_distance_to_city > 200:
                outliers['extreme_values'].append(i)
        
        return outliers
    
    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """計算兩點間的 Haversine 距離（公里）"""
        import math
        
        lat1, lon1 = math.radians(lat1), math.radians(lon1)
        lat2, lon2 = math.radians(lat2), math.radians(lon2)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return 6371 * c  # 地球半徑（公里）
    
    def convert_twd97_to_wgs84(self, x: float, y: float) -> Tuple[float, float]:
        """將 TWD97 座標轉換為 WGS84（簡化版）"""
        # 這裡使用簡化的轉換公式，實際應用中建議使用 pyproj
        import math
        
        # TWD97 參數
        a = 6378137.0
        f = 1/298.257222101
        e2 = f * (2 - f)
        
        # 中央經線
        lon0 = math.radians(121)
        k0 = 0.9999
        
        # 簡化逆轉換
        lat = (y - 2750000) / 111000  # 粗略估計
        lon = (x - 250000) / 100000 + 121  # 粗略估計
        
        return lat, lon
    
    def generate_sample_data(self, n_points: int = 100) -> pd.DataFrame:
        """生成範例測試數據"""
        np.random.seed(42)
        
        data = []
        
        # 正常 WGS84 座標（70%）
        for i in range(int(n_points * 0.7)):
            city = np.random.choice(list(self.city_centers.keys()))
            center_lat, center_lon = self.city_centers[city]
            
            # 在城市中心周圍 20 公里內隨機分佈
            lat_offset = np.random.normal(0, 0.1)  # 約 10 公里
            lon_offset = np.random.normal(0, 0.1)
            
            data.append({
                'id': f'SHelter_{i:03d}',
                'name': f'避難所_{city}_{i}',
                'latitude': center_lat + lat_offset,
                'longitude': center_lon + lon_offset,
                'city': city,
                'crs': 'WGS84'
            })
        
        # TWD97 座標（15%）
        for i in range(int(n_points * 0.15), int(n_points * 0.85)):
            city = np.random.choice(list(self.city_centers.keys()))
            center_lat, center_lon = self.city_centers[city]
            
            # 轉換為 TWD97 並添加偏移
            x = 250000 + (center_lon - 121) * 100000 + np.random.normal(0, 5000)
            y = 2750000 + center_lat * 111000 + np.random.normal(0, 5000)
            
            data.append({
                'id': f'Shelter_{i:03d}',
                'name': f'避難所_{city}_{i}',
                'latitude': x,
                'longitude': y,
                'city': city,
                'crs': 'TWD97'
            })
        
        # (0,0) 座標（5%）
        for i in range(int(n_points * 0.85), int(n_points * 0.9)):
            data.append({
                'id': f'Shelter_{i:03d}',
                'name': f'避難所_未知_{i}',
                'latitude': 0,
                'longitude': 0,
                'city': '未知',
                'crs': 'UNKNOWN'
            })
        
        # 離群值（10%）
        for i in range(int(n_points * 0.9), n_points):
            # 隨機離群座標
            lat = np.random.uniform(-10, 40)
            lon = np.random.uniform(100, 140)
            
            data.append({
                'id': f'Shelter_{i:03d}',
                'name': f'避難所_離群_{i}',
                'latitude': lat,
                'longitude': lon,
                'city': '離群',
                'crs': 'OUTLIER'
            })
        
        return pd.DataFrame(data)
    
    def analyze_coordinate_quality(self, df: pd.DataFrame) -> Dict:
        """分析座標品質"""
        coordinates = list(zip(df['latitude'], df['longitude']))
        
        # CRS 分析
        crs_analysis = self.detect_crs(coordinates)
        
        # 離群值分析
        outliers_analysis = self.detect_outliers(coordinates)
        
        # 統計資訊
        total_points = len(df)
        quality_score = self._calculate_quality_score(crs_analysis, outliers_analysis, total_points)
        
        return {
            'total_points': total_points,
            'crs_analysis': crs_analysis,
            'outliers_analysis': outliers_analysis,
            'quality_score': quality_score,
            'recommendations': self._generate_recommendations(crs_analysis, outliers_analysis)
        }
    
    def _calculate_quality_score(self, crs_analysis: Dict, outliers_analysis: Dict, total_points: int) -> float:
        """計算座標品質分數（0-100）"""
        score = 100.0
        
        # CRS 一致性扣分
        unknown_crs = crs_analysis['UNKNOWN']
        score -= (unknown_crs / total_points) * 30
        
        # 離群值扣分
        total_outliers = len(outliers_analysis['zero_coordinates']) + \
                        len(outliers_analysis['outside_taiwan_wgs84']) + \
                        len(outliers_analysis['extreme_values'])
        score -= (total_outliers / total_points) * 40
        
        return max(0, score)
    
    def _generate_recommendations(self, crs_analysis: Dict, outliers_analysis: Dict) -> List[str]:
        """生成改善建議"""
        recommendations = []
        
        if crs_analysis['UNKNOWN'] > 0:
            recommendations.append(f"發現 {crs_analysis['UNKNOWN']} 個未知座標系統的點位，建議確認座標格式")
        
        if crs_analysis['TWD97'] > 0 and crs_analysis['WGS84'] > 0:
            recommendations.append("發現混合座標系統，建議統一轉換為 WGS84 格式")
        
        if outliers_analysis['zero_coordinates']:
            recommendations.append(f"發現 {len(outliers_analysis['zero_coordinates'])} 個 (0,0) 座標，需要修正")
        
        if outliers_analysis['outside_taiwan_wgs84']:
            recommendations.append(f"發現 {len(outliers_analysis['outside_taiwan_wgs84'])} 個台灣範圍外的座標，需要驗證")
        
        if outliers_analysis['extreme_values']:
            recommendations.append(f"發現 {len(outliers_analysis['extreme_values'])} 個極端值座標，建議檢查")
        
        return recommendations
    
    def create_visualization(self, df: pd.DataFrame, analysis_result: Dict) -> None:
        """創建視覺化圖表"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('避難收容處所座標品質分析', fontsize=16, fontweight='bold')
        
        # 1. CRS 分佈圓餅圖
        crs_data = analysis_result['crs_analysis']
        axes[0, 0].pie(crs_data.values(), labels=crs_data.keys(), autopct='%1.1f%%')
        axes[0, 0].set_title('座標系統分佈 (CRS Distribution)')
        
        # 2. 離群值統計
        outlier_counts = {
            '(0,0)座標': len(analysis_result['outliers_analysis']['zero_coordinates']),
            '台灣範圍外': len(analysis_result['outliers_analysis']['outside_taiwan_wgs84']),
            '極端值': len(analysis_result['outliers_analysis']['extreme_values'])
        }
        axes[0, 1].bar(outlier_counts.keys(), outlier_counts.values())
        axes[0, 1].set_title('離群值統計 (Outlier Statistics)')
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # 3. 座標散佈圖（只顯示合理的 WGS84 座標）
        valid_coords = []
        for lat, lon in zip(df['latitude'], df['longitude']):
            if (self.taiwan_bounds_wgs84['min_lat'] <= lat <= self.taiwan_bounds_wgs84['max_lat'] and
                self.taiwan_bounds_wgs84['min_lon'] <= lon <= self.taiwan_bounds_wgs84['max_lon']):
                valid_coords.append((lat, lon))
        
        if valid_coords:
            lats, lons = zip(*valid_coords)
            axes[1, 0].scatter(lons, lats, alpha=0.6, s=20)
            axes[1, 0].set_xlabel('經度 (Longitude)')
            axes[1, 0].set_ylabel('緯度 (Latitude)')
            axes[1, 0].set_title('台灣地區座標分佈')
            axes[1, 0].grid(True, alpha=0.3)
        
        # 4. 品質分數儀表板
        quality_score = analysis_result['quality_score']
        axes[1, 1].bar(['座標品質分數'], [quality_score], color='green' if quality_score > 70 else 'orange' if quality_score > 40 else 'red')
        axes[1, 1].set_ylim(0, 100)
        axes[1, 1].set_title(f'整體品質評分: {quality_score:.1f}/100')
        axes[1, 1].axhline(y=70, color='orange', linestyle='--', alpha=0.7, label='良好門檻')
        axes[1, 1].axhline(y=40, color='red', linestyle='--', alpha=0.7, label='及格門檻')
        axes[1, 1].legend()
        
        plt.tight_layout()
        plt.savefig('shelter_coordinate_quality_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def export_quality_report(self, df: pd.DataFrame, analysis_result: Dict, filename: str = 'shelter_quality_report.csv') -> None:
        """匯出品質報告"""
        # 添加品質標籤到原始資料
        df_with_quality = df.copy()
        df_with_quality['quality_status'] = '正常'
        df_with_quality['crs_detected'] = ''
        
        for i, (lat, lon) in enumerate(zip(df['latitude'], df['longitude'])):
            crs_type = self._classify_single_coordinate(lat, lon)
            df_with_quality.loc[i, 'crs_detected'] = crs_type
            
            # 標記問題
            if lat == 0 and lon == 0:
                df_with_quality.loc[i, 'quality_status'] = '(0,0)座標'
            elif i in analysis_result['outliers_analysis']['outside_taiwan_wgs84']:
                df_with_quality.loc[i, 'quality_status'] = '台灣範圍外'
            elif i in analysis_result['outliers_analysis']['extreme_values']:
                df_with_quality.loc[i, 'quality_status'] = '極端值'
        
        # 儲存詳細報告
        df_with_quality.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"詳細品質報告已儲存至: {filename}")
    
    def run_analysis(self, data_file: str = None, sample_size: int = 100) -> Dict:
        """執行完整分析"""
        print("=" * 60)
        print("避難收容處所座標品質檢查器")
        print("=" * 60)
        
        # 載入或生成數據
        if data_file and os.path.exists(data_file):
            print(f"載入數據: {data_file}")
            df = pd.read_csv(data_file)
        else:
            print(f"生成範例數據 ({sample_size} 個點位)")
            df = self.generate_sample_data(sample_size)
        
        # 執行分析
        print("執行座標品質分析...")
        analysis_result = self.analyze_coordinate_quality(df)
        
        # 顯示結果
        self._print_analysis_results(analysis_result)
        
        # 創建視覺化
        print("生成視覺化圖表...")
        self.create_visualization(df, analysis_result)
        
        # 匯出報告
        print("匯出品質報告...")
        self.export_quality_report(df, analysis_result)
        
        return analysis_result
    
    def _print_analysis_results(self, result: Dict) -> None:
        """列印分析結果"""
        print("\n" + "=" * 40)
        print("分析結果")
        print("=" * 40)
        
        print(f"總點位數: {result['total_points']}")
        print(f"品質分數: {result['quality_score']:.1f}/100")
        
        print("\n座標系統分佈:")
        for crs, count in result['crs_analysis'].items():
            percentage = (count / result['total_points']) * 100
            print(f"  {crs}: {count} ({percentage:.1f}%)")
        
        print("\n離群值統計:")
        outliers = result['outliers_analysis']
        print(f"  (0,0)座標: {len(outliers['zero_coordinates'])}")
        print(f"  台灣範圍外: {len(outliers['outside_taiwan_wgs84'])}")
        print(f"  極端值: {len(outliers['extreme_values'])}")
        
        print("\n改善建議:")
        for i, rec in enumerate(result['recommendations'], 1):
            print(f"  {i}. {rec}")

def main():
    """主程式"""
    import os
    
    # 創建檢查器實例
    checker = ShelterCoordinateQualityChecker()
    
    # 執行分析（使用範例數據）
    result = checker.run_analysis(sample_size=150)
    
    print("\n" + "=" * 60)
    print("分析完成！")
    print("=" * 60)
    print("生成檔案:")
    print("- shelter_coordinate_quality_analysis.png (視覺化圖表)")
    print("- shelter_quality_report.csv (詳細報告)")

if __name__ == "__main__":
    main()
