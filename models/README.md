# LaMa AI 模型目录

本目录用于缓存 LaMa AI 模型文件，避免首次使用时等待下载。

## 模型信息

- **模型**: LaMa (Resolution-robust Large Mask Inpainting)
- **来源**: [esenmgz/simple-lama](https://huggingface.co/esenmgz/simple-lama)
- **大小**: ~200MB
- **用途**: 高质量无痕修复（通过 `--ai` 参数启用）

## 自动下载

首次使用 `--ai` 参数时，模型会自动下载到此目录。

## 手动下载

如需预先下载模型，可运行：

```bash
python3 -c "from lib.model_loader import ensure_model_downloaded; ensure_model_downloaded()"
```

## 国内镜像

下载时会自动使用**清华大学 TUNA 镜像**加速：

```
https://mirrors.tuna.tsinghua.edu.cn/huggingface
```

## 文件说明

- `best.ckpt` - LaMa 模型权重文件
- `config.json` - 模型配置文件（可选）

## 离线使用

模型下载一次后，可完全离线使用。模型缓存在此目录中，不会随 skill 更新而丢失。
