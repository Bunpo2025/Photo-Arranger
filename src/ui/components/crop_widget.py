#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
クロップウィジェットモジュール

画像の切り抜き範囲を選択するためのオーバーレイウィジェット
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QSpinBox, QComboBox, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QRect, QPoint
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QCursor


class CropOverlay(QWidget):
    """クロップ範囲選択オーバーレイ"""
    
    # 切り抜き確定シグナル (x, y, width, height)
    crop_confirmed = pyqtSignal(int, int, int, int)
    # キャンセルシグナル
    crop_cancelled = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        
        # 画像領域（親ウィジェット上の表示領域）
        self.image_rect = QRect()
        # 元画像のサイズ
        self.original_image_size = (0, 0)
        
        # クロップ範囲（表示座標系）
        self.crop_rect = QRect()
        
        # アスペクト比（None=自由、(3, 2)など）
        self.aspect_ratio: tuple | None = (3, 2)
        
        # ドラッグ状態
        self.dragging = False
        self.drag_start = QPoint()
        self.drag_mode = None  # 'create', 'move', 'resize_tl', 'resize_tr', 'resize_bl', 'resize_br', 'resize_t', 'resize_b', 'resize_l', 'resize_r'
        self.drag_offset = QPoint()
        
        # リサイズハンドルのサイズ
        self.handle_size = 10
        
        # スタイル
        self.setStyleSheet("background: transparent;")
    
    def set_image_rect(self, rect: QRect, original_size: tuple):
        """
        画像の表示領域と元サイズを設定
        
        Args:
            rect: 表示領域（ウィジェット座標系）
            original_size: 元画像のサイズ (width, height)
        """
        self.image_rect = rect
        self.original_image_size = original_size
        
        # 初期クロップ範囲を画像全体に設定
        self.crop_rect = QRect(rect)
        self._constrain_aspect_ratio()
        self.update()
    
    def set_aspect_ratio(self, ratio: tuple | None):
        """
        アスペクト比を設定
        
        Args:
            ratio: (幅, 高さ) のタプル、Noneで自由選択
        """
        self.aspect_ratio = ratio
        if self.crop_rect.isValid():
            self._constrain_aspect_ratio()
            self.update()
    
    def _constrain_aspect_ratio(self):
        """アスペクト比に従ってクロップ範囲を調整"""
        if self.aspect_ratio is None or not self.crop_rect.isValid():
            return
        
        target_ratio = self.aspect_ratio[0] / self.aspect_ratio[1]
        current_ratio = self.crop_rect.width() / max(1, self.crop_rect.height())
        
        center = self.crop_rect.center()
        
        if current_ratio > target_ratio:
            # 幅が広すぎる → 幅を縮める
            new_width = int(self.crop_rect.height() * target_ratio)
            new_rect = QRect(0, 0, new_width, self.crop_rect.height())
        else:
            # 高さが高すぎる → 高さを縮める
            new_height = int(self.crop_rect.width() / target_ratio)
            new_rect = QRect(0, 0, self.crop_rect.width(), new_height)
        
        new_rect.moveCenter(center)
        
        # 画像領域内に収める
        if new_rect.left() < self.image_rect.left():
            new_rect.moveLeft(self.image_rect.left())
        if new_rect.top() < self.image_rect.top():
            new_rect.moveTop(self.image_rect.top())
        if new_rect.right() > self.image_rect.right():
            new_rect.moveRight(self.image_rect.right())
        if new_rect.bottom() > self.image_rect.bottom():
            new_rect.moveBottom(self.image_rect.bottom())
        
        self.crop_rect = new_rect
    
    def get_crop_region(self) -> tuple:
        """
        元画像座標系でのクロップ範囲を取得
        
        Returns:
            (x, y, width, height) のタプル
        """
        if not self.image_rect.isValid() or self.original_image_size[0] == 0:
            return (0, 0, 0, 0)
        
        # 表示座標から元画像座標への変換
        scale_x = self.original_image_size[0] / self.image_rect.width()
        scale_y = self.original_image_size[1] / self.image_rect.height()
        
        x = int((self.crop_rect.x() - self.image_rect.x()) * scale_x)
        y = int((self.crop_rect.y() - self.image_rect.y()) * scale_y)
        width = int(self.crop_rect.width() * scale_x)
        height = int(self.crop_rect.height() * scale_y)
        
        return (x, y, width, height)
    
    def paintEvent(self, event):
        """描画イベント"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        if not self.image_rect.isValid():
            return
        
        # 暗いオーバーレイ（クロップ範囲外）
        overlay_color = QColor(0, 0, 0, 150)
        
        # 上部
        if self.crop_rect.top() > self.image_rect.top():
            painter.fillRect(
                self.image_rect.left(),
                self.image_rect.top(),
                self.image_rect.width(),
                self.crop_rect.top() - self.image_rect.top(),
                overlay_color
            )
        
        # 下部
        if self.crop_rect.bottom() < self.image_rect.bottom():
            painter.fillRect(
                self.image_rect.left(),
                self.crop_rect.bottom() + 1,
                self.image_rect.width(),
                self.image_rect.bottom() - self.crop_rect.bottom(),
                overlay_color
            )
        
        # 左部
        if self.crop_rect.left() > self.image_rect.left():
            painter.fillRect(
                self.image_rect.left(),
                self.crop_rect.top(),
                self.crop_rect.left() - self.image_rect.left(),
                self.crop_rect.height(),
                overlay_color
            )
        
        # 右部
        if self.crop_rect.right() < self.image_rect.right():
            painter.fillRect(
                self.crop_rect.right() + 1,
                self.crop_rect.top(),
                self.image_rect.right() - self.crop_rect.right(),
                self.crop_rect.height(),
                overlay_color
            )
        
        # クロップ範囲の枠線
        pen = QPen(QColor(255, 255, 255), 2)
        pen.setStyle(Qt.PenStyle.SolidLine)
        painter.setPen(pen)
        painter.drawRect(self.crop_rect)
        
        # 三分割ガイドライン
        pen.setColor(QColor(255, 255, 255, 100))
        pen.setWidth(1)
        painter.setPen(pen)
        
        third_w = self.crop_rect.width() // 3
        third_h = self.crop_rect.height() // 3
        
        # 垂直線
        painter.drawLine(
            self.crop_rect.left() + third_w, self.crop_rect.top(),
            self.crop_rect.left() + third_w, self.crop_rect.bottom()
        )
        painter.drawLine(
            self.crop_rect.left() + third_w * 2, self.crop_rect.top(),
            self.crop_rect.left() + third_w * 2, self.crop_rect.bottom()
        )
        
        # 水平線
        painter.drawLine(
            self.crop_rect.left(), self.crop_rect.top() + third_h,
            self.crop_rect.right(), self.crop_rect.top() + third_h
        )
        painter.drawLine(
            self.crop_rect.left(), self.crop_rect.top() + third_h * 2,
            self.crop_rect.right(), self.crop_rect.top() + third_h * 2
        )
        
        # リサイズハンドル
        handle_color = QColor(255, 255, 255)
        painter.setBrush(QBrush(handle_color))
        pen.setColor(QColor(50, 50, 50))
        pen.setWidth(1)
        painter.setPen(pen)
        
        handles = self._get_resize_handles()
        for handle_rect in handles.values():
            painter.drawRect(handle_rect)
        
        # 十字カーソル表示（中央）
        center = self.crop_rect.center()
        cross_size = 15
        pen.setColor(QColor(255, 255, 255))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawLine(center.x() - cross_size, center.y(), center.x() + cross_size, center.y())
        painter.drawLine(center.x(), center.y() - cross_size, center.x(), center.y() + cross_size)
    
    def _get_resize_handles(self) -> dict:
        """リサイズハンドルの矩形を取得"""
        hs = self.handle_size
        r = self.crop_rect
        
        return {
            'resize_tl': QRect(r.left() - hs//2, r.top() - hs//2, hs, hs),
            'resize_tr': QRect(r.right() - hs//2, r.top() - hs//2, hs, hs),
            'resize_bl': QRect(r.left() - hs//2, r.bottom() - hs//2, hs, hs),
            'resize_br': QRect(r.right() - hs//2, r.bottom() - hs//2, hs, hs),
            'resize_t': QRect(r.center().x() - hs//2, r.top() - hs//2, hs, hs),
            'resize_b': QRect(r.center().x() - hs//2, r.bottom() - hs//2, hs, hs),
            'resize_l': QRect(r.left() - hs//2, r.center().y() - hs//2, hs, hs),
            'resize_r': QRect(r.right() - hs//2, r.center().y() - hs//2, hs, hs),
        }
    
    def _get_drag_mode(self, pos: QPoint) -> str | None:
        """マウス位置からドラッグモードを判定"""
        handles = self._get_resize_handles()
        
        for mode, rect in handles.items():
            if rect.contains(pos):
                return mode
        
        if self.crop_rect.contains(pos):
            return 'move'
        
        if self.image_rect.contains(pos):
            return 'create'
        
        return None
    
    def mousePressEvent(self, event):
        """マウス押下イベント"""
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.pos()
            self.drag_mode = self._get_drag_mode(pos)
            
            if self.drag_mode:
                self.dragging = True
                self.drag_start = pos
                
                if self.drag_mode == 'move':
                    self.drag_offset = pos - self.crop_rect.topLeft()
                elif self.drag_mode == 'create':
                    self.crop_rect = QRect(pos, pos)
    
    def mouseMoveEvent(self, event):
        """マウス移動イベント"""
        pos = event.pos()
        
        if self.dragging:
            if self.drag_mode == 'move':
                new_pos = pos - self.drag_offset
                new_rect = QRect(new_pos, self.crop_rect.size())
                
                # 画像領域内に制限
                if new_rect.left() < self.image_rect.left():
                    new_rect.moveLeft(self.image_rect.left())
                if new_rect.top() < self.image_rect.top():
                    new_rect.moveTop(self.image_rect.top())
                if new_rect.right() > self.image_rect.right():
                    new_rect.moveRight(self.image_rect.right())
                if new_rect.bottom() > self.image_rect.bottom():
                    new_rect.moveBottom(self.image_rect.bottom())
                
                self.crop_rect = new_rect
            
            elif self.drag_mode == 'create':
                self.crop_rect = QRect(self.drag_start, pos).normalized()
                self.crop_rect = self.crop_rect.intersected(self.image_rect)
                if self.aspect_ratio:
                    self._constrain_aspect_ratio()
            
            elif self.drag_mode.startswith('resize'):
                self._handle_resize(pos)
            
            self.update()
        else:
            # カーソル変更
            mode = self._get_drag_mode(pos)
            if mode in ('resize_tl', 'resize_br'):
                self.setCursor(QCursor(Qt.CursorShape.SizeFDiagCursor))
            elif mode in ('resize_tr', 'resize_bl'):
                self.setCursor(QCursor(Qt.CursorShape.SizeBDiagCursor))
            elif mode in ('resize_t', 'resize_b'):
                self.setCursor(QCursor(Qt.CursorShape.SizeVerCursor))
            elif mode in ('resize_l', 'resize_r'):
                self.setCursor(QCursor(Qt.CursorShape.SizeHorCursor))
            elif mode == 'move':
                self.setCursor(QCursor(Qt.CursorShape.SizeAllCursor))
            else:
                self.setCursor(QCursor(Qt.CursorShape.CrossCursor))
    
    def _handle_resize(self, pos: QPoint):
        """リサイズ処理"""
        r = QRect(self.crop_rect)
        min_size = 20
        
        if 'l' in self.drag_mode:
            new_left = max(self.image_rect.left(), min(pos.x(), r.right() - min_size))
            r.setLeft(new_left)
        if 'r' in self.drag_mode:
            new_right = min(self.image_rect.right(), max(pos.x(), r.left() + min_size))
            r.setRight(new_right)
        if 't' in self.drag_mode:
            new_top = max(self.image_rect.top(), min(pos.y(), r.bottom() - min_size))
            r.setTop(new_top)
        if 'b' in self.drag_mode:
            new_bottom = min(self.image_rect.bottom(), max(pos.y(), r.top() + min_size))
            r.setBottom(new_bottom)
        
        self.crop_rect = r
        
        if self.aspect_ratio:
            self._constrain_aspect_ratio()
    
    def mouseReleaseEvent(self, event):
        """マウスリリースイベント"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            self.drag_mode = None
    
    def confirm_crop(self):
        """クロップを確定"""
        x, y, w, h = self.get_crop_region()
        if w > 0 and h > 0:
            self.crop_confirmed.emit(x, y, w, h)
    
    def cancel_crop(self):
        """クロップをキャンセル"""
        self.crop_cancelled.emit()


