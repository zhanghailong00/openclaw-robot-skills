#!/usr/local/miniconda3/bin/python
"""
物体搜寻 - 步骤3：计算堆叠位置

功能：检测桌面物品，计算堆叠位置（像素坐标和机械臂坐标）
用法：python 03_calc_position.py
"""

import sys
import os
import json
import subprocess

# 导入统一配置
from config import (
    PYTHON_PATH, DETECT_SCRIPT, COORD_SCRIPT, TARGET_ITEMS,
    ABOVE_HEIGHT, LEFT_DISTANCE, DOWN_HEIGHT, RIGHT_DISTANCE
)


# ==================== 工具函数 ====================

def run_script(script_path, args=None):
    """运行子脚本并解析JSON"""
    cmd = [PYTHON_PATH, script_path]
    if args:
        cmd.extend(args)

    print(f"执行命令: {' '.join(cmd)}")
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


def pixel_to_arm(px, py):
    """像素坐标转机械臂坐标"""
    result = run_script(COORD_SCRIPT, ["--px", str(px), "--py", str(py), "--json"])
    if result and 'arm_target' in result:
        arm = result['arm_target']
        return [arm['x'], arm['y'], arm['z']]
    return None


# ==================== 主函数 ====================

def main():
    """主函数"""
    print("=" * 60)
    print("物体搜寻 - 步骤3：计算堆叠位置")
    print("=" * 60)

    # 1. 调用 YOLO 检测
    print("\n[1] 调用 YOLO 检测...")
    result = run_script(DETECT_SCRIPT)

    if not result:
        print("错误：检测失败")
        return

    if result.get('status') != 'ok':
        print(f"错误：{result.get('error')}")
        return

    # 2. 解析检测结果（过滤目标物品）
    all_detections = result.get('detections', [])
    count = result.get('count', 0)

    # 只保留目标物品
    target_detections = [d for d in all_detections if d['class'] in TARGET_ITEMS]

    print(f"\n[2] 检测结果:")
    print(f"  所有物品数量: {count}")
    print(f"  目标物品数量: {len(target_detections)}")

    if len(target_detections) == 0:
        print("  桌面没有目标物品，无法计算堆叠位置")
        return

    # 3. 计算像素坐标的平均值（堆叠中心）
    print(f"\n[3] 计算堆叠中心（像素坐标）:")

    sum_cx = 0
    sum_cy = 0

    for i, det in enumerate(target_detections):
        cx = det.get('cx', 0)
        cy = det.get('cy', 0)
        print(f"  物品 {i+1}: ({cx:.1f}, {cy:.1f}) - {det.get('label')}")

        sum_cx += cx
        sum_cy += cy

    avg_cx = sum_cx / len(target_detections)
    avg_cy = sum_cy / len(target_detections)

    print(f"\n  堆叠中心（像素）: ({avg_cx:.1f}, {avg_cy:.1f})")

    # 4. 转换为机械臂坐标
    print(f"\n[4] 转换为机械臂坐标:")

    arm_pos = pixel_to_arm(avg_cx, avg_cy)

    if arm_pos:
        print(f"  堆叠中心（机械臂）: ({arm_pos[0]:.1f}, {arm_pos[1]:.1f}, {arm_pos[2]:.1f})")
    else:
        print(f"  坐标转换失败，使用默认位置")
        arm_pos = [150, 0, -31]
        print(f"  默认位置: {arm_pos}")

    # 5. 计算推倒位置（上方左移下降右移推倒）
    print(f"\n[5] 计算推倒位置:")

    # 推倒参数（从配置文件读取）
    above_height = ABOVE_HEIGHT
    left_distance = LEFT_DISTANCE
    down_height = DOWN_HEIGHT
    right_distance = RIGHT_DISTANCE

    print(f"  推倒方式: 上方左移下降右移推倒")
    print(f"  推倒参数:")
    print(f"    物体上方高度: {above_height}mm")
    print(f"    向左移动距离: {left_distance}mm")
    print(f"    下降高度: {down_height}mm")
    print(f"    向右推倒距离: {right_distance}mm")

    # 步骤1：物体上方100mm
    above_pos = [arm_pos[0], arm_pos[1], arm_pos[2] + above_height]
    print(f"\n  步骤1 - 物体上方: ({above_pos[0]:.1f}, {above_pos[1]:.1f}, {above_pos[2]:.1f})")

    # 步骤2：水平向左移动20mm（Y轴负方向）
    left_pos = [arm_pos[0], arm_pos[1] - left_distance, arm_pos[2] + above_height]
    print(f"  步骤2 - 向左移动: ({left_pos[0]:.1f}, {left_pos[1]:.1f}, {left_pos[2]:.1f})")

    # 步骤3：下降高度70mm
    down_pos = [arm_pos[0], arm_pos[1] - left_distance, arm_pos[2] + above_height - down_height]
    print(f"  步骤3 - 下降高度: ({down_pos[0]:.1f}, {down_pos[1]:.1f}, {down_pos[2]:.1f})")

    # 步骤4：向右移动80mm（推倒，Y轴正方向）
    right_pos = [arm_pos[0], arm_pos[1] - left_distance + right_distance, arm_pos[2] + above_height - down_height]
    print(f"  步骤4 - 向右推倒: ({right_pos[0]:.1f}, {right_pos[1]:.1f}, {right_pos[2]:.1f})")

    # 6. 输出总结
    print(f"\n[6] 总结:")
    print(f"  物品数量: {len(target_detections)}")
    print(f"  像素中心: ({avg_cx:.1f}, {avg_cy:.1f})")
    print(f"  机械臂位置: ({arm_pos[0]:.1f}, {arm_pos[1]:.1f}, {arm_pos[2]:.1f})")
    print(f"  步骤1 - 物体上方: ({above_pos[0]:.1f}, {above_pos[1]:.1f}, {above_pos[2]:.1f})")
    print(f"  步骤2 - 向左移动: ({left_pos[0]:.1f}, {left_pos[1]:.1f}, {left_pos[2]:.1f})")
    print(f"  步骤3 - 下降高度: ({down_pos[0]:.1f}, {down_pos[1]:.1f}, {down_pos[2]:.1f})")
    print(f"  步骤4 - 向右推倒: ({right_pos[0]:.1f}, {right_pos[1]:.1f}, {right_pos[2]:.1f})")


if __name__ == "__main__":
    main()
