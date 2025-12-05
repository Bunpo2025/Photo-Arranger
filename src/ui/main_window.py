#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
メインウィンドウモジュール
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QFileDialog, QMessageBox,
    QSplitter, QLabel, QFrame
)
from PyQt6.QtCore import Qt

from src.ui.components.image_panel import ImagePanel
from src.ui.components.slider_panel import SliderPanel
from src.ui.components.crop_widget import CropControlPanel
from src.ui.components.resolution_dialog import ResolutionDialog
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
        
        # クロップモード管理
        self.crop_mode_active = False
        self.crop_target_panel = None  # 'A' or 'B'
        self.crop_control_panel: CropControlPanel | None = None
        
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
        
        # 写真A のヘッダー（開くボタン、クロップボタン、保存ボタン）
        header_a = QHBoxLayout()
        self.open_a_button = QPushButton("📁 写真A を開く")
        self.open_a_button.setMinimumHeight(36)
        header_a.addWidget(self.open_a_button)
        
        self.crop_a_button = QPushButton("✂ 切り抜き")
        self.crop_a_button.setMinimumHeight(36)
        self.crop_a_button.setStyleSheet("""
            QPushButton {
                background-color: #8e44ad;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
            }
            QPushButton:hover {
                background-color: #9b59b6;
            }
            QPushButton:disabled {
                background-color: #555;
                color: #888;
            }
        """)
        header_a.addWidget(self.crop_a_button)
        
        header_a.addStretch()
        
        self.save_a_button = QPushButton("💾 Aを保存")
        self.save_a_button.setMinimumHeight(36)
        self.save_a_button.setMinimumWidth(100)
        header_a.addWidget(self.save_a_button)
        
        left_layout.addLayout(header_a)
        
        # クロップコントロールコンテナA（初期は非表示）
        self.crop_control_container_a = QWidget()
        self.crop_control_layout_a = QVBoxLayout(self.crop_control_container_a)
        self.crop_control_layout_a.setContentsMargins(0, 0, 0, 0)
        self.crop_control_container_a.setVisible(False)
        left_layout.addWidget(self.crop_control_container_a)
        
        self.image_panel_a = ImagePanel("写真A（基準）")
        self.slider_panel_a = SliderPanel()
        left_layout.addWidget(self.image_panel_a, stretch=1)
        left_layout.addWidget(self.slider_panel_a)
        
        # 右側（写真B - 補正対象）
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(5, 5, 5, 5)
        right_layout.setSpacing(8)
        
        # 写真B のヘッダー（開くボタン、クロップボタン、解像度変更、保存ボタン）
        header_b = QHBoxLayout()
        self.open_b_button = QPushButton("📁 写真B を開く")
        self.open_b_button.setMinimumHeight(36)
        header_b.addWidget(self.open_b_button)
        
        self.crop_b_button = QPushButton("✂ 切り抜き")
        self.crop_b_button.setMinimumHeight(36)
        self.crop_b_button.setStyleSheet("""
            QPushButton {
                background-color: #8e44ad;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
            }
            QPushButton:hover {
                background-color: #9b59b6;
            }
            QPushButton:disabled {
                background-color: #555;
                color: #888;
            }
        """)
        header_b.addWidget(self.crop_b_button)
        
        header_b.addStretch()
        
        self.save_b_button = QPushButton("💾 Bを保存")
        self.save_b_button.setMinimumHeight(36)
        self.save_b_button.setMinimumWidth(100)
        header_b.addWidget(self.save_b_button)
        
        right_layout.addLayout(header_b)
        
        # クロップコントロールコンテナB（初期は非表示）
        self.crop_control_container_b = QWidget()
        self.crop_control_layout_b = QVBoxLayout(self.crop_control_container_b)
        self.crop_control_layout_b.setContentsMargins(0, 0, 0, 0)
        self.crop_control_container_b.setVisible(False)
        right_layout.addWidget(self.crop_control_container_b)
        
        self.image_panel_b = ImagePanel("写真B（補正対象）")
        self.slider_panel_b = SliderPanel()
        right_layout.addWidget(self.image_panel_b, stretch=1)
        right_layout.addWidget(self.slider_panel_b)
        
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([640, 640])
        
        main_layout.addWidget(splitter, stretch=1)
        
        # 自動補正ボタン（中央配置）
        button_container = QWidget()
        button_layout = QVBoxLayout(button_container)
        button_layout.setSpacing(10)
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        # 自動補正ボタン行
        auto_match_row = QHBoxLayout()
        auto_match_row.addStretch()
        
        self.auto_match_button = QPushButton("🎨 自動補正")
        self.auto_match_button.setMinimumWidth(400)
        self.auto_match_button.setMinimumHeight(40)
        self.auto_match_button.setStyleSheet("""
            QPushButton {
                background-color: #2980b9;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 10px 30px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3498db;
            }
            QPushButton:pressed {
                background-color: #1f6dad;
            }
        """)
        auto_match_row.addWidget(self.auto_match_button)
        
        # 自動補正履歴ラベル
        self.auto_match_history = QLabel("")
        self.auto_match_history.setStyleSheet("color: #888; font-size: 10px;")
        auto_match_row.addWidget(self.auto_match_history)
        
        auto_match_row.addStretch()
        button_layout.addLayout(auto_match_row)
        
        # 画像サイズ変更ボタン行
        resolution_row = QHBoxLayout()
        resolution_row.addStretch()
        
        self.resolution_button = QPushButton("📐 画像サイズ変更")
        self.resolution_button.setMinimumWidth(400)
        self.resolution_button.setMinimumHeight(40)
        self.resolution_button.setStyleSheet("""
            QPushButton {
                background-color: #16a085;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 10px 24px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1abc9c;
            }
            QPushButton:pressed {
                background-color: #0e6655;
            }
        """)
        resolution_row.addWidget(self.resolution_button)
        
        # 画像サイズ変更履歴ラベル
        self.resolution_history = QLabel("")
        self.resolution_history.setStyleSheet("color: #888; font-size: 10px;")
        resolution_row.addWidget(self.resolution_history)
        
        resolution_row.addStretch()
        button_layout.addLayout(resolution_row)
        
        # コンテナを中央配置
        container_layout = QHBoxLayout()
        container_layout.addStretch()
        container_layout.addWidget(button_container)
        container_layout.addStretch()
        main_layout.addLayout(container_layout)
    
    def _connect_signals(self):
        """シグナルを接続"""
        # ファイルを開く
        self.open_a_button.clicked.connect(lambda: self._open_image("A"))
        self.open_b_button.clicked.connect(lambda: self._open_image("B"))
        
        # 保存
        self.save_a_button.clicked.connect(lambda: self._save_image("A"))
        self.save_b_button.clicked.connect(lambda: self._save_image("B"))
        
        # 自動補正
        self.auto_match_button.clicked.connect(self._auto_match)
        
        # スライダー変更
        self.slider_panel_a.values_changed.connect(self._on_slider_a_changed)
        self.slider_panel_b.values_changed.connect(self._on_slider_b_changed)
        
        # クロップ
        self.crop_a_button.clicked.connect(lambda: self._start_crop("A"))
        self.crop_b_button.clicked.connect(lambda: self._start_crop("B"))
        self.image_panel_a.crop_confirmed.connect(lambda x, y, w, h: self._on_crop_confirmed("A", x, y, w, h))
        self.image_panel_b.crop_confirmed.connect(lambda x, y, w, h: self._on_crop_confirmed("B", x, y, w, h))
        self.image_panel_a.crop_cancelled.connect(self._on_crop_cancelled)
        self.image_panel_b.crop_cancelled.connect(self._on_crop_cancelled)
        
        # 解像度変更
        self.resolution_button.clicked.connect(self._open_resolution_dialog)
    
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
                    self._update_image_info("A")
                else:
                    self.image_panel_b.load_image(file_path)
                    self.slider_panel_b.reset()
                    self._update_image_info("B")
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
    
    def _auto_match(self):
        """自動補正（画像全体のヒストグラムマッチング）"""
        if not self._check_images_loaded():
            return
        
        try:
            # 写真A（基準の処理済み画像）→ 写真B（補正対象の処理済み画像）
            # スライダーで調整済みの状態から補正を適用
            source_image = self.image_panel_b.processed_image
            reference_image = self.image_panel_a.processed_image
            
            result = self.color_matcher.match_histograms(
                source_image,    # 補正対象（B の処理済み画像）
                reference_image  # 基準（A の処理済み画像）
            )
            
            # 結果をBの新しいオリジナルとして設定（調整を確定）
            self.image_panel_b.original_image = result.copy()
            self.image_panel_b.set_processed_image(result)
            self.slider_panel_b.reset()
            
            # 履歴更新
            filename_a = self.image_panel_a.get_filename() or "写真A"
            filename_b = self.image_panel_b.get_filename() or "写真B"
            self.auto_match_history.setText(f"({filename_a} → {filename_b})")
            
        except Exception as e:
            QMessageBox.critical(self, "エラー", f"補正に失敗しました:\n{str(e)}")
    
    def _check_images_loaded(self) -> bool:
        """両方の画像が読み込まれているか確認"""
        if self.image_panel_a.processed_image is None or \
           self.image_panel_b.processed_image is None:
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
    
    def _start_crop(self, panel: str):
        """クロップモードを開始"""
        image_panel = self.image_panel_a if panel == "A" else self.image_panel_b
        
        if image_panel.processed_image is None:
            QMessageBox.warning(self, "警告", f"写真{panel} が読み込まれていません")
            return
        
        # 既にクロップモードなら終了
        if self.crop_mode_active:
            self._end_crop_mode()
            return
        
        # クロップモード開始
        if image_panel.start_crop_mode():
            self.crop_mode_active = True
            self.crop_target_panel = panel
            
            # クロップコントロールパネルを作成・表示
            self.crop_control_panel = CropControlPanel()
            self.crop_control_panel.aspect_ratio_changed.connect(self._on_crop_ratio_changed)
            self.crop_control_panel.confirm_clicked.connect(self._on_crop_confirm_clicked)
            self.crop_control_panel.cancel_clicked.connect(self._on_crop_cancel_clicked)
            
            # 対応するパネルのレイアウトに追加
            if panel == "A":
                self.crop_control_layout_a.addWidget(self.crop_control_panel)
                self.crop_control_container_a.setVisible(True)
            else:
                self.crop_control_layout_b.addWidget(self.crop_control_panel)
                self.crop_control_container_b.setVisible(True)
            
            # 他のボタンを無効化
            self._set_buttons_enabled(False)
    
    def _end_crop_mode(self):
        """クロップモードを終了"""
        if self.crop_target_panel == "A":
            self.image_panel_a.stop_crop_mode()
            # クロップコントロールパネルを削除
            if self.crop_control_panel:
                self.crop_control_layout_a.removeWidget(self.crop_control_panel)
                self.crop_control_panel.deleteLater()
                self.crop_control_panel = None
            self.crop_control_container_a.setVisible(False)
        elif self.crop_target_panel == "B":
            self.image_panel_b.stop_crop_mode()
            # クロップコントロールパネルを削除
            if self.crop_control_panel:
                self.crop_control_layout_b.removeWidget(self.crop_control_panel)
                self.crop_control_panel.deleteLater()
                self.crop_control_panel = None
            self.crop_control_container_b.setVisible(False)
        
        self.crop_mode_active = False
        self.crop_target_panel = None
        
        # ボタンを有効化
        self._set_buttons_enabled(True)
    
    def _on_crop_ratio_changed(self, ratio):
        """クロップ比率変更時"""
        if self.crop_target_panel == "A":
            self.image_panel_a.set_crop_aspect_ratio(ratio)
        elif self.crop_target_panel == "B":
            self.image_panel_b.set_crop_aspect_ratio(ratio)
    
    def _on_crop_confirm_clicked(self):
        """クロップ確定ボタンクリック時"""
        if self.crop_target_panel == "A":
            self.image_panel_a.confirm_crop()
        elif self.crop_target_panel == "B":
            self.image_panel_b.confirm_crop()
    
    def _on_crop_cancel_clicked(self):
        """クロップキャンセルボタンクリック時"""
        self._end_crop_mode()
    
    def _on_crop_confirmed(self, panel: str, x: int, y: int, width: int, height: int):
        """クロップ確定時"""
        image_panel = self.image_panel_a if panel == "A" else self.image_panel_b
        slider_panel = self.slider_panel_a if panel == "A" else self.slider_panel_b
        
        # 切り抜きを実行
        if image_panel.processed_image is not None:
            cropped = self.image_processor.crop_image(
                image_panel.processed_image, x, y, width, height
            )
            # 切り抜き後の画像を新しいオリジナルとして設定
            image_panel.original_image = cropped.copy()
            image_panel.set_processed_image(cropped)
            slider_panel.reset()
        
        self._end_crop_mode()
        QMessageBox.information(self, "完了", f"写真{panel} を切り抜きました")
    
    def _on_crop_cancelled(self):
        """クロップキャンセル時"""
        self._end_crop_mode()
    
    def _set_buttons_enabled(self, enabled: bool):
        """ボタンの有効/無効を切り替え"""
        self.open_a_button.setEnabled(enabled)
        self.open_b_button.setEnabled(enabled)
        self.crop_a_button.setEnabled(enabled)
        self.crop_b_button.setEnabled(enabled)
        self.auto_match_button.setEnabled(enabled)
        self.resolution_button.setEnabled(enabled)
        self.save_a_button.setEnabled(enabled)
        self.save_b_button.setEnabled(enabled)
    
    def _open_resolution_dialog(self):
        """解像度変更ダイアログを開く"""
        size_a = self.image_panel_a.get_image_size()
        size_b = self.image_panel_b.get_image_size()
        
        # どちらかに画像があるかチェック
        if size_a[0] == 0 and size_b[0] == 0:
            QMessageBox.warning(self, "警告", "画像が読み込まれていません")
            return
        
        dialog = ResolutionDialog(self, size_a, size_b)
        
        if dialog.exec():
            result_a, result_b, result_dpi = dialog.get_results()
            history_parts = []
            
            # 写真Aのリサイズ
            if result_a and self.image_panel_a.processed_image is not None:
                old_size = self.image_panel_a.get_image_size()
                resized = self.image_processor.resize_image(
                    self.image_panel_a.processed_image,
                    width=result_a['width'],
                    height=result_a['height'],
                    maintain_aspect=False
                )
                self.image_panel_a.original_image = resized.copy()
                self.image_panel_a.set_processed_image(resized)
                self.image_panel_a.set_dpi(result_dpi)  # 画像パネルにDPIを設定
                self.slider_panel_a.reset()
                # DPIを含めて画像情報を更新
                self.slider_panel_a.update_image_info(result_a['width'], result_a['height'], result_dpi)
                history_parts.append(f"A:{old_size[0]}x{old_size[1]}→{result_a['width']}x{result_a['height']}")
            elif self.image_panel_a.processed_image is not None:
                # サイズ変更なしでもDPIを更新
                self.image_panel_a.set_dpi(result_dpi)  # 画像パネルにDPIを設定
                size = self.image_panel_a.get_image_size()
                self.slider_panel_a.update_image_info(size[0], size[1], result_dpi)
            
            # 写真Bのリサイズ
            if result_b and self.image_panel_b.processed_image is not None:
                old_size = self.image_panel_b.get_image_size()
                resized = self.image_processor.resize_image(
                    self.image_panel_b.processed_image,
                    width=result_b['width'],
                    height=result_b['height'],
                    maintain_aspect=False
                )
                self.image_panel_b.original_image = resized.copy()
                self.image_panel_b.set_processed_image(resized)
                self.image_panel_b.set_dpi(result_dpi)  # 画像パネルにDPIを設定
                self.slider_panel_b.reset()
                # DPIを含めて画像情報を更新
                self.slider_panel_b.update_image_info(result_b['width'], result_b['height'], result_dpi)
                history_parts.append(f"B:{old_size[0]}x{old_size[1]}→{result_b['width']}x{result_b['height']}")
            elif self.image_panel_b.processed_image is not None:
                # サイズ変更なしでもDPIを更新
                self.image_panel_b.set_dpi(result_dpi)  # 画像パネルにDPIを設定
                size = self.image_panel_b.get_image_size()
                self.slider_panel_b.update_image_info(size[0], size[1], result_dpi)
            
            # 履歴更新
            if history_parts:
                self.resolution_history.setText(f"({', '.join(history_parts)}, DPI:{result_dpi})")
            else:
                self.resolution_history.setText(f"(DPI: {result_dpi})")
            
            QMessageBox.information(self, "完了", "解像度を変更しました")
    
    def _update_image_info(self, panel: str):
        """画像情報を更新"""
        if panel == "A":
            size = self.image_panel_a.get_image_size()
            self.slider_panel_a.update_image_info(size[0], size[1])
        else:
            size = self.image_panel_b.get_image_size()
            self.slider_panel_b.update_image_info(size[0], size[1])
