#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LaMa AI 模型加载器 - 支持国内镜像
PPT Logo Remover - Model Loader Module

使用清华 TUNA 镜像加速 HuggingFace 模型下载，支持本地缓存。
"""

import os
import sys
import subprocess
from pathlib import Path

# 模型配置
LAMA_MODEL_ID = "esenmgz/simple-lama"

HF_MIRROR = "https://mirrors.tuna.tsinghua.edu.cn/huggingface"


def _has_nvidia_gpu():
    """检测系统是否有 NVIDIA GPU（不依赖 torch）"""
    try:
        result = subprocess.run(['nvidia-smi'], capture_output=True, timeout=5)
        return result.returncode == 0
    except Exception:
        return False


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
    except Exception:
        pass


def get_skill_model_dir():
    """
    获取 skill 内部的模型目录

    Returns:
        Path: skill 的 models 目录路径
    """
    scripts_dir = Path(__file__).parent
    skill_dir = scripts_dir.parent
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


def get_lama_with_fallback(model_dir=None, device=None, verbose=True):
    """
    获取 LaMa 模型实例（支持 skill 本地模型优先）

    Args:
        model_dir: 自定义模型目录（可选）
        device: 运行设备（None=自动检测GPU, 'cpu', 'cuda'）
        verbose: 是否显示详细信息

    Returns:
        SimpleLama: LaMa 模型实例
    """
    # 自动检测 GPU
    if device is None:
        import torch
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        if verbose:
            if device == 'cuda':
                gpu_name = torch.cuda.get_device_name(0)
                print(f"  [OK] 使用设备: {device} ({gpu_name})")
            else:
                print(f"  [OK] 使用设备: {device} (CPU)")
                # 检查是否安装了 CPU 版 torch 但系统有 GPU
                if _has_nvidia_gpu():
                    print(f"  [警告] 检测到 NVIDIA GPU 但 torch 无 CUDA 支持")
                    print(f"  [提示] 请运行 setup.bat 重装 CUDA 版 PyTorch:")

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
