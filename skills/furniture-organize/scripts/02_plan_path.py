#!/usr/local/miniconda3/bin/python
"""
家具整理 - 路径规划
功能：根据起点、终点和障碍物规划运动路径，支持简单避障
"""

import sys
import json
import math
import argparse

# ==================== 配置 ====================

# 安全高度（mm）
SAFE_HEIGHT = 80

# 机械臂基准高度
ARM_BASE_HEIGHT = 30

# 最小安全距离（mm）
MIN_SAFE_DISTANCE = 50


# ==================== 路径规划器 ====================

class PathPlanner:
    """路径规划器"""

    def __init__(self):
        self.safe_height = SAFE_HEIGHT

    def plan_path(self, start, end, obstacles=None, grab=False, place=False):
        """
        规划运动路径

        参数：
            start: 起点 [x, y, z]
            end: 终点 [x, y, z]
            obstacles: 障碍物列表 [{'center': [x,y,z], 'radius': r}, ...]
            grab: 是否是抓取动作
            place: 是否是放置动作

        返回：
            path: 路径点列表
        """
        path = []

        # 1. 起点 → 安全高度
        if start[2] < self.safe_height:
            path.append({
                'action': 'move',
                'position': [start[0], start[1], self.safe_height],
                'comment': '抬升到安全高度'
            })

        # 2. 检查是否需要避障
        need_detour = False
        if obstacles:
            need_detour = self._need_detour(start, end, obstacles)

        # 3. 移动到目标上方
        if need_detour:
            # 有障碍物，绕行
            detour_point = self._calculate_detour_point(start, end, obstacles)
            path.append({
                'action': 'move',
                'position': [detour_point[0], detour_point[1], self.safe_height],
                'comment': '绕过障碍物'
            })

        path.append({
            'action': 'move',
            'position': [end[0], end[1], self.safe_height],
            'comment': '移动到目标上方'
        })

        # 4. 下降到目标位置
        path.append({
            'action': 'move',
            'position': [end[0], end[1], end[2]],
            'comment': '下降到目标位置'
        })

        # 5. 执行动作（抓取或放置）
        if grab:
            path.append({
                'action': 'grab',
                'position': [end[0], end[1], end[2]],
                'comment': '执行抓取'
            })
        elif place:
            path.append({
                'action': 'place',
                'position': [end[0], end[1], end[2]],
                'comment': '执行放置'
            })

        # 6. 抬起
        path.append({
            'action': 'move',
            'position': [end[0], end[1], self.safe_height],
            'comment': '完成后抬起'
        })

        return path

    def plan_grab_path(self, start, target_pos, obstacles=None):
        """规划抓取路径"""
        return self.plan_path(start, target_pos, obstacles, grab=True)

    def plan_place_path(self, start, place_pos, obstacles=None):
        """规划放置路径"""
        return self.plan_path(start, place_pos, obstacles, place=True)

    def plan_grab_and_place(self, grab_pos, place_pos, obstacles=None):
        """规划完整的抓取-放置路径"""
        path = []

        # 1. 从当前位置到抓取位置（抓取）
        grab_path = self.plan_grab_path(
            [grab_pos[0], grab_pos[1], self.safe_height],
            grab_pos,
            obstacles
        )
        path.extend(grab_path)

        # 2. 从抓取位置到放置位置（放置）
        place_path = self.plan_place_path(
            [grab_pos[0], grab_pos[1], self.safe_height],
            place_pos,
            obstacles
        )
        path.extend(place_path)

        return path

    def _need_detour(self, start, end, obstacles):
        """判断是否需要绕行"""
        for obs in obstacles:
            if self._line_intersects_sphere(start, end, obs):
                return True
        return False

    def _line_intersects_sphere(self, start, end, sphere):
        """检查线段是否与球体相交"""
        center = sphere.get('center', [0, 0, 0])
        radius = sphere.get('radius', 30)

        # 线段参数方程: P = start + t * (end - start), t ∈ [0, 1]
        # 计算球心到线段的最短距离
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

        # 最近点
        nearest_x = start[0] + t * dx
        nearest_y = start[1] + t * dy
        nearest_z = start[2] + t * dz

        # 计算距离
        distance = math.sqrt(
            (nearest_x - center[0])**2 +
            (nearest_y - center[1])**2 +
            (nearest_z - center[2])**2
        )

        return distance < (radius + MIN_SAFE_DISTANCE)

    def _calculate_detour_point(self, start, end, obstacles):
        """计算绕行点"""
        # 找到路径上最近的障碍物
        nearest_obs = None
        min_distance = float('inf')

        for obs in obstacles:
            # 计算障碍物中心到线段的距离
            center = obs.get('center', [0, 0, 0])
            distance = self._point_to_line_distance(center, start, end)
            if distance < min_distance:
                min_distance = distance
                nearest_obs = obs

        if nearest_obs:
            obs_center = nearest_obs.get('center', [0, 0, 0])
            obs_radius = nearest_obs.get('radius', 30)

            # 判断绕行方向
            # 使用向量叉积判断障碍物在路径的哪一侧
            cross_product = (end[0] - start[0]) * (obs_center[1] - start[1]) - \
                           (end[1] - start[1]) * (obs_center[0] - start[0])

            if cross_product > 0:
                # 障碍物在左侧，从右侧绕
                detour_y = obs_center[1] - obs_radius - MIN_SAFE_DISTANCE
            else:
                # 障碍物在右侧，从左侧绕
                detour_y = obs_center[1] + obs_radius + MIN_SAFE_DISTANCE

            return [obs_center[0], detour_y, self.safe_height]

        # 默认：直接到目标上方
        return [end[0], end[1], self.safe_height]

    def _point_to_line_distance(self, point, line_start, line_end):
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


