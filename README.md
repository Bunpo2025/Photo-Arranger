# Photo-Arranger

同一被写体で撮影時期の異なる2枚の写真の色調と明るさを合わせるWindows デスクトップアプリケーション。

## 機能

- **画像読み込み**: JPEG形式の画像を2枚読み込み、左右に並べて表示
- **自動色調補正**: 
  - カラーチャート（Macbeth Chart等）を使用した高精度補正
  - 画像全体の分析による補正
- **手動調整**: 色温度、色かぶり、明るさをスライダーで個別調整
- **画像保存**: 補正後の画像をJPEG形式で保存

## スクリーンショット

（開発後に追加予定）

## インストール

### 必要条件
- Python 3.10 以上
- Windows 10/11

### セットアップ

```bash
# リポジトリをクローン
git clone https://github.com/yourusername/Photo-Matching.git
cd Photo-Matching

# 仮想環境を作成（推奨）
python -m venv venv
.\venv\Scripts\activate

# 依存関係をインストール
pip install -r requirements.txt
```

## 使い方

```bash
python main.py
```

1. **画像を開く**: ツールバーの「Open A」「Open B」ボタンで2枚の画像を読み込み
2. **自動補正**: 「Auto Match」ボタンをクリックして自動色調補正を実行
3. **手動調整**: 各画像下のスライダーで微調整
4. **保存**: 「Save A」「Save B」ボタンで補正後の画像を保存

## プロジェクト構成

```
Photo-Matching/
├── main.py                 # エントリーポイント
├── requirements.txt        # Python依存関係
├── requirements.md         # 要件定義書
├── specification.md        # 詳細仕様書
├── src/
│   ├── app.py              # アプリケーション初期化
│   ├── ui/                 # UIコンポーネント
│   │   ├── main_window.py
│   │   └── components/
│   │       ├── image_panel.py
│   │       └── slider_panel.py
│   ├── core/               # コア機能
│   │   ├── image_processor.py
│   │   ├── color_matcher.py
│   │   └── chart_detector.py
│   └── utils/
│       └── file_handler.py
├── tests/                  # テストコード
├── assets/                 # 静的リソース
│   └── icons/
└── docs/                   # ドキュメント
```

## 開発

### テスト実行

```bash
pytest tests/
```

### コーディング規約
- PEP 8 準拠
- Type Hints 使用

## ライセンス

MIT License

## 作者

（あなたの名前）


