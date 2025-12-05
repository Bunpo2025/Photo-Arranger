#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Photo-Arranger - メインエントリーポイント

同一被写体で撮影時期の異なる2枚の写真の色調と明るさを合わせるアプリケーション
"""

import sys
from pathlib import Path

# プロジェクトルートをsys.pathに追加
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.app import PhotoArrangerApp


def main():
    """アプリケーションのメインエントリーポイント"""
    app = PhotoArrangerApp(sys.argv)
    sys.exit(app.run())


if __name__ == "__main__":
    main()


