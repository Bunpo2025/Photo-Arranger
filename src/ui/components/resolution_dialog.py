#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
解像度変更ダイアログモジュール
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QSpinBox, QDoubleSpinBox, QLineEdit,
    QGroupBox, QFrame, QCheckBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIntValidator, QDoubleValidator


class ResolutionDialog(QDialog):
    """解像度変更ダイアログ"""
    
    def __init__(self, parent=None, image_size_a: tuple = None, image_size_b: tuple = None):
        """
        初期化
        
        Args:
            parent: 親ウィジェット
            image_size_a: 写真Aのサイズ (width, height)
            image_size_b: 写真Bのサイズ (width, height)
        """
        super().__init__(parent)
        self.image_size_a = image_size_a or (0, 0)
        self.image_size_b = image_size_b or (0, 0)
        
        # 結果を保持
        self.result_a = None  # {'width': int, 'height': int} or None
        self.result_b = None
        self.result_dpi = 300  # デフォルトDPI
        
        self._setup_ui()
        self._connect_signals()
        self._update_preview()
    
    def _setup_ui(self):
        """UIをセットアップ"""
        self.setWindowTitle("解像度変更")
        self.setMinimumWidth(500)
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
            }
            QLabel {
                color: #ffffff;
                font-size: 13px;
            }
            QGroupBox {
                color: #ffffff;
                font-weight: bold;
                border: 1px solid #555;
                border-radius: 6px;
                margin-top: 10px;
                padding: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QCheckBox {
                color: #ffffff;
                font-size: 13px;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #555;
                border-radius: 3px;
                background-color: #2a2a2a;
            }
            QCheckBox::indicator:checked {
                background-color: #3498db;
                border-color: #3498db;
            }
            QCheckBox::indicator:hover {
                border-color: #3498db;
            }
            QLineEdit, QSpinBox, QDoubleSpinBox {
                background-color: #3a3a3a;
                color: #ffffff;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 6px 10px;
                font-size: 13px;
            }
            QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
                border: 1px solid #3498db;
            }
            QPushButton {
                background-color: #3a3a3a;
                color: #ffffff;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 8px 20px;
                font-size: 13px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
            QPushButton#applyButton {
                background-color: #2980b9;
                border: none;
            }
            QPushButton#applyButton:hover {
                background-color: #3498db;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 適用対象選択（チェックボックス）
        target_group = QGroupBox("適用対象")
        target_layout = QVBoxLayout(target_group)
        
        self.apply_to_a = QCheckBox(f"写真A（現在: {self.image_size_a[0]} x {self.image_size_a[1]} px）")
        self.apply_to_a.setChecked(self.image_size_a[0] > 0)
        self.apply_to_a.setEnabled(self.image_size_a[0] > 0)
        target_layout.addWidget(self.apply_to_a)
        
        self.apply_to_b = QCheckBox(f"写真B（現在: {self.image_size_b[0]} x {self.image_size_b[1]} px）")
        self.apply_to_b.setChecked(self.image_size_b[0] > 0)
        self.apply_to_b.setEnabled(self.image_size_b[0] > 0)
        target_layout.addWidget(self.apply_to_b)
        
        layout.addWidget(target_group)
        
        # サイズ指定
        size_group = QGroupBox("サイズ指定")
        size_layout = QVBoxLayout(size_group)
        
        # パーセント指定
        percent_layout = QHBoxLayout()
        percent_layout.addWidget(QLabel("パーセント:"))
        self.percent_input = QSpinBox()
        self.percent_input.setRange(1, 1000)
        self.percent_input.setValue(100)
        self.percent_input.setSuffix(" %")
        self.percent_input.setMinimumWidth(100)
        percent_layout.addWidget(self.percent_input)
        percent_layout.addStretch()
        size_layout.addLayout(percent_layout)
        
        # 区切り線
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.Shape.HLine)
        separator1.setStyleSheet("background-color: #444;")
        size_layout.addWidget(separator1)
        
        # ピクセル指定
        pixel_layout = QHBoxLayout()
        pixel_layout.addWidget(QLabel("幅:"))
        self.width_input = QLineEdit()
        self.width_input.setValidator(QIntValidator(1, 99999))
        self.width_input.setPlaceholderText("px")
        self.width_input.setMinimumWidth(80)
        # 初期値は現在の画像サイズ
        init_width = self.image_size_a[0] if self.image_size_a[0] > 0 else (self.image_size_b[0] if self.image_size_b[0] > 0 else 1920)
        self.width_input.setText(str(init_width))
        pixel_layout.addWidget(self.width_input)
        
        pixel_layout.addWidget(QLabel("高さ:"))
        self.height_input = QLineEdit()
        self.height_input.setValidator(QIntValidator(1, 99999))
        self.height_input.setPlaceholderText("px")
        self.height_input.setMinimumWidth(80)
        init_height = self.image_size_a[1] if self.image_size_a[1] > 0 else (self.image_size_b[1] if self.image_size_b[1] > 0 else 1080)
        self.height_input.setText(str(init_height))
        pixel_layout.addWidget(self.height_input)
        
        pixel_layout.addStretch()
        size_layout.addLayout(pixel_layout)
        
        # cm指定
        cm_layout = QHBoxLayout()
        cm_layout.addWidget(QLabel("幅:"))
        self.width_cm_input = QLineEdit()
        self.width_cm_input.setValidator(QDoubleValidator(0.1, 999.9, 2))
        self.width_cm_input.setPlaceholderText("cm")
        self.width_cm_input.setMinimumWidth(80)
        cm_layout.addWidget(self.width_cm_input)
        
        cm_layout.addWidget(QLabel("高さ:"))
        self.height_cm_input = QLineEdit()
        self.height_cm_input.setValidator(QDoubleValidator(0.1, 999.9, 2))
        self.height_cm_input.setPlaceholderText("cm")
        self.height_cm_input.setMinimumWidth(80)
        cm_layout.addWidget(self.height_cm_input)
        
        cm_layout.addStretch()
        size_layout.addLayout(cm_layout)
        
        # ヒント
        self.hint_label = QLabel("※ パーセント・ピクセル・cm いずれかで指定")
        self.hint_label.setStyleSheet("color: #888; font-size: 11px;")
        size_layout.addWidget(self.hint_label)
        
        layout.addWidget(size_group)
        
        # オプション
        options_layout = QHBoxLayout()
        self.maintain_aspect = QCheckBox("アスペクト比を維持")
        self.maintain_aspect.setChecked(True)
        options_layout.addWidget(self.maintain_aspect)
        options_layout.addStretch()
        layout.addLayout(options_layout)
        
        # プレビュー情報
        self.preview_label = QLabel()
        self.preview_label.setStyleSheet("color: #5dade2; font-size: 12px;")
        layout.addWidget(self.preview_label)
        
        # ボタン
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_button = QPushButton("キャンセル")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        self.apply_button = QPushButton("適用")
        self.apply_button.setObjectName("applyButton")
        self.apply_button.clicked.connect(self._apply)
        button_layout.addWidget(self.apply_button)
        
        layout.addLayout(button_layout)
    
    def _connect_signals(self):
        """シグナルを接続"""
        self.apply_to_a.stateChanged.connect(self._update_preview)
        self.apply_to_b.stateChanged.connect(self._update_preview)
        
        self.percent_input.valueChanged.connect(self._on_percent_changed)
        self.width_input.textChanged.connect(self._on_width_changed)
        self.height_input.textChanged.connect(self._on_height_changed)
        self.width_cm_input.textChanged.connect(self._on_width_cm_changed)
        self.height_cm_input.textChanged.connect(self._on_height_cm_changed)
        self.maintain_aspect.stateChanged.connect(self._update_preview)
    
    def _on_percent_changed(self):
        """パーセント変更時"""
        percent = self.percent_input.value()
        target_size = self._get_reference_size()
        if target_size[0] > 0 and target_size[1] > 0:
            new_width = int(target_size[0] * percent / 100)
            new_height = int(target_size[1] * percent / 100)
            
            self.width_input.blockSignals(True)
            self.height_input.blockSignals(True)
            self.width_cm_input.blockSignals(True)
            self.height_cm_input.blockSignals(True)
            
            self.width_input.setText(str(new_width))
            self.height_input.setText(str(new_height))
            self.width_cm_input.clear()
            self.height_cm_input.clear()
            
            self.width_input.blockSignals(False)
            self.height_input.blockSignals(False)
            self.width_cm_input.blockSignals(False)
            self.height_cm_input.blockSignals(False)
        self._update_preview()
    
    def _on_width_changed(self):
        """幅ピクセル変更時"""
        if self.maintain_aspect.isChecked():
            try:
                width = int(self.width_input.text())
                target_size = self._get_reference_size()
                if target_size[0] > 0 and target_size[1] > 0:
                    aspect = target_size[1] / target_size[0]
                    new_height = int(width * aspect)
                    self.height_input.blockSignals(True)
                    self.height_input.setText(str(new_height))
                    self.height_input.blockSignals(False)
            except ValueError:
                pass
        # cm入力をクリア、パーセント更新
        self._clear_cm_and_update_percent()
        self._update_preview()
    
    def _on_height_changed(self):
        """高さピクセル変更時"""
        if self.maintain_aspect.isChecked():
            try:
                height = int(self.height_input.text())
                target_size = self._get_reference_size()
                if target_size[0] > 0 and target_size[1] > 0:
                    aspect = target_size[0] / target_size[1]
                    new_width = int(height * aspect)
                    self.width_input.blockSignals(True)
                    self.width_input.setText(str(new_width))
                    self.width_input.blockSignals(False)
            except ValueError:
                pass
        # cm入力をクリア、パーセント更新
        self._clear_cm_and_update_percent()
        self._update_preview()
    
    def _clear_cm_and_update_percent(self):
        """cm入力をクリアしてパーセントを更新"""
        self.width_cm_input.blockSignals(True)
        self.height_cm_input.blockSignals(True)
        self.percent_input.blockSignals(True)
        
        self.width_cm_input.clear()
        self.height_cm_input.clear()
        
        # パーセント計算
        try:
            target_size = self._get_reference_size()
            width = int(self.width_input.text()) if self.width_input.text() else 0
            if target_size[0] > 0 and width > 0:
                percent = int(width / target_size[0] * 100)
                self.percent_input.setValue(percent)
        except ValueError:
            pass
        
        self.width_cm_input.blockSignals(False)
        self.height_cm_input.blockSignals(False)
        self.percent_input.blockSignals(False)
    
    def _on_width_cm_changed(self):
        """幅cm変更時"""
        try:
            width_cm = float(self.width_cm_input.text().replace(',', '.'))
            dpi = 300  # 固定DPI
            width_px = int(width_cm / 2.54 * dpi)
            
            self.width_input.blockSignals(True)
            self.percent_input.blockSignals(True)
            self.width_input.setText(str(width_px))
            self.width_input.blockSignals(False)
            self.percent_input.blockSignals(False)
            
            if self.maintain_aspect.isChecked():
                target_size = self._get_reference_size()
                if target_size[0] > 0 and target_size[1] > 0:
                    aspect = target_size[1] / target_size[0]
                    height_px = int(width_px * aspect)
                    height_cm = height_px * 2.54 / dpi
                    
                    self.height_input.blockSignals(True)
                    self.height_cm_input.blockSignals(True)
                    self.height_input.setText(str(height_px))
                    self.height_cm_input.setText(f"{height_cm:.2f}")
                    self.height_input.blockSignals(False)
                    self.height_cm_input.blockSignals(False)
            
            # パーセント更新
            self._update_percent_from_pixel()
        except ValueError:
            pass
        self._update_preview()
    
    def _on_height_cm_changed(self):
        """高さcm変更時"""
        try:
            height_cm = float(self.height_cm_input.text().replace(',', '.'))
            dpi = 300  # 固定DPI
            height_px = int(height_cm / 2.54 * dpi)
            
            self.height_input.blockSignals(True)
            self.percent_input.blockSignals(True)
            self.height_input.setText(str(height_px))
            self.height_input.blockSignals(False)
            self.percent_input.blockSignals(False)
            
            if self.maintain_aspect.isChecked():
                target_size = self._get_reference_size()
                if target_size[0] > 0 and target_size[1] > 0:
                    aspect = target_size[0] / target_size[1]
                    width_px = int(height_px * aspect)
                    width_cm = width_px * 2.54 / dpi
                    
                    self.width_input.blockSignals(True)
                    self.width_cm_input.blockSignals(True)
                    self.width_input.setText(str(width_px))
                    self.width_cm_input.setText(f"{width_cm:.2f}")
                    self.width_input.blockSignals(False)
                    self.width_cm_input.blockSignals(False)
            
            # パーセント更新
            self._update_percent_from_pixel()
        except ValueError:
            pass
        self._update_preview()
    
    def _update_percent_from_pixel(self):
        """ピクセルからパーセントを更新"""
        try:
            target_size = self._get_reference_size()
            width = int(self.width_input.text()) if self.width_input.text() else 0
            if target_size[0] > 0 and width > 0:
                percent = int(width / target_size[0] * 100)
                self.percent_input.blockSignals(True)
                self.percent_input.setValue(percent)
                self.percent_input.blockSignals(False)
        except ValueError:
            pass
    
    def _get_reference_size(self) -> tuple:
        """参照サイズを取得（チェックされている方）"""
        if self.apply_to_a.isChecked() and self.image_size_a[0] > 0:
            return self.image_size_a
        elif self.apply_to_b.isChecked() and self.image_size_b[0] > 0:
            return self.image_size_b
        return (0, 0)
    
    def _get_target_size(self) -> tuple:
        """入力されたサイズを取得"""
        try:
            width = int(self.width_input.text()) if self.width_input.text() else 0
            height = int(self.height_input.text()) if self.height_input.text() else 0
            return (width, height)
        except ValueError:
            return (0, 0)
    
    def _calculate_new_size(self, original_size: tuple) -> tuple:
        """新しいサイズを計算（アスペクト比維持の場合）"""
        if original_size[0] == 0 or original_size[1] == 0:
            return (0, 0)
        
        target = self._get_target_size()
        if target[0] <= 0 or target[1] <= 0:
            return original_size
        
        # アスペクト比を維持する場合、元画像の比率に合わせる
        aspect = original_size[0] / original_size[1]
        target_aspect = target[0] / target[1]
        
        if target_aspect > aspect:
            # ターゲットが横長 → 高さを基準にする
            new_h = target[1]
            new_w = int(new_h * aspect)
        else:
            # ターゲットが縦長または同じ → 幅を基準にする
            new_w = target[0]
            new_h = int(new_w / aspect)
        
        return (max(1, new_w), max(1, new_h))
    
    def _update_preview(self):
        """プレビュー表示を更新"""
        preview_text = ""
        target = self._get_target_size()
        
        if self.apply_to_a.isChecked() and self.image_size_a[0] > 0:
            if self.maintain_aspect.isChecked():
                new_size = self._calculate_new_size(self.image_size_a)
            else:
                new_size = target if target[0] > 0 and target[1] > 0 else self.image_size_a
            preview_text += f"写真A: {self.image_size_a[0]}x{self.image_size_a[1]} → {new_size[0]}x{new_size[1]} px\n"
        
        if self.apply_to_b.isChecked() and self.image_size_b[0] > 0:
            if self.maintain_aspect.isChecked():
                new_size = self._calculate_new_size(self.image_size_b)
            else:
                new_size = target if target[0] > 0 and target[1] > 0 else self.image_size_b
            preview_text += f"写真B: {self.image_size_b[0]}x{self.image_size_b[1]} → {new_size[0]}x{new_size[1]} px"
        
        self.preview_label.setText(preview_text.strip())
    
    def _apply(self):
        """適用"""
        target = self._get_target_size()
        
        # ターゲットサイズが無効な場合はキャンセル
        if target[0] <= 0 or target[1] <= 0:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "警告", "有効なサイズを入力してください")
            return
        
        # DPIを固定値300に設定
        self.result_dpi = 300
        
        if self.apply_to_a.isChecked() and self.image_size_a[0] > 0:
            if self.maintain_aspect.isChecked():
                new_size = self._calculate_new_size(self.image_size_a)
            else:
                new_size = target
            if new_size[0] > 0 and new_size[1] > 0:
                self.result_a = {'width': new_size[0], 'height': new_size[1]}
        
        if self.apply_to_b.isChecked() and self.image_size_b[0] > 0:
            if self.maintain_aspect.isChecked():
                new_size = self._calculate_new_size(self.image_size_b)
            else:
                new_size = target
            if new_size[0] > 0 and new_size[1] > 0:
                self.result_b = {'width': new_size[0], 'height': new_size[1]}
        
        self.accept()
    
    def get_results(self) -> tuple:
        """
        結果を取得
        
        Returns:
            (result_a, result_b, dpi) のタプル
            各結果は {'width': int, 'height': int} または None
            dpi は整数値
        """
        return (self.result_a, self.result_b, self.result_dpi)
    
    def set_target(self, panel: str):
        """
        対象パネルを設定
        
        Args:
            panel: "A" または "B"
        """
        if panel == "A":
            self.apply_to_a.setChecked(True)
            self.apply_to_b.setChecked(False)
        elif panel == "B":
            self.apply_to_a.setChecked(False)
            self.apply_to_b.setChecked(True)
        self._update_preview()
