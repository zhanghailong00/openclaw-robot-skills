#!/usr/local/miniconda3/bin/python
"""
对比测试脚本

功能：对比有无障碍物时的路径差异
用法：python test_compare.py
"""

import sys
import os
import json
import math
import time

# 加载机械臂 SDK
sys.path.insert(0, "/home/HwHiAiUser/arm_voice_soft")
sys.path.insert(0, "/home/HwHiAiUser/arm_voice_soft/utils_arm")

from arm4dof import Arm4DoF

# ==================== 配置 ====================

SAFE_HEIGHT = 80
SAFE_POS = [150, 0, 80]
HOVER_HEIGHT = 25
MIN_SAFE_DISTANCE = 50
MOVE_TIME = 0.75
GRIPPER_TIME = 0.5

# ==================== 避障函数 ====================

def line_intersects_sphere(start, end, sphere):
    """检查线段是否与球体相交"""
    center = sphere.get('center', [0, 0, 0])
    radius = sphere.get('radius', 30)

    dx = end[0] - start[0]
    dy = end[1] - start[1]
    dz = end[2] - start[2]

    cx = center[0] - start[0]
    cy = center[1] - start[1]
    cz = center[2] - start[2]

    t = (cx * dx + cy * dy + cz * dz) / (dx * dx + dy * dy + dz * dz + 1e-10)
    t = max(0, min(1, t))

    nearest_x = start[0] + t * dx
    nearest_y = start[1] + t * dy
    nearest_z = start[2] + t * dz

    distance = math.sqrt(
        (nearest_x - center[0])**2 +
        (nearest_y - center[1])**2 +
        (nearest_z - center[2])**2
    )

    return distance < (radius + MIN_SAFE_DISTANCE)


def need_detour(start, end, obstacles):
    """判断是否需要绕行"""
    if not obstacles:
        return False

    for obs in obstacles:
        if line_intersects_sphere(start, end, obs):
            return True
    return False


def point_to_line_distance(point, line_start, line_end):
    """计算点到线段的距离"""
    dx = line_end[0] - line_start[0]
    dy = line_end[1] - line_start[1]

    length = math.sqrt(dx * dx + dy * dy)
    if length == 0:
        return math.sqrt(
            (point[0] - line_start[0])**2 +
            (point[1] - line_start[1])**2
        )

    t = ((point[0] - line_start[0]) * dx + (point[1] - line_start[1]) * dy) / (length * length)
    t = max(0, min(1, t))

    nearest_x = line_start[0] + t * dx
    nearest_y = line_start[1] + t * dy

    return math.sqrt(
        (point[0] - nearest_x)**2 +
        (point[1] - nearest_y)**2
    )


def calculate_detour_point(start, end, obstacles):
    """计算绕行点"""
    nearest_obs = None
    min_distance = float('inf')

    for obs in obstacles:
        center = obs.get('center', [0, 0, 0])
        distance = point_to_line_distance(center, start, end)
        if distance < min_distance:
            min_distance = distance
            nearest_obs = obs

    if nearest_obs:
        obs_center = nearest_obs.get('center', [0, 0, 0])
        obs_radius = nearest_obs.get('radius', 30)

        cross_product = (end[0] - start[0]) * (obs_center[1] - start[1]) - \
                       (end[1] - start[1]) * (obs_center[0] - start[0])

        if cross_product > 0:
            detour_y = obs_center[1] - obs_radius - MIN_SAFE_DISTANCE
        else:
            detour_y = obs_center[1] + obs_radius + MIN_SAFE_DISTANCE

        return [obs_center[0], detour_y, SAFE_HEIGHT]

    return [end[0], end[1], SAFE_HEIGHT]


# ==================== 主函数 ====================

