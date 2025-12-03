# scripts/fetch_observed_tide.py
# 実測データを30分ごとに取得

import pandas as pd
import re
import json
import requests
from datetime import datetime
from pathlib import Path

def fetch_tide_data(url='https://www1.kaiho.mlit.go.jp/TIDE/gauge/gauge.php?s=0163'):
    """海上保安庁のWebページから潮位データを取得"""
    try:
        response = requests.get(url, timeout=30)
        response.encoding = 'utf-8'
        return response.text
    except Exception as e:
        print(f"データ取得エラー: {e}")
        return None

def extract_observed_tide(content):
    """HTMLコンテンツから5分ごとの観測潮位データを抽出"""
    obs_section_match = re.search(
        r'観測データ[：:]\s*[５5]分毎瞬間値.*?year\s+date\s+time\s+cm(.*?)(?=<|$)', 
        content, 
        re.DOTALL
    )
    
    if not obs_section_match:
        print("観測データセクションが見つかりませんでした")
        return []
    
    obs_data_text = obs_section_match.group(1)
    data_pattern = r'(\d{4})\s+(\d{1,2})\s+(\d{1,2})\s+(\d{1,2})\s+(\d{1,2})\s+(\d+|9999)'
    matches = re.findall(data_pattern, obs_data_text)
    
    data_rows = []
    for match in matches:
        year, month, day, hour, minute, tide_cm = match
        if tide_cm != '9999':  # 欠損値を除外
            datetime_str = f"{year}-{month.zfill(2)}-{day.zfill(2)}T{hour.zfill(2)}:{minute.zfill(2)}:00"
            data_rows.append({
                'datetime': datetime_str,
                'tide': int(tide_cm),
                'type': 'observed'
            })
    
    return data_rows

def save_data(data, output_dir='data/observed'):
    """データをJSON形式で保存"""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # 現在の日付でファイル名を生成
    today = datetime.now().strftime('%Y-%m-%d')
    output_file = Path(output_dir) / f'oita_observed_{today}.json'
    
    # 既存データがあれば読み込んで結合
    existing_data = []
    if output_file.exists():
        with open(output_file, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
    
    # 重複を除去してマージ
    all_data = existing_data + data
    unique_data = {item['datetime']: item for item in all_data}.values()
    sorted_data = sorted(unique_data, key=lambda x: x['datetime'])
    
    # 保存
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(sorted_data, f, ensure_ascii=False, indent=2)
    
    # 最新データファイルも作成（Webアプリ用）
    latest_file = Path(output_dir) / 'latest.json'
    # 直近24時間分のみ
    recent_data = [d for d in sorted_data if d['datetime'] >= (datetime.now().isoformat()[:10] + 'T00:00:00')]
    with open(latest_file, 'w', encoding='utf-8') as f:
        json.dump(recent_data[-288:], f, ensure_ascii=False, indent=2)  # 24時間×12(5分間隔)
    
    print(f"✅ データを保存しました: {output_file}")
    print(f"   データ件数: {len(sorted_data)} 件")
    print(f"   最新データ件数: {len(recent_data[-288:])} 件")
    
    return len(sorted_data)

def main():
    print("=" * 60)
    print("🌊 実測潮位データ取得開始")
    print(f"   取得時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # データ取得
    content = fetch_tide_data()
    if content is None:
        print("❌ データの取得に失敗しました")
        return
    
    # データ抽出
    data = extract_observed_tide(content)
    if not data:
        print("❌ 観測潮位データを抽出できませんでした")
        return
    
    print(f"✅ {len(data)} 件のデータを取得しました")
    
    # データ保存
    total_count = save_data(data)
    
    print("=" * 60)
    print("✅ 処理完了")
    print("=" * 60)

if __name__ == "__main__":
    main()
