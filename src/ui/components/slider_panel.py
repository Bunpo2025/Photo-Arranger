#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
調整スライダーパネルモジュール
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal


class SliderPanel(QWidget):
    """調整スライダーパネルクラス"""
    
    # 値変更シグナル
    values_changed = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self._image_size = (0, 0)
        self._dpi = 300  # デフォルトDPI
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """UIをセットアップ"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(8)
        
        # 色温度スライダー
        self.temperature_slider = self._create_slider_row("色温度", -100, 100, 0)
        layout.addLayout(self.temperature_slider["layout"])
        
        # 色かぶりスライダー
        self.tint_slider = self._create_slider_row("色かぶり", -100, 100, 0)
        layout.addLayout(self.tint_slider["layout"])
        
        # 明るさスライダー
        self.brightness_slider = self._create_slider_row("明るさ", -100, 100, 0)
        layout.addLayout(self.brightness_slider["layout"])
        
        # リセットボタン + 画像情報表示
        info_layout = QHBoxLayout()
        
        # 画像情報ラベル
        self.info_label = QLabel("画像: -- | -- cm × -- cm")
        self.info_label.setStyleSheet("color: #888; font-size: 11px;")
        info_layout.addWidget(self.info_label)
        
        info_layout.addStretch()
        
        self.reset_button = QPushButton("リセット")
        self.reset_button.setMaximumWidth(100)
        info_layout.addWidget(self.reset_button)
        
        layout.addLayout(info_layout)
    
    def _create_slider_row(
        self,
        label_text: str,
        min_val: int,
        max_val: int,
        default_val: int
    ) -> dict:
        """
        スライダー行を作成
        
        Args:
            label_text: ラベルテキスト
            min_val: 最小値
            max_val: 最大値
            default_val: デフォルト値
        
        Returns:
            スライダー行の情報を含む辞書
        """
        layout = QHBoxLayout()
        
        # ラベル
        label = QLabel(label_text)
        label.setMinimumWidth(60)
        label.setStyleSheet("color: #ffffff; font-size: 13px;")
        
        # スライダー
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)
        slider.setValue(default_val)
        slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        slider.setTickInterval(50)
        slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 6px;
                background: #444;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #3498db;
                width: 16px;
                margin: -5px 0;
                border-radius: 8px;
            }
            QSlider::handle:horizontal:hover {
                background: #2980b9;
            }
        """)
        
        # 値表示ラベル
        value_label = QLabel(str(default_val))
        value_label.setMinimumWidth(40)
        value_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        value_label.setStyleSheet("color: #5dade2; font-size: 13px; font-weight: bold;")
        
        layout.addWidget(label)
        layout.addWidget(slider, stretch=1)
        layout.addWidget(value_label)
        
        return {
            "layout": layout,
            "slider": slider,
            "value_label": value_label,
            "default": default_val
        }
    
    def _connect_signals(self):
        """シグナルを接続"""
        self.temperature_slider["slider"].valueChanged.connect(self._on_value_changed)
        self.tint_slider["slider"].valueChanged.connect(self._on_value_changed)
        self.brightness_slider["slider"].valueChanged.connect(self._on_value_changed)
        self.reset_button.clicked.connect(self.reset)
    
    def _on_value_changed(self):
        """スライダー値変更時"""
        # 値表示を更新
        temp_val = self.temperature_slider["slider"].value()
        tint_val = self.tint_slider["slider"].value()
        bright_val = self.brightness_slider["slider"].value()
        
        self.temperature_slider["value_label"].setText(str(temp_val))
        self.tint_slider["value_label"].setText(str(tint_val))
        self.brightness_slider["value_label"].setText(str(bright_val))
        
        # シグナル発火
        self.values_changed.emit({
            "temperature": temp_val,
            "tint": tint_val,
            "brightness": bright_val
        })
    
    def _update_info_display(self):
        """情報表示を更新"""
        width, height = self._image_size
        dpi = self._dpi
        
        if width > 0 and height > 0:
            # cm計算
            width_cm = width * 2.54 / dpi
            height_cm = height * 2.54 / dpi
            self.info_label.setText(
                f"{width} × {height} px | {width_cm:.1f} cm × {height_cm:.1f} cm"
            )
        else:
            self.info_label.setText("画像: -- | -- cm × -- cm")
    
    def reset(self):
        """スライダーをリセット"""
        self.temperature_slider["slider"].setValue(self.temperature_slider["default"])
        self.tint_slider["slider"].setValue(self.tint_slider["default"])
        self.brightness_slider["slider"].setValue(self.brightness_slider["default"])
    
    def get_values(self) -> dict:
        """
        現在の値を取得
        
        Returns:
            現在の調整値
        """
        return {
            "temperature": self.temperature_slider["slider"].value(),
            "tint": self.tint_slider["slider"].value(),
            "brightness": self.brightness_slider["slider"].value()
        }
    
    def update_image_info(self, width: int, height: int, dpi: int = None):
        """
        画像情報を更新
        
        Args:
            width: 画像幅（ピクセル）
            height: 画像高さ（ピクセル）
            dpi: DPI値（Noneの場合は現在の値を維持）
        """
        self._image_size = (width, height)
        if dpi is not None:
            self._dpi = dpi
        self._update_info_display()
    
    def clear_image_info(self):
        """画像情報をクリア"""
        self._image_size = (0, 0)
        self.info_label.setText("画像: -- | -- cm × -- cm")
    
    def get_dpi(self) -> int:
        """現在のDPI値を取得"""
        return self._dpi
    
    def set_dpi(self, dpi: int):
        """DPI値を設定"""
        self._dpi = dpi
        self._update_info_display()
