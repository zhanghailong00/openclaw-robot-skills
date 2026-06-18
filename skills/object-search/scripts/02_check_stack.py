#!/usr/local/miniconda3/bin/python
"""
物体搜寻 - 步骤2：判断是否需要推倒

功能：检测桌面物品，判断是否堆叠，是否需要推倒
用法：python 02_check_stack.py
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

# 堆叠判断阈值
STACK_THRESHOLD = 3  # 检测到的物品数量 < 3 认为是堆叠


# ==================== 工具函数 ====================

def run_script(script_path, args=None):
    """运行子脚本并解析JSON（激活 conda base 环境）"""
    # 构建命令，在 conda base 环境下运行
    cmd_str = f"source /home/HwHiAiUser/miniconda3/bin/activate base && {PYTHON_PATH} {script_path}"
    if args:
        cmd_str += " " + " ".join(args)

    print(f"执行命令: {cmd_str}")
    result = subprocess.run(cmd_str, shell=True, capture_output=True, text=True)

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
    print("物体搜寻 - 步骤2：判断是否需要推倒")
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

    # 3. 判断是否堆叠
    print(f"\n[3] 堆叠判断:")
    is_stacked = count < STACK_THRESHOLD
    print(f"  堆叠阈值: {STACK_THRESHOLD}")
    print(f"  检测数量: {count}")
    print(f"  是否堆叠: {'是' if is_stacked else '否'}")

    # 4. 判断是否需要推倒
    print(f"\n[4] 推倒判断:")
    missing_items = TARGET_ITEMS - detected_classes
    has_all_items = len(missing_items) == 0

    print(f"  目标物品: {TARGET_ITEMS}")
    print(f"  检测到: {detected_classes}")
    print(f"  缺少: {missing_items}")
    print(f"  是否齐全: {'是' if has_all_items else '否'}")

    # 5. 决定下一步动作
    print(f"\n[5] 下一步动作:")

    if has_all_items:
        print(f"  ✓ 检测到所有目标物品")
        print(f"  动作: 开始整理（调用家居整理 skill）")
    elif is_stacked:
        print(f"  ✗ 物品堆叠，需要推倒")
        print(f"  动作: 执行推倒动作")
    else:
        print(f"  ✗ 物品散落，但类别不全")
        print(f"  动作: 继续检测或推倒")

    # 6. 输出总结
    print(f"\n[6] 总结:")
    print(f"  物品数量: {count}")
    print(f"  是否堆叠: {is_stacked}")
    print(f"  是否齐全: {has_all_items}")
    print(f"  下一步: {'整理' if has_all_items else '推倒'}")


if __name__ == "__main__":
    main()
