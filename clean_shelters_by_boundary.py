#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
根據鄉鎮市區界線清理異常避難收容處所點位
確保所有點位都在台灣本島或離島的陸地上
"""

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, Polygon
import numpy as np

class ShelterBoundaryCleaner:
    """避難收容處所邊界清理器"""
    
    def __init__(self):
        self.town_boundary = None
        self.shelter_data = None
        self.cleaned_data = None
        self.removed_data = None
    
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
    
    def perform_spatial_join(self, shelter_gdf: gpd.GeoDataFrame):
        """執行空間連接檢查點位是否在界線內"""
        print("執行空間連接檢查...")
        
        # 執行空間連接
        joined = gpd.sjoin(shelter_gdf, self.town_boundary, how='left', predicate='within')
        
        # 分類點位
        inside_boundary = joined[~joined['index_right'].isna()]
        outside_boundary = joined[joined['index_right'].isna()]
        
        print(f"界線內點位: {len(inside_boundary)} 筆")
        print(f"界線外點位: {len(outside_boundary)} 筆")
        
        return inside_boundary, outside_boundary
    
    def analyze_outside_points(self, outside_points: gpd.GeoDataFrame):
        """分析界線外的點位"""
        if len(outside_points) == 0:
            print("沒有界線外的點位")
            return
        
        print(f"\n分析 {len(outside_points)} 筆界線外點位...")
        
        # 計算到台灣中心的距離
        taiwan_center = Point(121.0, 23.8)
        
        distances = []
        for idx, row in outside_points.iterrows():
            point = row.geometry
            distance = point.distance(taiwan_center) * 111  # 大約每度111公里
            distances.append(distance)
        
        outside_points['distance_to_center'] = distances
        
        # 顯示界線外點位詳細資訊
        print(f"\n界線外點位詳細資訊:")
        for idx, row in outside_points.iterrows():
            name = row.get('避難收容處所名稱', 'N/A')
            county = row.get('縣市及鄉鎮市區', 'N/A')
            lat = row['緯度']
            lon = row['經度']
            distance = row['distance_to_center']
            
            print(f"  {name}")
            print(f"    位置: {county}")
            print(f"    座標: ({lat:.6f}, {lon:.6f})")
            print(f"    距離台灣中心: {distance:.1f}公里")
            print()
        
        return outside_points
    
    def clean_data(self):
        """清理數據，移除界線外的點位"""
        print("=" * 60)
        print("根據鄉鎮市區界線清理避難收容處所數據")
        print("=" * 60)
        
        # 載入資料
        if not self.load_boundary_data("data/鄉鎮市區界線/TOWN_MOI_1140318.shp"):
            return
        
        if not self.load_shelter_data("避難收容處所點位檔案v9_with_indoor.csv"):
            return
        
        # 創建點位
        shelter_gdf = self.create_shelter_points()
        
        # 執行空間連接
        inside_boundary, outside_boundary = self.perform_spatial_join(shelter_gdf)
        
        # 分析界線外點位
        analyzed_outside = self.analyze_outside_points(outside_boundary)
        
        # 保存清理結果
        self.cleaned_data = inside_boundary.drop(columns=['index_right'], errors='ignore')
        self.removed_data = analyzed_outside
        
        # 生成統計報告
        self.generate_cleaning_report()
        
        # 儲存結果
        self.save_results()
        
        print("\n" + "=" * 60)
        print("邊界清理完成！")
        print("=" * 60)
    
    def generate_cleaning_report(self):
        """生成清理報告"""
        print(f"\n清理統計報告:")
        print(f"  原始數據: {len(self.shelter_data)} 筆")
        print(f"  界線內點位: {len(self.cleaned_data)} 筆")
        print(f"  界線外點位: {len(self.removed_data)} 筆")
        print(f"  保留比例: {len(self.cleaned_data)/len(self.shelter_data)*100:.1f}%")
        
        # 按縣市統計移除的點位
        if len(self.removed_data) > 0:
            print(f"\n移除點位按縣市分佈:")
            county_counts = self.removed_data['縣市及鄉鎮市區'].value_counts()
            for county, count in county_counts.items():
                print(f"  {county}: {count} 筆")
        
        # 按設施類型統計
        if len(self.removed_data) > 0:
            print(f"\n移除點位按設施類型分佈:")
            indoor_count = self.removed_data['is_indoor'].sum()
            outdoor_count = len(self.removed_data) - indoor_count
            print(f"  室內設施: {indoor_count} 筆")
            print(f"  戶外設施: {outdoor_count} 筆")
    
    def save_results(self):
        """儲存清理結果"""
        # 儲存清理後的數據
        cleaned_file = "避難收容處所點位檔案v9_boundary_cleaned.csv"
        self.cleaned_data.to_csv(cleaned_file, index=False, encoding='utf-8-sig')
        print(f"\n清理後數據已儲存至: {cleaned_file}")
        
        # 儲存被移除的數據
        if len(self.removed_data) > 0:
            removed_file = "避難收容處所點位檔案v9_boundary_removed.csv"
            # 移除臨時欄位
            removed_clean = self.removed_data.drop(columns=['index_right', 'distance_to_center'], errors='ignore')
            removed_clean.to_csv(removed_file, index=False, encoding='utf-8-sig')
            print(f"被移除的異常點位已儲存至: {removed_file}")
        
        # 儲存清理報告
        report_data = {
            '項目': ['原始數據', '界線內點位', '界線外點位', '保留比例'],
            '數量': [len(self.shelter_data), len(self.cleaned_data), len(self.removed_data), 
                    f"{len(self.cleaned_data)/len(self.shelter_data)*100:.1f}%"],
            '說明': ['原始避難收容處所數據', '在鄉鎮市區界線內的點位', 
                    '在鄉鎮市區界線外的異常點位', '清理後保留的比例']
        }
        
        report_df = pd.DataFrame(report_data)
        report_df.to_csv('boundary_cleaning_report.csv', index=False, encoding='utf-8-sig')
        print("清理報告已儲存至: boundary_cleaning_report.csv")

def main():
    """主程式"""
    cleaner = ShelterBoundaryCleaner()
    cleaner.clean_data()

if __name__ == "__main__":
    main()
