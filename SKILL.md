---
name: ppt-logo-remover
description: 移除 PPTX 中的 logo/水印/品牌标识。当用户提到 PPT 有 logo 需要移除、清理水印、去掉品牌标识、NotebookLM/Canva/Gamma 平台 logo 时必须使用此技能。即使没有明确说"logo"，只要涉及 PPT 清理品牌痕迹、去掉平台标识、清理模板水印，都应触发。
---

# PPT Logo 移除工具

## 何时使用

- PPT 中有 logo/水印/品牌标识需要移除
- NotebookLM、Canva、Gamma 等 AI 工具生成的 PPT 需要清理平台标识
- 模板网站下载的 PPT 需要移除作者水印
- 用户提供了 logo 截图和 PPT 文件
- 批量移除多个 PPT 中的 logo

## 快速开始

```bash
# 固定位置模式（默认右下角）
python3 scripts/ppt-logo-remover.py "演示.pptx" -v

# 模板匹配模式（提供 logo 截图，自动定位）
python3 scripts/ppt-logo-remover.py "演示.pptx" logo.png -v

# LaMa AI 高质量修复
python3 scripts/ppt-logo-remover.py "演示.pptx" logo.png --ai -v
```

输出：`演示_clear.pptx`

## 参数

| 参数 | 说明 |
|------|------|
| `pptx_path` | 输入 PPTX 文件 |
| `logo_image` | Logo 截图（可选，启用 SIFT 自动定位） |
| `-o, --output` | 输出路径（默认 `xxx_clear.pptx`） |
| `--logo-pos x1,y1,x2,y2` | 固定位置坐标（基于 1376x768，自动缩放） |
| `--pages 2-4,7,last` | 指定页码 |
| `--ai` | LaMa AI 高质量修复（首次自动下载模型 ~200MB） |
| `-v` | 详细进度 |

## 修复模式

| | 默认（OpenCV） | AI（LaMa） |
|---|---|---|
| 启用 | 默认 | `--ai` |
| 效果 | 快速，轻微痕迹 | 近乎无痕 |
| 速度 | ~1秒/图 | ~3-5秒/图(CPU) |
| 首次使用 | 即用 | 下载模型 ~200MB |

## 处理流程

1. 解压 PPTX（本质是 ZIP）
2. 提取 `ppt/media/` 下所有图片
3. **逐图独立计算** logo 坐标（SIFT 检测或按实际尺寸缩放）
4. Inpainting 修复每张图片
5. 重新打包 PPTX

## 注意事项

- 文件名中避免中文和英文之间有空格
- Logo 截图建议用 PNG，仅包含 logo 本身
- 坐标基于 1376x768 标准尺寸，脚本会自动按比例缩放到每张图的实际分辨率
- 算法细节见 `references/tech-details.md`，常见问题见 `references/faq.md`，更多示例见 `references/examples.md`

## 环境要求

- Python 3.7+
- 首次使用运行 `bash setup.sh`（Linux/macOS）或 `setup.bat`（Windows）
- 自动安装依赖并创建虚拟环境
