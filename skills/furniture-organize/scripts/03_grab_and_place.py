#!/usr/local/miniconda3/bin/python
"""
家具整理 - 抓取放置执行（重构版）

功能：一次进程完成抓取放置，支持避障
硬件：4-DOF 机械臂（UART 串口，/dev/ttyUSB1）
优势：相比子进程方式，减少5次Python启动，节省约2.75秒

用法：
  # 基础用法
  python 03_grab_and_place.py --obj hanbao --grab-pos 163,53,-31 --place 100,0,-31

  # 带障碍物
  python 03_grab_and_place.py --obj hanbao --grab-pos 163,53,-31 --place 100,0,-31 --obstacles "130,25,80,30"

  # 关闭避障（更快）
  python 03_grab_and_place.py --obj hanbao --grab-pos 163,53,-31 --place 100,0,-31 --no-avoid

输出：JSON 格式
"""

import sys
import os
import json
import math
import argparse
import time

# 加载机械臂 SDK
sys.path.insert(0, "/home/HwHiAiUser/arm_voice_soft")
sys.path.insert(0, "/home/HwHiAiUser/arm_voice_soft/utils_arm")

from arm4dof import Arm4DoF

# ==================== 配置 ====================

# 安全高度（mm）
SAFE_HEIGHT = 80

# 安全位坐标
SAFE_POS = [150, 0, 80]

# 悬停高度（抓取/放置位置上方）
HOVER_HEIGHT = 25

# 最小安全距离（mm）
MIN_SAFE_DISTANCE = 50

# 运动时间（秒）
MOVE_TIME = 0.75

# 夹爪动作时间（秒）
GRIPPER_TIME = 0.5

# 物品中文名称
TYPE_LABELS = {
    'cola': '可乐',
    'hanbao': '汉堡',
    'shutiao': '薯条',
    'panzi': '盘子',
}

# 物品默认高度（mm）
DEFAULT_HEIGHT = -31.2


# ==================== 避障功能 ====================

def line_intersects_sphere(start, end, sphere):
    """检查线段是否与球体相交"""
    center = sphere.get('center', [0, 0, 0])
    radius = sphere.get('radius', 30)

    # 线段方向向量
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    dz = end[2] - start[2]

    # 球心到起点的向量
    cx = center[0] - start[0]
    cy = center[1] - start[1]
    cz = center[2] - start[2]

    # 计算投影参数 t
    t = (cx * dx + cy * dy + cz * dz) / (dx * dx + dy * dy + dz * dz + 1e-10)
    t = max(0, min(1, t))  # 限制在 [0, 1] 范围内

    # 线段上最近点
    nearest_x = start[0] + t * dx
    nearest_y = start[1] + t * dy
    nearest_z = start[2] + t * dz

    # 计算距离
    distance = math.sqrt(
        (nearest_x - center[0])**2 +
        (nearest_y - center[1])**2 +
        (nearest_z - center[2])**2
    )

    # 判断是否碰撞
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

    # 线段长度
    length = math.sqrt(dx * dx + dy * dy)
    if length == 0:
        return math.sqrt(
            (point[0] - line_start[0])**2 +
            (point[1] - line_start[1])**2
        )

    # 计算投影参数
    t = ((point[0] - line_start[0]) * dx + (point[1] - line_start[1]) * dy) / (length * length)
    t = max(0, min(1, t))

    # 最近点
    nearest_x = line_start[0] + t * dx
    nearest_y = line_start[1] + t * dy

    return math.sqrt(
        (point[0] - nearest_x)**2 +
        (point[1] - nearest_y)**2
    )


def calculate_detour_point(start, end, obstacles):
    """计算绕行点"""
    # 找到最近的障碍物
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

        # 使用向量叉积判断障碍物在路径的哪一侧
        cross_product = (end[0] - start[0]) * (obs_center[1] - start[1]) - \
                       (end[1] - start[1]) * (obs_center[0] - start[0])

        if cross_product > 0:
            # 障碍物在左侧，从右侧绕
            detour_y = obs_center[1] - obs_radius - MIN_SAFE_DISTANCE
        else:
            # 障碍物在右侧，从左侧绕
            detour_y = obs_center[1] + obs_radius + MIN_SAFE_DISTANCE

        return [obs_center[0], detour_y, SAFE_HEIGHT]

    # 默认：直接到目标上方
    return [end[0], end[1], SAFE_HEIGHT]


