#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PPT Logo Remover - Core Library
"""

from .utils import (
    DEFAULT_LOGO_X1,
    DEFAULT_LOGO_Y1,
    DEFAULT_LOGO_X2,
    DEFAULT_LOGO_Y2,
    SAMPLE_MARGIN,
    SIFT_MIN_MATCHES,
    SIFT_RATIO_THRESHOLD,
    SIFT_MIN_CONFIDENCE,
    generate_output_path,
    parse_logo_pos,
    parse_pages_spec,
    get_image_files,
)

from .locator import (
    detect_logo_sift,
    find_logo_in_image,
)

from .inpainting import (
    get_lama_model,
    remove_logo_inpaint,
)

from .pptx_processor import (
    process_pptx,
)

from .model_loader import (
    setup_hf_mirror,
    get_skill_model_dir,
    get_local_model_path,
    download_model_to_skill,
    ensure_model_downloaded,
)

from .slide_mapper import (
    get_slide_image_map,
    get_images_for_pages,
)

__all__ = [
    # Constants
    'DEFAULT_LOGO_X1',
    'DEFAULT_LOGO_Y1',
    'DEFAULT_LOGO_X2',
    'DEFAULT_LOGO_Y2',
    'SAMPLE_MARGIN',
    'SIFT_MIN_MATCHES',
    'SIFT_RATIO_THRESHOLD',
    'SIFT_MIN_CONFIDENCE',
    # Utils
    'generate_output_path',
    'parse_logo_pos',
    'parse_pages_spec',
    'get_image_files',
    # Locator
    'detect_logo_sift',
    'find_logo_in_image',
    # Inpainting
    'get_lama_model',
    'remove_logo_inpaint',
    # Processor
    'process_pptx',
    # Model Loader
    'setup_hf_mirror',
    'get_skill_model_dir',
    'get_local_model_path',
    'download_model_to_skill',
    'ensure_model_downloaded',
    # Slide Mapper
    'get_slide_image_map',
    'get_images_for_pages',
]

__version__ = '5.0.0'
