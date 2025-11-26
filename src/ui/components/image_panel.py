#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
画像表示パネルモジュール
"""

import cv2
import numpy as np
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage


class ImagePanel(QFrame):
    """画像表示パネルクラス"""
    
    def __init__(self, title: str = ""):
        super().__init__()
        self.title = title
        self.original_image: np.ndarray | None = None
        self.processed_image: np.ndarray | None = None
        
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
        画像を保存
        
        Args:
            file_path: 保存先パス
        """
        if self.processed_image is not None:
            if not file_path.lower().endswith(('.jpg', '.jpeg')):
                file_path += '.jpg'
            
            # 日本語パス対応のため、エンコードしてから書き込み
            success, encoded_image = cv2.imencode('.jpg', self.processed_image, [cv2.IMWRITE_JPEG_QUALITY, 95])
            if success:
                with open(file_path, 'wb') as f:
                    f.write(encoded_image.tobytes())
            else:
                raise ValueError("画像のエンコードに失敗しました")
    
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

