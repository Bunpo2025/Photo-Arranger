#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
メインウィンドウモジュール
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QFileDialog, QMessageBox,
    QSplitter, QMenu, QLabel
)
from PyQt6.QtCore import Qt

from src.ui.components.image_panel import ImagePanel
from src.ui.components.slider_panel import SliderPanel
from src.core.image_processor import ImageProcessor
from src.core.color_matcher import ColorMatcher


class MainWindow(QMainWindow):
    """メインウィンドウクラス"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Photo-Arranger")
        self.setMinimumSize(960, 600)
        self.resize(1280, 800)
        
        # 背景を黒に設定
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a1a;
            }
            QWidget {
                background-color: #1a1a1a;
                color: #ffffff;
            }
            QPushButton {
                background-color: #3a3a3a;
                color: #ffffff;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
                border-color: #666;
            }
            QPushButton:pressed {
                background-color: #2a2a2a;
            }
            QPushButton::menu-indicator {
                image: none;
                width: 0px;
            }
            QMenu {
                background-color: #2a2a2a;
                color: #ffffff;
                border: 1px solid #555;
            }
            QMenu::item:selected {
                background-color: #3498db;
            }
            QSplitter::handle {
                background-color: #333;
            }
        """)
        
        # コアコンポーネント初期化
        self.image_processor = ImageProcessor()
        self.color_matcher = ColorMatcher()
        
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """UIをセットアップ"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # スプリッター（左右の画像パネル）
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左側（写真A - 基準）
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(5, 5, 5, 5)
        left_layout.setSpacing(8)
        
        # 写真A のヘッダー（開くボタン）
        header_a = QHBoxLayout()
        self.open_a_button = QPushButton("📁 写真A を開く")
        self.open_a_button.setMinimumHeight(36)
        header_a.addWidget(self.open_a_button)
        header_a.addStretch()
        left_layout.addLayout(header_a)
        
        self.image_panel_a = ImagePanel("写真A（基準）")
        self.slider_panel_a = SliderPanel()
        left_layout.addWidget(self.image_panel_a, stretch=1)
        left_layout.addWidget(self.slider_panel_a)
        
        # 右側（写真B - 補正対象）
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(5, 5, 5, 5)
        right_layout.setSpacing(8)
        
        # 写真B のヘッダー（開くボタン）
        header_b = QHBoxLayout()
        self.open_b_button = QPushButton("📁 写真B を開く")
        self.open_b_button.setMinimumHeight(36)
        header_b.addWidget(self.open_b_button)
        header_b.addStretch()
        right_layout.addLayout(header_b)
        
        self.image_panel_b = ImagePanel("写真B（補正対象）")
        self.slider_panel_b = SliderPanel()
        right_layout.addWidget(self.image_panel_b, stretch=1)
        right_layout.addWidget(self.slider_panel_b)
        
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([640, 640])
        
        main_layout.addWidget(splitter, stretch=1)
        
        # 自動補正ボタン（中央配置）
        auto_match_layout = QHBoxLayout()
        auto_match_layout.addStretch()
        
        self.auto_match_button = QPushButton("🎨 自動補正 ▼")
        self.auto_match_button.setMinimumWidth(200)
        self.auto_match_button.setMinimumHeight(40)
        self.auto_match_button.setStyleSheet("""
            QPushButton {
                background-color: #2980b9;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 10px 24px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3498db;
            }
            QPushButton:pressed {
                background-color: #1f6dad;
            }
        """)
        auto_match_menu = QMenu()
        auto_match_menu.setStyleSheet("""
            QMenu {
                background-color: #2a2a2a;
                color: #ffffff;
                border: 1px solid #555;
                padding: 5px;
            }
            QMenu::item {
                padding: 8px 20px;
            }
            QMenu::item:selected {
                background-color: #3498db;
            }
        """)
        self.match_with_chart_action = auto_match_menu.addAction("カラーチャートで補正")
        self.match_without_chart_action = auto_match_menu.addAction("画像全体で補正")
        self.auto_match_button.setMenu(auto_match_menu)
        
        auto_match_layout.addWidget(self.auto_match_button)
        auto_match_layout.addStretch()
        main_layout.addLayout(auto_match_layout)
        
        # フッター（保存ボタン - 中央配置）
        footer_layout = QHBoxLayout()
        footer_layout.addStretch()
        
        self.save_a_button = QPushButton("💾 Aを保存")
        self.save_a_button.setMinimumWidth(120)
        self.save_a_button.setMinimumHeight(36)
        footer_layout.addWidget(self.save_a_button)
        
        footer_layout.addSpacing(20)
        
        self.save_b_button = QPushButton("💾 Bを保存")
        self.save_b_button.setMinimumWidth(120)
        self.save_b_button.setMinimumHeight(36)
        footer_layout.addWidget(self.save_b_button)
        
        footer_layout.addStretch()
        main_layout.addLayout(footer_layout)
    
    def _connect_signals(self):
        """シグナルを接続"""
        # ファイルを開く
        self.open_a_button.clicked.connect(lambda: self._open_image("A"))
        self.open_b_button.clicked.connect(lambda: self._open_image("B"))
        
        # 保存
        self.save_a_button.clicked.connect(lambda: self._save_image("A"))
        self.save_b_button.clicked.connect(lambda: self._save_image("B"))
        
        # 自動補正
        self.match_with_chart_action.triggered.connect(self._auto_match_with_chart)
        self.match_without_chart_action.triggered.connect(self._auto_match_without_chart)
        
        # スライダー変更
        self.slider_panel_a.values_changed.connect(self._on_slider_a_changed)
        self.slider_panel_b.values_changed.connect(self._on_slider_b_changed)
    
    def _open_image(self, panel: str):
        """画像を開く"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            f"写真{panel} を開く",
            "",
            "JPEG画像 (*.jpg *.jpeg);;すべてのファイル (*)"
        )
        
        if file_path:
            try:
                if panel == "A":
                    self.image_panel_a.load_image(file_path)
                    self.slider_panel_a.reset()
                else:
                    self.image_panel_b.load_image(file_path)
                    self.slider_panel_b.reset()
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "エラー",
                    f"ファイルを開けませんでした:\n{str(e)}"
                )
    
    def _save_image(self, panel: str):
        """画像を保存"""
        image_panel = self.image_panel_a if panel == "A" else self.image_panel_b
        
        if image_panel.original_image is None:
            QMessageBox.warning(self, "警告", "保存する画像がありません")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            f"写真{panel} を保存",
            "",
            "JPEG画像 (*.jpg)"
        )
        
        if file_path:
            try:
                image_panel.save_image(file_path)
                QMessageBox.information(self, "完了", "画像を保存しました")
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "エラー",
                    f"ファイルを保存できませんでした:\n{str(e)}"
                )
    
    def _auto_match_with_chart(self):
        """カラーチャートを使用した自動補正"""
        if not self._check_images_loaded():
            return
        
        try:
            # 写真A（基準）→ 写真B（補正対象）
            result = self.color_matcher.match_with_chart(
                self.image_panel_b.original_image,  # 補正対象（B）
                self.image_panel_a.original_image   # 基準（A）
            )
            
            if result is not None:
                self.image_panel_b.set_processed_image(result)
            else:
                reply = QMessageBox.question(
                    self,
                    "カラーチャート未検出",
                    "カラーチャートが検出できませんでした。\n画像全体で補正しますか？",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    self._auto_match_without_chart()
        except Exception as e:
            QMessageBox.critical(self, "エラー", f"補正に失敗しました:\n{str(e)}")
    
    def _auto_match_without_chart(self):
        """画像全体を使用した自動補正"""
        if not self._check_images_loaded():
            return
        
        try:
            # 写真A（基準）→ 写真B（補正対象）
            result = self.color_matcher.match_histograms(
                self.image_panel_b.original_image,  # 補正対象（B）
                self.image_panel_a.original_image   # 基準（A）
            )
            self.image_panel_b.set_processed_image(result)
        except Exception as e:
            QMessageBox.critical(self, "エラー", f"補正に失敗しました:\n{str(e)}")
    
    def _check_images_loaded(self) -> bool:
        """両方の画像が読み込まれているか確認"""
        if self.image_panel_a.original_image is None or \
           self.image_panel_b.original_image is None:
            QMessageBox.warning(
                self,
                "警告",
                "両方の画像を読み込んでください"
            )
            return False
        return True
    
    def _on_slider_a_changed(self, values: dict):
        """写真A のスライダー変更時"""
        if self.image_panel_a.original_image is not None:
            processed = self.image_processor.apply_adjustments(
                self.image_panel_a.original_image,
                values
            )
            self.image_panel_a.set_processed_image(processed)
    
    def _on_slider_b_changed(self, values: dict):
        """写真B のスライダー変更時"""
        if self.image_panel_b.original_image is not None:
            processed = self.image_processor.apply_adjustments(
                self.image_panel_b.original_image,
                values
            )
            self.image_panel_b.set_processed_image(processed)
