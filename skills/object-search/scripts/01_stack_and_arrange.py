#!/usr/local/miniconda3/bin/python
"""
堆叠方块整理

功能：
1. 检测堆叠状态
2. 机械臂推倒堆叠
3. 检测是否识别到所有物品
4. 使用家居整理 skill 排列

用法：
  python 06_stack_and_arrange.py
"""

import sys
import os
import json
import math
import time
import subprocess

# 加载机械臂 SDK
sys.path.insert(0, "/home/HwHiAiUser/arm_voice_soft")
sys.path.insert(0, "/home/HwHiAiUser/arm_voice_soft/utils_arm")

from arm4dof import Arm4DoF

# 导入统一配置
from object_search_config import (
    PYTHON_PATH, DETECT_SCRIPT, COORD_SCRIPT, ARRANGE_SCRIPT,
    SAFE_HEIGHT, SAFE_POS, MAX_PUSH_COUNT, TARGET_ITEMS,
    ABOVE_HEIGHT, LEFT_DISTANCE, DOWN_HEIGHT, RIGHT_DISTANCE
)


# ==================== 工具函数 ====================

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


def detect_objects():
    """检测桌面物品"""
    result = run_script(DETECT_SCRIPT)
    if not result or result.get('status') != 'ok':
        return []
    return result.get('detections', [])


def pixel_to_arm(px, py):
    """像素坐标转机械臂坐标"""
    result = run_script(COORD_SCRIPT, ["--px", str(px), "--py", str(py), "--json"])
    if result and 'arm_target' in result:
        arm = result['arm_target']
        return [arm['x'], arm['y'], arm['z']]
    return [150, 0, -31]  # 默认位置


# ==================== 推倒动作 ====================

def push_over_stack(arm, stack_pos):
    """
    推倒堆叠（上方左移下降右移推倒）

    参数：
        arm: 机械臂对象
        stack_pos: 堆叠位置 [x, y, z]
    """
    # 推倒参数（从配置文件读取）
    above_height = ABOVE_HEIGHT
    left_distance = LEFT_DISTANCE
    down_height = DOWN_HEIGHT
    right_distance = RIGHT_DISTANCE

    print(f"  推倒方式: 上方左移下降右移推倒")

    # 步骤1：物体上方100mm
    above_pos = [stack_pos[0], stack_pos[1], stack_pos[2] + above_height]
    print(f"  步骤1 - 移动到物体上方: {above_pos}")
    arm.move(above_pos, t=0.75, wait=True)

    # 步骤2：水平向左移动20mm（Y轴负方向）
    left_pos = [stack_pos[0], stack_pos[1] - left_distance, stack_pos[2] + above_height]
    print(f"  步骤2 - 向左移动: {left_pos}")
    arm.move(left_pos, t=0.5, wait=True)

    # 步骤3：下降高度50mm
    down_pos = [stack_pos[0], stack_pos[1] - left_distance, stack_pos[2] + above_height - down_height]
    print(f"  步骤3 - 下降高度: {down_pos}")
    arm.move(down_pos, t=0.5, wait=True)

    # 步骤4：向右移动80mm（推倒，Y轴正方向）
    right_pos = [stack_pos[0], stack_pos[1] - left_distance + right_distance, stack_pos[2] + above_height - down_height]
    print(f"  步骤4 - 向右推倒: {right_pos}")
    arm.move(right_pos, t=0.5, wait=True)

    # 步骤5：抬起到安全高度
    print(f"  步骤5 - 抬起到安全高度")
    arm.move([right_pos[0], right_pos[1], SAFE_HEIGHT], t=0.75, wait=True)


# ==================== 主函数 ====================

