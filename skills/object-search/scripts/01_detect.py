#!/usr/local/miniconda3/bin/python
"""
物体搜寻 - 步骤1：检测桌面物品

功能：调用 YOLO 检测桌面物品，输出检测结果
用法：python 01_detect.py
"""

import sys
import os
import json
import subprocess

# ==================== 配置 ====================

PYTHON_PATH = "/usr/local/miniconda3/bin/python"
SKILLS_DIR = "/home/HwHiAiUser/.openclaw/workspace/skills"

# 视觉检测脚本路径
DETECT_SCRIPT = os.path.join(SKILLS_DIR, "vision-detect/scripts/02_run_detection.py")

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


# ==================== 主函数 ====================

def main():
    """主函数"""
    print("=" * 60)
    print("物体搜寻 - 步骤1：检测桌面物品")
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

    # 2. 解析检测结果
    detections = result.get('detections', [])
    count = result.get('count', 0)

    print(f"\n[2] 检测结果:")
    print(f"  检测到 {count} 个物品")

    if count == 0:
        print("  桌面没有物品")
        return

    # 3. 过滤目标物品（忽略盘子等非目标物品）
    print(f"\n[3] 物品详情:")

    all_detections = detections  # 所有检测结果
    target_detections = []  # 目标物品检测结果
    detected_classes = set()

    for i, det in enumerate(all_detections):
        item_class = det.get('class')

        # 只处理目标物品
        if item_class in TARGET_ITEMS:
            target_detections.append(det)
            detected_classes.add(item_class)

            print(f"  物品 {len(target_detections)}:")
            print(f"    类别: {det.get('class')} ({det.get('label')})")
            print(f"    置信度: {det.get('confidence', 0):.3f}")
            print(f"    像素坐标: ({det.get('cx', 0):.1f}, {det.get('cy', 0):.1f})")
        else:
            print(f"  物品 {i+1}: {det.get('label')} (忽略，非目标物品)")

    # 4. 判断是否检测到所有目标物品
    print(f"\n[4] 目标物品检测:")
    print(f"  目标物品: {TARGET_ITEMS}")
    print(f"  检测到: {detected_classes}")

    missing_items = TARGET_ITEMS - detected_classes
    if missing_items:
        print(f"  缺少: {missing_items}")
        print(f"  结论: 需要继续检测或推倒")
    else:
        print(f"  ✓ 检测到所有目标物品")
        print(f"  结论: 可以开始整理")

    # 5. 输出总结
    print(f"\n[5] 总结:")
    print(f"  所有物品数量: {count}")
    print(f"  目标物品数量: {len(target_detections)}")
    print(f"  目标物品类别: {detected_classes}")
    print(f"  是否完成: {'是' if not missing_items else '否'}")


if __name__ == "__main__":
    main()
