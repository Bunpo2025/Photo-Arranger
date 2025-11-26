#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
カラーチャート検出モジュール
"""

import cv2
import numpy as np
from typing import Optional, Tuple
from dataclasses import dataclass


@dataclass
class ChartRegion:
    """カラーチャート領域"""
    corners: np.ndarray  # 4つの角の座標
    patches: list  # 各パッチの中心座標


class ChartDetector:
    """カラーチャート検出クラス"""
    
    # Macbeth ColorChecker の標準パッチ数
    MACBETH_ROWS = 4
    MACBETH_COLS = 6
    MACBETH_PATCHES = 24
    
    def __init__(self):
        pass
    
    def detect_chart(self, image: np.ndarray) -> Optional[ChartRegion]:
        """
        画像内のカラーチャートを検出
        
        Args:
            image: 入力画像（BGR形式）
        
        Returns:
            検出されたチャート領域、または None
        """
        # グレースケール変換
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # エッジ検出
        edges = cv2.Canny(gray, 50, 150)
        
        # 輪郭検出
        contours, _ = cv2.findContours(
            edges,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        # 四角形の輪郭を探す
        for contour in sorted(contours, key=cv2.contourArea, reverse=True):
            # 輪郭を近似
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            # 4点の多角形かつ十分な面積があるか
            if len(approx) == 4 and cv2.contourArea(approx) > 10000:
                # カラーチャートの可能性をチェック
                if self._validate_chart(image, approx):
                    corners = approx.reshape(4, 2)
                    patches = self._calculate_patch_centers(corners)
                    return ChartRegion(corners=corners, patches=patches)
        
        return None
    
    def _validate_chart(
        self,
        image: np.ndarray,
        contour: np.ndarray
    ) -> bool:
        """
        検出された領域がカラーチャートかどうかを検証
        
        Args:
            image: 入力画像
            contour: 検出された輪郭
        
        Returns:
            カラーチャートと判定された場合True
        """
        # 領域を切り出して分析
        rect = cv2.boundingRect(contour)
        x, y, w, h = rect
        
        # アスペクト比チェック（Macbethは約1.5:1）
        aspect_ratio = w / h if h > 0 else 0
        if not (1.2 < aspect_ratio < 2.0 or 0.5 < aspect_ratio < 0.85):
            return False
        
        # 領域内の色の多様性をチェック
        roi = image[y:y+h, x:x+w]
        if roi.size == 0:
            return False
        
        # ヒストグラムの分散で色の多様性を確認
        hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        h_hist = cv2.calcHist([hsv_roi], [0], None, [180], [0, 180])
        s_hist = cv2.calcHist([hsv_roi], [1], None, [256], [0, 256])
        
        h_std = np.std(h_hist)
        s_std = np.std(s_hist)
        
        # 色相と彩度の分布が十分に広いか
        if h_std < 100 or s_std < 100:
            return False
        
        return True
    
    def _calculate_patch_centers(
        self,
        corners: np.ndarray
    ) -> list:
        """
        チャートのパッチ中心座標を計算
        
        Args:
            corners: チャートの4つの角の座標
        
        Returns:
            各パッチの中心座標リスト
        """
        # 角を並べ替え（左上から時計回り）
        corners = self._order_points(corners)
        
        patches = []
        rows = self.MACBETH_ROWS
        cols = self.MACBETH_COLS
        
        # 各パッチの中心を計算
        for row in range(rows):
            for col in range(cols):
                # パッチの相対位置（0-1）
                rel_x = (col + 0.5) / cols
                rel_y = (row + 0.5) / rows
                
                # バイリニア補間で実座標を計算
                center = self._bilinear_interpolate(corners, rel_x, rel_y)
                patches.append(center)
        
        return patches
    
    def _order_points(self, pts: np.ndarray) -> np.ndarray:
        """
        4点を左上から時計回りに並べ替え
        
        Args:
            pts: 4点の座標
        
        Returns:
            並べ替え後の座標
        """
        rect = np.zeros((4, 2), dtype=np.float32)
        
        # 合計で左上と右下を特定
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]  # 左上
        rect[2] = pts[np.argmax(s)]  # 右下
        
        # 差で右上と左下を特定
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]  # 右上
        rect[3] = pts[np.argmax(diff)]  # 左下
        
        return rect
    
    def _bilinear_interpolate(
        self,
        corners: np.ndarray,
        rel_x: float,
        rel_y: float
    ) -> Tuple[float, float]:
        """
        バイリニア補間で座標を計算
        
        Args:
            corners: 4つの角の座標（左上から時計回り）
            rel_x: X方向の相対位置（0-1）
            rel_y: Y方向の相対位置（0-1）
        
        Returns:
            補間後の座標
        """
        top = corners[0] + rel_x * (corners[1] - corners[0])
        bottom = corners[3] + rel_x * (corners[2] - corners[3])
        point = top + rel_y * (bottom - top)
        
        return tuple(point)
    
    def extract_colors(
        self,
        image: np.ndarray,
        chart: ChartRegion,
        patch_size: int = 10
    ) -> Optional[np.ndarray]:
        """
        チャートから各パッチの色を抽出
        
        Args:
            image: 入力画像
            chart: チャート領域情報
            patch_size: サンプリングする領域のサイズ
        
        Returns:
            各パッチの平均色（Nx3配列）、または None
        """
        if chart is None or not chart.patches:
            return None
        
        colors = []
        h, w = image.shape[:2]
        
        for center in chart.patches:
            cx, cy = int(center[0]), int(center[1])
            
            # 範囲チェック
            x1 = max(0, cx - patch_size)
            y1 = max(0, cy - patch_size)
            x2 = min(w, cx + patch_size)
            y2 = min(h, cy + patch_size)
            
            if x2 <= x1 or y2 <= y1:
                continue
            
            # パッチ領域の平均色を計算
            patch = image[y1:y2, x1:x2]
            mean_color = np.mean(patch, axis=(0, 1))
            colors.append(mean_color)
        
        if len(colors) < self.MACBETH_PATCHES // 2:
            return None
        
        return np.array(colors)


