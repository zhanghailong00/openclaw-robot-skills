#!/usr/bin/env python3
"""停止传送带。"""
import subprocess

print("停止传送带...")
try:
    r = subprocess.run(["sudo", "/usr/bin/gpio_operate", "set_value", "2", "15", "1"], capture_output=True, text=True, timeout=5)
    if r.returncode == 0:
        print("  传送带已停止 ✅")
    else:
        print(f"  停止失败: {r.stderr}")
except Exception as e:
    print(f"  错误: {e}")
