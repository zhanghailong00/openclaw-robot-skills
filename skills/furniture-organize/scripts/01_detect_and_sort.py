#!/usr/local/miniconda3/bin/python
"""
家具整理 - 检测与优先级排序
功能：调用YOLO检测桌面物品，按优先级排序后输出物品列表
"""

import sys
import os
import json
import math
import subprocess

# ==================== 配置 ====================

# Python解释器路径
PYTHON_PATH = "/usr/local/miniconda3/bin/python"

# 技能目录
SKILLS_DIR = "/home/HwHiAiUser/.openclaw/workspace/skills"

# 视觉检测脚本路径
VISION_DETECT_SCRIPT = os.path.join(SKILLS_DIR, "vision-detect/scripts/02_run_detection.py")

# 坐标转换脚本路径（一次性完成像素→工作台→机械臂转换）
COORD_TRANSFORM_SCRIPT = os.path.join(SKILLS_DIR, "coord-transform/scripts/02_convert.py")

# 物品类型优先级配置
TYPE_PRIORITY = {
    'cola': 4,      # 可乐 - 最高优先级（饮料先放）
    'hanbao': 3,    # 汉堡 - 中等优先级
    'panzi': 2,     # 盘子 - 较低优先级
    'shutiao': 1,   # 薯条 - 最低优先级
}

# 物品中文名称
TYPE_LABELS = {
    'cola': '可乐',
    'hanbao': '汉堡',
    'shutiao': '薯条',
    'panzi': '盘子',
}

# ==================== 坐标转换 ====================

def pixel_to_arm(px, py):
    """
    像素坐标转机械臂坐标
    调用 coord-transform 的 02_convert.py（一次性完成转换）
    """
    cmd = [
        PYTHON_PATH,
        COORD_TRANSFORM_SCRIPT,
        "--px", str(px),
        "--py", str(py),
        "--json"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return None, None, None

    try:
        # 尝试从stdout中提取JSON
        stdout = result.stdout.strip()
        start = stdout.find('{')
        end = stdout.rfind('}') + 1
        if start != -1 and end > start:
            json_str = stdout[start:end]
            data = json.loads(json_str)

            # 获取机械臂坐标
            arm = data.get('arm_target', {})
            return arm.get('x'), arm.get('y'), arm.get('z')
    except json.JSONDecodeError:
        pass

    return None, None, None


# ==================== 优先级排序 ====================

def calculate_priority(objects):
    """
    计算物品优先级

    优先级规则：
    1. 类型优先级：可乐(3) > 汉堡(2) > 薯条(1)
    2. 同类型按距离中心远近排序，近的优先
    """
    for obj in objects:
        # 获取类型优先级
        type_score = TYPE_PRIORITY.get(obj.get('class', ''), 0)

        # 获取机械臂坐标
        arm_x = obj.get('arm_x')
        arm_y = obj.get('arm_y')

        if arm_x is not None and arm_y is not None:
            # 计算到中心的距离（越近越好）
            # 工作台中心大约在 (0, 0)，机械臂坐标中心大约在 (150, 0)
            distance = math.sqrt((arm_x - 150)**2 + arm_y**2)
            distance_score = 1 / (distance + 1)
        else:
            distance_score = 0

        # 综合分数：类型优先级 + 距离分数
        obj['priority'] = type_score * 10 + distance_score

    # 按优先级降序排列
    objects.sort(key=lambda x: x.get('priority', 0), reverse=True)

    # 添加排名
    for i, obj in enumerate(objects):
        obj['rank'] = i + 1

    return objects


# ==================== 主函数 ====================

def main():
    """主函数"""
    # 1. 调用视觉检测
    print("正在检测桌面物品...")
    cmd = [
        PYTHON_PATH,
        VISION_DETECT_SCRIPT
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    # 调试：打印实际输出
    print(f"[DEBUG] stdout: {result.stdout}")
    print(f"[DEBUG] stderr: {result.stderr}")
    print(f"[DEBUG] returncode: {result.returncode}")

    # 2. 解析检测结果
    try:
        # 尝试从stdout中提取JSON（可能有多行输出）
        stdout = result.stdout.strip()
        # 找到第一个 { 和最后一个 } 之间的内容
        start = stdout.find('{')
        end = stdout.rfind('}') + 1
        if start != -1 and end > start:
            json_str = stdout[start:end]
            detection_result = json.loads(json_str)
        else:
            raise json.JSONDecodeError("No JSON found", stdout, 0)
    except json.JSONDecodeError as e:
        print(json.dumps({
            "error": "视觉检测结果解析失败",
            "detail": str(e),
            "stdout": result.stdout,
            "stderr": result.stderr,
            "status": "error"
        }, ensure_ascii=False))
        sys.exit(1)

    if detection_result.get('status') != 'ok':
        print(json.dumps({
            "error": "视觉检测失败",
            "detail": detection_result,
            "status": "error"
        }, ensure_ascii=False))
        sys.exit(1)

    detections = detection_result.get('detections', [])

    if not detections:
        print(json.dumps({
            "objects": [],
            "count": 0,
            "message": "桌面没有检测到物品",
            "status": "ok"
        }, ensure_ascii=False))
        return

    # 3. 坐标转换
    print(f"检测到 {len(detections)} 个物品，正在转换坐标...")
    objects = []

    for det in detections:
        obj = {
            'class': det.get('class', ''),
            'label': det.get('label', ''),
            'confidence': det.get('confidence', 0),
            'cx': det.get('cx', 0),
            'cy': det.get('cy', 0),
        }

        # 像素坐标转机械臂坐标
        arm_x, arm_y, arm_z = pixel_to_arm(det['cx'], det['cy'])
        if arm_x is not None:
            obj['arm_x'] = arm_x
            obj['arm_y'] = arm_y
            obj['arm_z'] = arm_z
        else:
            obj['arm_x'] = 0
            obj['arm_y'] = 0
            obj['arm_z'] = -31.2

        objects.append(obj)

    # 4. 优先级排序
    print("正在计算优先级...")
    sorted_objects = calculate_priority(objects)

    # 5. 输出结果
    output = {
        "objects": sorted_objects,
        "count": len(sorted_objects),
        "status": "ok"
    }

    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
