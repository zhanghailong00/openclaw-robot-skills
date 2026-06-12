# 送餐详细步骤

本文档包含送餐流程的完整命令。SKILL.md 中只有概览，详细执行步骤在这里。

## 步骤 3：抓取物体

用步骤 2 拿到的 arm_target 坐标（设为 ax, ay, az）执行抓取：

```bash
# 归零
python3 /home/HwHiAiUser/.openclaw/workspace/skills/arm-basic/scripts/02_homing.py

# 打开夹爪
python3 /home/HwHiAiUser/.openclaw/workspace/skills/arm-basic/scripts/03_gripper.py --action open

# 移动到目标上方（az + 25mm 悬停）
python3 /home/HwHiAiUser/.openclaw/workspace/skills/arm-basic/scripts/04_move_to.py --x 154.6 --y -50.6 --z -6.2

# 下降到目标
python3 /home/HwHiAiUser/.openclaw/workspace/skills/arm-basic/scripts/04_move_to.py --x 154.6 --y -50.6 --z -31.2

# 夹取
python3 /home/HwHiAiUser/.openclaw/workspace/skills/arm-basic/scripts/03_gripper.py --action close

# 抬起（az + 50mm）
python3 /home/HwHiAiUser/.openclaw/workspace/skills/arm-basic/scripts/04_move_to.py --x 154.6 --y -50.6 --z 18.8
```

注意：上面的坐标是示例，实际值从步骤 2 的 arm_target 取得。az+25 和 az+50 是在 arm_target.z 基础上加 25mm 和 50mm。

## 步骤 4：放到传送带

传送带起始端机械臂坐标：**(215.0, 69.9, -31.2)**，可直接传给 move_to。

```bash
# 移动到传送带起始端上方（-31.2 + 25 = -6.2mm 悬停）
python3 /home/HwHiAiUser/.openclaw/workspace/skills/arm-basic/scripts/04_move_to.py --x 215.0 --y 69.9 --z -6.2

# 下降到传送带（Z = -31.2mm）
python3 /home/HwHiAiUser/.openclaw/workspace/skills/arm-basic/scripts/04_move_to.py --x 215.0 --y 69.9 --z -31.2

# 松开
python3 /home/HwHiAiUser/.openclaw/workspace/skills/arm-basic/scripts/03_gripper.py --action open

# 抬起（-31.2 + 25 = -6.2mm）
python3 /home/HwHiAiUser/.openclaw/workspace/skills/arm-basic/scripts/04_move_to.py --x 215.0 --y 69.9 --z -6.2

# 移到安全位
python3 /home/HwHiAiUser/.openclaw/workspace/skills/arm-basic/scripts/04_move_to.py --x 150 --y 0 --z 80
```

## 步骤 5：传送带运输

```bash
# 等物体到位
python3 /home/HwHiAiUser/.openclaw/workspace/skills/conveyor-belt/scripts/04_wait_object_at_start.py

# 启动传送带
python3 /home/HwHiAiUser/.openclaw/workspace/skills/conveyor-belt/scripts/02_belt_on.py

# 等物体到达末端
python3 /home/HwHiAiUser/.openclaw/workspace/skills/conveyor-belt/scripts/05_wait_object_at_end.py

# 停止传送带
python3 /home/HwHiAiUser/.openclaw/workspace/skills/conveyor-belt/scripts/03_belt_off.py
```

## 步骤 6：从末端取餐

传送带末端机械臂坐标：**(209.8, -80.0, -31.2)**，可直接传给 move_to。

```bash
# 打开夹爪
python3 /home/HwHiAiUser/.openclaw/workspace/skills/arm-basic/scripts/03_gripper.py --action open

# 移动到末端上方（-31.2 + 25 = -6.2mm 悬停）
python3 /home/HwHiAiUser/.openclaw/workspace/skills/arm-basic/scripts/04_move_to.py --x 209.8 --y -80.0 --z -6.2

# 下降到末端（Z = -31.2mm）
python3 /home/HwHiAiUser/.openclaw/workspace/skills/arm-basic/scripts/04_move_to.py --x 209.8 --y -80.0 --z -31.2

# 夹取
python3 /home/HwHiAiUser/.openclaw/workspace/skills/arm-basic/scripts/03_gripper.py --action close

# 抬起（-31.2 + 25 = -6.2mm）
python3 /home/HwHiAiUser/.openclaw/workspace/skills/arm-basic/scripts/04_move_to.py --x 209.8 --y -80.0 --z -6.2
```

## 步骤 7：放到盘子

盘子位置由步骤 1 检测得到（class="panzi" 的 cx, cy），通过 coord-transform 转换为机械臂坐标：

```bash
# 转换盘子坐标
python3 /home/HwHiAiUser/.openclaw/workspace/skills/coord-transform/scripts/02_convert.py --px <盘子cx> --py <盘子cy> --json
```

拿到 arm_target 后，放置：

```bash
# 移动到盘子上方
python3 /home/HwHiAiUser/.openclaw/workspace/skills/arm-basic/scripts/04_move_to.py --x <plate_ax> --y <plate_ay> --z <plate_az+25>

# 下降到盘子
python3 /home/HwHiAiUser/.openclaw/workspace/skills/arm-basic/scripts/04_move_to.py --x <plate_ax> --y <plate_ay> --z <plate_az>

# 松开
python3 /home/HwHiAiUser/.openclaw/workspace/skills/arm-basic/scripts/03_gripper.py --action open

# 抬起
python3 /home/HwHiAiUser/.openclaw/workspace/skills/arm-basic/scripts/04_move_to.py --x <plate_ax> --y <plate_ay> --z <plate_az+50>
```

注意：plate_ax/ay/az 是 coord-transform 转换出来的 arm_target 值。

## 步骤 8：归零

```bash
python3 /home/HwHiAiUser/.openclaw/workspace/skills/arm-basic/scripts/02_homing.py
```
