#!/usr/local/miniconda3/bin/python
"""检测安防模块和交通模块是否正常通信。"""
import sys

print("=== 安防/交通模块检测 ===")

# 检测安防模块 (Ascene)
try:
    import Ascene
    print("\n[安防模块 Ascene]")
    print(f"  模块路径: {Ascene.__file__ if hasattr(Ascene, '__file__') else '预编译'}")
    # 读取红外光电开关（只检测通信，pin2 = button/IR sensor）
    Ascene.pinMode(2, "INPUT")
    val = Ascene.digitalRead(2)
    print(f"  红外光电开关(pin2): {'有物体' if val == 0 else '无物体'}")
    print(f"  通信正常 ✅")
except ImportError:
    sys.path.insert(0, "/home/HwHiAiUser/orangepi_test")
    try:
        import Ascene
        Ascene.pinMode(2, "INPUT")
        val = Ascene.digitalRead(2)
        print(f"  Ascene 模块: 加载成功")
        print(f"  红外光电开关(pin2): {'有物体' if val == 0 else '无物体'}")
    except Exception as e:
        print(f"  Ascene 模块: 加载失败 - {e}")

# 检测交通模块 (Bscene)
try:
    import Bscene
    print("\n[交通模块 Bscene]")
    Bscene.pinMode(0, "INPUT")  # sensor pin on traffic module
    val = Bscene.digitalRead(0)
    print(f"  传感器(pin0): {'有物体' if val == 0 else '无物体'}")
    print(f"  通信正常 ✅")
except ImportError:
    sys.path.insert(0, "/home/HwHiAiUser/orangepi_test")
    try:
        import Bscene
        print(f"  Bscene 模块: 加载成功")
    except Exception as e:
        print(f"  Bscene 模块: 加载失败 - {e}")

# 检测 GPIO 命令
try:
    import subprocess
    r = subprocess.run(["sudo", "/usr/bin/gpio_operate", "get_value", "2", "15"], capture_output=True, text=True, timeout=5)
    print(f"\n[GPIO 传送带]")
    print(f"  命令可用: {'✅' if r.returncode == 0 else '❌'}")
    print(f"  当前状态: {r.stdout.strip()}")
except Exception as e:
    print(f"  gpio_operate: 错误 - {e}")

print("\n结果：检测完成")
