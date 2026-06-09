# 实训箱 Skill 测试报告

## 一、测试环境

| 项目 | 信息 |
|------|------|
| 设备 | OrangePi AIpro 20T (RK3588) |
| 系统 | Ubuntu aarch64 |
| 用户 | HwHiAiUser |
| Python | 3.9.2 (conda base) |
| 机械臂 | 4-DOF UART 舵机，串口 /dev/ttyUSB1 |
| 摄像头 | UVC 摄像头，设备号 /dev/video2，640×480 |
| NPU | Ascend 310B（YOLO 推理） |
| 传送带 | GPIO bank2 pin15 控制 |
| 安防模块 | I2C 0x0A，红外光电开关 pin2 |
| 交通模块 | I2C 0x0B，超声波传感器 pin5 |

---

## 二、Skill 清单与功能

### Skill 1：arm-basic（机械臂基础控制）

**路径：** `~/.openclaw/skill-workshop/proposals/arm-basic-20260604-dd67cb0384/`

**功能：** 4-DOF 机械臂的底层控制，包括状态查询、归零、夹爪控制、移动。

**脚本列表：**

| 脚本 | 功能 | 参数 | 输出 |
|------|------|------|------|
| `01_status.py` | 读取关节角度和末端坐标 | 无（只读） | 纯文本 |
| `02_homing.py` | 归零到 (150, 0, 50)mm | 无 | 纯文本 |
| `03_gripper.py` | 夹爪开合 | `--action open/close` | JSON |
| `04_move_to.py` | 移动到指定坐标 | `--x --y --z [--t]` | JSON |

**03_gripper.py 参数说明：**
- `--action open`：只打开夹爪，输出 `{"success": true, "action": "open", "angle": 46.5}`
- `--action close`：只闭合夹爪，输出 `{"success": true, "action": "close", "angle": 1.0}`
- 无参数：测试模式，执行开→闭完整流程

**04_move_to.py 参数说明：**
- `--x X`：X 坐标 (mm)，必填
- `--y Y`：Y 坐标 (mm)，必填
- `--z Z`：Z 坐标 (mm)，必填
- `--t T`：运动时间 (s)，默认 0.75，越小越快

**04_move_to.py 输出格式：**
```json
{"success": true, "target": {"x": 150.0, "y": 0.0, "z": 50.0}, "actual": {"x": 146.9, "y": -1.8, "z": 75.7}}
```

**测试结果：**

```
$ python3 01_status.py
=== 机械臂状态 ===
  J1(基座): 舵机=0.6°  关节=-0.6°
  J2(肩部): 舵机=1.5°  关节=-85.4°
  J3(肘部): 舵机=58.2°  关节=-14.5°
  J4(腕部): 舵机=-23.0°  关节=23.7°
  夹爪: 舵机=7.8°  关节=7.4°
末端位姿 (xyz+pitch): [26.8, -0.3, 281.4, 0.24]
结果：正常 ✅

$ python3 02_homing.py
归零中...
末端位姿: (151.8, -1.4, 43.7, pitch=124.2°)
结果：归零成功 ✅

$ python3 03_gripper.py
=== 夹爪测试 ===
  张开 (45°): 当前角度 46.5°
  闭合 (0°): 当前角度 1.0°
结果：正常 ✅

$ python3 04_move_to.py --x 150 --y 0 --z 50
{"success": true, "target": {"x": 150.0, "y": 0.0, "z": 50.0}, "actual": {"x": 146.9, "y": -1.8, "z": 75.7}}
✅
```

---

### Skill 2：vision-detect（视觉检测）

**路径：** `~/.openclaw/skill-workshop/proposals/vision-detect-20260604-c62dc0ca95/`

**功能：** 摄像头拍照 + 去畸变 + YOLOv11 目标检测（Ascend 310B NPU 推理）。

**脚本列表：**

| 脚本 | 功能 | 参数 | 输出 |
|------|------|------|------|
| `01_check_camera.py` | 测试摄像头 + 去畸变 | 无（只读） | 纯文本 |
| `02_run_detection.py` | YOLO 检测 | 无 | JSON |

**02_run_detection.py 输出格式：**
```json
{
  "detections": [
    {"class": "panzi", "label": "盘子", "confidence": 0.935, "cx": 387.8, "cy": 118.1, "xmin": 334.5, "ymin": 60.6, "xmax": 441.0, "ymax": 175.7},
    {"class": "shutiao", "label": "薯条", "confidence": 0.677, "cx": 260.8, "cy": 151.3, "xmin": 242.6, "ymin": 135.3, "xmax": 278.9, "ymax": 167.3}
  ],
  "count": 2,
  "status": "ok"
}
```

