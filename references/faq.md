# 常见问题

## 模板匹配找不到 logo？

1. logo 截图不清晰或包含过多背景 → 重新截取仅包含 logo 的区域
2. logo 旋转过大 → SIFT 支持旋转，但过大会降低精度
3. logo 颜色与背景接近 → 改用固定位置模式 `--logo-pos`

## Logo 没被完全移除？

- 模板匹配模式：检查匹配置信度（加 `-v` 查看），低于 0.6 可能定位不准
- 固定位置模式：用 `--logo-pos` 扩大移除区域

## 移除后有明显痕迹？

- 默认模式对渐变/复杂背景效果有限
- 尝试 `--ai` 模式，LaMa 对复杂背景修复效果更好

## 报错 "无效的 PPTX 文件"？

- 用 PowerPoint/WPS 重新保存为 PPTX 格式
- 确认文件可以正常打开

## 依赖缺失？

```bash
# 重新运行 setup
bash setup.sh    # Linux/macOS
setup.bat        # Windows

# 或手动安装
pip install Pillow numpy opencv-python
```

## GPU 加速

```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```
