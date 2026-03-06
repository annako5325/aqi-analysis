#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
根據設施名稱新增 is_indoor 欄位
判斷避難收容處所是否為室內設施
"""

import pandas as pd
import re

def add_indoor_classification():
    """新增室內分類欄位"""
    print("=" * 60)
    print("新增 is_indoor 欄位 - 室內設施分類")
    print("=" * 60)
    
    # 讀取數據
    try:
        df = pd.read_csv('避難收容處所點位檔案v9_final.csv')
        print(f"載入數據: {len(df)} 筆")
    except Exception as e:
        print(f"載入數據失敗: {e}")
        return
    
    print(f"原始欄位: {list(df.columns)}")
    
    # 定義室內設施關鍵字
    indoor_keywords = [
        # 學校相關
        '國小', '國中', '高中', '中學', '小學', '大學', '學院', '幼稚園', '托兒所',
        # 活動中心相關
        '活動中心', '社區中心', '里民活動中心', '村里活動中心', '社區活動中心',
        # 辦公處所相關
        '辦公處', '公所', '區公所', '鄉公所', '鎮公所', '縣公所', '市公所',
        '村里辦公處', '里辦公處', '村辦公處',
        # 宗教場所相關
        '寺廟', '宮', '廟', '寺', '教堂', '禮拜堂', '教會',
        # 體育館相關
        '體育館', '運動中心', '健身房', '籃球場', '羽球場', '網球場', '排球場',
        # 其他室內設施
        '圖書館', '文化中心', '社教館', '集會所', '禮堂', '會堂', '會議室',
        '教室', '校舍', '校舍', '校區', '校園', '學校',
        '消防局', '消防分隊', '警察局', '派出所', '衛生所', '診所',
        '市場', '超市', '百貨', '商場', '商店', '餐廳', '旅館', '飯店',
        '銀行', '郵局', '車站', '機場', '港務',
        '福利中心', '服務中心', '照護中心', '養護中心',
        '倉庫', '車庫', '停車場', '地下室'
    ]
    
    # 定義戶外設施關鍵字
    outdoor_keywords = [
        '公園', '廣場', '綠地', '草地', '花園', '庭園', '園地',
        '河濱公園', '濕地公園', '森林公園', '兒童公園', '運動公園',
        '運動場', '球場', '田徑場', '操場', '遊樂場', '遊戲場',
        '海灘', '沙灘', '海岸', '港口', '碼頭', '漁港',
        '山區', '山頂', '山腳', '山坡', '山谷', '溪邊', '河邊',
        '橋下', '路邊', '街邊', '空地', '開放空間'
    ]
    
    def classify_facility(name):
        """分類設施是否為室內"""
        if pd.isna(name) or name == '':
            return False
        
        name = str(name).strip()
        
        # 檢查是否包含戶外關鍵字（優先判斷）
        for keyword in outdoor_keywords:
            if keyword in name:
                return False
        
        # 檢查是否包含室內關鍵字
        for keyword in indoor_keywords:
            if keyword in name:
                return True
        
        # 特殊規則處理
        # 如果名稱包含特定模式，進行額外判斷
        patterns = [
            (r'.*公園$', False),  # 以公園結尾
            (r'.*廣場$', False),  # 以廣場結尾
            (r'.*綠地$', False),  # 以綠地結尾
            (r'.*運動場$', False),  # 以運動場結尾
            (r'.*學校$', True),   # 以學校結尾
            (r'.*國小$', True),   # 以國小結尾
            (r'.*國中$', True),   # 以國中結尾
            (r'.*高中$', True),   # 以高中結尾
            (r'.*中心$', True),   # 以中心結尾
            (r'.*活動中心$', True),  # 以活動中心結尾
            (r'.*辦公處$', True),  # 以辦公處結尾
            (r'.*宮$', True),     # 以宮結尾
            (r'.*寺$', True),     # 以寺結尾
            (r'.*廟$', True),     # 以廟結尾
            (r'.*體育館$', True),  # 以體育館結尾
        ]
        
        for pattern, is_indoor in patterns:
            if re.match(pattern, name):
                return is_indoor
        
        # 如果無法確定，默認為室內（較保守的分類）
        return True
    
    # 應用分類
    print("\n分類設施類型...")
    df['is_indoor'] = df['避難收容處所名稱'].apply(classify_facility)
    
    # 統計結果
    indoor_count = df['is_indoor'].sum()
    outdoor_count = len(df) - indoor_count
    
    print(f"\n分類結果統計:")
    print(f"  室內設施: {indoor_count} 筆 ({indoor_count/len(df)*100:.1f}%)")
    print(f"  戶外設施: {outdoor_count} 筆 ({outdoor_count/len(df)*100:.1f}%)")
    print(f"  總計: {len(df)} 筆")
    
    # 顯示分類範例
    print(f"\n室內設施範例:")
    indoor_examples = df[df['is_indoor'] == True]['避難收容處所名稱'].head(10)
    for name in indoor_examples:
        print(f"  ✓ {name}")
    
    print(f"\n戶外設施範例:")
    outdoor_examples = df[df['is_indoor'] == False]['避難收容處所名稱'].head(10)
    for name in outdoor_examples:
        print(f"  ✗ {name}")
    
    # 按縣市統計
    print(f"\n各縣市室內/戶外設施分佈:")
    county_stats = df.groupby('縣市及鄉鎮市區').agg({
        'is_indoor': ['count', 'sum']
    }).round(1)
    county_stats.columns = ['總數', '室內數']
    county_stats['戶外數'] = county_stats['總數'] - county_stats['室內數']
    county_stats['室內比例'] = (county_stats['室內數'] / county_stats['總數'] * 100).round(1)
    county_stats['戶外比例'] = (county_stats['戶外數'] / county_stats['總數'] * 100).round(1)
    
    # 顯示前10個縣市
    print(county_stats.head(10).to_string())
    
    # 儲存結果
    output_file = '避難收容處所點位檔案v9_with_indoor.csv'
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n新增室內分類後的數據已儲存至: {output_file}")
    
    # 儲存統計報告
    county_stats.to_csv('indoor_outdoor_statistics.csv', encoding='utf-8-sig')
    print("室內/戶外統計報告已儲存至: indoor_outdoor_statistics.csv")
    
    # 生成詳細報告
    generate_detailed_report(df, indoor_count, outdoor_count)
    
    print("\n" + "=" * 60)
    print("室內設施分類完成！")
    print("=" * 60)

def generate_detailed_report(df, indoor_count, outdoor_count):
    """生成詳細報告"""
    print("\n生成詳細報告...")
    
    # 按設施類型詳細統計
    facility_types = {}
    
    for idx, row in df.iterrows():
        name = row['避難收容處所名稱']
        is_indoor = row['is_indoor']
        county = row['縣市及鄉鎮市區']
        
        # 提取設施類型
        facility_type = extract_facility_type(name)
        
        if facility_type not in facility_types:
            facility_types[facility_type] = {'indoor': 0, 'outdoor': 0, 'counties': set()}
        
        if is_indoor:
            facility_types[facility_type]['indoor'] += 1
        else:
            facility_types[facility_type]['outdoor'] += 1
        
        facility_types[facility_type]['counties'].add(county)
    
    # 創設施類型統計報告
    facility_report = []
    for facility_type, stats in facility_types.items():
        total = stats['indoor'] + stats['outdoor']
        indoor_pct = (stats['indoor'] / total * 100) if total > 0 else 0
        outdoor_pct = (stats['outdoor'] / total * 100) if total > 0 else 0
        
        facility_report.append({
            '設施類型': facility_type,
            '總數': total,
            '室內數': stats['indoor'],
            '戶外數': stats['outdoor'],
            '室內比例': f'{indoor_pct:.1f}%',
            '戶外比例': f'{outdoor_pct:.1f}%',
            '分佈縣市數': len(stats['counties'])
        })
    
    # 按總數排序
    facility_report.sort(key=lambda x: x['總數'], reverse=True)
    
    facility_df = pd.DataFrame(facility_report)
    facility_df.to_csv('facility_type_classification.csv', index=False, encoding='utf-8-sig')
    print("設施類型分類報告已儲存至: facility_type_classification.csv")
    
    # 顯示前10種設施類型
    print(f"\n前10種設施類型:")
    print(facility_df.head(10).to_string(index=False))

def extract_facility_type(name):
    """提取設施類型"""
    if pd.isna(name) or name == '':
        return '未知'
    
    name = str(name).strip()
    
    # 定義設施類型提取規則
    type_patterns = [
        (r'.*國小.*', '國小'),
        (r'.*國中.*', '國中'),
        (r'.*高中.*', '高中'),
        (r'.*中學.*', '中學'),
        (r'.*小學.*', '小學'),
        (r'.*大學.*', '大學'),
        (r'.*學院.*', '學院'),
        (r'.*活動中心.*', '活動中心'),
        (r'.*社區中心.*', '社區中心'),
        (r'.*辦公處.*', '辦公處'),
        (r'.*公所.*', '公所'),
        (r'.*宮.*', '宮廟'),
        (r'.*寺.*', '寺廟'),
        (r'.*廟.*', '寺廟'),
        (r'.*教堂.*', '教堂'),
        (r'.*教會.*', '教會'),
        (r'.*體育館.*', '體育館'),
        (r'.*圖書館.*', '圖書館'),
        (r'.*文化中心.*', '文化中心'),
        (r'.*公園.*', '公園'),
        (r'.*廣場.*', '廣場'),
        (r'.*綠地.*', '綠地'),
        (r'.*運動場.*', '運動場'),
        (r'.*禮堂.*', '禮堂'),
        (r'.*會堂.*', '會堂'),
        (r'.*集會所.*', '集會所'),
        (r'.*市場.*', '市場'),
        (r'.*衛生所.*', '衛生所'),
        (r'.*消防.*', '消防'),
        (r'.*警察.*', '警察'),
        (r'.*福利中心.*', '福利中心'),
        (r'.*服務中心.*', '服務中心'),
    ]
    
    for pattern, facility_type in type_patterns:
        if re.search(pattern, name):
            return facility_type
    
    # 如果無法匹配，返回通用類型
    if '中心' in name:
        return '其他中心'
    elif '校' in name:
        return '其他學校'
    elif '公園' in name:
        return '其他公園'
    elif '廣場' in name:
        return '其他廣場'
    else:
        return '其他設施'

if __name__ == "__main__":
    add_indoor_classification()
