#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檢查 TWD97 距離計算結果
"""

import pandas as pd

def main():
    try:
        # 讀取 CSV 檔案
        df = pd.read_csv('outputs/aqi_analysis.csv')
        
        print("=" * 50)
        print("TWD97 距離計算結果檢查")
        print("=" * 50)
        
        # 顯示前 5 筆資料
        print("\n前 5 筆測站資料:")
        print(df.head().to_string(index=False))
        
        # 距離統計
        print(f"\n距離統計:")
        print(f"總測站數: {len(df)}")
        
        # 找出最近和最遠的測站
        nearest = df.iloc[0]
        farthest = df.iloc[-1]
        
        print(f"最近測站: {nearest['測站名稱']} ({nearest['距離台北車站(公里)']} 公里)")
        print(f"最遠測站: {farthest['測站名稱']} ({farthest['距離台北車站(公里)']} 公里)")
        
        # 計算平均距離
        avg_distance = df['距離台北車站(公里)'].mean()
        print(f"平均距離: {avg_distance:.2f} 公里")
        
        # 顯示距離分佈
        print(f"\n距離分佈:")
        print(f"10公里內: {len(df[df['距離台北車站(公里)'] <= 10])} 個測站")
        print(f"10-50公里: {len(df[(df['距離台北車站(公里)'] > 10) & (df['距離台北車站(公里)'] <= 50)])} 個測站")
        print(f"50-100公里: {len(df[(df['距離台北車站(公里)'] > 50) & (df['距離台北車站(公里)'] <= 100)])} 個測站")
        print(f"100公里以上: {len(df[df['距離台北車站(公里)'] > 100])} 個測站")
        
        print("\n" + "=" * 50)
        print("檢查完成！")
        print("=" * 50)
        
    except Exception as e:
        print(f"檢查時發生錯誤: {e}")

if __name__ == "__main__":
    main()