def main():
    """主函数"""
    print("=" * 60)
    print("堆叠方块整理")
    print("=" * 60)

    # 清空已放置位置记录（开始新的整理任务）
    from object_search_config import PLACED_POSITIONS_FILE
    if os.path.exists(PLACED_POSITIONS_FILE):
        os.remove(PLACED_POSITIONS_FILE)
        print("已清空放置位置记录")

    # 初始化机械臂
    try:
        arm = Arm4DoF(device="/dev/ttyUSB1", is_init_pose=False)
    except Exception as e:
        print(f"错误：机械臂连接失败 - {e}")
        sys.exit(1)

    # 移动到安全位置
    print("\n移动到安全位置...")
    arm.move(SAFE_POS, t=0.75, wait=True)

    # 循环推倒，直到检测到所有物品
    push_count = 0
    detected_classes = set()

    for push_count in range(MAX_PUSH_COUNT):
        print(f"\n{'='*60}")
        print(f"[第 {push_count + 1}/{MAX_PUSH_COUNT} 次尝试]")
        print(f"{'='*60}")

        # 1. 移动到安全位置（避免遮挡摄像头）
        print("\n  [1] 移动到安全位置...")
        arm.move(SAFE_POS, t=0.75, wait=True)
        time.sleep(0.5)  # 等待稳定

        # 2. 检测桌面物品（过滤目标物品）
        print("\n  [2] 检测桌面物品...")
        all_detections = detect_objects()

        # 只保留目标物品
        detections = [d for d in all_detections if d['class'] in TARGET_ITEMS]
        detected_classes = {d['class'] for d in detections}

        print(f"  所有物品数量: {len(all_detections)}")
        print(f"  目标物品数量: {len(detections)}")
        print(f"  目标物品类别: {detected_classes}")

        # 3. 检查是否检测到所有目标物品
        if TARGET_ITEMS.issubset(detected_classes):
            print(f"\n  ✓ 检测到所有目标物品: {TARGET_ITEMS}")
            break

        # 4. 判断是否需要继续推倒
        if len(detected_classes) < 3:
            print(f"\n  检测到 {len(detected_classes)} 个目标物品，需要继续推倒")

            # 计算堆叠位置
            if detections:
                avg_x = sum(d['cx'] for d in detections) / len(detections)
                avg_y = sum(d['cy'] for d in detections) / len(detections)
                stack_pos = pixel_to_arm(avg_x, avg_y)
                print(f"  堆叠位置: {stack_pos}")
            else:
                stack_pos = [150, 0, -31]
                print(f"  使用默认堆叠位置: {stack_pos}")

            # 执行推倒
            print(f"\n  [5] 执行推倒...")
            push_over_stack(arm, stack_pos)

            # 等待方块稳定
            print("\n  等待方块稳定...")
            time.sleep(1.5)

        else:
            print(f"\n  检测到 {len(detected_classes)} 个物品，但类别不全")
            print(f"  缺少: {TARGET_ITEMS - detected_classes}")

            # 可以选择继续推倒或停止
            # 这里选择继续推倒
            if detections:
                avg_x = sum(d['cx'] for d in detections) / len(detections)
                avg_y = sum(d['cy'] for d in detections) / len(detections)
                stack_pos = pixel_to_arm(avg_x, avg_y)
            else:
                stack_pos = [150, 0, -31]

            print(f"\n  [5] 执行推倒...")
            push_over_stack(arm, stack_pos)

            print("\n  等待方块稳定...")
            time.sleep(1.5)

    # 检查最终状态
    print(f"\n{'='*60}")
    print("推倒完成，开始整理")
    print(f"{'='*60}")

    if not TARGET_ITEMS.issubset(detected_classes):
        print(f"\n警告：未检测到所有目标物品")
        print(f"  检测到: {detected_classes}")
        print(f"  目标: {TARGET_ITEMS}")
        print(f"  缺少: {TARGET_ITEMS - detected_classes}")

        # 询问是否继续
        print("\n继续整理已检测到的物品...")

    # 使用家居整理 skill 排列
    print("\n[步骤3] 使用家居整理 skill 排列...")

    for item in ['cola', 'hanbao', 'shutiao']:
        if item in detected_classes:
            print(f"\n  抓取 {item}...")
            cmd = [
                PYTHON_PATH,
                ARRANGE_SCRIPT,
                "--target", item,
                "--no-avoid"  # 关闭避障，先测试基本功能
            ]
            try:
                subprocess.run(cmd, capture_output=False, text=True)
            except Exception as e:
                print(f"  错误：{e}")
        else:
            print(f"\n  跳过 {item}（未检测到）")

    # 回到安全位置
    print("\n回到安全位置...")
    arm.move(SAFE_POS, t=0.75, wait=True)

    print("\n" + "=" * 60)
    print("堆叠方块整理完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
