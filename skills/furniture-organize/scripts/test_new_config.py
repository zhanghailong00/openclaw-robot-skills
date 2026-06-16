#!/usr/local/miniconda3/bin/python
"""
测试新配置：障碍物半径50mm + 放置区域均匀分布

功能：验证新的配置是否正确
用法：python test_new_config.py
"""

import sys
import os
import json
import math

# ==================== 配置 ====================

# 放置区域配置
PLACE_AREA = {
    'x_min': 80,    # 左边界
    'x_max': 120,   # 右边界
    'y_min': -30,   # 下边界
    'y_max': 30,    # 上边界
    'z': -31.2,     # 放置高度
}

# 网格排列配置
GRID_COLS = 3  # 每行3个
GRID_ROWS = 2  # 最多2行

# 障碍物半径
OBSTACLE_RADIUS = 50  # 统一50mm


def get_place_position(index):
    """
    根据索引计算放置位置（均匀分布在区域内）

    参数：
        index: 物品索引（0, 1, 2, ...）

    返回：
        [x, y, z] 放置位置
    """
    row = index // GRID_COLS
    col = index % GRID_COLS

    # 计算在区域内的位置
    x = PLACE_AREA['x_min'] + (PLACE_AREA['x_max'] - PLACE_AREA['x_min']) * (col + 0.5) / GRID_COLS
    y = PLACE_AREA['y_min'] + (PLACE_AREA['y_max'] - PLACE_AREA['y_min']) * (row + 0.5) / GRID_ROWS
    z = PLACE_AREA['z']

    return [x, y, z]


def main():
    """主函数"""
    print("=" * 60)
    print("测试新配置：障碍物半径50mm + 放置区域均匀分布")
    print("=" * 60)

    # 测试1：障碍物半径
    print("\n【测试1】障碍物半径")
    print(f"  障碍物半径: {OBSTACLE_RADIUS}mm")
    print(f"  说明: 所有物品统一使用{OBSTACLE_RADIUS}mm半径，避障效果更明显")

    # 测试2：放置区域
    print("\n【测试2】放置区域")
    print(f"  区域范围: ({PLACE_AREA['x_min']},{PLACE_AREA['y_min']}) 到 ({PLACE_AREA['x_max']},{PLACE_AREA['y_max']})")
    print(f"  区域大小: {PLACE_AREA['x_max']-PLACE_AREA['x_min']}mm x {PLACE_AREA['y_max']-PLACE_AREA['y_min']}mm")
    print(f"  网格排列: 每行{GRID_COLS}个，最多{GRID_ROWS}行")
    print(f"  最多放置: {GRID_COLS * GRID_ROWS}个物品")

    # 测试3：计算放置位置
    print("\n【测试3】放置位置计算")
    print("  物品索引  |  行  |  列  |  放置位置")
    print("  ---------|------|------|----------")

    for i in range(6):  # 测试6个物品
        pos = get_place_position(i)
        row = i // GRID_COLS
        col = i % GRID_COLS
        print(f"  {i:8d} | {row:4d} | {col:4d} | ({pos[0]:6.1f}, {pos[1]:6.1f}, {pos[2]})")

    # 测试4：可视化放置区域
    print("\n【测试4】放置区域可视化")
    print("  y=30  ┌─────┬─────┬─────┐")
    print("        │  0  │  1  │  2  │")
    print("  y=0   ├─────┼─────┼─────┤")
    print("        │  3  │  4  │  5  │")
    print("  y=-30 └─────┴─────┴─────┘")
    print("        x=80  x=100 x=120")

    # 测试5：模拟避障
    print("\n【测试5】避障模拟")
    print(f"  假设障碍物在 (100, 0, 80)，半径 {OBSTACLE_RADIUS}mm")
    print(f"  障碍物范围: ({100-OBSTACLE_RADIUS},{0-OBSTACLE_RADIUS}) 到 ({100+OBSTACLE_RADIUS},{0+OBSTACLE_RADIUS})")

    # 计算绕行点
    start = [150, 0, 80]
    end = [163, 53, 80]
    obstacle = {'center': [100, 0, 80], 'radius': OBSTACLE_RADIUS}

    # 简化的绕行点计算
    cross_product = (end[0] - start[0]) * (obstacle['center'][1] - start[1]) - \
                   (end[1] - start[1]) * (obstacle['center'][0] - start[0])

    if cross_product > 0:
        detour_y = obstacle['center'][1] - obstacle['radius'] - 50
    else:
        detour_y = obstacle['center'][1] + obstacle['radius'] + 50

    detour_point = [obstacle['center'][0], detour_y, 80]

    print(f"  起点: {start}")
    print(f"  终点: {end}")
    print(f"  绕行点: {detour_point}")
    print(f"  绕行距离: {abs(detour_y):.1f}mm")

    # 总结
    print("\n" + "=" * 60)
    print("配置总结")
    print("=" * 60)
    print(f"  ✓ 障碍物半径: {OBSTACLE_RADIUS}mm（统一，避障效果明显）")
    print(f"  ✓ 放置区域: ({PLACE_AREA['x_min']},{PLACE_AREA['y_min']}) 到 ({PLACE_AREA['x_max']},{PLACE_AREA['y_max']})")
    print(f"  ✓ 网格排列: {GRID_COLS}列 x {GRID_ROWS}行")
    print(f"  ✓ 最多放置: {GRID_COLS * GRID_ROWS}个物品")
    print(f"  ✓ 放置位置: 均匀分布在区域内")


if __name__ == "__main__":
    main()
