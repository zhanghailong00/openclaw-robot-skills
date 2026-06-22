#!/usr/local/miniconda3/bin/python
"""
检测物品坐标

功能：检测桌面上的物品，输出机械臂坐标
用法：python detect_positions.py
"""

import sys
import os
import json
import subprocess

# ==================== 配置 ====================

PYTHON_PATH = "/usr/local/miniconda3/bin/python"
SKILLS_DIR = "/home/HwHiAiUser/.openclaw/workspace/skills"

# 脚本路径
DETECT_SCRIPT = os.path.join(SKILLS_DIR, "vision-detect/scripts/02_run_detection.py")
COORD_SCRIPT = os.path.join(SKILLS_DIR, "coord-transform/scripts/02_convert.py")

# 目标物品
TARGET_ITEMS = {'cola', 'hanbao', 'shutiao'}


def run_script(script_path, args=None):
    """运行子脚本并解析JSON"""
    cmd = [PYTHON_PATH, script_path]
    if args:
        cmd.extend(args)

    result = subprocess.run(cmd, capture_output=True, text=True)

    # 解析JSON（处理多行输出）
    stdout = result.stdout.strip()
    json_objects = []
    i = 0
    while i < len(stdout):
        start = stdout.find('{', i)
        if start == -1:
            break

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

    return json_objects[-1] if json_objects else None


def main():
    """主函数"""
    print("=" * 60)
    print("检测物品坐标")
    print("=" * 60)

    # 1. 检测物品
    print("\n[1] 检测桌面物品...")
    result = run_script(DETECT_SCRIPT)

    if not result or result.get('status') != 'ok':
        print("❌ 检测失败")
        return

    detections = result.get('detections', [])
    print(f"检测到 {len(detections)} 个物品")

    # 2. 转换坐标
    print("\n[2] 转换坐标...")
    items = []

    for det in detections:
        item_class = det.get('class', '')
        if item_class not in TARGET_ITEMS:
            continue

        # 像素坐标
        px = det.get('cx', 0)
        py = det.get('cy', 0)

        # 转换为机械臂坐标
        cmd = [PYTHON_PATH, COORD_SCRIPT, "--px", str(px), "--py", str(py), "--json"]
        coord_result = run_script(COORD_SCRIPT, ["--px", str(px), "--py", str(py), "--json"])

        if coord_result and 'arm_target' in coord_result:
            arm = coord_result['arm_target']
            items.append({
                'class': item_class,
                'label': det.get('label', ''),
                'confidence': det.get('confidence', 0),
                'pixel': {'x': px, 'y': py},
                'arm': {'x': arm['x'], 'y': arm['y'], 'z': arm['z']}
            })

    # 3. 输出结果
    print("\n[3] 检测结果:")
    print(f"{'物品':<10} {'置信度':<10} {'像素坐标':<20} {'机械臂坐标'}")
    print("-" * 70)

    for item in items:
        print(f"{item['label']:<10} {item['confidence']:<10.3f} ({item['pixel']['x']:.1f}, {item['pixel']['y']:.1f})  ({item['arm']['x']:.1f}, {item['arm']['y']:.1f}, {item['arm']['z']:.1f})")

    # 4. 输出放置区域建议
    if len(items) >= 2:
        print("\n[4] 放置区域建议:")

        # 计算边界
        x_values = [item['arm']['x'] for item in items]
        y_values = [item['arm']['y'] for item in items]

        x_min = min(x_values) - 10  # 留出边距
        x_max = max(x_values) + 10
        y_min = min(y_values) - 10
        y_max = max(y_values) + 10

        print(f"PLACE_AREA = {{")
        print(f"    'x_min': {x_min:.0f},    # X左边界")
        print(f"    'x_max': {x_max:.0f},   # X右边界")
        print(f"    'y_min': {y_min:.0f},    # Y下边界")
        print(f"    'y_max': {y_max:.0f},   # Y上边界")
        print(f"    'z': {items[0]['arm']['z']:.1f}      # 放置高度")
        print(f"}}")


if __name__ == "__main__":
    main()
