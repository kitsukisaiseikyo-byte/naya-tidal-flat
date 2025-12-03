# ============================================
# scripts/fetch_tide_prediction.py
# 予測データを毎日0時に取得
# ============================================

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
from pathlib import Path

AREA_CODE = "4402"  # 大分鶴崎
BACK_PARAM = "3"
DAYS_TO_FETCH = 7
BASE_URL = "https://www1.kaiho.mlit.go.jp/TIDE/pred2/cgi-bin/TidePredCgi.cgi"

def fetch_prediction_data(target_date):
    """指定日の潮位予測データを取得"""
    params = {
        'area': AREA_CODE,
        'back': BACK_PARAM,
        'year': target_date.strftime('%Y'),
        'month': target_date.strftime('%m'),
        'day': target_date.strftime('%d')
    }
    
    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, 'html.parser')
        
        target_table = soup.find('table', bgcolor="#e3ffe3")
        if not target_table:
            return None
        
        rows = target_table.find_all('tr')
        hours_0_11 = [td.text.strip() for td in rows[0].find_all('td')[1:]]
        levels_0_11 = [td.text.strip() for td in rows[1].find_all('td')[1:]]
        hours_12_23 = [td.text.strip() for td in rows[2].find_all('td')[1:]]
        levels_12_23 = [td.text.strip() for td in rows[3].find_all('td')[1:]]
        
        hours = hours_0_11 + hours_12_23
        levels = levels_0_11 + levels_12_23
        
        data = []
        for j in range(24):
            time_str = f"{hours[j].zfill(2)}:00:00"
            level_cm = levels[j].replace(' ', '')
            datetime_str = f"{target_date.strftime('%Y-%m-%d')}T{time_str}"
            
            data.append({
                'datetime': datetime_str,
                'tide': int(level_cm),
                'type': 'prediction'
            })
        
        return data
        
    except Exception as e:
        print(f"❌ {target_date.strftime('%Y-%m-%d')} の取得エラー: {e}")
        return None

def save_prediction_data(all_data, output_dir='data/prediction'):
    """予測データを保存"""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # 日付ごとのファイル名
    today = datetime.now().strftime('%Y-%m-%d')
    output_file = Path(output_dir) / f'oita_prediction_{today}.json'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    # 最新ファイル
    latest_file = Path(output_dir) / 'latest.json'
    with open(latest_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 予測データを保存: {output_file}")
    print(f"   データ件数: {len(all_data)} 件")

def main():
    print("=" * 60)
    print("📊 7日間潮位予測データ取得開始")
    print(f"   取得時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    start_date = datetime.now().date()
    all_data = []
    
    for i in range(DAYS_TO_FETCH):
        target_date = start_date + timedelta(days=i)
        print(f"📅 {target_date.strftime('%Y-%m-%d')} のデータを取得中...")
        
        data = fetch_prediction_data(target_date)
        if data:
            all_data.extend(data)
            print(f"   ✅ {len(data)} 件取得")
        else:
            print(f"   ⚠️ 取得失敗")
    
    if all_data:
        save_prediction_data(all_data)
        print("=" * 60)
        print(f"✅ 全 {len(all_data)} 件のデータ取得完了")
        print("=" * 60)
    else:
        print("❌ データを取得できませんでした")

if __name__ == "__main__":
    main()
