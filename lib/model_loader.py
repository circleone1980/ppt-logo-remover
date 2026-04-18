#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LaMa AI 模型加载器 - 支持国内镜像
PPT Logo Remover - Model Loader Module

使用清华 TUNA 镜像加速 HuggingFace 模型下载，支持本地缓存。
"""

import os
import sys
from pathlib import Path

# 模型配置
LAMA_MODEL_ID = "esenmgz/simple-lama"
LAMA_MODEL_FILES = ["big-lama.pt", "best.ckpt"]  # 主要模型文件（.pt 是 PyTorch 格式）

# 清华 TUNA HuggingFace 镜像
HF_MIRROR = "https://mirrors.tuna.tsinghua.edu.cn/huggingface"


def setup_hf_mirror():
    """
    设置 HuggingFace 镜像环境变量（优先使用清华 TUNA 镜像）

    这会在当前进程和子进程中生效，加速模型下载。
    """
    # 设置 HuggingFace 镜像
    os.environ['HF_ENDPOINT'] = HF_MIRROR

    # 可选：使用 huggingface-cli 配置（如果已安装）
    try:
        import subprocess
        subprocess.run(
            [sys.executable, '-m', 'huggingface_hub', 'cli', 'set-endpoint', HF_MIRROR],
            capture_output=True,
            timeout=5
        )
    except:
        pass  # 忽略 huggingface-cli 未安装的情况


def get_skill_model_dir():
    """
    获取 skill 内部的模型目录

    Returns:
        Path: skill 的 models 目录路径
    """
    # 获取本文件的目录（lib/）
    lib_dir = Path(__file__).parent
    # skill 根目录
    skill_dir = lib_dir.parent
    # models 目录
    model_dir = skill_dir / 'models'
    return model_dir


def get_local_model_path():
    """
    获取本地缓存的模型路径

    Returns:
        Path or None: 模型文件路径，如果不存在则返回 None
    """
    model_dir = get_skill_model_dir()
    if not model_dir.exists():
        return None

    # 查找模型文件（包括 .pt 格式）
    for pattern in ['*.pt', '*.ckpt', '*.pth', '*.safetensors']:
        matches = list(model_dir.glob(pattern))
        if matches:
            return matches[0]

    return None


def download_model_to_skill(verbose=True):
    """
    下载 LaMa 模型到 skill 内部（使用清华镜像）

    Args:
        verbose: 是否显示下载进度

    Returns:
        Path: 下载后的模型文件路径
    """
    setup_hf_mirror()

    # 创建模型目录
    model_dir = get_skill_model_dir()
    model_dir.mkdir(parents=True, exist_ok=True)

    if verbose:
        print(f"  [使用清华镜像] 正在下载 LaMa AI 模型...")
        print(f"  镜像源: {HF_MIRROR}")

    # 使用 huggingface_hub 下载
    try:
        from huggingface_hub import snapshot_download

        # 下载模型到 skill 的 models 目录
        model_path = snapshot_download(
            repo_id=LAMA_MODEL_ID,
            local_dir=str(model_dir),
            local_dir_use_symlinks=False,
            resume_download=True,
        )

        if verbose:
            print(f"  [OK] 模型下载完成: {model_path}")

        return Path(model_path)

    except ImportError:
        # 首次使用 AI 模式，安装依赖
        import subprocess
        if verbose:
            print("  [首次使用 AI 模式] 正在安装 simple-lama-inpainting...")

        # 使用清华 PyPI 镜像 + --no-deps（Pillow 已通过 conda 安装）
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', 'simple-lama-inpainting',
            '-i', 'https://pypi.tuna.tsinghua.edu.cn/simple',
            '--no-deps', '-q'
        ])
    except Exception as e:
        if verbose:
            print(f"  警告: 模型下载失败 - {e}")
        return None


def get_lama_with_fallback(model_dir=None, device='cpu', verbose=True):
    """
    获取 LaMa 模型实例（支持 skill 本地模型优先）

    Args:
        model_dir: 自定义模型目录（可选）
        device: 运行设备 ('cpu' 或 'cuda')
        verbose: 是否显示详细信息

    Returns:
        SimpleLama: LaMa 模型实例
    """
    # 首先检查本地模型，通过 LAMA_MODEL 环境变量传递给 SimpleLama
    local_model = get_local_model_path()
    if local_model:
        os.environ['LAMA_MODEL'] = str(local_model)
        try:
            if verbose:
                print("  [OK] 使用本地缓存的模型")
            from simple_lama_inpainting import SimpleLama
            return SimpleLama(device=device)
        except Exception as e:
            if verbose:
                print(f"  警告: 本地模型加载失败，尝试在线下载 - {e}")
            os.environ.pop('LAMA_MODEL', None)

    # 降级到在线下载（使用镜像）
    try:
        from simple_lama_inpainting import SimpleLama
        return SimpleLama(device=device)
    except ImportError:
        # 首次使用，安装依赖
        import subprocess
        if verbose:
            print("  [首次使用 AI 模式] 正在安装 simple-lama-inpainting...")
        setup_hf_mirror()  # 设置镜像后再安装
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'simple-lama-inpainting', '-q'])
        from simple_lama_inpainting import SimpleLama
        return SimpleLama(device=device)


def ensure_model_downloaded(verbose=True):
    """
    确保 LaMa 模型已下载到 skill 内部

    这可以避免首次使用时等待下载。
    注意：LaMa 使用 PyTorch hub 缓存 (~/.cache/torch/hub/checkpoints/)，
    本地 models 目录用于备份和离线部署。

    Args:
        verbose: 是否显示详细信息

    Returns:
        bool: 模型是否已存在或下载成功
    """
    # 检查 PyTorch hub 缓存（LaMa 实际使用的位置）
    torch_cache = Path.home() / '.cache' / 'torch' / 'hub' / 'checkpoints' / 'big-lama.pt'
    skill_model = get_local_model_path()

    if torch_cache.exists():
        if verbose:
            print("  [OK] LaMa 模型已就绪（PyTorch 缓存）")
        return True

    if skill_model:
        if verbose:
            print("  [OK] LaMa 模型已缓存（skill 目录）")
        return True

    if verbose:
        print("  [首次使用] 正在初始化 LaMa AI 模型...")

    # 让 SimpleLama 自己处理下载（它使用 PyTorch hub）
    try:
        from simple_lama_inpainting import SimpleLama
        SimpleLama()  # 触发下载
        if verbose:
            print("  [OK] LaMa 模型初始化完成")
        return True
    except Exception as e:
        if verbose:
            print(f"  警告: 模型初始化失败 - {e}")
        return False


if __name__ == '__main__':
    # 测试：下载模型到 skill
    print("测试模型下载...")
    setup_hf_mirror()
    print(f"HF_ENDPOINT = {os.environ.get('HF_ENDPOINT')}")

    success = ensure_model_downloaded(verbose=True)
    if success:
        print("\n模型下载成功！")
        print(f"模型位置: {get_local_model_path()}")
    else:
        print("\n模型下载失败！")
