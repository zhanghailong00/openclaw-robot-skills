#!/usr/bin/env python3
"""
实训箱自检脚本（wrapper 版本）
通过 monkey-patch 解决 smbus2 新版本 read_i2c_block_data 缺少 length 参数的问题
不修改原始 traffic.py / security.py
"""
import sys, os, time, subprocess

# 路径设置
sys.path.insert(0, "/home/HwHiAiUser/arm_voice_soft")

# ===== Monkey-patch: 给 smbus2 的 read_i2c_block_data 加默认 length =====
import smbus2

_original_read_i2c_block_data = smbus2.SMBus.read_i2c_block_data

def _patched_read_i2c_block_data(self, i2c_addr, register, length=None, force=None):
    """兼容旧调用方式：bus.read_i2c_block_data(addr, reg) 自动补 length=32"""
    if length is None:
        length = 32
    return _original_read_i2c_block_data(self, i2c_addr, register, length, force)

smbus2.SMBus.read_i2c_block_data = _patched_read_i2c_block_data
# ===== Monkey-patch 结束 =====

results = []

def add_check(name, status, detail):
    results.append({"name": name, "status": status, "detail": detail})

# 1. 检查机械臂串口
print("检查机械臂串口...")
if os.path.exists("/dev/ttyUSB1"):
    add_check("机械臂串口", "pass", "/dev/ttyUSB1 存在")
else:
    add_check("机械臂串口", "fail", "/dev/ttyUSB1 不存在，请检查USB连接")

# 2. 检查机械臂通信
print("检查机械臂通信...")
try:
    from arm4dof import Arm4DoF
    arm = Arm4DoF()
    thetas = arm.get_thetas()
    if thetas is not None:
        add_check("机械臂通信", "pass", "通信正常，当前角度: {}".format([round(t, 2) for t in thetas]))
    else:
        add_check("机械臂通信", "fail", "读取角度失败")
except Exception as e:
    add_check("机械臂通信", "fail", str(e))

# 3. 检查OpenClaw服务
print("检查OpenClaw服务...")
try:
    result = subprocess.run(
        ["pgrep", "-f", "openclaw"],
        capture_output=True, text=True, timeout=5
    )
    if result.returncode == 0:
        add_check("OpenClaw服务", "pass", "进程运行中 (PID: {})".format(result.stdout.strip()))
    else:
        add_check("OpenClaw服务", "fail", "未运行，请执行启动命令")
except Exception as e:
    add_check("OpenClaw服务", "fail", "检查失败: {}".format(e))

# 4. 检查红外传感器（使用 Hardware.security）
print("检查红外传感器...")
try:
    import Hardware.security as security
    security.pinMode(2, "INPUT")
    time.sleep(0.1)
    val = security.digitalRead(2)
    if val == -1:
        add_check("红外传感器", "fail", "未响应，模块可能未连接")
    else:
        add_check("红外传感器", "pass", "正常，当前值: {} ({})".format(val, "有物体" if val == 0 else "无物体"))
except Exception as e:
    add_check("红外传感器", "fail", str(e))

# 5. 检查超声波传感器（使用 Hardware.traffic）
print("检查超声波传感器...")
try:
    import Hardware.traffic as traffic
    dist = traffic.ultrasonicRead(5)
    if dist is None or dist < 0:
        add_check("超声波传感器", "fail", "读取失败")
    else:
        add_check("超声波传感器", "pass", "正常，距离: {}cm".format(round(dist, 1)))
except Exception as e:
    add_check("超声波传感器", "fail", str(e))

# 生成报告
fail_count = sum(1 for c in results if c["status"] == "fail")

if fail_count == 0:
    status = "all_pass"
    summary = "全部通过，设备状态正常"
elif fail_count <= 2:
    status = "partial"
    fail_names = [c["name"] for c in results if c["status"] == "fail"]
    summary = "{}项异常：{}，相关功能可能受限".format(fail_count, "、".join(fail_names))
else:
    status = "critical"
    fail_names = [c["name"] for c in results if c["status"] == "fail"]
    summary = "{}项异常：{}，请检查硬件连接".format(fail_count, "、".join(fail_names))

print("\n" + "=" * 40)
print("实训箱自检报告")
print("=" * 40)
for c in results:
    icon = "✅" if c["status"] == "pass" else "❌"
    print("{} {}: {}".format(icon, c["name"], c["detail"]))
print("=" * 40)
print("{}".format(summary))
