#!/usr/local/miniconda3/bin/python
"""
物体搜寻 - 步骤4：执行推倒动作

功能：检测堆叠位置，执行机械臂推倒动作
用法：python 04_push_over.py
"""

import sys
import os
import json
import subprocess

# 加载机械臂 SDK
sys.path.insert(0, "/home/HwHiAiUser/arm_voice_soft")
sys.path.insert(0, "/home/HwHiAiUser/arm_voice_soft/utils_arm")

from arm4dof import Arm4DoF

# 导入统一配置
from config import (
    PYTHON_PATH, DETECT_SCRIPT, COORD_SCRIPT,
    SAFE_HEIGHT, SAFE_POS, TARGET_ITEMS,
    ABOVE_HEIGHT, LEFT_DISTANCE, DOWN_HEIGHT, RIGHT_DISTANCE
)

# 目标物品（只有可乐、汉堡、薯条，盘子无法堆叠）
TARGET_ITEMS = {'cola', 'hanbao', 'shutiao'}


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
    print("物体搜寻 - 步骤4：执行推倒动作")
    print("=" * 60)

    # 1. 初始化机械臂
    print("\n[1] 初始化机械臂...")
    try:
        arm = Arm4DoF(device="/dev/ttyUSB1", is_init_pose=False)
        print("  ✓ 机械臂初始化成功")
    except Exception as e:
        print(f"  ✗ 机械臂初始化失败: {e}")
        return

    # 2. 移动到安全位置
    print("\n[2] 移动到安全位置...")
    print(f"  目标位置: {SAFE_POS}")
    arm.move(SAFE_POS, t=0.75, wait=True)
    print("  ✓ 移动完成")

    # 3. 调用 YOLO 检测
    print("\n[3] 调用 YOLO 检测...")
    result = run_script(DETECT_SCRIPT)

    if not result or result.get('status') != 'ok':
        print("  ✗ 检测失败")
        return

    all_detections = result.get('detections', [])
    count = result.get('count', 0)

    # 只保留目标物品
    detections = [d for d in all_detections if d['class'] in TARGET_ITEMS]
    target_count = len(detections)

    print(f"  ✓ 检测到 {count} 个物品，其中目标物品 {target_count} 个")

    if target_count == 0:
        print("  桌面没有目标物品，无需推倒")
        return

    # 4. 计算堆叠中心（只使用目标物品）
    print("\n[4] 计算堆叠中心...")

    sum_cx = 0
    sum_cy = 0
    for det in detections:
        cx = det.get('cx', 0)
        cy = det.get('cy', 0)
        label = det.get('label', '未知')
        print(f"    {label}: ({cx:.1f}, {cy:.1f})")

        sum_cx += cx
        sum_cy += cy

    avg_cx = sum_cx / target_count
    avg_cy = sum_cy / target_count
    print(f"  像素中心: ({avg_cx:.1f}, {avg_cy:.1f})")

    # 5. 转换为机械臂坐标
    print("\n[5] 转换为机械臂坐标...")
    stack_pos = pixel_to_arm(avg_cx, avg_cy)

    if not stack_pos:
        print("  坐标转换失败，使用默认位置")
        stack_pos = [150, 0, -31]

    print(f"  机械臂位置: ({stack_pos[0]:.1f}, {stack_pos[1]:.1f}, {stack_pos[2]:.1f})")

    # 6. 计算推倒位置
    print("\n[6] 计算推倒位置...")

    # 新方案：移动到物体上方，然后左移、下降、右移推倒
    # 推倒参数（从配置文件读取）
    above_height = ABOVE_HEIGHT
    left_distance = LEFT_DISTANCE
    down_height = DOWN_HEIGHT
    right_distance = RIGHT_DISTANCE

    # 步骤1：物体上方100mm
    above_pos = [stack_pos[0], stack_pos[1], stack_pos[2] + above_height]

    # 步骤2：水平向左移动20mm（Y轴负方向）
    left_pos = [stack_pos[0], stack_pos[1] - left_distance, stack_pos[2] + above_height]

    # 步骤3：下降高度50mm
    down_pos = [stack_pos[0], stack_pos[1] - left_distance, stack_pos[2] + above_height - down_height]

    # 步骤4：向右移动80mm（推倒，Y轴正方向）
    right_pos = [stack_pos[0], stack_pos[1] - left_distance + right_distance, stack_pos[2] + above_height - down_height]

    print(f"  推倒方式: 上方左移下降右移推倒")
    print(f"  堆叠位置: ({stack_pos[0]:.1f}, {stack_pos[1]:.1f}, {stack_pos[2]:.1f})")
    print(f"  步骤1 - 物体上方: ({above_pos[0]:.1f}, {above_pos[1]:.1f}, {above_pos[2]:.1f})")
    print(f"  步骤2 - 向左移动: ({left_pos[0]:.1f}, {left_pos[1]:.1f}, {left_pos[2]:.1f})")
    print(f"  步骤3 - 下降高度: ({down_pos[0]:.1f}, {down_pos[1]:.1f}, {down_pos[2]:.1f})")
    print(f"  步骤4 - 向右推倒: ({right_pos[0]:.1f}, {right_pos[1]:.1f}, {right_pos[2]:.1f})")

    # 7. 执行推倒
    print("\n[7] 执行推倒动作...")

    # 7.1 移动到物体上方80mm
    print(f"  [7.1] 移动到物体上方: {above_pos}")
    arm.move(above_pos, t=0.75, wait=True)
    print("  ✓ 移动完成")

    # 7.2 水平向左移动20mm
    print(f"  [7.2] 向左移动: {above_pos} → {left_pos}")
    arm.move(left_pos, t=0.5, wait=True)
    print("  ✓ 移动完成")

    # 7.3 下降高度40mm
    print(f"  [7.3] 下降高度: {left_pos} → {down_pos}")
    arm.move(down_pos, t=0.5, wait=True)
    print("  ✓ 下降完成")

    # 7.4 向右移动20mm（推倒）
    print(f"  [7.4] 向右推倒: {down_pos} → {right_pos}")
    arm.move(right_pos, t=0.5, wait=True)
    print("  ✓ 推倒完成")

    # 7.5 抬起
    print(f"  [7.5] 抬起到安全高度")
    arm.move([right_pos[0], right_pos[1], SAFE_HEIGHT], t=0.75, wait=True)
    print("  ✓ 抬起完成")

    # 8. 回到安全位置
    print("\n[8] 回到安全位置...")
    arm.move(SAFE_POS, t=0.75, wait=True)
    print("  ✓ 回到安全位置")

    # 9. 输出总结
    print(f"\n[9] 总结:")
    print(f"  检测到物品: {count} 个（目标物品 {target_count} 个）")
    print(f"  推倒方式: 上方左移下降右移推倒")
    print(f"  堆叠位置: ({stack_pos[0]:.1f}, {stack_pos[1]:.1f}, {stack_pos[2]:.1f})")
    print(f"  步骤1 - 物体上方: ({above_pos[0]:.1f}, {above_pos[1]:.1f}, {above_pos[2]:.1f})")
    print(f"  步骤2 - 向左移动: ({left_pos[0]:.1f}, {left_pos[1]:.1f}, {left_pos[2]:.1f})")
    print(f"  步骤3 - 下降高度: ({down_pos[0]:.1f}, {down_pos[1]:.1f}, {down_pos[2]:.1f})")
    print(f"  步骤4 - 向右推倒: ({right_pos[0]:.1f}, {right_pos[1]:.1f}, {right_pos[2]:.1f})")
    print(f"  推倒完成: 是")


if __name__ == "__main__":
    main()