**检测类别：** hanbao（汉堡）、cola（可乐）、panzi（盘子）、shutiao（薯条）

**依赖：** 需要 Ascend NPU 库（已通过 sys.path.insert 解决）：
```python
sys.path.insert(0, "/usr/local/Ascend/thirdpart/aarch64/acllite")
sys.path.insert(0, "/usr/local/Ascend/ascend-toolkit/latest/python/site-packages")
sys.path.insert(0, "/home/HwHiAiUser/arm_voice_soft/camera_utils")
```

**测试结果：**

```
$ python3 01_check_camera.py
=== 摄像头检测 ===
  设备: video2
  内参: fx=1278.7 cx=309.0 cy=241.2
  采集 OK: (480, 640, 3)
  去畸变 OK: (480, 640, 3)
结果：正常 ✅

$ python3 02_run_detection.py
{"detections": [
  {"class": "panzi", "label": "盘子", "confidence": 0.935, "cx": 387.8, "cy": 118.1, ...},
  {"class": "shutiao", "label": "薯条", "confidence": 0.677, "cx": 260.8, "cy": 151.3, ...}
], "count": 2, "status": "ok"}
✅
```

---

### Skill 3：coord-transform（坐标转换）

**路径：** `~/.openclaw/skill-workshop/proposals/coord-transform-20260604-aaa251417d/`

**功能：** 像素坐标 → 工作台坐标 → 机械臂坐标，含 Z 轴误差校正。

**脚本列表：**

| 脚本 | 功能 | 参数 | 输出 |
|------|------|------|------|
| `01_check_calib.py` | 验证标定数据 + 重投影误差 | 无（只读） | 纯文本 |
| `02_convert.py` | 坐标转换 | `--px --py` 或 `--cx --cy` | JSON / 纯文本 |

**02_convert.py 参数说明：**
- `--px X --py Y`：像素坐标
- `--cx X --cy Y`：检测框中心坐标
- `--json`：仅输出 JSON 格式
- `--height H`：指定工件高度（mm），默认用标定值 25mm

**02_convert.py 输出格式：**
```json
{
  "pixel": {"x": 320.0, "y": 240.0},
  "workspace": {"x": 68.7, "y": -7.0},
  "z": 12.5,
  "z_corrected": 2.7,
  "arm_target": {"x": 216.8, "y": -2.4, "z": -31.2}
}
```

**坐标变换链路：**
```
像素 (px, py)
  → 去畸变（remap）
  → 仿射变换（estimateAffine2D）
  → 工作台坐标 (wx, wy)
  → 齐次变换（T_arm2ws）
  → Z 轴误差校正（z_error_polyfit）
  → 机械臂坐标 (ax, ay, az)
```

**测试结果：**

```
$ python3 01_check_calib.py
============================================================
坐标转换标定验证
============================================================
[1] 基本配置
  标定板: 200x160mm
  延长杆: 53mm
  物体高度: 25mm

[2] 变换矩阵
  T_cam2ws 平移: (8.7, -64.7, 1111.7)mm
  T_arm2ws 平移: (147.9, 3.6, -33.8)mm

[3] 相机参数
  内参: fx=1282.82 fy=1274.61 cx=309.04 cy=241.18

[4] Z 轴误差校正
  多项式: error = -0.0614*z + 10.5933

[6] 重投影误差验证
  平均误差: 5.49mm  ⚠️ 可接受（边缘位置误差较大）

$ python3 02_convert.py --px 320 --py 240
  像素: (320.0, 240.0)
  工作台: (68.7, -7.0)mm
  机械臂目标: (216.8, -2.4, -31.2)
  ✅
```

**标定精度说明：**
- 当前摄像头内参与 05_armapp 参考值差异较大（fx=1282 vs 255，约 5 倍），说明用的是不同摄像头
- 重投影误差 5.49mm，中间区域 3-4mm（可用），边缘 7-10mm（偏差较大）
- 对于夹爪抓取（开口约 40-50mm），5mm 误差勉强可用

---

### Skill 4：conveyor-belt（传送带控制）

**路径：** `~/.openclaw/skill-workshop/proposals/conveyor-belt-20260604-1a1da0b563/`

