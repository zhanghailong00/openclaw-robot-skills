#!/usr/local/miniconda3/bin/python
"""
避障可视化测试脚本

功能：显示详细的运动轨迹，帮助理解避障过程
用法：python test_avoid_visual.py
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
    print("避障可视化测试")
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

    # 初始化机械臂
    try:
        arm = Arm4DoF(device="/dev/ttyUSB1", is_init_pose=False)
    except Exception as e:
        print(f"\n错误：机械臂连接失败 - {e}")
        print("请检查串口连接")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("开始执行抓取流程")
    print("=" * 60)

    try:
        # 1. 打开夹爪
        print("\n[步骤1] 打开夹爪")
        arm.gripper_open(degrees=25, t=GRIPPER_TIME)

        # 2. 转向目标方向
        print("\n[步骤2] 转向目标方向")
        theta0 = math.atan2(grab_pos[1], grab_pos[0])
        print(f"  目标角度: {math.degrees(theta0):.1f}°")
        arm.set_joint2({0: theta0}, T=0.5)

        # 3. 避障判断（抓取）
        print("\n[步骤3] 避障判断（抓取）")
        current_pos = SAFE_POS
        target_hover = [grab_pos[0], grab_pos[1], SAFE_HEIGHT]

        print(f"  当前位置: {current_pos}")
        print(f"  目标上方: {target_hover}")

        if need_detour(current_pos, target_hover, obstacles):
            print("  ✓ 检测到障碍物，需要绕行")

            # 显示障碍物信息
            for i, obs in enumerate(obstacles):
                print(f"  障碍物{i+1}: {obs['label']} - 中心{obs['center']}, 半径{obs['radius']}mm")

            detour_point = calculate_detour_point(current_pos, target_hover, obstacles)
            print(f"  ✓ 计算绕行点: {detour_point}")

            # 计算绕行距离
            detour_distance = math.sqrt(
                (detour_point[0] - current_pos[0])**2 +
                (detour_point[1] - current_pos[1])**2
            )
            print(f"  ✓ 绕行距离: {detour_distance:.1f}mm")

            print("\n  开始绕行...")
            arm.move(detour_point, t=MOVE_TIME, wait=True)
            print(f"  ✓ 绕行完成，当前位置: {detour_point}")
        else:
            print("  ✗ 未检测到障碍物，直接移动")

        # 4. 移动到抓取位置上方
        print("\n[步骤4] 移动到抓取位置上方")
        hover_pos = [grab_pos[0], grab_pos[1], grab_pos[2] + HOVER_HEIGHT]
        print(f"  目标位置: {hover_pos}")
        arm.move(hover_pos, t=MOVE_TIME, wait=True)
        print(f"  ✓ 移动完成")

        # 5. 下降到抓取位置
        print("\n[步骤5] 下降到抓取位置")
        print(f"  目标位置: {grab_pos}")
        arm.move(grab_pos, t=MOVE_TIME, wait=True)
        time.sleep(0.3)
        print(f"  ✓ 下降完成")

        # 6. 夹取
        print("\n[步骤6] 夹取")
        arm.gripper_close(t=GRIPPER_TIME)
        time.sleep(0.3)
        print(f"  ✓ 夹取完成")

        # 7. 抬起
        print("\n[步骤7] 抬起")
        print(f"  目标位置: {hover_pos}")
        arm.move(hover_pos, t=MOVE_TIME, wait=True)
        print(f"  ✓ 抬起完成")

        # 8. 安全位过渡
        print("\n[步骤8] 安全位过渡")
        print(f"  目标位置: {SAFE_POS}")
        arm.move(SAFE_POS, t=MOVE_TIME, wait=True)
        print(f"  ✓ 安全位过渡完成")

        # 9. 避障判断（放置）
        print("\n[步骤9] 避障判断（放置）")
        current_pos = SAFE_POS
        place_hover = [place_pos[0], place_pos[1], SAFE_HEIGHT]

        print(f"  当前位置: {current_pos}")
        print(f"  目标上方: {place_hover}")

        if need_detour(current_pos, place_hover, obstacles):
            print("  ✓ 检测到障碍物，需要绕行")

            detour_point = calculate_detour_point(current_pos, place_hover, obstacles)
            print(f"  ✓ 计算绕行点: {detour_point}")

            detour_distance = math.sqrt(
                (detour_point[0] - current_pos[0])**2 +
                (detour_point[1] - current_pos[1])**2
            )
            print(f"  ✓ 绕行距离: {detour_distance:.1f}mm")

            print("\n  开始绕行...")
            arm.move(detour_point, t=MOVE_TIME, wait=True)
            print(f"  ✓ 绕行完成，当前位置: {detour_point}")
        else:
            print("  ✗ 未检测到障碍物，直接移动")

        # 10. 移动到放置位置上方
        print("\n[步骤10] 移动到放置位置上方")
        place_hover_pos = [place_pos[0], place_pos[1], place_pos[2] + HOVER_HEIGHT]
        print(f"  目标位置: {place_hover_pos}")
        arm.move(place_hover_pos, t=MOVE_TIME, wait=True)
        print(f"  ✓ 移动完成")

        # 11. 下降到放置位置
        print("\n[步骤11] 下降到放置位置")
        print(f"  目标位置: {place_pos}")
        arm.move(place_pos, t=MOVE_TIME, wait=True)
        time.sleep(0.3)
        print(f"  ✓ 下降完成")

        # 12. 松开
        print("\n[步骤12] 松开夹爪")
        arm.gripper_open(degrees=25, t=GRIPPER_TIME)
        time.sleep(0.3)
        print(f"  ✓ 松开完成")

        # 13. 抬起
        print("\n[步骤13] 抬起")
        print(f"  目标位置: {place_hover_pos}")
        arm.move(place_hover_pos, t=MOVE_TIME, wait=True)
        print(f"  ✓ 抬起完成")

        # 14. 回到安全位
        print("\n[步骤14] 回到安全位")
        print(f"  目标位置: {SAFE_POS}")
        arm.move(SAFE_POS, t=MOVE_TIME, wait=True)
        print(f"  ✓ 回到安全位完成")

        print("\n" + "=" * 60)
        print("抓取流程完成")
        print("=" * 60)

        # 显示运动轨迹总结
        print("\n运动轨迹总结：")
        print(f"  1. 安全位: {SAFE_POS}")
        print(f"  2. 绕行点: {detour_point if need_detour(SAFE_POS, [grab_pos[0], grab_pos[1], SAFE_HEIGHT], obstacles) else '无'}")
        print(f"  3. 抓取上方: {hover_pos}")
        print(f"  4. 抓取位置: {grab_pos}")
        print(f"  5. 安全位: {SAFE_POS}")
        print(f"  6. 绕行点: {detour_point if need_detour(SAFE_POS, [place_pos[0], place_pos[1], SAFE_HEIGHT], obstacles) else '无'}")
        print(f"  7. 放置上方: {place_hover_pos}")
        print(f"  8. 放置位置: {place_pos}")
        print(f"  9. 安全位: {SAFE_POS}")

    except Exception as e:
        print(f"\n错误：{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
