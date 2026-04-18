#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PPTX 幻灯片-图片映射模块
PPT Logo Remover - Slide Mapper Module

解析 PPTX 内部结构，建立页码到图片文件的映射关系。
"""

import os
import re
import zipfile

NS_REL = 'http://schemas.openxmlformats.org/package/2006/relationships'
NS_PRES = 'http://schemas.openxmlformats.org/presentationml/2006/main'

IMAGE_REL_TYPE = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/image'
SLIDE_REL_TYPE = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide'

PROCESSABLE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.bmp'}


def get_slide_image_map(zip_path):
    """
    解析 PPTX，返回页码到图片文件的映射

    Args:
        zip_path: PPTX 文件路径

    Returns:
        tuple: ({页码: [图片文件名列表]}, 总页数)
    """
    slide_image_map = {}

    with zipfile.ZipFile(zip_path, 'r') as z:
        names = z.namelist()

        # 读取 presentation.xml 获取幻灯片顺序
        pres_rels = _parse_rels(z, 'ppt/_rels/presentation.xml.rels')
        slide_order = _get_slide_order(z, pres_rels)

        if not slide_order:
            # fallback: 按 slideN.xml 文件名排序
            slide_order = _fallback_slide_order(names)

        for page_num, slide_path in enumerate(slide_order, 1):
            rels_path = 'ppt/slides/_rels/' + os.path.basename(slide_path) + '.rels'
            slide_rels = _parse_rels(z, rels_path)

            images = []
            for target in slide_rels.values():
                fname = os.path.basename(target).lower()
                ext = os.path.splitext(fname)[1]
                if ext in PROCESSABLE_EXTENSIONS:
                    images.append(os.path.basename(target))

            slide_image_map[page_num] = images

    return slide_image_map, len(slide_order)


def get_images_for_pages(slide_image_map, page_numbers, media_dir):
    """
    根据指定页码，返回需要处理的去重图片列表

    Args:
        slide_image_map: {页码: [图片文件名列表]}
        page_numbers: set of int, 需要处理的页码
        media_dir: ppt/media 目录路径

    Returns:
        list: 排序后的图片文件名列表
    """
    all_images = set()
    for page in sorted(page_numbers):
        if page in slide_image_map:
            all_images.update(slide_image_map[page])

    # 只保留实际存在且可处理的文件
    existing = set(os.listdir(media_dir)) if os.path.exists(media_dir) else set()
    result = sorted(img for img in all_images
                    if img in existing
                    and os.path.splitext(img.lower())[1] in PROCESSABLE_EXTENSIONS)
    return result


def _parse_rels(z, rels_path):
    """解析 .rels 文件，返回 {rId: Target} 字典"""
    if rels_path not in z.namelist():
        return {}

    content = z.read(rels_path).decode('utf-8')
    rels = {}
    for match in re.finditer(
            r'Target="([^"]+)"[^>]*Id="([^"]+)"'
            r'|Id="([^"]+)"[^>]*Target="([^"]+)"',
            content):
        if match.group(1) and match.group(2):
            rels[match.group(2)] = match.group(1)
        elif match.group(3) and match.group(4):
            rels[match.group(3)] = match.group(4)
    return rels


def _get_slide_order(z, pres_rels):
    """从 presentation.xml 获取幻灯片的真实顺序"""
    if 'ppt/presentation.xml' not in z.namelist():
        return []

    content = z.read('ppt/presentation.xml').decode('utf-8')

    # 提取 sldIdLst 中的 r:id 值
    rids = []
    for match in re.finditer(r'<p:sldId[^>]*r:id="([^"]*)"', content):
        rids.append(match.group(1))

    # 也可匹配带命名空间的格式
    if not rids:
        for match in re.finditer(
                r'<p:sldId[^>]*(?:xmlns:r="[^"]*"[^>]*)?'
                r'(?:r:id|{[^}]*}id)="([^"]*)"', content):
            rids.append(match.group(1))

    if not rids:
        return []

    # 将 rId 映射到 slide 文件路径
    slides = []
    for rid in rids:
        target = pres_rels.get(rid, '')
        if target and ('slide' in target.lower()):
            # 处理相对路径 (../slides/slide1.xml -> ppt/slides/slide1.xml)
            if target.startswith('../'):
                target = 'ppt/' + target[3:]
            elif not target.startswith('ppt/'):
                target = 'ppt/' + target
            slides.append(target)

    return slides


def _fallback_slide_order(names):
    """fallback: 按 slideN.xml 文件名排序"""
    slides = []
    for name in names:
        m = re.match(r'ppt/slides/slide(\d+)\.xml$', name)
        if m:
            slides.append((int(m.group(1)), name))
    slides.sort(key=lambda x: x[0])
    return [s[1] for s in slides]
