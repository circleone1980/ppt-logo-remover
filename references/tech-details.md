# 技术细节

## SIFT 特征匹配

- **算法**: SIFT (Scale-Invariant Feature Transform)
- **匹配器**: FLANN 快速近似最近邻
- **外点剔除**: RANSAC
- **Lowe's Ratio Test**: 0.7 阈值
- **最少匹配点**: 4 个
- **最小置信度**: 0.3（内点比例）

**优势**: 旋转不变、尺度不变（50%-200% 缩放）、光照鲁棒

## OpenCV Inpainting（默认模式）

- **算法**: Telea 快速行进算法（Fast Marching Method）
- **掩码扩展**: 5px kernel, dilate 2 次
- **修复半径**: 10 像素
- **速度**: ~1秒/图

## LaMa AI（`--ai` 模式）

- **论文**: Safronov et al., "Resolution-robust Large Mask Inpainting with Fourier Convolutions", 2022
- **核心**: Fast Fourier Convolutions 获取更大感受野
- **训练**: 256x256，可处理 ~2K 分辨率
- **模型大小**: ~200MB，首次使用自动下载
- **镜像**: 清华 TUNA 镜像加速
- **速度**: ~3-5秒/图(CPU)，GPU <1秒/图

## 固定位置模式

- **标准尺寸**: 1376x768（NotebookLM 等工具标准输出）
- **默认位置**: 右下角 (1255,725) 到 (1376,768)
- **逐图缩放**: 每张图按自身尺寸等比换算坐标
  - `scale_x = actual_width / 1376`
  - `scale_y = actual_height / 768`
