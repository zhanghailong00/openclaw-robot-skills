---
name: vision-detect
description: YOLO 目标检测：拍照 + NPU 推理，返回物体像素坐标。当用户提到检测物体、识别餐品、拍照、看看桌上有什么时使用。即使用户没有明确说"检测"，只要涉及"看到"、"识别"、"位置"，也应该触发。
allowed-tools: [exec]
---

# vision-detect

摄像头拍照，去畸变后用 YOLO 检测物体，输出像素坐标。检测类别：汉堡、可乐、盘子、薯条。

## 脚本目录

`/home/HwHiAiUser/.openclaw/workspace/skills/vision-detect/scripts/`

## 脚本列表

### 01_check_camera.py — 测试摄像头（只读）

```bash
python3 /home/HwHiAiUser/.openclaw/workspace/skills/vision-detect/scripts/01_check_camera.py
```

参数：无
用途：检查摄像头是否正常，能否采集和去畸变

### 02_run_detection.py — YOLO 目标检测（只读）

```bash
python3 /home/HwHiAiUser/.openclaw/workspace/skills/vision-detect/scripts/02_run_detection.py
```

参数：无
用途：拍照 → 去畸变 → YOLO 检测 → 输出检测结果 JSON

输出示例：
```json
{
  "detections": [
    {"class": "hanbao", "label": "汉堡", "confidence": 0.92, "cx": 240.0, "cy": 185.0, "xmin": 200.0, "ymin": 150.0, "xmax": 280.0, "ymax": 220.0},
    {"class": "panzi", "label": "盘子", "confidence": 0.94, "cx": 387.8, "cy": 118.1, "xmin": 334.5, "ymin": 60.6, "xmax": 441.0, "ymax": 175.7}
  ],
  "count": 2,
  "status": "ok"
}
```

## 输出字段说明

| 字段 | 含义 |
|------|------|
| class | 物体类别英文名（hanbao/cola/panzi/shutiao） |
| label | 物体类别中文名 |
| confidence | 置信度 0~1 |
| cx, cy | 检测框中心像素坐标 |
| xmin, ymin, xmax, ymax | 检测框像素坐标 |

## 使用规则

1. 输出的 cx, cy 可直接传给 `coord-transform` 的 `02_convert.py --px cx --py cy` 做坐标转换
2. 工作台上没东西时 count=0，属于正常
3. 每次调用会初始化 NPU，耗时约 3-5 秒
4. 拿到 cx, cy 后传给 `coord-transform` 的 `02_convert.py --px cx --py cy --json` 做坐标转换
