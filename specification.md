# 詳細仕様書 (Detailed Specification)

## 1. システム構成

### 1.1 技術スタック
| カテゴリ | 技術 |
|---------|------|
| 言語 | Python 3.10+ |
| UIフレームワーク | PyQt6 |
| 画像処理 | OpenCV, NumPy, Pillow |
| カラーチャート検出 | OpenCV (ArUco/Color Detection) |

### 1.2 アーキテクチャ
```
Photo-Arranger/
├── main.py                 # エントリーポイント
├── src/
│   ├── app.py              # アプリケーション初期化
│   ├── ui/                 # UI コンポーネント
│   │   ├── main_window.py  # メインウィンドウ
│   │   └── components/     # UIパーツ
│   │       ├── image_panel.py    # 画像表示パネル
│   │       └── slider_panel.py   # 調整スライダー
│   ├── core/               # コア機能
│   │   ├── image_processor.py    # 画像処理エンジン
│   │   ├── color_matcher.py      # 色調マッチング
│   │   └── chart_detector.py     # カラーチャート検出
│   └── utils/              # ユーティリティ
│       └── file_handler.py       # ファイル操作
├── tests/                  # テストコード
├── assets/                 # 静的リソース
│   └── icons/              # アイコン類
└── docs/                   # ドキュメント
```

---

## 2. UI詳細設計

### 2.1 メインウィンドウ
- **サイズ**: 1280 x 800 (初期値)、最小サイズ 960 x 600
- **リサイズ**: 可能（アスペクト比維持で画像もリサイズ）

### 2.2 レイアウト構成
```
┌──────────────────────────────────────────────────────────────┐
│                        ツールバー                              │
│  [📁 Open A] [📁 Open B]                    [Auto Match ▼]   │
├─────────────────────────────┬────────────────────────────────┤
│                             │                                │
│        Photo A              │          Photo B               │
│       (Target)              │        (Reference)             │
│                             │                                │
│                             │                                │
├─────────────────────────────┼────────────────────────────────┤
│ 色温度:  ──●────────────    │ 色温度:  ──●────────────       │
│ 色かぶり: ────●──────────   │ 色かぶり: ────●──────────      │
│ 明るさ:  ─────●─────────    │ 明るさ:  ─────●─────────       │
│ [リセット]                   │ [リセット]                      │
├─────────────────────────────┴────────────────────────────────┤
│              [💾 Save A]           [💾 Save B]                │
└──────────────────────────────────────────────────────────────┘
```

### 2.3 コンポーネント詳細

#### 2.3.1 画像パネル (ImagePanel)
| プロパティ | 説明 |
|-----------|------|
| image | 表示する画像データ (QPixmap) |
| original_image | 元画像データ（補正適用前） |
| zoom_level | ズームレベル (1.0 = 100%) |
| fit_mode | フィットモード (FIT_WIDTH, FIT_HEIGHT, FIT_BOTH) |

| メソッド | 説明 |
|---------|------|
| load_image(path) | 画像を読み込み表示 |
| update_display() | 補正値を適用して再描画 |
| reset() | 補正をリセット |

#### 2.3.2 調整スライダー (SliderPanel)
| パラメータ | 範囲 | デフォルト | 単位 |
|-----------|------|-----------|------|
| 色温度 (Temperature) | -100 ~ +100 | 0 | - |
| 色かぶり (Tint) | -100 ~ +100 | 0 | - |
| 明るさ (Brightness) | -100 ~ +100 | 0 | - |

#### 2.3.3 Auto Match ボタン
- クリックでドロップダウンメニュー表示
  - 「カラーチャートで補正」
  - 「画像全体で補正」

---

## 3. コア機能詳細設計

### 3.1 画像処理エンジン (ImageProcessor)

#### 3.1.1 色温度補正
```python
def adjust_temperature(image: np.ndarray, value: int) -> np.ndarray:
    """
    色温度を調整する
    
    Args:
        image: 入力画像 (BGR形式)
        value: 補正値 (-100 ~ +100)
               負: 青みを増す（クール）
               正: 赤みを増す（ウォーム）
    
    Returns:
        補正後の画像
    """
```

