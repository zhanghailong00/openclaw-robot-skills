#!/usr/bin/env python3
"""
舵机控制脚本

功能：控制智慧家居场景板上的舵机旋转到指定角度
硬件：智慧家居场景板上的舵机（Dscene 模块，D3 口）
原理：通过 PWM 信号控制舵机旋转角度（0-180°）

用法：
  python3 03_servo.py --angle 90         # 旋转到 90°
  python3 03_servo.py --angle 0          # 旋转到 0°
  python3 03_servo.py --sweep            # 扫描模式（0→180→0）
  python3 03_servo.py --detach           # 释放舵机

输出：JSON 格式
"""
import sys, json, argparse, time

# 加载传感器驱动（舵机在 Dscene 模块上）
sys.path.insert(0, "/home/HwHiAiUser/.openclaw/workspace/python_sensor")
import Dscene

# 舵机引脚（智慧家居场景板，D3 口）
SERVO_PIN = 3

# 命令行参数解析
parser = argparse.ArgumentParser(description="舵机控制")
parser.add_argument("--angle", type=int, help="目标角度 (0-180)")
parser.add_argument("--sweep", action="store_true", help="扫描模式（0→180→0）")
parser.add_argument("--detach", action="store_true", help="释放舵机")
args = parser.parse_args()

try:
    # 连接舵机
    Dscene.Servo_Attach(SERVO_PIN)

    if args.sweep:
        # 扫描模式：0→180→0
        for angle in range(0, 181):
            Dscene.Servo_Write(SERVO_PIN, angle)
            time.sleep(0.02)
        for angle in range(180, -1, -1):
            Dscene.Servo_Write(SERVO_PIN, angle)
            time.sleep(0.02)
        Dscene.Servo_Detach(SERVO_PIN)
        result = {"success": True, "action": "sweep", "range": "0-180-0"}

    elif args.angle is not None:
        # 旋转到指定角度
        angle = max(0, min(180, args.angle))  # 限制在 0-180 范围内
        Dscene.Servo_Write(SERVO_PIN, angle)
        time.sleep(0.5)
        Dscene.Servo_Detach(SERVO_PIN)
        result = {"success": True, "angle": angle}

    elif args.detach:
        # 释放舵机
        Dscene.Servo_Detach(SERVO_PIN)
        result = {"success": True, "action": "detach"}

    else:
        result = {"success": False, "error": "Specify --angle, --sweep, or --detach"}

    print(json.dumps(result, ensure_ascii=False))

except Exception as e:
    print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False))
    sys.exit(1)
