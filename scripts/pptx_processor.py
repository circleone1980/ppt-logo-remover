#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PPTX 文件处理模块
PPT Logo Remover - PPTX Processor Module

负责解压、处理和重新打包 PPTX 文件。
"""

import os
import zipfile
import shutil
import tempfile
from pathlib import Path

from PIL import Image

from locator import find_logo_in_image
from inpainting import remove_logo_inpaint
from utils import REFERENCE_WIDTH, REFERENCE_HEIGHT, IMAGE_EXTENSIONS
from utils import parse_pages_spec
from slide_mapper import get_slide_image_map, get_images_for_pages


def process_pptx(input_pptx, output_pptx, logo_template=None, logo_coords=None,
                  use_ai=True, verbose=True, pages=None):
    """
    处理 PPTX 文件，移除 logo

    两阶段策略：
    1. 第一阶段：用 SIFT 特征匹配在第一张图片中找到 logo 位置
    2. 第二阶段：在目标图片中使用 Inpainting 无痕修复

    Args:
        input_pptx: 输入 PPTX 文件路径
        output_pptx: 输出 PPTX 文件路径
        logo_template: logo 模板图片路径（可选，提供则使用 SIFT 自动定位）
        logo_coords: 固定 logo 位置 (x1, y1, x2, y2)（可选，SIFT 失败时使用）
        use_ai: 是否使用 LaMa AI 修复（默认 True），False 则使用 OpenCV
        verbose: 是否显示详细输出
        pages: 页码规格字符串（可选，如 "2-4,7,last"）

    Returns:
        bool: 处理成功返回 True，失败返回 False

    Raises:
        Exception: 处理失败时抛出异常
    """
    work_dir = tempfile.mkdtemp(prefix='ppt_logo_')
    clean_media_dir = os.path.join(work_dir, 'clean_media')
    os.makedirs(clean_media_dir)

    # 加载 logo 模板（如果提供）
    if logo_template and os.path.exists(logo_template):
        template_img = Image.open(logo_template)
        if verbose:
            print(f"Logo 模板：{template_img.width}x{template_img.height} 像素")
    else:
        template_img = None
        if verbose and logo_coords:
            print(f"使用固定位置模式：({logo_coords[0]},{logo_coords[1]}) - ({logo_coords[2]},{logo_coords[3]})")

    try:
        # 解压 PPTX
        with zipfile.ZipFile(input_pptx, 'r') as zip_ref:
            zip_ref.extractall(work_dir)

        media_dir = os.path.join(work_dir, 'ppt', 'media')
        if not os.path.exists(media_dir):
            raise Exception("无效的 PPTX 文件：未找到 media 目录")

        # ========== 构建页码-图片映射 ==========
        slide_image_map, total_pages = get_slide_image_map(input_pptx)

        if verbose:
            print(f"共 {total_pages} 页幻灯片")

        # ========== 确定要处理的图片子集 ==========
        page_numbers = parse_pages_spec(pages, total_pages)

        if page_numbers:
            # 用户指定了具体页码
            target_images = get_images_for_pages(slide_image_map, page_numbers, media_dir)
            if verbose:
                print(f"指定页码: {sorted(page_numbers)}")
                print(f"涉及图片: {len(target_images)} 张")
        else:
            # 未指定页码 -> 处理全部
            target_images = sorted([
                f for f in os.listdir(media_dir)
                if os.path.splitext(f.lower())[1] in IMAGE_EXTENSIONS
            ])

        total = len(target_images)

        if verbose:
            print(f"待处理图片: {total} 张")

        if total == 0:
            if verbose:
                print("没有需要处理的图片")
            # 仍然复制原文件
            shutil.copy2(input_pptx, output_pptx)
            return True

        # ========== 处理每张图片（逐图独立计算 logo 坐标）==========
        if verbose:
            mode = "SIFT 模板匹配" if template_img else "固定位置"
            print(f"\n处理模式：{mode}")

        processed = 0

        for i, img_name in enumerate(target_images):
            img_path = os.path.join(media_dir, img_name)
            output_path = os.path.join(clean_media_dir, img_name)

            try:
                img = Image.open(img_path)

                # 逐图独立计算 logo 坐标
                current_bounds = None

                if template_img:
                    # 模板匹配模式：对每张图做 SIFT 检测
                    current_bounds = find_logo_in_image(img, template_img)

                if current_bounds is None and logo_coords:
                    # 固定位置模式：按当前图片实际尺寸等比缩放
                    w, h = img.size
                    scale_x = w / REFERENCE_WIDTH
                    scale_y = h / REFERENCE_HEIGHT
                    x1 = int(logo_coords[0] * scale_x)
                    y1 = int(logo_coords[1] * scale_y)
                    x2 = int(logo_coords[2] * scale_x)
                    y2 = int(logo_coords[3] * scale_y)
                    current_bounds = (x1, y1, x2, y2)

                if current_bounds:
                    cleaned = remove_logo_inpaint(img, *current_bounds, use_ai=use_ai)
                    ext = os.path.splitext(img_name)[1].lower()
                    fmt = 'JPEG' if ext in ('.jpg', '.jpeg') else 'PNG'
                    cleaned.save(output_path, fmt)
                    processed += 1
                else:
                    shutil.copy(img_path, output_path)

            except Exception as e:
                if verbose:
                    print(f"  警告：处理 {img_name} 失败 - {e}")
                shutil.copy(img_path, output_path)

            if verbose and (i + 1) % 10 == 0:
                print(f"  进度：{i + 1}/{total}")

        if verbose:
            print(f"\n处理完成：{processed}/{total} 张图片")

        # 重新打包 PPTX
        with zipfile.ZipFile(output_pptx, 'w', zipfile.ZIP_DEFLATED) as zip_out:
            for root, dirs, files in os.walk(work_dir):
                # 跳过 clean_media_dir（会在处理原图时替换）
                if os.path.normpath(root) == os.path.normpath(clean_media_dir):
                    continue

                for file in files:
                    file_path = os.path.join(root, file)
                    arc_name = os.path.relpath(file_path, work_dir)

                    # 使用清理后的 media 文件
                    arc_normalized = arc_name.replace('\\', '/')
                    if arc_normalized.startswith('ppt/media/') and os.path.splitext(file.lower())[1] in IMAGE_EXTENSIONS:
                        clean_path = os.path.join(clean_media_dir, file)
                        if os.path.exists(clean_path):
                            zip_out.write(clean_path, arc_name)
                            continue

                    zip_out.write(file_path, arc_name)

        return True

    finally:
        shutil.rmtree(work_dir, ignore_errors=True)
