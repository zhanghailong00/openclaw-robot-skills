---
name: self-check
description: "当用户说'自检'、'检查硬件'、'系统检查'、'排查问题'、'设备检查'时使用。检查实训箱硬件状态，诊断常见问题。任务执行中遇到问题也可以检查"
---

# 实训箱自检

检查实训箱硬件状态，帮助诊断问题。

## 脚本

### 01_check_all_wrapper.py
检查所有硬件状态，输出诊断报告。通过 monkey-patch 解决 smbus2 版本兼容问题，不修改原始代码。

**路径：** `skills/self-check/scripts/01_check_all_wrapper.py`

**参数：** 无

**检查项目：**
1. 机械臂串口（/dev/ttyUSB1）
2. 机械臂通信（Arm4DoF初始化）
3. OpenClaw服务（进程检查）
4. 红外传感器（Ascene.digitalRead）
5. 超声波传感器（Bscene.ultrasonicRead）

**输出示例：**
```json
{
  "status": "partial",
  "checks": [
    {"name": "机械臂串口", "status": "pass", "detail": "/dev/ttyUSB1 存在"},
    {"name": "机械臂通信", "status": "pass", "detail": "Arm4DoF 初始化成功"},
    {"name": "OpenClaw服务", "status": "pass", "detail": "进程运行中"},
    {"name": "红外传感器", "status": "fail", "detail": "未响应"},
    {"name": "超声波传感器", "status": "pass", "detail": "距离 15.2cm"}
  ],
  "summary": "1项异常：红外传感器未响应，传送带功能受限"
}
```
