---
name: arm-delivery
description: 完整送餐流程：视觉检测 → 抓取 → 传送带运输 → 放置。当用户提到送餐、放到盘子里、抓取并运输时使用。即使用户没有明确说"送餐"，只要涉及"把X放到Y"、"夹起来运走"，也应该触发此流程参考。
allowed-tools: [exec]
---

# arm-delivery

送餐流程的参考文档。**不要直接调用 01_workflow.py**，龙虾应该根据下面的步骤，自己调用各个 Skill 完成送餐。

## 送餐步骤概览

| 步骤 | 调用 Skill | 做什么 |
|------|-----------|--------|
| 1 | vision-detect | 检测餐品和盘子位置，拿到像素坐标 cx, cy |
| 2 | coord-transform | 把像素坐标转换为机械臂坐标 arm_target |
| 3 | arm-basic | 归零 → 开爪 → 移到目标上方 → 下降 → 夹取 → 抬起 |
| 4 | coord-transform + arm-basic | 转换传送带坐标 → 移到传送带 → 松开 |
| 5 | conveyor-belt | 等物体到位 → 启动传送带 → 等到达末端 → 停止 |
| 6 | arm-basic | 从传送带末端取餐 |
| 7 | coord-transform + arm-basic | 转换盘子坐标 → 移到盘子 → 松开 |
| 8 | arm-basic | 归零 |

## 关键参数

| 参数 | 像素坐标 | 机械臂坐标 | 说明 |
|------|---------|-----------|------|
| 传送带起始端 | (405, 220) | **(215.0, 69.9, -31.2)** | 可直接传给 move_to |
| 传送带末端 | (255, 231) | **(209.8, -80.0, -31.2)** | 可直接传给 move_to |

| 参数 | 值 | 说明 |
|------|-----|------|
| 物体高度 | 25mm | object.yaml 中的 height |
| 安全悬停高度 | Z+25mm | 下降前先悬停 |
| 抬起高度 | Z+25mm | 抓取后抬起 |

**重要：传送带坐标是机械臂坐标，可直接传给 move_to，无需转换！**

## 详细步骤

完整命令参见：[references/delivery-steps.md](references/delivery-steps.md)
