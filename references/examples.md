# 使用示例

## 移除 NotebookLM logo

```bash
# 从 PPT 任意一页截取 logo 保存为 logo.png
python3 scripts/ppt-logo-remover.py "演示.pptx" logo.png -v
```

## 移除已知固定位置的 logo

```bash
# 默认右下角
python3 scripts/ppt-logo-remover.py "演示.pptx" -v

# 自定义位置
python3 scripts/ppt-logo-remover.py "演示.pptx" --logo-pos 1200,700,1376,768 -v
```

## AI 高质量修复

```bash
python3 scripts/ppt-logo-remover.py "演示.pptx" logo.png --ai -v
```

## 指定页码

```bash
python3 scripts/ppt-logo-remover.py "演示.pptx" --pages 2-4 -v
python3 scripts/ppt-logo-remover.py "演示.pptx" --pages 1,3,5 -v
python3 scripts/ppt-logo-remover.py "演示.pptx" --pages last -v
python3 scripts/ppt-logo-remover.py "演示.pptx" --pages 2-4,7,last -v
```

## 批量处理

```bash
for f in *.pptx; do
    python3 scripts/ppt-logo-remover.py "$f" logo.png -v
done
```

## 处理 Canva 导出

```bash
python3 scripts/ppt-logo-remover.py "canva-design.pptx" canva-logo.png -v
```

## 自定义输出路径

```bash
python3 scripts/ppt-logo-remover.py "演示.pptx" logo.png -o "cleaned/演示.pptx" -v
```
