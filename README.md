# 🏖️ 納屋港 干潟出現予測システム

大分県杵築市納屋港における干潟の出現を予測する自動更新システムです。　

予測データVS実測データ比較を追加しました。・・・12/5

公開URL:https://kitsukisaiseikyo-byte.github.io/naya-tidal-flat/

## 📊 機能

- **実測データ**: 海上保安庁から30分ごとに自動取得（大分港の実測値）
- **予測データ**: 毎日0時に7日分の潮位予測を自動取得
- **自動更新**: GitHub Actions により24時間365日稼働
- **データ蓄積**: JSON形式で日次保存、過去データも参照可能
- **リアルタイム表示**: GitHub Pages で公開、自動デプロイ

## 🚀 セットアップ

### 1. リポジトリのクローン

```bash
git clone https://github.com/YOUR_USERNAME/naya-tidal-flat.git
cd naya-tidal-flat
```

### 2. ディレクトリ構造

```
naya-tidal-flat/
├── .github/
│   └── workflows/
│       ├── update-observed-data.yml      # 30分ごと実測データ取得
│       ├── update-prediction-data.yml    # 毎日0時予測データ取得
│       └── deploy-github-pages.yml       # GitHub Pages デプロイ
├── scripts/
│   ├── fetch_observed_tide.py           # 実測データ取得スクリプト
│   └── fetch_tide_prediction.py         # 予測データ取得スクリプト
├── data/
│   ├── observed/                         # 実測データ保存先
│   │   ├── latest.json                  # 最新24時間分
│   │   └── oita_observed_YYYY-MM-DD.json
│   └── prediction/                       # 予測データ保存先
│       ├── latest.json                  # 最新7日分
│       └── oita_prediction_YYYY-MM-DD.json
├── index.html                            # Webアプリ本体
└── README.md
```

### 3. GitHub Pages の有効化

1. GitHub リポジトリの Settings > Pages
2. Source: "GitHub Actions" を選択
3. 保存

### 4. 初回データ取得（手動）

```bash
# 実測データ取得
python scripts/fetch_observed_tide.py

# 予測データ取得
python scripts/fetch_tide_prediction.py

# コミット & プッシュ
git add data/
git commit -m "Initial data fetch"
git push
```

## 🔄 自動更新スケジュール

| データ種類 | 更新頻度 | 実行時刻（UTC） | 実行時刻（JST） | ワークフロー |
|----------|---------|--------------|--------------|------------|
| 実測データ | 30分ごと | 0,30分 毎時 | 9,39分 毎時 | update-observed-data.yml |
| 予測データ | 毎日1回 | 0:15 | 9:15 | update-prediction-data.yml |

## 📈 データ形式

### 実測データ（observed）

```json
[
  {
    "datetime": "2024-11-14T12:00:00",
    "tide": 125,
    "type": "observed"
  }
]
```

### 予測データ（prediction）

```json
[
  {
    "datetime": "2024-11-14T12:00:00",
    "tide": 130,
    "type": "prediction"
  }
]
```

## 🛠️ カスタマイズ

### 干潟判定閾値の変更

`index.html` の初期値を変更:

```javascript
const [threshold, setThreshold] = React.useState(120); // 閾値(cm)
```

### 作業時間帯の変更

```javascript
const [minTime, setMinTime] = React.useState(6);  // 開始時刻
const [maxTime, setMaxTime] = React.useState(18); // 終了時刻
```

### 更新頻度の変更

`.github/workflows/update-observed-data.yml`:

```yaml
schedule:
  - cron: '0,30 * * * *'  # 30分ごと → 15分ごとなら '*/15 * * * *'
```

## 📊 データの精度

- **実測データ**: 海上保安庁公式データ（5分間隔）
- **予測データ**: 海上保安庁潮汐予測（調和解析による）
- **納屋港推定**: 大分港データから地形補正（要キャリブレーション）

## 🔗 参考リンク

- [海上保安庁 潮汐・海面水位情報](https://www1.kaiho.mlit.go.jp/TIDE/)
- [大分港 リアルタイム潮位](https://www1.kaiho.mlit.go.jp/TIDE/gauge/gauge.php?s=0163)

## 📝 ライセンス

MIT License

## 🤝 貢献

Issue や Pull Request を歓迎します！

---
 
**最終更新**: 2025-12-5