class CropControlPanel(QFrame):
    """クロップ操作パネル"""
    
    # アスペクト比変更シグナル
    aspect_ratio_changed = pyqtSignal(object)  # tuple | None
    # 確定シグナル
    confirm_clicked = pyqtSignal()
    # キャンセルシグナル
    cancel_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """UIをセットアップ"""
        self.setStyleSheet("""
            CropControlPanel {
                background-color: #2a2a2a;
                border: 1px solid #555;
                border-radius: 6px;
            }
            QLabel {
                color: #ffffff;
                font-size: 13px;
            }
            QSpinBox {
                background-color: #3a3a3a;
                color: #ffffff;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 4px 8px;
                min-width: 60px;
            }
            QComboBox {
                background-color: #3a3a3a;
                color: #ffffff;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 4px 8px;
                min-width: 100px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #2a2a2a;
                color: #ffffff;
                selection-background-color: #3498db;
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
            }
            QPushButton#confirmButton {
                background-color: #27ae60;
                border: none;
            }
            QPushButton#confirmButton:hover {
                background-color: #2ecc71;
            }
            QPushButton#cancelButton {
                background-color: #c0392b;
                border: none;
            }
            QPushButton#cancelButton:hover {
                background-color: #e74c3c;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(15)
        
        layout.addStretch()
        
        # アスペクト比選択
        ratio_label = QLabel("比率:")
        layout.addWidget(ratio_label)
        
        self.ratio_combo = QComboBox()
        self.ratio_combo.addItem("自由", None)
        self.ratio_combo.addItem("3:2（横）", (3, 2))
        self.ratio_combo.addItem("2:3（縦）", (2, 3))
        self.ratio_combo.addItem("4:3（横）", (4, 3))
        self.ratio_combo.addItem("3:4（縦）", (3, 4))
        self.ratio_combo.addItem("16:9（横）", (16, 9))
        self.ratio_combo.addItem("9:16（縦）", (9, 16))
        self.ratio_combo.addItem("1:1（正方形）", (1, 1))
        self.ratio_combo.addItem("カスタム", "custom")
        self.ratio_combo.setCurrentIndex(1)  # デフォルト: 3:2
        layout.addWidget(self.ratio_combo)
        
        # カスタム比率入力
        self.custom_width = QSpinBox()
        self.custom_width.setRange(1, 100)
        self.custom_width.setValue(3)
        self.custom_width.setVisible(False)
        layout.addWidget(self.custom_width)
        
        self.custom_separator = QLabel(":")
        self.custom_separator.setVisible(False)
        layout.addWidget(self.custom_separator)
        
        self.custom_height = QSpinBox()
        self.custom_height.setRange(1, 100)
        self.custom_height.setValue(2)
        self.custom_height.setVisible(False)
        layout.addWidget(self.custom_height)
        
        layout.addSpacing(30)
        
        # ボタン
        self.cancel_button = QPushButton("キャンセル")
        self.cancel_button.setObjectName("cancelButton")
        layout.addWidget(self.cancel_button)
        
        layout.addSpacing(10)
        
        self.confirm_button = QPushButton("✓ 切り抜き確定")
        self.confirm_button.setObjectName("confirmButton")
        layout.addWidget(self.confirm_button)
        
        layout.addStretch()
    
    def _connect_signals(self):
        """シグナルを接続"""
        self.ratio_combo.currentIndexChanged.connect(self._on_ratio_changed)
        self.custom_width.valueChanged.connect(self._on_custom_ratio_changed)
        self.custom_height.valueChanged.connect(self._on_custom_ratio_changed)
        self.confirm_button.clicked.connect(self.confirm_clicked)
        self.cancel_button.clicked.connect(self.cancel_clicked)
    
    def _on_ratio_changed(self):
        """アスペクト比選択変更時"""
        data = self.ratio_combo.currentData()
        
        if data == "custom":
            self.custom_width.setVisible(True)
            self.custom_separator.setVisible(True)
            self.custom_height.setVisible(True)
            self._on_custom_ratio_changed()
        else:
            self.custom_width.setVisible(False)
            self.custom_separator.setVisible(False)
            self.custom_height.setVisible(False)
            self.aspect_ratio_changed.emit(data)
    
    def _on_custom_ratio_changed(self):
        """カスタム比率変更時"""
        ratio = (self.custom_width.value(), self.custom_height.value())
        self.aspect_ratio_changed.emit(ratio)

