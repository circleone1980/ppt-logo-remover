#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
无痕修复模块
PPT Logo Remover - Inpainting Module

提供 OpenCV Inpainting 和 LaMa AI 两种无痕修复方法。
支持清华 TUNA 镜像加速下载和本地模型缓存。
"""

import sys
import subprocess
import numpy as np
import cv2
from PIL import Image

# LaMa AI 模型（延迟初始化）
_simple_lama_instance = None
_simple_lama_available = False


def get_lama_model():
    """
    获取 LaMa 模型单例

    优先使用 skill 内部缓存的模型，如不存在则使用清华 TUNA 镜像下载。
    首次调用时会自动安装依赖并下载模型（约 200MB）。

    Returns:
        SimpleLama: LaMa AI 模型实例
    """
    global _simple_lama_instance, _simple_lama_available

    if _simple_lama_instance is None:
        # 导入模型加载器（包含镜像配置）
        from .model_loader import get_lama_with_fallback, ensure_model_downloaded

        # 确保模型已下载（使用清华镜像）
        ensure_model_downloaded(verbose=True)

        # 获取模型实例
        _simple_lama_instance = get_lama_with_fallback()
        _simple_lama_available = True
        print("  [OK] LaMa 模型初始化完成")

    return _simple_lama_instance


def remove_logo_inpaint(img, x1, y1, x2, y2, use_ai=False):
    """
    移除 logo，支持两种修复模式

    Args:
        img: PIL.Image - 输入图像
        x1, y1, x2, y2: int - logo 边界框坐标
        use_ai: bool - 是否使用 LaMa AI（默认 False 使用 OpenCV）

    Returns:
        PIL.Image: 修复后的图像
    """
    w, h = img.size

    # 确保边界有效
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(w, x2), min(h, y2)

    if x2 <= x1 or y2 <= y1:
        return img

    # 转换为 RGB
    if img.mode != 'RGB':
        img = img.convert('RGB')

    # 创建掩码（logo 区域为白色，其余为黑色）
    mask_array = np.zeros((h, w), dtype=np.uint8)
    mask_array[y1:y2, x1:x2] = 255

    # 稍微扩大掩码边缘以确保完全覆盖
    kernel = np.ones((5, 5), np.uint8)
    mask_array = cv2.dilate(mask_array, kernel, iterations=2)

    if use_ai:
        # 使用 LaMa AI 修复
        # 转换掩码为 PIL Image（LaMa 需要）
        mask_pil = Image.fromarray(mask_array, mode='L')
        simple_lama = get_lama_model()
        result = simple_lama(img, mask_pil)
        return result
    else:
        # 使用 OpenCV Inpainting（默认）
        img_array = np.array(img)
        inpainted = cv2.inpaint(img_array, mask_array, inpaintRadius=10, flags=cv2.INPAINT_TELEA)
        return Image.fromarray(inpainted)