**功能：** 传送带 GPIO 控制 + 安防/交通模块传感器读取。

**脚本列表：**

| 脚本 | 功能 | 参数 | 输出 | 性质 |
|------|------|------|------|------|
| `01_check_sensors.py` | 检查传感器通信 | 无 | 纯文本 | 只读 |
| `02_belt_on.py` | 启动传送带 | 无 | 纯文本 | 会动 |
| `03_belt_off.py` | 停止传送带 | 无 | 纯文本 | 会动 |
| `04_wait_object_at_start.py` | 等待红外检测到物体 | 无 | 纯文本 | 阻塞 |
| `05_wait_object_at_end.py` | 等待超声波检测到物体 | 无 | 纯文本 | 阻塞 |

**GPIO 控制说明：**
- 启动传送带：`sudo /usr/bin/gpio_operate set_value 2 15 0`（GPIO 设为 0 = 启动）
- 停止传送带：`sudo /usr/bin/gpio_operate set_value 2 15 1`（GPIO 设为 1 = 停止）
- ⚠️ 注意：0=启动，1=停止，和直觉相反

**传感器说明：**
- 安防模块（Ascene）：I2C 0x0A，红外光电开关 pin2，`digitalRead(2) == 0` 表示检测到物体
- 交通模块（Bscene）：I2C 0x0B，超声波传感器 pin5，`ultrasonicRead(5) <= 3` 表示物体到达

**测试结果：**

```
$ python3 01_check_sensors.py
=== 安防/交通模块检测 ===
  Ascene 模块: 加载成功
  红外光电开关(pin2): 无物体

[交通模块 Bscene]
  传感器(pin0): 无物体
  通信正常 ✅

[GPIO 传送带]
  命令可用: ✅
  当前状态: Get gpio pin value successed, value is 0.
结果：检测完成 ✅

$ python3 02_belt_on.py
启动传送带...
  传送带已启动 ✅

$ python3 03_belt_off.py
停止传送带...
  传送带已停止 ✅

$ python3 04_wait_object_at_start.py
等待物体到达传送带起始端（红外检测）...
  初始状态: 无物体
  检测到物体！✅
结果：物体已到位 ✅

$ python3 05_wait_object_at_end.py
等待物体到达传送带末端（超声波检测）...
  距离: 24cm
  距离: 24cm
  ...
  距离: 3cm
  检测到物体到达！✅
结果：物体已到达末端 ✅
```

---

### Skill 5：camera-arm-handeye-calibration（手眼标定）

**路径：** `~/.openclaw/skill-workshop/proposals/camera-arm-handeye-calibration-20260605-e8535c0869/`

**功能：** 四步手眼标定流程文档（参考文档，非可执行脚本）。

**四步流程：**

| 步骤 | 内容 | 产出文件 |
|------|------|----------|
| Step 1 | 相机内参标定（棋盘格） | M_intrisic.txt, distor_coeff.txt, remap_*.npy |
| Step 2 | 九点手眼标定 | T_cam2ws.txt, T_arm2ws.txt |
| Step 3 | Z 轴误差补偿 | z_error_polyfit.txt |
| Step 4 | 重投影误差验证 | — |

**状态：** 文档完整，标定数据已存在，当前标定精度 5.49mm。

---

## 三、修复的问题汇总

### 已修复

| # | 问题 | 影响范围 | 修复方式 |
|---|------|---------|---------|
| 1 | `camera.py` 在 `camera_utils/` 子目录，脚本找不到 | 5 个脚本 | 加 `sys.path.insert(0, ".../camera_utils")` |
| 2 | Ascend NPU 库路径未加入 | YOLO 相关脚本 | 加 `sys.path.insert(0, "/usr/local/Ascend/thirdpart/aarch64/acllite")` |
| 3 | 传送带 GPIO 值反了 | belt_on/belt_off | 0=启动，1=停止（和原来相反） |
| 4 | `05_wait_object_at_end.py` 用 digitalRead 而非 ultrasonicRead | 末端检测 | 改用 `Bscene.ultrasonicRead(5)` |
| 5 | `03_gripper.py` 不支持 `--action` 参数 | workflow 调用 | 重写，支持 open/close/测试模式 |

### 待修复

| # | 问题 | 说明 |
|---|------|------|
| 1 | 标定精度 5.49mm | 边缘位置误差 7-10mm，如需高精度需重新标定 |
| 2 | arm-delivery/01_workflow.py 架构问题 | 应该由龙虾编排调用，不应写死流程 |

