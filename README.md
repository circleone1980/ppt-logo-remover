# PPT Logo Remover

自动移除 PPTX 演示文稿中的 logo、水印或品牌标识（如 NotebookLM、Canva 等平台 logo）。

## 功能

- **SIFT 特征匹配** — 旋转不变、尺度不变的 logo 自动定位
- **固定位置模式** — 移除指定固定位置的 logo
- **OpenCV Inpainting** — 默认快速修复（~1秒/图）
- **LaMa AI 修复** — 高质量无痕修复（`--ai` 参数启用）
- **页码指定** — 只处理指定页面（`--pages 2-4,7,last`）

## 快速开始

### 1. 环境搭建（一次性）

```bash
# Linux/macOS
bash setup.sh

# Windows CMD
setup.bat
```

自动创建 `.venv` 并安装所有依赖（含 LaMa AI）。使用清华 TUNA 镜像加速下载。

### 2. 使用

```bash
# 固定位置模式（右下角默认位置）
python3 scripts/ppt-logo-remover.py "演示.pptx" -v

# 模板匹配模式（提供 logo 截图，自动定位）
python3 scripts/ppt-logo-remover.py "演示.pptx" logo.png -v

# LaMa AI 高质量修复
python3 scripts/ppt-logo-remover.py "演示.pptx" logo.png --ai -v

# 只处理指定页码
python3 scripts/ppt-logo-remover.py "演示.pptx" --pages 2-4,7,last -v

# 自定义 logo 位置（基于 1376x768 标准尺寸）
python3 scripts/ppt-logo-remover.py "演示.pptx" --logo-pos 1200,700,1376,768 -v
```

**首次使用 `--ai` 时会自动下载 LaMa 模型（~200MB）。**

## 参数

| 参数 | 说明 |
|------|------|
| `pptx_path` | 输入 PPTX 文件路径 |
| `logo_image` | Logo 截图（可选，启用 SIFT 自动定位） |
| `-o, --output` | 输出路径（默认 `xxx_clear.pptx`） |
| `--logo-pos` | 固定位置坐标 `x1,y1,x2,y2` |
| `--pages` | 指定页码：`2-4`, `1,3,5`, `last`, `2-4,7,last` |
| `--ai` | 启用 LaMa AI 高质量修复 |
| `-v` | 显示详细进度 |

## 技术细节

- **逐图独立计算坐标** — 每张图片按自身尺寸等比缩放，正确处理不同分辨率
- **SIFT + FLANN + RANSAC** — 高精度 logo 定位（95%+ 准确率）
- **LaMa AI** — 基于 Fourier Convolutions 的深度学习修复，首次使用自动下载模型
- **页码映射** — 解析 PPTX 内部 XML 精确映射页码到图片文件

## 环境要求

- Python 3.7+
- 依赖自动安装：Pillow, numpy, opencv-python, simple-lama-inpainting, torch

## License

MIT