def main():
    """主函数"""
    print("=" * 60)
    print("对比测试：有无障碍物的路径差异")
    print("=" * 60)

    # 测试场景
    grab_pos = [163, 53, -31]
    place_pos = [100, 0, -31]
    obstacles = [
        {'center': [140, 25, 80], 'radius': 50, 'label': '薯条'}
    ]

    print(f"\n场景设置：")
    print(f"  起点（安全位）: {SAFE_POS}")
    print(f"  抓取位置: {grab_pos}")
    print(f"  放置位置: {place_pos}")
    print(f"  障碍物: {obstacles[0]['label']} - 中心{obstacles[0]['center']}, 半径{obstacles[0]['radius']}mm")

    # 计算路径
    print("\n" + "=" * 60)
    print("路径计算")
    print("=" * 60)

    # 无障碍物路径
    print("\n【无障碍物】")
    no_avoid_path = [
        SAFE_POS,
        [grab_pos[0], grab_pos[1], SAFE_HEIGHT],
        [grab_pos[0], grab_pos[1], grab_pos[2] + HOVER_HEIGHT],
        grab_pos,
        [grab_pos[0], grab_pos[1], grab_pos[2] + HOVER_HEIGHT],
        SAFE_POS,
        [place_pos[0], place_pos[1], SAFE_HEIGHT],
        [place_pos[0], place_pos[1], place_pos[2] + HOVER_HEIGHT],
        place_pos,
        [place_pos[0], place_pos[1], place_pos[2] + HOVER_HEIGHT],
        SAFE_POS
    ]

    print("运动轨迹：")
    for i, point in enumerate(no_avoid_path):
        print(f"  {i+1}. {point}")

    # 有障碍物路径
    print("\n【有障碍物】")
    avoid_path = []

    # 抓取阶段
    avoid_path.append(SAFE_POS)

    # 检查是否需要绕行
    target_hover = [grab_pos[0], grab_pos[1], SAFE_HEIGHT]
    if need_detour(SAFE_POS, target_hover, obstacles):
        detour_point = calculate_detour_point(SAFE_POS, target_hover, obstacles)
        avoid_path.append(detour_point)
        print(f"  检测到障碍物，绕行点: {detour_point}")
    else:
        print("  未检测到障碍物")

    avoid_path.append(target_hover)
    avoid_path.append([grab_pos[0], grab_pos[1], grab_pos[2] + HOVER_HEIGHT])
    avoid_path.append(grab_pos)
    avoid_path.append([grab_pos[0], grab_pos[1], grab_pos[2] + HOVER_HEIGHT])
    avoid_path.append(SAFE_POS)

    # 放置阶段
    place_hover = [place_pos[0], place_pos[1], SAFE_HEIGHT]
    if need_detour(SAFE_POS, place_hover, obstacles):
        detour_point = calculate_detour_point(SAFE_POS, place_hover, obstacles)
        avoid_path.append(detour_point)
        print(f"  检测到障碍物，绕行点: {detour_point}")
    else:
        print("  未检测到障碍物")

    avoid_path.append(place_hover)
    avoid_path.append([place_pos[0], place_pos[1], place_pos[2] + HOVER_HEIGHT])
    avoid_path.append(place_pos)
    avoid_path.append([place_pos[0], place_pos[1], place_pos[2] + HOVER_HEIGHT])
    avoid_path.append(SAFE_POS)

    print("\n运动轨迹：")
    for i, point in enumerate(avoid_path):
        print(f"  {i+1}. {point}")

    # 计算路径长度
    print("\n" + "=" * 60)
    print("路径长度对比")
    print("=" * 60)

    def calculate_path_length(path):
        """计算路径长度"""
        total_length = 0
        for i in range(len(path) - 1):
            dx = path[i+1][0] - path[i][0]
            dy = path[i+1][1] - path[i][1]
            dz = path[i+1][2] - path[i][2]
            length = math.sqrt(dx*dx + dy*dy + dz*dz)
            total_length += length
        return total_length

    no_avoid_length = calculate_path_length(no_avoid_path)
    avoid_length = calculate_path_length(avoid_path)
    extra_length = avoid_length - no_avoid_length

    print(f"\n无障碍物路径长度: {no_avoid_length:.1f}mm")
    print(f"有障碍物路径长度: {avoid_length:.1f}mm")
    print(f"额外绕行长度: {extra_length:.1f}mm")
    print(f"增加时间: {extra_length / 100:.2f}秒")

    # 询问是否执行
    print("\n" + "=" * 60)
    print("是否执行测试？")
    print("=" * 60)
    print("\n1. 执行【无障碍物】路径")
    print("2. 执行【有障碍物】路径")
    print("3. 退出")

    choice = input("\n请选择 (1/2/3): ").strip()

    if choice not in ['1', '2']:
        print("退出测试")
        return

    # 初始化机械臂
    try:
        arm = Arm4DoF(device="/dev/ttyUSB1", is_init_pose=False)
    except Exception as e:
        print(f"\n错误：机械臂连接失败 - {e}")
        print("请检查串口连接")
        sys.exit(1)

    # 选择路径
    if choice == '1':
        path = no_avoid_path
        path_name = "无障碍物"
    else:
        path = avoid_path
        path_name = "有障碍物"

    print(f"\n开始执行【{path_name}】路径...")

    try:
        # 执行路径
        for i, point in enumerate(path):
            print(f"  {i+1}. 移动到: {point}")
            arm.move(point, t=MOVE_TIME, wait=True)
            time.sleep(0.2)

        print(f"\n【{path_name}】路径执行完成")

    except Exception as e:
        print(f"\n错误：{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
