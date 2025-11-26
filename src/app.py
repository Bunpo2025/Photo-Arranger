#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
アプリケーション初期化モジュール
"""

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from src.ui.main_window import MainWindow


class PhotoArrangerApp:
    """Photo-Arrangerアプリケーションクラス"""
    
    def __init__(self, argv: list):
        """
        アプリケーションを初期化
        
        Args:
            argv: コマンドライン引数
        """
        self.app = QApplication(argv)
        self.app.setApplicationName("Photo-Arranger")
        self.app.setApplicationVersion("1.0.0")
        
        # ハイDPIサポート
        self.app.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )
        
        self.main_window = MainWindow()
    
    def run(self) -> int:
        """
        アプリケーションを実行
        
        Returns:
            終了コード
        """
        self.main_window.show()
        return self.app.exec()