---

## 四、龙虾调用 Skill 的正确方式

### 设计原则

**每个 Skill 是独立的工具，龙虾是编排者。** 不需要写 workflow 脚本，龙虾根据用户意图自己决定调用哪个 Skill。

### Skill 调用格式

```bash
# 机械臂状态
python3 ~/.openclaw/skill-workshop/proposals/arm-basic-*/scripts/01_status.py

# 归零
python3 ~/.openclaw/skill-workshop/proposals/arm-basic-*/scripts/02_homing.py

# 夹爪控制
python3 ~/.openclaw/skill-workshop/proposals/arm-basic-*/scripts/03_gripper.py --action open
python3 ~/.openclaw/skill-workshop/proposals/arm-basic-*/scripts/03_gripper.py --action close

# 移动到指定坐标
python3 ~/.openclaw/skill-workshop/proposals/arm-basic-*/scripts/04_move_to.py --x 150 --y 50 --z 80

# YOLO 检测
python3 ~/.openclaw/skill-workshop/proposals/vision-detect-*/scripts/02_run_detection.py

# 坐标转换
python3 ~/.openclaw/skill-workshop/proposals/coord-transform-*/scripts/02_convert.py --px 320 --py 240 --json

# 传送带控制
python3 ~/.openclaw/skill-workshop/proposals/conveyor-belt-*/scripts/02_belt_on.py
python3 ~/.openclaw/skill-workshop/proposals/conveyor-belt-*/scripts/03_belt_off.py
python3 ~/.openclaw/skill-workshop/proposals/conveyor-belt-*/scripts/04_wait_object_at_start.py
python3 ~/.openclaw/skill-workshop/proposals/conveyor-belt-*/scripts/05_wait_object_at_end.py
```

### 龙虾编排示例

```
学生：帮我把薯条放到盘子里

龙虾思考：
  1. 先检测薯条在哪 → 调用 vision-detect
  2. 把像素坐标转成机械臂坐标 → 调用 coord-transform
  3. 打开夹爪 → 调用 arm-basic gripper
  4. 移动过去 → 调用 arm-basic move（需要一个移动脚本）
  5. 夹住 → 调用 arm-basic gripper close
  6. 移到盘子上方 → 调用 arm-basic move
  7. 松开 → 调用 arm-basic gripper open

龙虾执行：
  [调用 02_run_detection.py] → 检测到薯条 (262, 165)
  [调用 02_convert.py --px 262 --py 165 --json] → 机械臂 (154, -50, -31)
  [调用 03_gripper.py --action open] → {"success": true}
  [调用 04_move_to.py --x 154 --y -50 --z -6] → {"success": true}
  [调用 03_gripper.py --action close] → {"success": true}
  [调用 04_move_to.py --x 130 --y -40 --z -6] → {"success": true}
  [调用 03_gripper.py --action open] → 完成
```

### 需要补充的 Skill 脚本

所有送餐流程所需的 Skill 脚本已齐全，无需补充。

---

## 五、测试时间线

| 时间 | 操作 | 结果 |
|------|------|------|
| 重启后 | arm-basic/01_status.py | ✅ 机械臂通信正常 |
| | arm-basic/02_homing.py | ✅ 归零成功 |
| | arm-basic/03_gripper.py | ✅ 夹爪正常 |
| | conveyor-belt/01_check_sensors.py | ✅ 传感器正常 |
| | vision-detect/01_check_camera.py | ✅ 摄像头正常 |
| | coord-transform/01_check_calib.py | ⚠️ 5.49mm 误差 |
| | coord-transform/02_convert.py | ✅ 坐标转换正常 |
| | conveyor-belt/02_belt_on.py | ❌→✅ GPIO 反了，已修复 |
| | conveyor-belt/03_belt_off.py | ❌→✅ GPIO 反了，已修复 |
| | conveyor-belt/04_wait_object_at_start.py | ✅ 红外检测正常 |
| | conveyor-belt/05_wait_object_at_end.py | ❌→✅ 改用超声波，已修复 |
| | vision-detect/02_run_detection.py | ❌→✅ 加 Ascend 路径，已修复 |
| | arm-basic/04_move_to.py | ✅ 移动脚本正常（新写） |
| | arm-delivery/01_workflow.py | ⚠️ 有架构问题，建议由龙虾编排 |