#### 3.1.2 色かぶり補正
```python
def adjust_tint(image: np.ndarray, value: int) -> np.ndarray:
    """
    色かぶり（グリーン/マゼンタ）を調整する
    
    Args:
        image: 入力画像 (BGR形式)
        value: 補正値 (-100 ~ +100)
               負: グリーン方向
               正: マゼンタ方向
    
    Returns:
        補正後の画像
    """
```

#### 3.1.3 明るさ補正
```python
def adjust_brightness(image: np.ndarray, value: int) -> np.ndarray:
    """
    明るさを調整する
    
    Args:
        image: 入力画像 (BGR形式)
        value: 補正値 (-100 ~ +100)
    
    Returns:
        補正後の画像
    """
```

### 3.2 色調マッチング (ColorMatcher)

#### 3.2.1 ヒストグラムマッチング
```python
def match_histograms(source: np.ndarray, reference: np.ndarray) -> np.ndarray:
    """
    参照画像のヒストグラムに合わせてソース画像を補正
    
    Args:
        source: 補正対象画像
        reference: 参照画像
    
    Returns:
        補正後の画像
    """
```

#### 3.2.2 色転送 (Color Transfer)
```python
def color_transfer(source: np.ndarray, reference: np.ndarray) -> np.ndarray:
    """
    Lab色空間での色転送アルゴリズム
    参照画像の色調をソース画像に適用
    
    Args:
        source: 補正対象画像
        reference: 参照画像
    
    Returns:
        補正後の画像
    """
```

### 3.3 カラーチャート検出 (ChartDetector)

#### 3.3.1 チャート検出
```python
def detect_chart(image: np.ndarray) -> Optional[ChartRegion]:
    """
    画像内のカラーチャート（Macbeth ColorChecker等）を検出
    
    Args:
        image: 入力画像
    
    Returns:
        検出されたチャート領域、または None
    """
```

#### 3.3.2 チャートベース補正
```python
def match_by_chart(
    source: np.ndarray, 
    reference: np.ndarray,
    source_chart: ChartRegion,
    reference_chart: ChartRegion
) -> np.ndarray:
    """
    両画像のカラーチャートを基準に色調を合わせる
    
    Args:
        source: 補正対象画像
        reference: 参照画像
        source_chart: ソース画像のチャート領域
        reference_chart: 参照画像のチャート領域
    
    Returns:
        補正後の画像
    """
```

---

## 4. データフロー

### 4.1 画像読み込みフロー
```
[ファイル選択] → [JPEG読み込み] → [画像検証] → [表示用リサイズ] → [パネル表示]
                                       ↓
                              [元画像をメモリ保持]
```

### 4.2 自動補正フロー
```
[Auto Match クリック]
       ↓
[補正モード選択]
       ├── カラーチャートあり
       │      ↓
       │   [両画像からチャート検出]
       │      ↓
       │   [チャートの色値抽出]
       │      ↓
       │   [色変換行列計算]
       │      ↓
       │   [補正適用]
       │
       └── カラーチャートなし
              ↓
           [ヒストグラム分析]
              ↓
           [色転送アルゴリズム適用]
              ↓
           [補正適用]
```

### 4.3 保存フロー
```
[Save クリック] → [元画像に補正適用] → [JPEG圧縮] → [ファイル保存ダイアログ] → [保存]
```

---

## 5. エラーハンドリング

| エラーケース | 処理 |
|-------------|------|
| 非対応ファイル形式 | エラーダイアログ「JPEG形式のみ対応しています」 |
| ファイル読み込み失敗 | エラーダイアログ「ファイルを開けませんでした」 |
| カラーチャート未検出 | 警告ダイアログ「カラーチャートが検出できませんでした。画像全体で補正しますか？」 |
| 保存失敗 | エラーダイアログ「ファイルを保存できませんでした」 |

---

## 6. パフォーマンス要件

| 項目 | 目標値 |
|------|--------|
| 画像読み込み (10MB JPEG) | < 2秒 |
| 自動補正処理 | < 3秒 |
| スライダー調整レスポンス | < 100ms |
| メモリ使用量 (2枚読み込み時) | < 500MB |

---

## 7. 将来の拡張予定

- [ ] RAW形式対応
- [ ] バッチ処理機能
- [ ] 補正プリセット保存/読み込み
- [ ] Undo/Redo機能
- [ ] 比較表示モード（スライド/オーバーレイ）


