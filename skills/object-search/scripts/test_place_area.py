#!/usr/local/miniconda3/bin/python
"""
测试放置区域

功能：让机械臂移动到放置区域的几个关键位置，检查是否都能到达
用法：python test_place_area.py
"""

import sys
import os
import time

# 加载机械臂 SDK
sys.path.insert(0, "/home/HwHiAiUser/arm_voice_soft")
sys.path.insert(0, "/home/HwHiAiUser/arm_voice_soft/utils_arm")

from arm4dof import Arm4DoF

# 放置区域配置
PLACE_AREA = {
    'x_min': 50,    # X左边界
    'x_max': 100,   # X右边界
    'y_min': 70,    # Y下边界
    'y_max': 120,   # Y上边界
    'z': -25        # 放置高度
}

# 安全位置
SAFE_POS = [150, 0, 80]


def main():
    """主函数"""
    print("=" * 60)
    print("测试放置区域")
    print("=" * 60)

    # 初始化机械臂
    try:
        arm = Arm4DoF(device="/dev/ttyUSB1", is_init_pose=False)
        print("✅ 机械臂初始化成功")
    except Exception as e:
        print(f"❌ 机械臂初始化失败: {e}")
        return

    # 移动到安全位置
    print(f"\n移动到安全位置: {SAFE_POS}")
    arm.move(SAFE_POS, t=0.75, wait=True)
    time.sleep(0.5)

    # 测试位置列表
    test_positions = [
        # 放置区域的四个角
        ([PLACE_AREA['x_min'], PLACE_AREA['y_min'], PLACE_AREA['z']], "左下角"),
        ([PLACE_AREA['x_min'], PLACE_AREA['y_max'], PLACE_AREA['z']], "左上角"),
        ([PLACE_AREA['x_max'], PLACE_AREA['y_min'], PLACE_AREA['z']], "右下角"),
        ([PLACE_AREA['x_max'], PLACE_AREA['y_max'], PLACE_AREA['z']], "右上角"),
        # 放置区域的中心
        ([(PLACE_AREA['x_min'] + PLACE_AREA['x_max']) / 2,
          (PLACE_AREA['y_min'] + PLACE_AREA['y_max']) / 2,
          PLACE_AREA['z']], "中心点"),
        # 网格位置（3个物品）
        ([50 + (100-50) * 0.5 / 3, 70 + (120-70) * 0.5 / 2, PLACE_AREA['z']], "位置0"),
        ([50 + (100-50) * 1.5 / 3, 70 + (120-70) * 0.5 / 2, PLACE_AREA['z']], "位置1"),
        ([50 + (100-50) * 2.5 / 3, 70 + (120-70) * 0.5 / 2, PLACE_AREA['z']], "位置2"),
    ]

    # 测试每个位置
    print(f"\n测试放置区域:")
    print(f"  X: {PLACE_AREA['x_min']} ~ {PLACE_AREA['x_max']}")
    print(f"  Y: {PLACE_AREA['y_min']} ~ {PLACE_AREA['y_max']}")
    print(f"  Z: {PLACE_AREA['z']}")

    success_count = 0
    fail_count = 0

    for pos, name in test_positions:
        print(f"\n测试 {name}: {pos}")
        try:
            arm.move(pos, t=0.75, wait=True)
            print(f"  ✅ 可到达")
            success_count += 1
        except Exception as e:
            print(f"  ❌ 不可到达: {e}")
            fail_count += 1
        time.sleep(0.3)

    # 回到安全位置
    print(f"\n回到安全位置: {SAFE_POS}")
    arm.move(SAFE_POS, t=0.75, wait=True)

    # 输出总结
    print(f"\n{'='*60}")
    print(f"测试完成")
    print(f"{'='*60}")
    print(f"  成功: {success_count} 个位置")
    print(f"  失败: {fail_count} 个位置")

    if fail_count == 0:
        print(f"\n✅ 放置区域合理！所有位置都可到达")
    else:
        print(f"\n⚠️ 放置区域需要调整！有 {fail_count} 个位置不可到达")


if __name__ == "__main__":
    main()
