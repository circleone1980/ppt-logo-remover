#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Logo 定位模块
PPT Logo Remover - Locator Module

使用 SIFT 特征匹配或模板匹配在图像中定位 logo 位置。
"""

import numpy as np
from PIL import Image
import cv2

from utils import SIFT_MIN_MATCHES, SIFT_RATIO_THRESHOLD


def detect_logo_sift(img, logo_template):
    """
    使用 SIFT 特征匹配定位 logo

    Args:
        img: PIL.Image - 待搜索的图像
        logo_template: PIL.Image - logo 模板图像

    Returns:
        tuple: ((x1, y1, x2, y2), confidence) 或 None（未检测到）
    """
    # 转换为灰度图
    img_gray = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)
    logo_gray = cv2.cvtColor(np.array(logo_template), cv2.COLOR_RGB2GRAY)

    # 初始化 SIFT
    sift = cv2.SIFT_create()

    # 检测关键点和计算描述符
    kp1, des1 = sift.detectAndCompute(logo_gray, None)
    kp2, des2 = sift.detectAndCompute(img_gray, None)

    if des1 is None or des2 is None or len(kp1) < SIFT_MIN_MATCHES or len(kp2) < SIFT_MIN_MATCHES:
        return None

    # FLANN 参数
    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)

    # 使用 FLANN 匹配器
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(des1, des2, k=2)

    # 应用比率测试（Lowe's ratio test）
    good_matches = []
    for m, n in matches:
        if m.distance < SIFT_RATIO_THRESHOLD * n.distance:
            good_matches.append(m)

    # 需要至少 4 个匹配点
    if len(good_matches) < SIFT_MIN_MATCHES:
        return None

    # 提取匹配点坐标
    src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
    dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

    # 计算 Homography 矩阵
    M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

    if M is None:
        return None

    # 获取 logo 模板的四个角点
    h, w = logo_gray.shape
    logo_corners = np.float32([[0, 0], [w-1, 0], [w-1, h-1], [0, h-1]]).reshape(-1, 1, 2)

    # 变换到图像坐标系
    transformed_corners = cv2.perspectiveTransform(logo_corners, M)

    # 计算边界框
    x_coords = [int(pt[0][0]) for pt in transformed_corners]
    y_coords = [int(pt[0][1]) for pt in transformed_corners]

    x1, x2 = max(0, min(x_coords)), min(img.width, max(x_coords))
    y1, y2 = max(0, min(y_coords)), min(img.height, max(y_coords))

    # 计算置信度（基于内点比例）
    inlier_count = np.sum(mask)
    inlier_ratio = inlier_count / len(good_matches) if len(good_matches) > 0 else 0
    confidence = float(inlier_ratio)

    return (x1, y1, x2, y2), confidence


def find_logo_in_image(img, logo_template):
    """
    在图像中查找 logo 位置

    Args:
        img: PIL.Image - 待搜索的图像
        logo_template: PIL.Image - logo 模板

    Returns:
        tuple: (x1, y1, x2, y2) 或 None（未找到）
    """
    if logo_template is not None:
        result = detect_logo_sift(img, logo_template)
        if result:
            (x1, y1, x2, y2), confidence = result
            margin = 5
            x1 = max(0, x1 - margin)
            y1 = max(0, y1 - margin)
            x2 = min(img.width, x2 + margin)
            y2 = min(img.height, y2 + margin)
            return (x1, y1, x2, y2)

    return None
