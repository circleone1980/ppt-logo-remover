#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PPT Logo Remover - CLI 入口点
移除 PPTX 文件中的 logo/水印/品牌标识

支持两种模式:
1. 模板匹配模式：根据提供的 logo 截图使用 SIFT 自动定位
2. 固定位置模式：移除右下角固定位置的 logo

支持两种修复方法:
1. 默认模式：OpenCV Inpainting（快速、轻量）
2. AI 模式：LaMa AI（高质量，需 --ai 参数）

支持指定页码 (--pages):
  --pages 2-4        只处理第2到4页
  --pages 1,3,5      只处理第1、3、5页
  --pages last       只处理最后一页
  --pages 2-4,7,last 混合指定
  不传则处理全部页面

Usage:
    # 模板匹配 + 默认修复
    python3 ppt-logo-remover.py "演示.pptx" "logo.png" -v

    # 模板匹配 + AI 高质量修复
    python3 ppt-logo-remover.py "演示.pptx" "logo.png" --ai -v

    # 固定位置模式
    python3 ppt-logo-remover.py "演示.pptx" -v

    # 只处理特定页码
    python3 ppt-logo-remover.py "演示.pptx" --pages 2-4 -v
    python3 ppt-logo-remover.py "演示.pptx" --pages last -v
"""

import sys
import os
import argparse
from pathlib import Path

# 添加 lib 目录到 Python 路径
script_path = Path(__file__).resolve()
script_root = script_path.parent.parent  # 技能根目录
sys.path.insert(0, str(script_root))

# 从当前工作目录解析（备用）
cwd = Path.cwd()
if (cwd / 'lib').exists():
    sys.path.insert(0, str(cwd))


def setup_python_path():
    """设置 Python 路径，优先使用 venv 中的包"""
    venv_dir = script_root / '.venv'

    if sys.platform == 'win32':
        site_packages = venv_dir / 'Lib' / 'site-packages'
    else:
        py_version = f'python{sys.version_info.major}.{sys.version_info.minor}'
        site_packages = venv_dir / 'lib' / py_version / 'site-packages'

    if site_packages.exists():
        sys.path.insert(0, str(site_packages))
        return True
    return False


def ensure_dependencies():
    """确保所需依赖已安装（回退方案）"""
    deps = {
        'PIL': 'Pillow',
        'numpy': 'numpy',
        'cv2': 'opencv-python',
    }

    import subprocess

    for module, package in deps.items():
        try:
            __import__(module)
        except ImportError:
            print(f"正在安装 {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package, '-q'])


# 优先使用 venv，失败则运行时安装
venv_ok = setup_python_path()
if not venv_ok:
    ensure_dependencies()

from lib.utils import (
    DEFAULT_LOGO_X1, DEFAULT_LOGO_Y1, DEFAULT_LOGO_X2, DEFAULT_LOGO_Y2,
    generate_output_path, parse_logo_pos
)
from lib.pptx_processor import process_pptx


def main():
    parser = argparse.ArgumentParser(
        description='PPT Logo Remover - 移除 PPTX 文件中的 logo/水印',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  # 模板匹配模式（推荐）：提供 logo 截图，自动定位并移除
  %(prog)s 演示.pptx logo.png -v

  # 模板匹配 + AI 高质量修复（LaMa）
  %(prog)s 演示.pptx logo.png --ai -v

  # 固定位置模式：使用默认位置（右下角）
  %(prog)s 演示.pptx -v

  # 自定义 logo 位置
  %(prog)s 演示.pptx --logo-pos 1200,700,1376,768 -v

  # 指定输出路径
  %(prog)s 演示.pptx logo.png -o 输出/干净版.pptx

  # 只处理特定页码
  %(prog)s 演示.pptx --pages 2-4 -v
  %(prog)s 演示.pptx --pages 1,3,5 -v
  %(prog)s 演示.pptx --pages last -v
  %(prog)s 演示.pptx --pages 2-4,7,last -v
        '''
    )

    parser.add_argument('pptx_path', help='输入的 PPTX 文件路径', type=Path)
    parser.add_argument('logo_image', nargs='?', default=None,
                        help='Logo 截图路径（提供此参数将启用 SIFT 自动定位）', type=Path)
    parser.add_argument('-o', '--output', dest='output_path', default=None,
                        help='输出文件路径（默认在输入文件同目录生成 xxx_clear.pptx）')
    parser.add_argument('--logo-pos', dest='logo_pos', default=None,
                        help='Logo 位置，格式：x1,y1,x2,y2（基于 1376x768 标准尺寸）')
    parser.add_argument('--pages', dest='pages', default=None,
                        help='指定处理的页码，支持格式: 2-4, 1,3,5, last, 2-4,7,last')
    parser.add_argument('-v', '--verbose', action='store_true', help='显示详细处理进度')
    parser.add_argument('--ai', '--use-lama', dest='use_ai', action='store_true',
                        help='使用 LaMa AI 高质量修复（需下载模型，效果更好但速度较慢）')

    args = parser.parse_args()

    # 转换为 Path 对象
    input_path = Path(args.pptx_path).expanduser().resolve()
    output_path = Path(args.output_path) if args.output_path else None
    logo_image = Path(args.logo_image).expanduser() if args.logo_image else None

    # 验证输入文件
    if not input_path.exists():
        print(f"错误：输入文件不存在 - {input_path}")
        sys.exit(1)

    # 验证 logo 文件（如果提供）
    if logo_image and not logo_image.exists():
        print(f"错误：Logo 文件不存在 - {logo_image}")
        sys.exit(1)

    # 确定输出路径
    if output_path is None:
        output_path = Path(generate_output_path(str(input_path)))
    else:
        output_path = Path(output_path).expanduser().resolve()

    # 确保输出目录存在
    output_dir = output_path.parent
    if output_dir and not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)

    # 解析 logo 位置
    logo_coords = None
    if args.logo_pos:
        logo_coords = parse_logo_pos(args.logo_pos)
        if not logo_coords:
            print(f"错误：无效的 logo 位置格式 - {args.logo_pos}")
            print("请使用格式：x1,y1,x2,y2（例如：1255,725,1376,768）")
            sys.exit(1)
    else:
        logo_coords = (DEFAULT_LOGO_X1, DEFAULT_LOGO_Y1, DEFAULT_LOGO_X2, DEFAULT_LOGO_Y2)

    # 显示配置信息
    if args.verbose:
        print("=" * 50)
        print("PPT Logo 移除工具 v5.0")
        print("=" * 50)
        print(f"输入：  {input_path}")
        print(f"输出：  {output_path}")
        if logo_image:
            print(f"模式：  模板匹配（SIFT 自动定位）")
            print(f"Logo 模板：{logo_image}")
        else:
            print(f"模式：  固定位置")
            print(f"Logo 位置：({logo_coords[0]},{logo_coords[1]}) - ({logo_coords[2]},{logo_coords[3]})")

        if args.pages:
            print(f"页码：  {args.pages}")
        else:
            print(f"页码：  全部页面")

        if args.use_ai:
            print(f"修复：  LaMa AI 高质量模式")
        else:
            print(f"修复：  OpenCV Inpainting（默认）")

        print("=" * 50)
        print()

    # 处理文件
    try:
        process_pptx(
            str(input_path),
            str(output_path),
            logo_template=str(logo_image) if logo_image else None,
            logo_coords=logo_coords,
            use_ai=args.use_ai,
            verbose=args.verbose,
            pages=args.pages
        )
        size_mb = output_path.stat().st_size / 1024 / 1024
        print(f"\n完成！输出文件：{output_path}")
        print(f"文件大小：{size_mb:.1f} MB")
    except Exception as e:
        print(f"\n错误：处理失败 - {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
