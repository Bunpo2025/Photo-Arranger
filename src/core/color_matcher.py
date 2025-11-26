#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
色調マッチングモジュール
"""

import cv2
import numpy as np
from typing import Optional

from src.core.chart_detector import ChartDetector


class ColorMatcher:
    """色調マッチングクラス"""
    
    def __init__(self):
        self.chart_detector = ChartDetector()
    
    def match_histograms(
        self,
        source: np.ndarray,
        reference: np.ndarray
    ) -> np.ndarray:
        """
        ヒストグラムマッチングで色調を合わせる
        
        Args:
            source: 補正対象画像（BGR形式）
            reference: 参照画像（BGR形式）
        
        Returns:
            補正後の画像
        """
        result = np.zeros_like(source)
        
        # 各チャンネルでヒストグラムマッチング
        for i in range(3):
            result[:, :, i] = self._match_channel_histogram(
                source[:, :, i],
                reference[:, :, i]
            )
        
        return result
    
    def _match_channel_histogram(
        self,
        source: np.ndarray,
        reference: np.ndarray
    ) -> np.ndarray:
        """
        単一チャンネルのヒストグラムマッチング
        
        Args:
            source: ソースチャンネル
            reference: 参照チャンネル
        
        Returns:
            マッチング後のチャンネル
        """
        # ヒストグラムを計算
        src_hist, _ = np.histogram(source.flatten(), 256, [0, 256])
        ref_hist, _ = np.histogram(reference.flatten(), 256, [0, 256])
        
        # 累積分布関数を計算
        src_cdf = src_hist.cumsum()
        ref_cdf = ref_hist.cumsum()
        
        # 正規化
        src_cdf = src_cdf / src_cdf[-1]
        ref_cdf = ref_cdf / ref_cdf[-1]
        
        # ルックアップテーブルを作成
        lookup_table = np.zeros(256, dtype=np.uint8)
        for i in range(256):
            diff = np.abs(ref_cdf - src_cdf[i])
            lookup_table[i] = np.argmin(diff)
        
        # マッピング適用
        result = lookup_table[source]
        
        return result
    
    def color_transfer(
        self,
        source: np.ndarray,
        reference: np.ndarray
    ) -> np.ndarray:
        """
        Lab色空間での色転送
        参照画像の色調をソース画像に適用
        
        Args:
            source: 補正対象画像（BGR形式）
            reference: 参照画像（BGR形式）
        
        Returns:
            補正後の画像
        """
        # Lab色空間に変換
        source_lab = cv2.cvtColor(source, cv2.COLOR_BGR2LAB).astype(np.float32)
        reference_lab = cv2.cvtColor(reference, cv2.COLOR_BGR2LAB).astype(np.float32)
        
        # 各チャンネルの平均と標準偏差を計算
        src_mean, src_std = [], []
        ref_mean, ref_std = [], []
        
        for i in range(3):
            src_mean.append(np.mean(source_lab[:, :, i]))
            src_std.append(np.std(source_lab[:, :, i]))
            ref_mean.append(np.mean(reference_lab[:, :, i]))
            ref_std.append(np.std(reference_lab[:, :, i]))
        
        # 色転送
        result_lab = source_lab.copy()
        for i in range(3):
            # ソースを正規化して参照のスケールに変換
            if src_std[i] > 0:
                result_lab[:, :, i] = (source_lab[:, :, i] - src_mean[i]) * \
                                      (ref_std[i] / src_std[i]) + ref_mean[i]
            else:
                result_lab[:, :, i] = ref_mean[i]
        
        # 値をクリップ
        result_lab[:, :, 0] = np.clip(result_lab[:, :, 0], 0, 255)
        result_lab[:, :, 1] = np.clip(result_lab[:, :, 1], 0, 255)
        result_lab[:, :, 2] = np.clip(result_lab[:, :, 2], 0, 255)
        
        # BGRに変換
        result = cv2.cvtColor(result_lab.astype(np.uint8), cv2.COLOR_LAB2BGR)
        
        return result
    
    def match_with_chart(
        self,
        source: np.ndarray,
        reference: np.ndarray
    ) -> Optional[np.ndarray]:
        """
        カラーチャートを使用して色調を合わせる
        
        Args:
            source: 補正対象画像（BGR形式）
            reference: 参照画像（BGR形式）
        
        Returns:
            補正後の画像、またはチャート未検出時はNone
        """
        # 両画像からカラーチャートを検出
        source_chart = self.chart_detector.detect_chart(source)
        reference_chart = self.chart_detector.detect_chart(reference)
        
        if source_chart is None or reference_chart is None:
            return None
        
        # チャートの色値を抽出
        source_colors = self.chart_detector.extract_colors(source, source_chart)
        reference_colors = self.chart_detector.extract_colors(reference, reference_chart)
        
        if source_colors is None or reference_colors is None:
            return None
        
        # 色変換行列を計算
        transform_matrix = self._calculate_color_transform(
            source_colors,
            reference_colors
        )
        
        # 変換を適用
        result = self._apply_color_transform(source, transform_matrix)
        
        return result
    
    def _calculate_color_transform(
        self,
        source_colors: np.ndarray,
        reference_colors: np.ndarray
    ) -> np.ndarray:
        """
        色変換行列を計算
        
        Args:
            source_colors: ソース画像のチャート色値
            reference_colors: 参照画像のチャート色値
        
        Returns:
            3x3の色変換行列
        """
        # 最小二乗法で変換行列を求める
        # reference = source * transform
        transform, _, _, _ = np.linalg.lstsq(
            source_colors,
            reference_colors,
            rcond=None
        )
        
        return transform
    
    def _apply_color_transform(
        self,
        image: np.ndarray,
        transform: np.ndarray
    ) -> np.ndarray:
        """
        色変換行列を適用
        
        Args:
            image: 入力画像
            transform: 色変換行列
        
        Returns:
            変換後の画像
        """
        # 画像を2D配列に変形
        h, w, c = image.shape
        pixels = image.reshape(-1, 3).astype(np.float32)
        
        # 変換適用
        transformed = np.dot(pixels, transform)
        
        # クリップして元の形状に戻す
        transformed = np.clip(transformed, 0, 255)
        result = transformed.reshape(h, w, c).astype(np.uint8)
        
        return result


