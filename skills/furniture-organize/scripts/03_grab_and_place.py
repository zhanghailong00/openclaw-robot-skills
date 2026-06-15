#!/usr/local/miniconda3/bin/python
"""
家具整理 - 抓取放置执行
功能：根据物品类别和放置位置，执行抓取和放置动作
"""

import sys
import os
import json
import math
import argparse
import subprocess

# ==================== 配置 ====================

# Python解释器路径
PYTHON_PATH = "/usr/local/miniconda3/bin/python"

# 技能目录
SKILLS_DIR = "/home/HwHiAiUser/.openclaw/workspace/skills"

# 坐标转换脚本路径
COORD_WS2ARM_SCRIPT = os.path.join(SKILLS_DIR, "coord-transform/scripts/04_ws2arm.py")

# 基础运动脚本路径
ARM_MOVE_SCRIPT = os.path.join(SKILLS_DIR, "arm-basic/scripts/04_move_to.py")

# 夹爪控制脚本路径
ARM_GRIPPER_SCRIPT = os.path.join(SKILLS_DIR, "arm-basic/scripts/03_gripper.py")

# 安全高度（mm）
SAFE_HEIGHT = 80

# 最小安全距离（mm）
MIN_SAFE_DISTANCE = 50

# 夹爪参数
GRIPPER_OPEN_DEGREES = 25
GRIPPER_CLOSE_DEGREES = 0
GRIPPER_SPEED = 50

# 物品中文名称
TYPE_LABELS = {
    'cola': '可乐',
    'hanbao': '汉堡',
    'shutiao': '薯条',
    'panzi': '盘子',
}

# 物品默认高度（mm）
DEFAULT_HEIGHT = -31.2


# ==================== 坐标转换 ====================

