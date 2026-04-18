#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具函数和常量定义
PPT Logo Remover - Utils Module
"""

import os
import re
from pathlib import Path

# 默认 logo 位置（基于 1376x768 标准图片尺寸）
DEFAULT_LOGO_X1 = 1255
DEFAULT_LOGO_Y1 = 725
DEFAULT_LOGO_X2 = 1376
DEFAULT_LOGO_Y2 = 768
SAMPLE_MARGIN = 20

# SIFT 匹配参数
SIFT_MIN_MATCHES = 4  # 最少匹配点数
SIFT_RATIO_THRESHOLD = 0.7  # Lowe's ratio test
SIFT_MIN_CONFIDENCE = 0.3  # 最小置信度（内点比例）


def generate_output_path(input_path):
    """
    生成输出文件路径，添加'_clear'后缀

    Args:
        input_path: 输入文件路径（str 或 Path）

    Returns:
        str: 输出文件路径
    """
    input_path = Path(input_path)
    dir_name = input_path.parent or '.'
    base_name = input_path.stem
    ext = input_path.suffix

    # 移除已存在的后缀，避免重复
    for suffix in ['_clear', ' - 无 logo', '-无 logo', '_no_logo', '-no_logo']:
        base_name = base_name.replace(suffix, '')

    return str(dir_name / f"{base_name}_clear{ext}")


def parse_logo_pos(pos_str):
    """
    解析 logo 位置坐标字符串

    Args:
        pos_str: 位置字符串，格式 "x1,y1,x2,y2"

    Returns:
        tuple: (x1, y1, x2, y2) 或 None（解析失败）
    """
    if not pos_str:
        return None

    try:
        parts = pos_str.split(',')
        if len(parts) != 4:
            return None
        coords = [int(p.strip()) for p in parts]
        if coords[2] > coords[0] and coords[3] > coords[1]:
            return tuple(coords)
    except (ValueError, AttributeError):
        pass

    return None


def get_image_files(media_dir):
    """
    获取目录中的所有图片文件

    Args:
        media_dir: PPTX 媒体目录路径

    Returns:
        list: 图片文件名列表（按文件名排序）
    """
    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp'}
    try:
        all_files = os.listdir(media_dir)
        image_files = [
            f for f in all_files
            if Path(f).suffix.lower() in image_extensions
        ]
        return sorted(image_files)
    except FileNotFoundError:
        return []


def parse_pages_spec(spec, total_pages):
    """
    解析页码规格字符串

    支持格式: "2-4", "1,3,5", "last", "2-4,7,last"
    None 或空字符串返回空集合（表示全部页面）

    Args:
        spec: 页码规格字符串
        total_pages: 总页数

    Returns:
        set: 页码集合（空集合表示全部页面）
    """
    if not spec:
        return set()

    result = set()
    for part in spec.split(','):
        part = part.strip()
        if not part:
            continue
        if part == 'last':
            result.add(total_pages)
        elif '-' in part:
            segments = part.split('-', 1)
            try:
                start = int(segments[0].strip())
                end = int(segments[1].strip())
                result.update(range(start, end + 1))
            except ValueError:
                pass
        else:
            try:
                result.add(int(part))
            except ValueError:
                pass

    valid = {p for p in result if 1 <= p <= total_pages}
    invalid = result - valid
    if invalid:
        print(f"  警告：忽略越界页码: {sorted(invalid)}")
    return valid