# ==================== 主函数 ====================

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='家具整理 - 抓取放置执行')
    parser.add_argument('--obj', type=str, required=True,
                        help='物品类别（cola/hanbao/shutiao/panzi）')
    parser.add_argument('--place', type=str, required=True,
                        help='放置位置坐标 x,y,z（机械臂坐标）')
    parser.add_argument('--grab-pos', type=str, default='',
                        help='抓取位置坐标 x,y,z（可选，默认从视觉获取）')
    parser.add_argument('--obstacles', type=str, default='',
                        help='障碍物列表 x1,y1,z1,r1;x2,y2,z2,r2（可选）')
    parser.add_argument('--no-avoid', action='store_true',
                        help='关闭避障功能（更快）')
    parser.add_argument('--no-safe', action='store_true',
                        help='不经过安全位（直接路径）')
    parser.add_argument('--json', action='store_true',
                        help='JSON格式输出')

    args = parser.parse_args()

    # 解析抓取位置
    if not args.grab_pos:
        print(json.dumps({"error": "未指定抓取位置"}, ensure_ascii=False))
        sys.exit(1)

    try:
        grab_pos = [float(x) for x in args.grab_pos.split(',')]
    except ValueError:
        print(json.dumps({"error": "抓取位置坐标格式错误"}, ensure_ascii=False))
        sys.exit(1)

    # 解析放置位置
    try:
        place_pos = [float(x) for x in args.place.split(',')]
    except ValueError:
        print(json.dumps({"error": "放置位置坐标格式错误"}, ensure_ascii=False))
        sys.exit(1)

    # 解析障碍物
    obstacles = []
    if args.obstacles:
        for obs_str in args.obstacles.split(';'):
            try:
                parts = [float(x) for x in obs_str.split(',')]
                if len(parts) >= 4:
                    obstacles.append({
                        'center': [parts[0], parts[1], parts[2]],
                        'radius': parts[3]
                    })
            except ValueError:
                continue

    # 获取物品标签
    label = TYPE_LABELS.get(args.obj, args.obj)

    print(f"开始抓取放置: {label}")
    print(f"抓取位置: {grab_pos}")
    print(f"放置位置: {place_pos}")
    if obstacles:
        print(f"障碍物数量: {len(obstacles)}")

    # 初始化机械臂
    try:
        arm = Arm4DoF(device="/dev/ttyUSB1", is_init_pose=False)
    except Exception as e:
        print(json.dumps({"success": False, "error": f"机械臂连接失败: {str(e)}"}, ensure_ascii=False))
        sys.exit(1)

    try:
        # ========== 抓取流程 ==========

        # 1. 打开夹爪
        print("打开夹爪")
        arm.gripper_open(degrees=25, t=GRIPPER_TIME)

        # 2. 转向目标方向（atan2计算）
        print("转向目标方向")
        theta0 = math.atan2(grab_pos[1], grab_pos[0])
        arm.set_joint2({0: theta0}, T=0.5)

        # 3. 避障：如果需要绕行
        if not args.no_avoid and obstacles:
            current_pos = SAFE_POS
            target_hover = [grab_pos[0], grab_pos[1], SAFE_HEIGHT]

            if need_detour(current_pos, target_hover, obstacles):
                print(f"[避障] 当前位置: {current_pos}")
                print(f"[避障] 目标上方: {target_hover}")
                print(f"[避障] 检测到障碍物，计算绕行路径")

                # 显示障碍物信息
                for i, obs in enumerate(obstacles):
                    print(f"[避障] 障碍物{i+1}: 中心{obs['center']}, 半径{obs['radius']}mm")

                detour_point = calculate_detour_point(current_pos, target_hover, obstacles)
                print(f"[避障] 绕行点: {detour_point}")
                print(f"[避障] 开始绕行...")
                arm.move(detour_point, t=MOVE_TIME, wait=True)
                print(f"[避障] 绕行完成，当前位置: {detour_point}")

        # 4. 移动到抓取位置上方（悬停）
        hover_pos = [grab_pos[0], grab_pos[1], grab_pos[2] + HOVER_HEIGHT]
        print(f"[轨迹] 移动到抓取位置上方: {hover_pos}")
        arm.move(hover_pos, t=MOVE_TIME, wait=True)

        # 5. 下降到抓取位置
        print(f"[轨迹] 下降到抓取位置: {grab_pos}")
        arm.move(grab_pos, t=MOVE_TIME, wait=True)
        time.sleep(0.3)

        # 6. 夹取
        print("[动作] 关闭夹爪")
        arm.gripper_close(t=GRIPPER_TIME)
        time.sleep(0.3)

        # 7. 抬起
        print(f"[轨迹] 抬起到悬停位置: {hover_pos}")
        arm.move(hover_pos, t=MOVE_TIME, wait=True)

        # 8. 安全位过渡（避免路径横甩）
        if not args.no_safe:
            print(f"[轨迹] 经过安全位过渡: {SAFE_POS}")
            arm.move(SAFE_POS, t=MOVE_TIME, wait=True)

        # ========== 放置流程 ==========

        # 9. 避障：如果需要绕行到放置位置
        if not args.no_avoid and obstacles:
            current_pos = SAFE_POS if not args.no_safe else [grab_pos[0], grab_pos[1], SAFE_HEIGHT]
            place_hover = [place_pos[0], place_pos[1], SAFE_HEIGHT]

            if need_detour(current_pos, place_hover, obstacles):
                print(f"[避障] 当前位置: {current_pos}")
                print(f"[避障] 目标上方: {place_hover}")
                print(f"[避障] 检测到障碍物，计算绕行路径")

                # 显示障碍物信息
                for i, obs in enumerate(obstacles):
                    print(f"[避障] 障碍物{i+1}: 中心{obs['center']}, 半径{obs['radius']}mm")

                detour_point = calculate_detour_point(current_pos, place_hover, obstacles)
                print(f"[避障] 绕行点: {detour_point}")
                print(f"[避障] 开始绕行...")
                arm.move(detour_point, t=MOVE_TIME, wait=True)
                print(f"[避障] 绕行完成，当前位置: {detour_point}")

        # 10. 移动到放置位置上方（悬停）
        place_hover_pos = [place_pos[0], place_pos[1], place_pos[2] + HOVER_HEIGHT]
        print(f"[轨迹] 移动到放置位置上方: {place_hover_pos}")
        arm.move(place_hover_pos, t=MOVE_TIME, wait=True)

        # 11. 下降到放置位置
        print(f"[轨迹] 下降到放置位置: {place_pos}")
        arm.move(place_pos, t=MOVE_TIME, wait=True)
        time.sleep(0.3)

        # 12. 松开
        print("[动作] 打开夹爪")
        arm.gripper_open(degrees=25, t=GRIPPER_TIME)
        time.sleep(0.3)

        # 13. 抬起
        print(f"[轨迹] 抬起到悬停位置: {place_hover_pos}")
        arm.move(place_hover_pos, t=MOVE_TIME, wait=True)

        # 14. 回到安全位（避免下次操作路径横甩）
        if not args.no_safe:
            print(f"[轨迹] 回到安全位: {SAFE_POS}")
            arm.move(SAFE_POS, t=MOVE_TIME, wait=True)

        # 输出结果
        result = {
            "success": True,
            "object": args.obj,
            "label": label,
            "grab_position": {"x": grab_pos[0], "y": grab_pos[1], "z": grab_pos[2]},
            "place_position": {"x": place_pos[0], "y": place_pos[1], "z": place_pos[2]},
            "obstacles_count": len(obstacles),
            "avoid_enabled": not args.no_avoid,
            "safe_enabled": not args.no_safe
        }

        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print("\n结果: 抓取放置完成")

    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
