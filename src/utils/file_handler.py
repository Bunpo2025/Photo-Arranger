#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ファイル操作ユーティリティモジュール
"""

import os
from pathlib import Path
from typing import Optional, Tuple

import cv2
import numpy as np


class FileHandler:
    """ファイル操作ユーティリティクラス"""
    
    SUPPORTED_FORMATS = {'.jpg', '.jpeg'}
    DEFAULT_JPEG_QUALITY = 95
    
    @staticmethod
    def load_image(file_path: str) -> Tuple[Optional[np.ndarray], Optional[str]]:
        """
        画像を読み込む（日本語パス・ネットワークパス対応）
        
        Args:
            file_path: ファイルパス
        
        Returns:
            (画像データ, エラーメッセージ) のタプル
            成功時はエラーメッセージがNone
        """
        path = Path(file_path)
        
        # 拡張子チェック
        if path.suffix.lower() not in FileHandler.SUPPORTED_FORMATS:
            return None, f"非対応のファイル形式です。JPEG形式のみ対応しています。"
        
        # 読み込み（日本語パス対応）
        try:
            with open(file_path, 'rb') as f:
                file_bytes = np.frombuffer(f.read(), dtype=np.uint8)
            
            image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
            if image is None:
                return None, f"画像をデコードできませんでした: {file_path}"
            return image, None
        except FileNotFoundError:
            return None, f"ファイルが見つかりません: {file_path}"
        except PermissionError:
            return None, f"ファイルへのアクセス権限がありません: {file_path}"
        except Exception as e:
            return None, f"読み込みエラー: {str(e)}"
    
    @staticmethod
    def save_image(
        image: np.ndarray,
        file_path: str,
        quality: int = DEFAULT_JPEG_QUALITY
    ) -> Optional[str]:
        """
        画像を保存（日本語パス対応）
        
        Args:
            image: 画像データ（BGR形式）
            file_path: 保存先パス
            quality: JPEG品質（0-100）
        
        Returns:
            エラーメッセージ、または成功時None
        """
        path = Path(file_path)
        
        # 拡張子を確認・追加
        if path.suffix.lower() not in FileHandler.SUPPORTED_FORMATS:
            path = path.with_suffix('.jpg')
        
        # ディレクトリが存在しない場合は作成
        path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # 日本語パス対応のため、エンコードしてから書き込み
            success, encoded_image = cv2.imencode(
                '.jpg',
                image,
                [cv2.IMWRITE_JPEG_QUALITY, quality]
            )
            if not success:
                return f"画像のエンコードに失敗しました: {file_path}"
            
            with open(str(path), 'wb') as f:
                f.write(encoded_image.tobytes())
            return None
        except Exception as e:
            return f"保存エラー: {str(e)}"
    
    @staticmethod
    def get_image_info(file_path: str) -> Optional[dict]:
        """
        画像の情報を取得
        
        Args:
            file_path: ファイルパス
        
        Returns:
            画像情報の辞書、または None
        """
        image, error = FileHandler.load_image(file_path)
        if image is None:
            return None
        
        path = Path(file_path)
        file_size = path.stat().st_size
        
        return {
            "path": str(path.absolute()),
            "filename": path.name,
            "width": image.shape[1],
            "height": image.shape[0],
            "channels": image.shape[2] if len(image.shape) > 2 else 1,
            "file_size": file_size,
            "file_size_mb": round(file_size / (1024 * 1024), 2)
        }
    
    @staticmethod
    def validate_file(file_path: str) -> Tuple[bool, str]:
        """
        ファイルを検証（日本語パス対応）
        
        Args:
            file_path: ファイルパス
        
        Returns:
            (有効かどうか, メッセージ) のタプル
        """
        path = Path(file_path)
        
        if path.suffix.lower() not in FileHandler.SUPPORTED_FORMATS:
            return False, "非対応のファイル形式です"
        
        # 読み込みテスト（日本語パス対応）
        try:
            with open(file_path, 'rb') as f:
                file_bytes = np.frombuffer(f.read(), dtype=np.uint8)
            
            image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
            if image is None:
                return False, "画像として読み込めません"
        except FileNotFoundError:
            return False, "ファイルが見つかりません"
        except PermissionError:
            return False, "アクセス権限がありません"
        except Exception:
            return False, "ファイルを開けません"
        
        return True, "有効なファイルです"

