#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ColorMatcher のテスト
"""

import pytest
import numpy as np

from src.core.color_matcher import ColorMatcher


class TestColorMatcher:
    """ColorMatcherのテストクラス"""
    
    @pytest.fixture
    def matcher(self):
        """ColorMatcherインスタンスを作成"""
        return ColorMatcher()
    
    @pytest.fixture
    def sample_image(self):
        """テスト用サンプル画像を作成"""
        # 100x100のランダム画像
        return np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
    
    def test_match_histograms_shape(self, matcher, sample_image):
        """ヒストグラムマッチングの出力形状テスト"""
        source = sample_image
        reference = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        
        result = matcher.match_histograms(source, reference)
        
        assert result.shape == source.shape
        assert result.dtype == np.uint8
    
    def test_match_histograms_range(self, matcher, sample_image):
        """ヒストグラムマッチングの値範囲テスト"""
        source = sample_image
        reference = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        
        result = matcher.match_histograms(source, reference)
        
        assert result.min() >= 0
        assert result.max() <= 255
    
    def test_color_transfer_shape(self, matcher, sample_image):
        """色転送の出力形状テスト"""
        source = sample_image
        reference = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        
        result = matcher.color_transfer(source, reference)
        
        assert result.shape == source.shape
        assert result.dtype == np.uint8
    
    def test_color_transfer_preserves_structure(self, matcher):
        """色転送が画像構造を保持するかテスト"""
        # グラデーション画像を作成
        source = np.zeros((100, 100, 3), dtype=np.uint8)
        for i in range(100):
            source[i, :, :] = i * 2
        
        reference = np.full((100, 100, 3), 128, dtype=np.uint8)
        
        result = matcher.color_transfer(source, reference)
        
        # 構造（グラデーション）が保持されていることを確認
        # 上部より下部の方が明るいはず
        assert np.mean(result[0:10, :, :]) < np.mean(result[90:100, :, :])
    
    def test_match_with_chart_no_chart(self, matcher, sample_image):
        """カラーチャートなしの場合のテスト"""
        source = sample_image
        reference = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        
        result = matcher.match_with_chart(source, reference)
        
        # チャートが検出されない場合はNoneを返す
        assert result is None


class TestImageProcessor:
    """ImageProcessorのテストクラス"""
    
    @pytest.fixture
    def processor(self):
        """ImageProcessorインスタンスを作成"""
        from src.core.image_processor import ImageProcessor
        return ImageProcessor()
    
    @pytest.fixture
    def sample_image(self):
        """テスト用サンプル画像を作成"""
        return np.full((100, 100, 3), 128, dtype=np.uint8)
    
    def test_adjust_temperature_warm(self, processor, sample_image):
        """暖色方向の色温度調整テスト"""
        result = processor.adjust_temperature(sample_image, 50)
        
        # 赤が増加、青が減少
        assert np.mean(result[:, :, 2]) > np.mean(sample_image[:, :, 2])  # Red
        assert np.mean(result[:, :, 0]) < np.mean(sample_image[:, :, 0])  # Blue
    
    def test_adjust_temperature_cool(self, processor, sample_image):
        """寒色方向の色温度調整テスト"""
        result = processor.adjust_temperature(sample_image, -50)
        
        # 青が増加、赤が減少
        assert np.mean(result[:, :, 0]) > np.mean(sample_image[:, :, 0])  # Blue
        assert np.mean(result[:, :, 2]) < np.mean(sample_image[:, :, 2])  # Red
    
    def test_adjust_brightness_increase(self, processor, sample_image):
        """明るさ増加テスト"""
        result = processor.adjust_brightness(sample_image, 50)
        
        assert np.mean(result) > np.mean(sample_image)
    
    def test_adjust_brightness_decrease(self, processor, sample_image):
        """明るさ減少テスト"""
        result = processor.adjust_brightness(sample_image, -50)
        
        assert np.mean(result) < np.mean(sample_image)
    
    def test_apply_adjustments_no_change(self, processor, sample_image):
        """調整なしの場合のテスト"""
        values = {"temperature": 0, "tint": 0, "brightness": 0}
        result = processor.apply_adjustments(sample_image, values)
        
        np.testing.assert_array_equal(result, sample_image)


