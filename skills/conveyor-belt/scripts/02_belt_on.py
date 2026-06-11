#!/usr/local/miniconda3/bin/python
"""启动传送带。"""
import subprocess, sys

print("启动传送带...")
try:
    r = subprocess.run(["sudo", "/usr/bin/gpio_operate", "set_direction", "2", "15", "1"], capture_output=True, text=True, timeout=5)
    r = subprocess.run(["sudo", "/usr/bin/gpio_operate", "set_value", "2", "15", "0"], capture_output=True, text=True, timeout=5)
    if r.returncode == 0:
        print("  传送带已启动 ✅")
    else:
        print(f"  启动失败: {r.stderr}")
        sys.exit(1)
except Exception as e:
    print(f"  错误: {e}")
    sys.exit(1)