def workspace_to_arm(ws_x, ws_y):
    """工作台坐标转机械臂坐标"""
    cmd = [
        PYTHON_PATH,
        COORD_WS2ARM_SCRIPT,
        "--ws", f"{ws_x},{ws_y}",
        "--json"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return None, None

    try:
        data = json.loads(result.stdout)
        if data.get('status') == 'ok':
            arm = data.get('arm', {})
            return arm.get('x'), arm.get('y')
    except json.JSONDecodeError:
        pass

    return None, None


# ==================== 机械臂控制 ====================

def parse_json_output(stdout):
    """从stdout中提取JSON对象"""
    try:
        stdout = stdout.strip()
        # 查找所有 JSON 对象
        json_objects = []
        i = 0
        while i < len(stdout):
            start = stdout.find('{', i)
            if start == -1:
                break

            # 找到匹配的结束括号
            depth = 0
            end = start
            for j in range(start, len(stdout)):
                if stdout[j] == '{':
                    depth += 1
                elif stdout[j] == '}':
                    depth -= 1
                    if depth == 0:
                        end = j + 1
                        break

            if depth == 0:
                json_str = stdout[start:end]
                try:
                    obj = json.loads(json_str)
                    json_objects.append(obj)
                except json.JSONDecodeError:
                    pass
                i = end
            else:
                i = start + 1

        # 返回最后一个JSON对象
        if json_objects:
            return json_objects[-1]
    except Exception:
        pass
    return None


def move_arm(x, y, z):
    """移动机械臂到指定位置"""
    cmd = [
        PYTHON_PATH,
        ARM_MOVE_SCRIPT,
        "--x", str(x),
        "--y", str(y),
        "--z", str(z)
    ]

    print(f"[DEBUG] 执行命令: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(f"[DEBUG] returncode: {result.returncode}")
    print(f"[DEBUG] stdout: {result.stdout[:200]}")
    print(f"[DEBUG] stderr: {result.stderr[:200]}")

    if result.returncode != 0:
        print(f"[DEBUG] move_arm 失败")
        return False

    data = parse_json_output(result.stdout)
    print(f"[DEBUG] 解析结果: {data}")
    if data:
        return data.get('success') == True
    return False


def control_gripper(open=True):
    """控制夹爪开合"""
    action = "open" if open else "close"

    cmd = [
        PYTHON_PATH,
        ARM_GRIPPER_SCRIPT,
        "--action", action
    ]

    print(f"[DEBUG] 执行命令: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(f"[DEBUG] returncode: {result.returncode}")
    print(f"[DEBUG] stdout: {result.stdout[:200]}")
    print(f"[DEBUG] stderr: {result.stderr[:200]}")

    if result.returncode != 0:
        print(f"[DEBUG] control_gripper 失败")
        return False

    data = parse_json_output(result.stdout)
    print(f"[DEBUG] 解析结果: {data}")
    if data:
        return data.get('success') == True
    return False


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


def move_with_obstacle_avoidance(start, end, obstacles=None):
    """带避障的移动"""
    # 1. 先抬升到安全高度
    if start[2] < SAFE_HEIGHT:
        print(f"  [避障] 抬升到安全高度")
        if not move_arm(start[0], start[1], SAFE_HEIGHT):
            return False

    # 2. 检查是否需要避障
    if obstacles and need_detour(start, end, obstacles):
        print(f"  [避障] 检测到障碍物，计算绕行路径")
        detour_point = calculate_detour_point(start, end, obstacles)
        print(f"  [避障] 绕行点: {detour_point}")

        # 移动到绕行点
        if not move_arm(detour_point[0], detour_point[1], SAFE_HEIGHT):
            return False

        # 从绕行点移动到目标上方
        if not move_arm(end[0], end[1], SAFE_HEIGHT):
            return False
    else:
        # 无障碍物，直接移动到目标上方
        if not move_arm(end[0], end[1], SAFE_HEIGHT):
            return False

    # 3. 下降到目标位置
    if not move_arm(end[0], end[1], end[2]):
        return False

    return True


# ==================== 抓取放置流程 ====================

def grab_object(grab_pos, obstacles=None):
    """
    抓取物品

    参数：
        grab_pos: [x, y, z] 抓取位置（机械臂坐标）
        obstacles: 障碍物列表（可选）
    """
    print(f"移动到抓取位置上方 ({grab_pos[0]}, {grab_pos[1]}, {SAFE_HEIGHT})")

    # 1. 移动到抓取位置上方（带避障）
    current_pos = [grab_pos[0], grab_pos[1], SAFE_HEIGHT]  # 假设当前位置
    if not move_with_obstacle_avoidance(current_pos, grab_pos, obstacles):
        return False, "移动到抓取位置上方失败"

    print(f"打开夹爪")
    # 2. 打开夹爪
    if not control_gripper(open=True):
        return False, "打开夹爪失败"

    print(f"下降到抓取位置 ({grab_pos[0]}, {grab_pos[1]}, {grab_pos[2]})")
    # 3. 下降到抓取位置
    if not move_arm(grab_pos[0], grab_pos[1], grab_pos[2]):
        return False, "下降到抓取位置失败"

    print(f"关闭夹爪")
    # 4. 关闭夹爪（抓取）
    if not control_gripper(open=False):
        return False, "关闭夹爪失败"

    print(f"抬起到安全高度")
    # 5. 抬起
    if not move_arm(grab_pos[0], grab_pos[1], SAFE_HEIGHT):
        return False, "抬起失败"

    return True, "抓取成功"


def place_object(place_pos, obstacles=None):
    """
    放置物品

    参数：
        place_pos: [x, y, z] 放置位置（机械臂坐标）
        obstacles: 障碍物列表（可选）
    """
    print(f"移动到放置位置上方 ({place_pos[0]}, {place_pos[1]}, {SAFE_HEIGHT})")

    # 1. 移动到放置位置上方（带避障）
    current_pos = [place_pos[0], place_pos[1], SAFE_HEIGHT]  # 假设当前位置
    if not move_with_obstacle_avoidance(current_pos, place_pos, obstacles):
        return False, "移动到放置位置上方失败"

    print(f"下降到放置位置 ({place_pos[0]}, {place_pos[1]}, {place_pos[2]})")
    # 2. 下降到放置位置
    if not move_arm(place_pos[0], place_pos[1], place_pos[2]):
        return False, "下降到放置位置失败"

    print(f"打开夹爪")
    # 3. 打开夹爪（放置）
    if not control_gripper(open=True):
        return False, "打开夹爪失败"

    print(f"抬起到安全高度")
    # 4. 抬起
    if not move_arm(place_pos[0], place_pos[1], SAFE_HEIGHT):
        return False, "抬起失败"

    return True, "放置成功"


def grab_and_place(grab_pos, place_pos, obstacles=None):
    """
    完整的抓取-放置流程

    参数：
        grab_pos: [x, y, z] 抓取位置
        place_pos: [x, y, z] 放置位置
        obstacles: 障碍物列表（可选）
    """
    # 1. 抓取
    success, message = grab_object(grab_pos, obstacles)
    if not success:
        return False, message

    # 2. 放置
    success, message = place_object(place_pos, obstacles)
    if not success:
        return False, message

    return True, "抓取放置完成"


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
    parser.add_argument('--grab-ws', type=str, default='',
                        help='抓取位置工作台坐标 x,y（可选，会自动转换为机械臂坐标）')
    parser.add_argument('--obstacles', type=str, default='',
                        help='障碍物列表 x1,y1,z1,r1;x2,y2,z2,r2（可选）')
    parser.add_argument('--json', action='store_true',
                        help='JSON格式输出')

    args = parser.parse_args()

    # 解析放置位置
    try:
        place_pos = [float(x) for x in args.place.split(',')]
    except ValueError:
        print(json.dumps({"error": "放置位置坐标格式错误"}, ensure_ascii=False))
        sys.exit(1)

    # 获取抓取位置
    grab_pos = None

    if args.grab_pos:
        # 直接使用机械臂坐标
        try:
            grab_pos = [float(x) for x in args.grab_pos.split(',')]
        except ValueError:
            print(json.dumps({"error": "抓取位置坐标格式错误"}, ensure_ascii=False))
            sys.exit(1)
    elif args.grab_ws:
        # 使用工作台坐标，需要转换
        try:
            ws_x, ws_y = [float(x) for x in args.grab_ws.split(',')]
            arm_x, arm_y = workspace_to_arm(ws_x, ws_y)
            if arm_x is None:
                print(json.dumps({"error": "工作台坐标转换失败"}, ensure_ascii=False))
                sys.exit(1)
            grab_pos = [arm_x, arm_y, DEFAULT_HEIGHT]
        except ValueError:
            print(json.dumps({"error": "工作台坐标格式错误"}, ensure_ascii=False))
            sys.exit(1)
    else:
        print(json.dumps({"error": "未指定抓取位置"}, ensure_ascii=False))
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

    # 执行抓取放置
    success, message = grab_and_place(grab_pos, place_pos, obstacles)

    # 输出结果
    output = {
        "object": args.obj,
        "label": label,
        "grab_position": {
            "x": grab_pos[0],
            "y": grab_pos[1],
            "z": grab_pos[2]
        },
        "place_position": {
            "x": place_pos[0],
            "y": place_pos[1],
            "z": place_pos[2]
        },
        "message": message,
        "status": "ok" if success else "error"
    }

    if args.json:
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print(f"\n结果: {message}")


if __name__ == "__main__":
    main()
