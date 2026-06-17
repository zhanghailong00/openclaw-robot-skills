#!/usr/local/miniconda3/bin/python
"""
物体搜寻 - 步骤5：检测推倒后状态

功能：推倒后检测桌面物品状态，判断是否需要继续推倒
用法：python 05_check_result.py
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
    print("物体搜寻 - 步骤5：检测推倒后状态")
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
    detected_classes = {d['class'] for d in target_detections}

    print(f"\n[2] 检测结果:")
    print(f"  所有物品数量: {count}")
    print(f"  目标物品数量: {len(target_detections)}")
    print(f"  目标物品类别: {detected_classes}")

    # 3. 显示每个物品的详细信息
    print(f"\n[3] 物品详情:")

    for i, det in enumerate(target_detections):
        cx = det.get('cx', 0)
        cy = det.get('cy', 0)
        label = det.get('label', '未知')
        confidence = det.get('confidence', 0)

        print(f"  物品 {i+1}: {label} ({confidence:.3f})")
        print(f"    像素坐标: ({cx:.1f}, {cy:.1f})")

        # 转换为机械臂坐标
        arm_pos = pixel_to_arm(cx, cy)
        if arm_pos:
            print(f"    机械臂坐标: ({arm_pos[0]:.1f}, {arm_pos[1]:.1f}, {arm_pos[2]:.1f})")
        else:
            print(f"    机械臂坐标: 转换失败")

    # 4. 判断是否检测到所有目标物品
    print(f"\n[4] 目标物品检测:")
    print(f"  目标物品: {TARGET_ITEMS}")
    print(f"  检测到: {detected_classes}")

    missing_items = TARGET_ITEMS - detected_classes
    has_all_items = len(missing_items) == 0

    if has_all_items:
        print(f"  ✓ 检测到所有目标物品")
    else:
        print(f"  ✗ 缺少: {missing_items}")

    # 5. 决定下一步动作
    print(f"\n[5] 下一步动作:")

    if has_all_items:
        print(f"  ✓ 可以开始整理")
        print(f"  动作: 调用家居整理 skill 排列物品")
    else:
        print(f"  ✗ 需要继续推倒")
        print(f"  动作: 再次执行推倒动作")

    # 6. 输出总结
    print(f"\n[6] 总结:")
    print(f"  物品数量: {count}")
    print(f"  物品类别: {detected_classes}")
    print(f"  是否齐全: {has_all_items}")
    print(f"  下一步: {'整理' if has_all_items else '推倒'}")


if __name__ == "__main__":
    main()
