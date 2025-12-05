#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
画像処理エンジンモジュール
"""

import cv2
import numpy as np


class ImageProcessor:
    """画像処理エンジンクラス"""
    
    def apply_adjustments(self, image: np.ndarray, values: dict) -> np.ndarray:
        """
        調整値を適用
        
        Args:
            image: 入力画像（BGR形式）
            values: 調整値の辞書
                - temperature: 色温度 (-100 ~ +100)
                - tint: 色かぶり (-100 ~ +100)
                - brightness: 明るさ (-100 ~ +100)
        
        Returns:
            処理後の画像
        """
        result = image.copy()
        
        # 色温度補正
        if values.get("temperature", 0) != 0:
            result = self.adjust_temperature(result, values["temperature"])
        
        # 色かぶり補正
        if values.get("tint", 0) != 0:
            result = self.adjust_tint(result, values["tint"])
        
        # 明るさ補正
        if values.get("brightness", 0) != 0:
            result = self.adjust_brightness(result, values["brightness"])
        
        return result
    
    def adjust_temperature(self, image: np.ndarray, value: int) -> np.ndarray:
        """
        色温度を調整
        
        Args:
            image: 入力画像（BGR形式）
            value: 補正値 (-100 ~ +100)
                   負: 青みを増す（クール）
                   正: 赤みを増す（ウォーム）
        
        Returns:
            補正後の画像
        """
        result = image.astype(np.float32)
        
        # 補正係数を計算（-100～+100 → -50～+50）
        adjustment = value * 0.5
        
        # 青チャンネルと赤チャンネルを調整
        result[:, :, 0] = np.clip(result[:, :, 0] - adjustment, 0, 255)  # Blue
        result[:, :, 2] = np.clip(result[:, :, 2] + adjustment, 0, 255)  # Red
        
        return result.astype(np.uint8)
    
    def adjust_tint(self, image: np.ndarray, value: int) -> np.ndarray:
        """
        色かぶり（グリーン/マゼンタ）を調整
        
        Args:
            image: 入力画像（BGR形式）
            value: 補正値 (-100 ~ +100)
                   負: グリーン方向
                   正: マゼンタ方向
        
        Returns:
            補正後の画像
        """
        result = image.astype(np.float32)
        
        # 補正係数を計算
        adjustment = value * 0.5
        
        # グリーンチャンネルを調整
        result[:, :, 1] = np.clip(result[:, :, 1] - adjustment, 0, 255)  # Green
        
        return result.astype(np.uint8)
    
    def adjust_brightness(self, image: np.ndarray, value: int) -> np.ndarray:
        """
        明るさを調整
        
        Args:
            image: 入力画像（BGR形式）
            value: 補正値 (-100 ~ +100)
        
        Returns:
            補正後の画像
        """
        # HSV変換して明度を調整
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        
        # 補正係数を計算（-100～+100 → -100～+100）
        adjustment = value
        
        # 明度を調整
        v = v.astype(np.float32)
        v = np.clip(v + adjustment, 0, 255)
        v = v.astype(np.uint8)
        
        # 再合成
        hsv = cv2.merge([h, s, v])
        result = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        
        return result
    
    def adjust_contrast(self, image: np.ndarray, value: int) -> np.ndarray:
        """
        コントラストを調整
        
        Args:
            image: 入力画像（BGR形式）
            value: 補正値 (-100 ~ +100)
        
        Returns:
            補正後の画像
        """
        # コントラスト係数を計算（0.5 ～ 1.5）
        factor = 1 + (value / 100)
        
        # 中央値（128）を基準にコントラスト調整
        result = image.astype(np.float32)
        result = (result - 128) * factor + 128
        result = np.clip(result, 0, 255)
        
        return result.astype(np.uint8)
    
    def adjust_saturation(self, image: np.ndarray, value: int) -> np.ndarray:
        """
        彩度を調整
        
        Args:
            image: 入力画像（BGR形式）
            value: 補正値 (-100 ~ +100)
        
        Returns:
            補正後の画像
        """
        # HSV変換して彩度を調整
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        
        # 彩度係数を計算（0 ～ 2）
        factor = 1 + (value / 100)
        
        # 彩度を調整
        s = s.astype(np.float32)
        s = np.clip(s * factor, 0, 255)
        s = s.astype(np.uint8)
        
        # 再合成
        hsv = cv2.merge([h, s, v])
        result = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        
        return result
    
    def crop_image(self, image: np.ndarray, x: int, y: int, width: int, height: int) -> np.ndarray:
        """
        画像を切り抜き
        
        Args:
            image: 入力画像（BGR形式）
            x: 左上のX座標
            y: 左上のY座標
            width: 切り抜き幅
            height: 切り抜き高さ
        
        Returns:
            切り抜かれた画像
        """
        h, w = image.shape[:2]
        
        # 座標のバリデーション
        x = max(0, min(x, w - 1))
        y = max(0, min(y, h - 1))
        width = max(1, min(width, w - x))
        height = max(1, min(height, h - y))
        
        return image[y:y+height, x:x+width].copy()
    
    def resize_image(
        self,
        image: np.ndarray,
        width: int | None = None,
        height: int | None = None,
        scale_percent: float | None = None,
        maintain_aspect: bool = True
    ) -> np.ndarray:
        """
        画像をリサイズ
        
        Args:
            image: 入力画像（BGR形式）
            width: 新しい幅（ピクセル）
            height: 新しい高さ（ピクセル）
            scale_percent: スケール（パーセント、100が等倍）
            maintain_aspect: アスペクト比を維持するか
        
        Returns:
            リサイズされた画像
        """
        h, w = image.shape[:2]
        
        if scale_percent is not None:
            # パーセント指定
            new_width = int(w * scale_percent / 100)
            new_height = int(h * scale_percent / 100)
        elif width is not None and height is not None:
            if maintain_aspect:
                # アスペクト比を維持
                aspect = w / h
                if width / height > aspect:
                    new_height = height
                    new_width = int(height * aspect)
                else:
                    new_width = width
                    new_height = int(width / aspect)
            else:
                new_width = width
                new_height = height
        elif width is not None:
            # 幅のみ指定
            new_width = width
            new_height = int(h * width / w) if maintain_aspect else h
        elif height is not None:
            # 高さのみ指定
            new_height = height
            new_width = int(w * height / h) if maintain_aspect else w
        else:
            return image.copy()
        
        # 最小サイズを保証
        new_width = max(1, new_width)
        new_height = max(1, new_height)
        
        # リサイズ（縮小時はINTER_AREA、拡大時はINTER_CUBIC）
        if new_width < w or new_height < h:
            interpolation = cv2.INTER_AREA
        else:
            interpolation = cv2.INTER_CUBIC
        
        return cv2.resize(image, (new_width, new_height), interpolation=interpolation)
    
    @staticmethod
    def cm_to_pixels(cm: float, dpi: int = 300) -> int:
        """
        センチメートルをピクセルに変換
        
        Args:
            cm: センチメートル値
            dpi: 解像度（dots per inch）
        
        Returns:
            ピクセル値
        """
        inches = cm / 2.54
        return int(inches * dpi)
    
    @staticmethod
    def pixels_to_cm(pixels: int, dpi: int = 300) -> float:
        """
        ピクセルをセンチメートルに変換
        
        Args:
            pixels: ピクセル値
            dpi: 解像度（dots per inch）
        
        Returns:
            センチメートル値
        """
        inches = pixels / dpi
        return inches * 2.54


