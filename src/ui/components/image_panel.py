#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
画像表示パネルモジュール
"""

import cv2
import numpy as np
from pathlib import Path
from PIL import Image
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QRect
from PyQt6.QtGui import QPixmap, QImage

from src.ui.components.crop_widget import CropOverlay, CropControlPanel


class ImagePanel(QFrame):
    """画像表示パネルクラス"""
    
    # クロップ確定シグナル (x, y, width, height)
    crop_confirmed = pyqtSignal(int, int, int, int)
    # クロップキャンセルシグナル
    crop_cancelled = pyqtSignal()
    
    def __init__(self, title: str = ""):
        super().__init__()
        self.title = title
        self.original_image: np.ndarray | None = None
        self.processed_image: np.ndarray | None = None
        self._file_path: str = ""
        self._dpi: int = 300  # デフォルトDPI
        
        # クロップモード
        self.crop_mode = False
        self.crop_overlay: CropOverlay | None = None
        self.crop_control: CropControlPanel | None = None
        
        # 画像表示領域のキャッシュ
        self._last_image_rect = QRect()
        
        self._setup_ui()
    
    def _setup_ui(self):
        """UIをセットアップ"""
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Sunken)
        self.setStyleSheet("""
            ImagePanel {
                background-color: #0d0d0d;
                border: 1px solid #333;
                border-radius: 4px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # タイトルラベル
        self.title_label = QLabel(self.title)
        self.title_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-weight: bold;
                padding: 5px;
            }
        """)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)
        
        # 画像表示ラベル
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        self.image_label.setText("画像をドラッグ＆ドロップ\nまたは\n上のボタンから開いてください")
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: #0a0a0a;
                color: #666;
                font-size: 14px;
                border: none;
            }
        """)
        layout.addWidget(self.image_label, stretch=1)
        
        # ファイル名表示ラベル
        self.filename_label = QLabel("")
        self.filename_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.filename_label.setStyleSheet("""
            QLabel {
                color: #aaa;
                font-size: 13px;
                padding: 4px;
            }
        """)
        layout.addWidget(self.filename_label)
        
        # ドラッグ＆ドロップを有効化
        self.setAcceptDrops(True)
    
    def load_image(self, file_path: str):
        """
        画像を読み込む
        
        Args:
            file_path: 画像ファイルのパス
        """
        # 日本語パスやネットワークパス対応のため、numpy経由で読み込む
        try:
            # ファイルをバイナリで読み込み
            with open(file_path, 'rb') as f:
                file_bytes = np.frombuffer(f.read(), dtype=np.uint8)
            
            # OpenCVでデコード（BGR形式）
            image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
            
            if image is None:
                raise ValueError(f"画像をデコードできません: {file_path}")
        except FileNotFoundError:
            raise ValueError(f"ファイルが見つかりません: {file_path}")
        except PermissionError:
            raise ValueError(f"ファイルへのアクセス権限がありません: {file_path}")
        except Exception as e:
            raise ValueError(f"画像を読み込めません: {file_path}\n{str(e)}")
        
        self.original_image = image.copy()
        self.processed_image = image.copy()
        self._file_path = file_path
        self._update_filename_display()
        self._update_display()
    
    def set_processed_image(self, image: np.ndarray):
        """
        処理済み画像を設定
        
        Args:
            image: 処理済み画像（BGR形式）
        """
        self.processed_image = image.copy()
        self._update_display()
    
    def save_image(self, file_path: str):
        """
        画像を保存（DPIメタデータ付き）
        
        Args:
            file_path: 保存先パス
        """
        if self.processed_image is not None:
            if not file_path.lower().endswith(('.jpg', '.jpeg')):
                file_path += '.jpg'
            
            # BGR → RGB変換
            rgb_image = cv2.cvtColor(self.processed_image, cv2.COLOR_BGR2RGB)
            
            # PILイメージに変換
            pil_image = Image.fromarray(rgb_image)
            
            # DPIメタデータを設定して保存
            pil_image.save(
                file_path,
                'JPEG',
                quality=95,
                dpi=(self._dpi, self._dpi)
            )
    
    def reset(self):
        """画像をリセット（元画像に戻す）"""
        if self.original_image is not None:
            self.processed_image = self.original_image.copy()
            self._update_display()
    
    def _update_display(self):
        """表示を更新"""
        if self.processed_image is None:
            return
        
        # BGR → RGB変換
        rgb_image = cv2.cvtColor(self.processed_image, cv2.COLOR_BGR2RGB)
        
        # QImageに変換
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        q_image = QImage(
            rgb_image.data,
            w, h,
            bytes_per_line,
            QImage.Format.Format_RGB888
        )
        
        # 表示サイズに合わせてスケール
        pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = pixmap.scaled(
            self.image_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        
        self.image_label.setPixmap(scaled_pixmap)
    
    def resizeEvent(self, event):
        """リサイズイベント"""
        super().resizeEvent(event)
        self._update_display()
        
        # クロップモード中はオーバーレイも更新
        if self.crop_mode and self.crop_overlay and self.processed_image is not None:
            self.crop_overlay.setGeometry(self.image_label.rect())
            image_rect = self._calculate_image_rect()
            h, w = self.processed_image.shape[:2]
            self.crop_overlay.set_image_rect(image_rect, (w, h))
    
    def dragEnterEvent(self, event):
        """ドラッグエンターイベント"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        """ドロップイベント"""
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if file_path.lower().endswith(('.jpg', '.jpeg')):
                try:
                    self.load_image(file_path)
                except Exception as e:
                    from PyQt6.QtWidgets import QMessageBox
                    QMessageBox.critical(
                        self,
                        "エラー",
                        f"ファイルを開けませんでした:\n{str(e)}"
                    )
    
    def start_crop_mode(self):
        """クロップモードを開始"""
        if self.processed_image is None:
            return False
        
        self.crop_mode = True
        
        # クロップオーバーレイを作成
        self.crop_overlay = CropOverlay(self.image_label)
        self.crop_overlay.setGeometry(self.image_label.rect())
        
        # 画像表示領域を計算して設定
        image_rect = self._calculate_image_rect()
        h, w = self.processed_image.shape[:2]
        self.crop_overlay.set_image_rect(image_rect, (w, h))
        
        # シグナル接続
        self.crop_overlay.crop_confirmed.connect(self._on_crop_confirmed)
        self.crop_overlay.crop_cancelled.connect(self._on_crop_cancelled)
        
        self.crop_overlay.show()
        self.crop_overlay.raise_()
        
        return True
    
    def stop_crop_mode(self):
        """クロップモードを終了"""
        self.crop_mode = False
        
        if self.crop_overlay:
            self.crop_overlay.hide()
            self.crop_overlay.deleteLater()
            self.crop_overlay = None
    
    def set_crop_aspect_ratio(self, ratio: tuple | None):
        """クロップのアスペクト比を設定"""
        if self.crop_overlay:
            self.crop_overlay.set_aspect_ratio(ratio)
    
    def confirm_crop(self):
        """クロップを確定"""
        if self.crop_overlay:
            self.crop_overlay.confirm_crop()
    
    def cancel_crop(self):
        """クロップをキャンセル"""
        self.stop_crop_mode()
        self.crop_cancelled.emit()
    
    def _calculate_image_rect(self) -> QRect:
        """画像の表示領域を計算"""
        if self.processed_image is None:
            return QRect()
        
        label_size = self.image_label.size()
        h, w = self.processed_image.shape[:2]
        
        # アスペクト比を維持してスケール
        scale_w = label_size.width() / w
        scale_h = label_size.height() / h
        scale = min(scale_w, scale_h)
        
        scaled_w = int(w * scale)
        scaled_h = int(h * scale)
        
        # 中央配置
        x = (label_size.width() - scaled_w) // 2
        y = (label_size.height() - scaled_h) // 2
        
        return QRect(x, y, scaled_w, scaled_h)
    
    def _on_crop_confirmed(self, x: int, y: int, width: int, height: int):
        """クロップ確定時"""
        self.stop_crop_mode()
        self.crop_confirmed.emit(x, y, width, height)
    
    def _on_crop_cancelled(self):
        """クロップキャンセル時"""
        self.stop_crop_mode()
        self.crop_cancelled.emit()
    
    def get_image_size(self) -> tuple:
        """
        現在の画像サイズを取得
        
        Returns:
            (width, height) のタプル
        """
        if self.processed_image is None:
            return (0, 0)
        h, w = self.processed_image.shape[:2]
        return (w, h)
    
    def _update_filename_display(self):
        """ファイル名表示を更新"""
        if self._file_path:
            filename = Path(self._file_path).name
            self.filename_label.setText(filename)
        else:
            self.filename_label.setText("")
    
    def get_filename(self) -> str:
        """
        現在のファイル名を取得
        
        Returns:
            ファイル名（パスなし）
        """
        if self._file_path:
            return Path(self._file_path).name
        return ""
    
    def get_filepath(self) -> str:
        """
        現在のファイルパスを取得
        
        Returns:
            ファイルパス
        """
        return self._file_path
    
    def set_dpi(self, dpi: int):
        """
        DPI値を設定
        
        Args:
            dpi: DPI値
        """
        self._dpi = dpi
    
    def get_dpi(self) -> int:
        """
        現在のDPI値を取得
        
        Returns:
            DPI値
        """
        return self._dpi

