#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用縣市界分區進行疊圖檢查
檢查避難收容處所是否在台灣行政區域內
"""

import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Tuple, Dict
import warnings
warnings.filterwarnings('ignore')

# 設定中文字體
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

class SpatialOverlayChecker:
    """空間疊圖檢查器"""
    
    def __init__(self):
        self.town_boundary = None
        self.shelter_data = None
        self.results = {}
    
    def load_boundary_data(self, shp_path: str) -> bool:
        """載入鄉鎮市區界線資料"""
        try:
            print(f"載入鄉鎮市區界線: {shp_path}")
            self.town_boundary = gpd.read_file(shp_path)
            print(f"成功載入 {len(self.town_boundary)} 個鄉鎮市區界線")
            
            # 檢查座標系統
            print(f"座標系統: {self.town_boundary.crs}")
            
            # 如果不是 WGS84，進行轉換
            if self.town_boundary.crs != 'EPSG:4326':
                print("轉換座標系統至 WGS84...")
                self.town_boundary = self.town_boundary.to_crs('EPSG:4326')
                print(f"轉換後座標系統: {self.town_boundary.crs}")
            
            return True
            
        except Exception as e:
            print(f"載入界線資料失敗: {e}")
            return False
    
    def load_shelter_data(self, csv_path: str) -> bool:
        """載入避難收容處所資料"""
        try:
            print(f"載入避難收容處所資料: {csv_path}")
            self.shelter_data = pd.read_csv(csv_path)
            print(f"成功載入 {len(self.shelter_data)} 筆避難收容處所資料")
            
            # 檢查必要欄位
            required_cols = ['經度', '緯度', '避難收容處所名稱']
            missing_cols = [col for col in required_cols if col not in self.shelter_data.columns]
            if missing_cols:
                print(f"缺少必要欄位: {missing_cols}")
                return False
            
            # 移除座標缺失值
            initial_count = len(self.shelter_data)
            self.shelter_data = self.shelter_data.dropna(subset=['經度', '緯度'])
            self.shelter_data = self.shelter_data[(self.shelter_data['經度'] != 0) & (self.shelter_data['緯度'] != 0)]
            print(f"移除座標缺失值後: {len(self.shelter_data)} 筆")
            
            return True
            
        except Exception as e:
            print(f"載入避難收容處所資料失敗: {e}")
            return False
    
    def create_shelter_points(self) -> gpd.GeoDataFrame:
        """創建避難收容處所點位 GeoDataFrame"""
        print("創建避難收容處所點位...")
        
        # 創建幾何點位
        geometry = [Point(lon, lat) for lon, lat in zip(self.shelter_data['經度'], self.shelter_data['緯度'])]
        
        # 創建 GeoDataFrame
        shelter_gdf = gpd.GeoDataFrame(
            self.shelter_data, 
            geometry=geometry, 
            crs='EPSG:4326'
        )
        
        print(f"創建 {len(shelter_gdf)} 個點位")
        return shelter_gdf
    
    def perform_spatial_overlay(self, shelter_gdf: gpd.GeoDataFrame) -> Dict:
        """執行空間疊圖分析"""
        print("執行空間疊圖分析...")
        
        # 執行空間連接
        print("進行點位與界線的空間連接...")
        joined = gpd.sjoin(shelter_gdf, self.town_boundary, how='left', predicate='within')
        
        # 分析結果
        total_points = len(joined)
        matched_points = len(joined.dropna(subset=['index_right']))
        unmatched_points = total_points - matched_points
        
        print(f"總點位數: {total_points}")
        print(f"界線內點位: {matched_points}")
        print(f"界線外點位: {unmatched_points}")
        
        # 分類結果
        results = {
            'total_points': total_points,
            'matched_points': matched_points,
            'unmatched_points': unmatched_points,
            'matched_percentage': (matched_points / total_points) * 100,
            'unmatched_percentage': (unmatched_points / total_points) * 100
        }
        
        return results, joined
    
    def analyze_unmatched_points(self, joined_gdf: gpd.GeoDataFrame) -> pd.DataFrame:
        """分析界線外的點位"""
        print("分析界線外的點位...")
        
        # 找出界線外的點位
        unmatched = joined_gdf[joined_gdf['index_right'].isna()].copy()
        
        if len(unmatched) == 0:
            print("沒有界線外的點位")
            return pd.DataFrame()
        
        print(f"界線外點位: {len(unmatched)} 筆")
        
        # 分析界線外點位的特徵
        print("\n界線外點位分析:")
        
        # 計算到台灣本島的距離
        taiwan_center = Point(121.0, 23.8)  # 台灣中心點
        
        distances = []
        for idx, row in unmatched.iterrows():
            point = row.geometry
            distance = point.distance(taiwan_center) * 111  # 大約每度111公里
            distances.append(distance)
        
        unmatched['distance_to_taiwan'] = distances
        
        # 分類界線外點位
        def classify_unmatched(row):
            lat = row['緯度']
            lon = row['經度']
            distance = row['distance_to_taiwan']
            
            # 離島地區
            if (24.0 <= lat <= 24.8) and (118.0 <= lon <= 118.5):
                return '金門'
            elif (26.0 <= lat <= 26.5) and (119.5 <= lon <= 120.5):
                return '馬祖'
            elif (23.5 <= lat <= 23.8) and (119.5 <= lon <= 119.8):
                return '澎湖'
            elif (22.0 <= lat <= 22.8) and (121.0 <= lon <= 122.0):
                return '蘭嶼'
            elif (22.0 <= lat <= 23.0) and (120.0 <= lon <= 121.5):
                return '綠島'
            elif distance < 50:
                return '台灣周邊'
            else:
                return '海外遠距'
        
        unmatched['location_category'] = unmatched.apply(classify_unmatched, axis=1)
        
        # 統計分類結果
        category_counts = unmatched['location_category'].value_counts()
        print("\n界線外點位分類:")
        for category, count in category_counts.items():
            print(f"  {category}: {count} 筆")
        
        return unmatched
    
    def create_visualization(self, joined_gdf: gpd.GeoDataFrame, unmatched: pd.DataFrame):
        """創建視覺化地圖"""
        print("創建視覺化地圖...")
        
        fig, axes = plt.subplots(1, 2, figsize=(15, 8))
        fig.suptitle('避難收容處所空間疊圖分析', fontsize=16, fontweight='bold')
        
        # 圖1: 全台灣地圖
        ax1 = axes[0]
        self.town_boundary.plot(ax=ax1, facecolor='lightgray', edgecolor='gray', alpha=0.7)
        
        # 界線內點位
        matched = joined_gdf.dropna(subset=['index_right'])
        if len(matched) > 0:
            matched.plot(ax=ax1, color='blue', markersize=2, alpha=0.6, label='界線內')
        
        # 界線外點位
        if len(unmatched) > 0:
            unmatched.plot(ax=ax1, color='red', markersize=4, alpha=0.8, label='界線外')
        
        ax1.set_title('避難收容處所分佈圖')
        ax1.set_xlabel('經度')
        ax1.set_ylabel('緯度')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 圖2: 界線外點位特寫
        ax2 = axes[1]
        if len(unmatched) > 0:
            # 根據分類著色
            colors = {'金門': 'orange', '馬祖': 'purple', '澎湖': 'cyan', 
                     '蘭嶼': 'green', '綠島': 'pink', '台灣周邊': 'yellow', '海外遠距': 'red'}
            
            for category, group in unmatched.groupby('location_category'):
                color = colors.get(category, 'gray')
                group.plot(ax=ax2, color=color, markersize=6, alpha=0.8, label=category)
            
            ax2.set_title('界線外點位詳細分佈')
            ax2.set_xlabel('經度')
            ax2.set_ylabel('緯度')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
        else:
            ax2.text(0.5, 0.5, '沒有界線外點位', ha='center', va='center', 
                    transform=ax2.transAxes, fontsize=14)
            ax2.set_title('界線外點位分析')
        
        plt.tight_layout()
        plt.savefig('spatial_overlay_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def generate_report(self, results: Dict, unmatched: pd.DataFrame) -> None:
        """生成分析報告"""
        print("\n" + "=" * 60)
        print("空間疊圖分析報告")
        print("=" * 60)
        
        print(f"總分析點位: {results['total_points']}")
        print(f"界線內點位: {results['matched_points']} ({results['matched_percentage']:.1f}%)")
        print(f"界線外點位: {results['unmatched_points']} ({results['unmatched_percentage']:.1f}%)")
        
        if len(unmatched) > 0:
            print("\n界線外點位詳細資訊:")
            print(f"前10筆界線外點位:")
            
            for idx, row in unmatched.head(10).iterrows():
                name = row.get('避難收容處所名稱', 'N/A')
                county = row.get('縣市及鄉鎮市區', 'N/A')
                lat = row['緯度']
                lon = row['經度']
                category = row['location_category']
                distance = row['distance_to_taiwan']
                
                print(f"  {name}")
                print(f"    位置: {county}")
                print(f"    座標: ({lat:.6f}, {lon:.6f})")
                print(f"    分類: {category}")
                print(f"    距離台灣中心: {distance:.1f}公里")
                print()
        
        # 儲存報告
        self.save_report(results, unmatched)
    
    def save_report(self, results: Dict, unmatched: pd.DataFrame) -> None:
        """儲存分析報告"""
        # 儲存統計報告
        stats_df = pd.DataFrame({
            '項目': ['總點位數', '界線內點位', '界線外點位'],
            '數量': [results['total_points'], results['matched_points'], results['unmatched_points']],
            '比例': [100.0, results['matched_percentage'], results['unmatched_percentage']]
        })
        stats_df.to_csv('spatial_overlay_statistics.csv', index=False, encoding='utf-8-sig')
        
        # 儲存界線外點位
        if len(unmatched) > 0:
            unmatched.to_csv('unmatched_shelters.csv', index=False, encoding='utf-8-sig')
        
        print(f"\n報告已儲存:")
        print(f"- spatial_overlay_statistics.csv: 統計報告")
        print(f"- unmatched_shelters.csv: 界線外點位清單")
        print(f"- spatial_overlay_analysis.png: 視覺化地圖")
    
    def run_analysis(self, boundary_shp: str, shelter_csv: str):
        """執行完整分析"""
        print("=" * 60)
        print("避難收容處所空間疊圖檢查")
        print("=" * 60)
        
        # 載入資料
        if not self.load_boundary_data(boundary_shp):
            return
        
        if not self.load_shelter_data(shelter_csv):
            return
        
        # 創建點位
        shelter_gdf = self.create_shelter_points()
        
        # 執行疊圖分析
        results, joined = self.perform_spatial_overlay(shelter_gdf)
        
        # 分析界線外點位
        unmatched = self.analyze_unmatched_points(joined)
        
        # 創建視覺化
        self.create_visualization(joined, unmatched)
        
        # 生成報告
        self.generate_report(results, unmatched)
        
        print("\n" + "=" * 60)
        print("分析完成！")
        print("=" * 60)

def main():
    """主程式"""
    # 檢查必要套件
    try:
        import geopandas
        import shapely
    except ImportError:
        print("需要安裝 geopandas 和 shapely 套件")
        print("請執行: pip install geopandas shapely")
        return
    
    # 創建檢查器
    checker = SpatialOverlayChecker()
    
    # 執行分析
    boundary_shp = "data/鄉鎮市區界線/TOWN_MOI_1140318.shp"
    shelter_csv = "避難收容處所點位檔案v9_cleaned.csv"
    
    checker.run_analysis(boundary_shp, shelter_csv)

if __name__ == "__main__":
    main()