# ==================== 坐标转换 ====================

def workspace_to_arm(ws_x, ws_y):
    """工作台坐标转机械臂坐标"""
    # 直接使用 coord-transform 的转换函数
    # 这里简化处理，实际应调用 04_ws2arm.py
    arm_x = ws_x + 150
    arm_y = ws_y
    return arm_x, arm_y


def pixel_to_arm(px, py):
    """像素坐标转机械臂坐标"""
    # 像素→工作台→机械臂
    # 这里简化处理，实际应调用 coord-transform
    ws_x = px - 320
    ws_y = py - 240
    return workspace_to_arm(ws_x, ws_y)


# ==================== 主函数 ====================

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='家具整理 - 路径规划')
    parser.add_argument('--start', type=str, default='150,0,80',
                        help='起点坐标 x,y,z（默认150,0,80）')
    parser.add_argument('--end', type=str, required=True,
                        help='终点坐标 x,y,z')
    parser.add_argument('--obstacles', type=str, default='',
                        help='障碍物列表 x1,y1,z1,r1;x2,y2,z2,r2')
    parser.add_argument('--grab', action='store_true',
                        help='执行抓取动作')
    parser.add_argument('--place', action='store_true',
                        help='执行放置动作')
    parser.add_argument('--json', action='store_true',
                        help='JSON格式输出')

    args = parser.parse_args()

    # 解析起点
    try:
        start = [float(x) for x in args.start.split(',')]
    except ValueError:
        print(json.dumps({"error": "起点坐标格式错误"}, ensure_ascii=False))
        sys.exit(1)

    # 解析终点
    try:
        end = [float(x) for x in args.end.split(',')]
    except ValueError:
        print(json.dumps({"error": "终点坐标格式错误"}, ensure_ascii=False))
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

    # 规划路径
    planner = PathPlanner()
    path = planner.plan_path(
        start, end, obstacles,
        grab=args.grab,
        place=args.place
    )

    # 输出结果
    output = {
        "start": start,
        "end": end,
        "path": path,
        "step_count": len(path),
        "has_obstacle": len(obstacles) > 0,
        "status": "ok"
    }

    if args.json:
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        # 简洁输出
        print(f"起点: {start}")
        print(f"终点: {end}")
        print(f"路径点数: {len(path)}")
        print(f"有障碍物: {'是' if obstacles else '否'}")
        print("\n路径详情:")
        for i, step in enumerate(path):
            print(f"  {i+1}. {step['comment']}: {step['position']}")


if __name__ == "__main__":
    main()
