#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
?¿é›£?¶å®¹?•æ? AQI é¢¨éšª?†æ??‡æ?å¢ƒæ¨¡??æ¨¡æ“¬é«?AQI ?…å?ä»¥é?è­‰é¢¨?ªæ?ç±¤é?è¼?"""

import pandas as pd
import numpy as np
from scipy.spatial import cKDTree
import math

class ShelterAQIRiskAnalysis:
    """?¿é›£?¶å®¹?•æ? AQI é¢¨éšª?†æ???""
    
    def __init__(self):
        self.shelter_data = None
        self.aqi_data = None
        self.risk_analysis = None
        
    def load_data(self):
        """è¼‰å…¥?¸æ?"""
        print("è¼‰å…¥?¸æ?...")
        
        # è¼‰å…¥?¿é›£?¶å®¹?•æ??¸æ?
        try:
            self.shelter_data = pd.read_csv('?¿é›£?¶å®¹?•æ?é»ä?æª”æ?v9_boundary_cleaned.csv')
            print(f"è¼‰å…¥?¿é›£?¶å®¹?•æ?: {len(self.shelter_data)} ç­?)
        except Exception as e:
            print(f"è¼‰å…¥?¿é›£?¶å®¹?•æ?å¤±æ?: {e}")
            return False
        
        # è¼‰å…¥ AQI æ¸¬ç??¸æ?
        try:
            self.aqi_data = pd.read_csv('extracted_85_aqi_stations.csv')
            print(f"è¼‰å…¥ AQI æ¸¬ç?: {len(self.aqi_data)} ç­?)
        except Exception as e:
            print(f"è¼‰å…¥ AQI æ¸¬ç?å¤±æ?: {e}")
            return False
        
        return True
    
    def simulate_high_aqi_scenario(self):
        """æ¨¡æ“¬é«?AQI ?…å?"""
        print("\n?²è??…å?æ¨¡æ“¬...")
        
        # æª¢æŸ¥?Ÿå? AQI ?†ä?
        original_stats = {
            'mean': self.aqi_data['AQI'].mean(),
            'max': self.aqi_data['AQI'].max(),
            'min': self.aqi_data['AQI'].min(),
            'good_count': len(self.aqi_data[self.aqi_data['AQI'] <= 50]),
            'moderate_count': len(self.aqi_data[(self.aqi_data['AQI'] > 50) & (self.aqi_data['AQI'] <= 100)]),
            'poor_count': len(self.aqi_data[self.aqi_data['AQI'] > 100])
        }
        
        print(f"?Ÿå? AQI çµ±è?:")
        print(f"  å¹³å??? {original_stats['mean']:.1f}")
        print(f"  ?€å¤§å€? {original_stats['max']}")
        print(f"  ?€å°å€? {original_stats['min']}")
        print(f"  ?¯å¥½ (??0): {original_stats['good_count']} ??)
        print(f"  ?®é€?(51-100): {original_stats['moderate_count']} ??)
        print(f"  ä¸ä½³ (>100): {original_stats['poor_count']} ??)
        
        # æ¨¡æ“¬?…å?ï¼šå?é«˜é?æ¸¬ç???AQI è¨­ç‚º 150
        print(f"\n?š¨ ?…å?æ¨¡æ“¬ï¼šå?é«˜é?æ¸¬ç? AQI è¨­ç‚º 150")
        
        # ?¾åˆ°é«˜é?æ¸¬ç?
        kaohsiung_stations = self.aqi_data[self.aqi_data['County'].str.contains('é«˜é?', na=False)]
        if len(kaohsiung_stations) > 0:
            # å°‡ç¬¬ä¸€?‹é??„æ¸¬ç«™ç? AQI è¨­ç‚º 150
            target_idx = kaohsiung_stations.index[0]
            original_aqi = self.aqi_data.loc[target_idx, 'AQI']
            self.aqi_data.loc[target_idx, 'AQI'] = 150
            self.aqi_data.loc[target_idx, 'PM25'] = 42.0  # å°æ???PM2.5
            
            print(f"  å°?{self.aqi_data.loc[target_idx, 'SiteName']} æ¸¬ç?")
            print(f"  AQI å¾?{original_aqi} èª¿æ•´??150")
            print(f"  PM2.5 èª¿æ•´??42.0 Î¼g/mÂ³")
        else:
            # å¦‚æ?æ²’æ??¾åˆ°é«˜é?æ¸¬ç?ï¼Œé¸?‡å??¨åœ°?€?„æ¸¬ç«?            southern_stations = self.aqi_data[
                (self.aqi_data['lat'] < 23.5) & 
                (self.aqi_data['lon'] > 120.0)
            ]
            if len(southern_stations) > 0:
                target_idx = southern_stations.index[0]
                original_aqi = self.aqi_data.loc[target_idx, 'AQI']
                self.aqi_data.loc[target_idx, 'AQI'] = 150
                self.aqi_data.loc[target_idx, 'PM25'] = 42.0
                
                print(f"  å°?{self.aqi_data.loc[target_idx, 'SiteName']} æ¸¬ç?")
                print(f"  AQI å¾?{original_aqi} èª¿æ•´??150")
                print(f"  PM2.5 èª¿æ•´??42.0 Î¼g/mÂ³")
        
        # é¡¯ç¤ºæ¨¡æ“¬å¾Œç?çµ±è?
        simulated_stats = {
            'mean': self.aqi_data['AQI'].mean(),
            'max': self.aqi_data['AQI'].max(),
            'min': self.aqi_data['AQI'].min(),
            'good_count': len(self.aqi_data[self.aqi_data['AQI'] <= 50]),
            'moderate_count': len(self.aqi_data[(self.aqi_data['AQI'] > 50) & (self.aqi_data['AQI'] <= 100)]),
            'poor_count': len(self.aqi_data[self.aqi_data['AQI'] > 100])
        }
        
        print(f"\næ¨¡æ“¬å¾?AQI çµ±è?:")
        print(f"  å¹³å??? {simulated_stats['mean']:.1f}")
        print(f"  ?€å¤§å€? {simulated_stats['max']}")
        print(f"  ?€å°å€? {simulated_stats['min']}")
        print(f"  ?¯å¥½ (??0): {simulated_stats['good_count']} ??)
        print(f"  ?®é€?(51-100): {simulated_stats['moderate_count']} ??)
        print(f"  ä¸ä½³ (>100): {simulated_stats['poor_count']} ??)
    
    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """è¨ˆç??©é??“ç?è·é›¢ï¼ˆå…¬?Œï?"""
        # ä½¿ç”¨ Haversine ?¬å?
        R = 6371  # ?°ç??Šå?ï¼ˆå…¬?Œï?
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat/2)**2 + 
              math.cos(lat1_rad) * math.cos(lat2_rad) * 
              math.sin(delta_lon/2)**2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    def find_nearest_aqi_station(self, shelter_lat, shelter_lon):
        """å°‹æ‰¾?€è¿‘ç? AQI æ¸¬ç?"""
        min_distance = float('inf')
        nearest_station = None
        
        for _, station in self.aqi_data.iterrows():
            distance = self.calculate_distance(
                shelter_lat, shelter_lon,
                station['lat'], station['lon']
            )
            
            if distance < min_distance:
                min_distance = distance
                nearest_station = station
        
        return nearest_station, min_distance
    
    def perform_risk_analysis(self):
        """?·è?é¢¨éšª?†æ?"""
        print("\n?·è?é¢¨éšª?†æ?...")
        
        risk_results = []
        
        for idx, shelter in self.shelter_data.iterrows():
            shelter_lat = shelter['ç·¯åº¦']
            shelter_lon = shelter['ç¶“åº¦']
            shelter_name = shelter['?¿é›£?¶å®¹?•æ??ç¨±']
            is_indoor = shelter['is_indoor']
            county = shelter.get('ç¸???Šé??®å??€', '?ªçŸ¥')
            
            # å°‹æ‰¾?€è¿‘ç? AQI æ¸¬ç?
            nearest_station, distance = self.find_nearest_aqi_station(
                shelter_lat, shelter_lon
            )
            
            if nearest_station is not None:
                nearest_aqi = nearest_station['AQI']
                nearest_station_name = nearest_station['SiteName']
                nearest_station_county = nearest_station['County']
                
                # é¢¨éšªæ¨™ç±¤?è¼¯
                if nearest_aqi > 100:
                    risk_level = "High Risk"
                    risk_description = f"?€è¿‘æ¸¬ç«?AQI {nearest_aqi} > 100"
                elif nearest_aqi > 50 and not is_indoor:
                    risk_level = "Warning"
                    risk_description = f"?€è¿‘æ¸¬ç«?AQI {nearest_aqi} > 50 ä¸”ç‚º?¶å?è¨­æ–½"
                else:
                    risk_level = "Low Risk"
                    risk_description = "é¢¨éšªè¼ƒä?"
                
                # è¨ˆç?é¢¨éšª?†æ•¸
                risk_score = 0
                if nearest_aqi > 100:
                    risk_score += 50
                elif nearest_aqi > 50:
                    risk_score += 25
                
                if not is_indoor:
                    risk_score += 20
                
                # è·é›¢?²ç½°ï¼ˆè??¢è?? ï?ä¸ç¢ºå®šæ€§è?é«˜ï?
                if distance > 20:
                    risk_score += 10
                elif distance > 10:
                    risk_score += 5
                
                risk_score = min(100, risk_score)  # ?åˆ¶?€å¤§å€¼ç‚º100
                
                result = {
                    '?¿é›£?¶å®¹?•æ??ç¨±': shelter_name,
                    'ç¸???Šé??®å??€': county,
                    'ç·¯åº¦': shelter_lat,
                    'ç¶“åº¦': shelter_lon,
                    'is_indoor': is_indoor,
                    'è¨­æ–½é¡å?': 'å®¤å…§è¨­æ–½' if is_indoor else '?¶å?è¨­æ–½',
                    '?€è¿‘AQIæ¸¬ç?': nearest_station_name,
                    'æ¸¬ç?ç¸??': nearest_station_county,
                    '?€è¿‘æ¸¬ç«™AQI': nearest_aqi,
                    'è·é›¢æ¸¬ç?(km)': round(distance, 2),
                    'é¢¨éšªç­‰ç?': risk_level,
                    'é¢¨éšª?è¿°': risk_description,
                    'é¢¨éšª?†æ•¸': risk_score,
                    'æ¨¡æ“¬?…å?': 'é«˜AQI?…å?æ¨¡æ“¬'
                }
                
                risk_results.append(result)
        
        self.risk_analysis = pd.DataFrame(risk_results)
        print(f"å®Œæ? {len(risk_results)} ?‹é¿??”¶å®¹è??€?„é¢¨?ªå???)
        
        return self.risk_analysis
    
    def generate_statistics(self):
        """?Ÿæ?çµ±è??±å?"""
        print("\n?Ÿæ?é¢¨éšª?†æ?çµ±è?...")
        
        if self.risk_analysis is None:
            print("è«‹å??·è?é¢¨éšª?†æ?")
            return
        
        # é¢¨éšªç­‰ç?çµ±è?
        risk_counts = self.risk_analysis['é¢¨éšªç­‰ç?'].value_counts()
        print(f"\né¢¨éšªç­‰ç??†ä?:")
        for risk_level, count in risk_counts.items():
            percentage = count / len(self.risk_analysis) * 100
            print(f"  {risk_level}: {count:,} ç­?({percentage:.1f}%)")
        
        # è¨­æ–½é¡å?çµ±è?
        facility_counts = self.risk_analysis['è¨­æ–½é¡å?'].value_counts()
        print(f"\nè¨­æ–½é¡å??†ä?:")
        for facility_type, count in facility_counts.items():
            percentage = count / len(self.risk_analysis) * 100
            print(f"  {facility_type}: {count:,} ç­?({percentage:.1f}%)")
        
        # é«˜é¢¨?ªè¨­?½è©³??        high_risk = self.risk_analysis[self.risk_analysis['é¢¨éšªç­‰ç?'] == 'High Risk']
        if len(high_risk) > 0:
            print(f"\né«˜é¢¨?ªè¨­??(??0??:")
            for _, row in high_risk.head(10).iterrows():
                print(f"  {row['?¿é›£?¶å®¹?•æ??ç¨±']} ({row['è¨­æ–½é¡å?']})")
                print(f"    ä½ç½®: {row['ç¸???Šé??®å??€']}")
                print(f"    ?€è¿‘æ¸¬ç«? {row['?€è¿‘AQIæ¸¬ç?']} (AQI: {row['?€è¿‘æ¸¬ç«™AQI']})")
                print(f"    è·é›¢: {row['è·é›¢æ¸¬ç?(km)']} km")
                print(f"    é¢¨éšª?†æ•¸: {row['é¢¨éšª?†æ•¸']}")
                print()
        
        # è­¦å?è¨­æ–½è©³æ?
        warning_risk = self.risk_analysis[self.risk_analysis['é¢¨éšªç­‰ç?'] == 'Warning']
        if len(warning_risk) > 0:
            print(f"\nè­¦å?é¢¨éšªè¨­æ–½ (????:")
            for _, row in warning_risk.head(5).iterrows():
                print(f"  {row['?¿é›£?¶å®¹?•æ??ç¨±']} ({row['è¨­æ–½é¡å?']})")
                print(f"    ä½ç½®: {row['ç¸???Šé??®å??€']}")
                print(f"    ?€è¿‘æ¸¬ç«? {row['?€è¿‘AQIæ¸¬ç?']} (AQI: {row['?€è¿‘æ¸¬ç«™AQI']})")
                print(f"    è·é›¢: {row['è·é›¢æ¸¬ç?(km)']} km")
                print(f"    é¢¨éšª?†æ•¸: {row['é¢¨éšª?†æ•¸']}")
                print()
    
    def save_results(self):
        """?²å??†æ?çµæ?"""
        if self.risk_analysis is None:
            print("è«‹å??·è?é¢¨éšª?†æ?")
            return
        
        # ç¢ºä? outputs ?®é?å­˜åœ¨
        import os
        os.makedirs('outputs', exist_ok=True)
        
        # ?²å?ä¸»è??†æ?çµæ?
        output_file = 'outputs/shelter_aqi_analysis.csv'
        self.risk_analysis.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\né¢¨éšª?†æ?çµæ?å·²å„²å­˜è‡³: {output_file}")
        
        # ?²å?çµ±è??˜è?
        summary_stats = {
            '?…ç›®': [
                'ç¸½é¿??”¶å®¹è??€?¸é?',
                'é«˜é¢¨?ªè¨­?½æ•¸??,
                'è­¦å?é¢¨éšªè¨­æ–½?¸é?', 
                'ä½é¢¨?ªè¨­?½æ•¸??,
                'å®¤å…§è¨­æ–½?¸é?',
                '?¶å?è¨­æ–½?¸é?',
                'å¹³å?é¢¨éšª?†æ•¸',
                '?€é«˜é¢¨?ªå???,
                'æ¨¡æ“¬?…å?èªªæ?'
            ],
            '?¸å€?: [
                len(self.risk_analysis),
                len(self.risk_analysis[self.risk_analysis['é¢¨éšªç­‰ç?'] == 'High Risk']),
                len(self.risk_analysis[self.risk_analysis['é¢¨éšªç­‰ç?'] == 'Warning']),
                len(self.risk_analysis[self.risk_analysis['é¢¨éšªç­‰ç?'] == 'Low Risk']),
                len(self.risk_analysis[self.risk_analysis['is_indoor'] == True]),
                len(self.risk_analysis[self.risk_analysis['is_indoor'] == False]),
                self.risk_analysis['é¢¨éšª?†æ•¸'].mean(),
                self.risk_analysis['é¢¨éšª?†æ•¸'].max(),
                'å°‡å??¨æ¸¬ç«™AQIè¨­ç‚º150?²è??…å?æ¨¡æ“¬'
            ]
        }
        
        summary_df = pd.DataFrame(summary_stats)
        summary_file = 'outputs/shelter_aqi_analysis_summary.csv'
        summary_df.to_csv(summary_file, index=False, encoding='utf-8-sig')
        print(f"çµ±è??˜è?å·²å„²å­˜è‡³: {summary_file}")
        
        # ?²å?æ¨¡æ“¬å¾Œç? AQI ?¸æ?
        simulation_file = 'outputs/simulated_aqi_stations.csv'
        self.aqi_data.to_csv(simulation_file, index=False, encoding='utf-8-sig')
        print(f"æ¨¡æ“¬å¾?AQI æ¸¬ç??¸æ?å·²å„²å­˜è‡³: {simulation_file}")
    
    def run_analysis(self):
        """?·è?å®Œæ•´?†æ?æµç?"""
        print("=" * 80)
        print("?¿é›£?¶å®¹?•æ? AQI é¢¨éšª?†æ??‡æ?å¢ƒæ¨¡??)
        print("=" * 80)
        
        # è¼‰å…¥?¸æ?
        if not self.load_data():
            print("è¼‰å…¥?¸æ?å¤±æ?")
            return
        
        # ?…å?æ¨¡æ“¬
        self.simulate_high_aqi_scenario()
        
        # ?·è?é¢¨éšª?†æ?
        self.perform_risk_analysis()
        
        # ?Ÿæ?çµ±è?
        self.generate_statistics()
        
        # ?²å?çµæ?
        self.save_results()
        
        print("\n" + "=" * 80)
        print("é¢¨éšª?†æ??‡æ?å¢ƒæ¨¡?¬å??ï?")
        print("=" * 80)
        print("?? è¼¸å‡ºæª”æ?:")
        print("   outputs/shelter_aqi_analysis.csv - è©³ç´°é¢¨éšª?†æ?çµæ?")
        print("   outputs/shelter_aqi_analysis_summary.csv - çµ±è??˜è?")
        print("   outputs/simulated_aqi_stations.csv - æ¨¡æ“¬å¾Œç?AQIæ¸¬ç??¸æ?")
        print("\n?š¨ ?…å?æ¨¡æ“¬èªªæ?:")
        print("   å·²å??—éƒ¨æ¸¬ç? AQI è¨­ç‚º 150")
        print("   é©—è?é¢¨éšªæ¨™ç±¤?è¼¯?¯å¦æ­?¢ºè§¸ç™¼")
        print("   ç¢ºä??½ç???'High Risk' æ¨™ç±¤")

def main():
    """ä¸»ç?å¼?""
    analyzer = ShelterAQIRiskAnalysis()
    analyzer.run_analysis()

if __name__ == "__main__":
    main()
