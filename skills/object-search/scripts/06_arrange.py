#!/usr/local/miniconda3/bin/python
"""
物体搜寻 - 步骤6：使用家居整理排列

功能：调用家居整理 skill 排列物品
用法：python 06_arrange.py
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
ARRANGE_SCRIPT = os.path.join(SKILLS_DIR, "furniture-organize/scripts/05_grab_avoid.py")

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
    print("物体搜寻 - 步骤6：使用家居整理排列")
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

    # 3. 检查是否检测到所有目标物品
    print(f"\n[3] 目标物品检测:")
    print(f"  目标物品: {TARGET_ITEMS}")
    print(f"  检测到: {detected_classes}")

    missing_items = TARGET_ITEMS - detected_classes
    if missing_items:
        print(f"  ✗ 缺少: {missing_items}")
        print(f"  无法开始整理，请先推倒堆叠")
        return

    print(f"  ✓ 检测到所有目标物品")

    # 4. 使用家居整理 skill 排列
    print(f"\n[4] 使用家居整理 skill 排列...")

    for item in ['cola', 'hanbao', 'shutiao']:
        if item in detected_classes:
            print(f"\n  [4.{list(TARGET_ITEMS).index(item)+1}] 抓取 {item}...")

            cmd = [
                PYTHON_PATH,
                ARRANGE_SCRIPT,
                "--target", item
            ]

            print(f"  执行命令: {' '.join(cmd)}")

            try:
                result = subprocess.run(cmd, capture_output=False, text=True)
                if result.returncode == 0:
                    print(f"  ✓ {item} 抓取完成")
                else:
                    print(f"  ✗ {item} 抓取失败")
            except Exception as e:
                print(f"  ✗ {item} 抓取失败: {e}")
        else:
            print(f"\n  [4.{list(TARGET_ITEMS).index(item)+1}] 跳过 {item}（未检测到）")

    # 5. 输出总结
    print(f"\n[5] 总结:")
    print(f"  物品数量: {count}")
    print(f"  物品类别: {detected_classes}")
    print(f"  排列完成: 是")


if __name__ == "__main__":
    main()
