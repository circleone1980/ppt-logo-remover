#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
MIRROR="-i https://pypi.tuna.tsinghua.edu.cn/simple"

echo "========================================"
echo "PPT Logo Remover v5.0 - Setup"
echo "========================================"

# Check for existing venv
if [ -f "$VENV_DIR/Scripts/python.exe" ] || [ -f "$VENV_DIR/bin/python" ]; then
    echo "Virtual environment already exists: $VENV_DIR"
    echo "Delete .venv directory to rebuild."
else
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    echo "Done."
fi

# Determine pip/python paths (Windows Git Bash vs Unix)
if [ -f "$VENV_DIR/Scripts/pip.exe" ]; then
    PIP="$VENV_DIR/Scripts/pip.exe"
    PYTHON="$VENV_DIR/Scripts/python.exe"
elif [ -f "$VENV_DIR/bin/pip" ]; then
    PIP="$VENV_DIR/bin/pip"
    PYTHON="$VENV_DIR/bin/python"
else
    echo "Error: pip not found in venv"
    exit 1
fi

echo "Upgrading pip..."
"$PYTHON" -m pip install --upgrade pip -q

echo "Installing dependencies (Pillow, numpy, opencv-python)..."
"$PIP" install -r "$SCRIPT_DIR/requirements.txt" $MIRROR

echo ""
echo "Detecting GPU..."
if command -v nvidia-smi &>/dev/null; then
    echo "[OK] NVIDIA GPU detected, installing CUDA PyTorch..."
    "$PIP" install torch torchvision --index-url https://download.pytorch.org/whl/cu126
else
    echo "[--] No NVIDIA GPU detected, installing CPU PyTorch..."
    "$PIP" install torch torchvision $MIRROR
fi

echo ""
echo "Installing simple-lama-inpainting..."
"$PIP" install simple-lama-inpainting $MIRROR

echo ""
echo "========================================"
echo "Setup complete!"
echo ""
echo "  venv: $VENV_DIR"
echo ""
echo "  Quick start:"
echo "    $PYTHON scripts/ppt-logo-remover.py demo.pptx -v"
echo "========================================"
