#!/usr/local/miniconda3/bin/python
"""
家具整理 - 主流程
功能：完整的整理流程：检测 → 排序 → 规划 → 抓取 → 放置
"""

import sys
import os
import json
import argparse
import subprocess

# ==================== 配置 ====================

# Python解释器路径
PYTHON_PATH = "/usr/local/miniconda3/bin/python"

# 技能目录
SKILLS_DIR = "/home/HwHiAiUser/.openclaw/workspace/skills"

# 子脚本路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DETECT_SORT_SCRIPT = os.path.join(SCRIPT_DIR, "01_detect_and_sort.py")
GRAB_PLACE_SCRIPT = os.path.join(SCRIPT_DIR, "03_grab_and_place.py")

# 基础运动脚本路径
ARM_HOME_SCRIPT = os.path.join(SKILLS_DIR, "arm-basic/scripts/02_move_home.py")

# 安全高度（mm）
SAFE_HEIGHT = 80

# 默认放置区域配置
DEFAULT_PLACE_ZONES = {
    'cola': {'x': 100, 'y': 50, 'z': -31.2},
    'hanbao': {'x': 100, 'y': 0, 'z': -31.2},
    'shutiao': {'x': 100, 'y': -50, 'z': -31.2},
    'panzi': {'x': 50, 'y': 0, 'z': -31.2},  # 盘子放在左边
}

# 物品中文名称
TYPE_LABELS = {
    'cola': '可乐',
    'hanbao': '汉堡',
    'shutiao': '薯条',
}


# ==================== 工具函数 ====================

def run_script(script_path, args=None):
    """运行子脚本"""
    cmd = [PYTHON_PATH, script_path]
    if args:
        cmd.extend(args)

    print(f"[DEBUG] 执行命令: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(f"[DEBUG] returncode: {result.returncode}")
    print(f"[DEBUG] stdout长度: {len(result.stdout)}")

    try:
        # 尝试从stdout中提取所有JSON对象
        stdout = result.stdout.strip()
        json_objects = []

        # 查找所有 JSON 对象
        i = 0
        while i < len(stdout):
            start = stdout.find('{', i)
            if start == -1:
                break

            # 找到匹配的结束括号
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

        print(f"[DEBUG] 找到 {len(json_objects)} 个JSON对象")

        # 返回最后一个JSON对象（最终结果）
        if json_objects:
            return json_objects[-1]
        else:
            raise json.JSONDecodeError("No JSON found", stdout, 0)

    except json.JSONDecodeError as e:
        print(f"[DEBUG] JSON解析失败: {e}")
        return {
            "error": f"脚本执行失败: {script_path}",
            "stdout": result.stdout,
            "stderr": result.stderr,
            "status": "error"
        }


def move_home():
        """移动到初始位置"""
        cmd = [
            PYTHON_PATH,
            ARM_HOME_SCRIPT,
            "--json"
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            return False

        try:
            data = json.loads(result.stdout)
            return data.get('status') == 'ok'
        except json.JSONDecodeError:
            return False


# ==================== 主流程 ====================

class FurnitureOrganizer:
    """家具整理主控制器"""

    def __init__(self, place_zones=None):
        """
        初始化

        参数：
            place_zones: 放置区域配置 dict
        """
        self.place_zones = place_zones or DEFAULT_PLACE_ZONES
        self.results = []

    def run(self, dry_run=False):
        """
        执行整理任务

        参数：
            dry_run: 是否只规划不执行
        """
        print("=" * 50)
        print("家具整理开始")
        print("=" * 50)

        # 1. 检测和排序
        print("\n[步骤1] 检测桌面物品...")
        detect_result = self._detect_and_sort()

        if detect_result.get('status') != 'ok':
            print(f"检测失败: {detect_result.get('error')}")
            return self._build_result(0, 0, [])

        objects = detect_result.get('objects', [])
        if not objects:
            print("桌面没有检测到物品，任务完成")
            return self._build_result(0, 0, [])

        print(f"检测到 {len(objects)} 个物品")
        for obj in objects:
            print(f"  - {obj.get('label', obj.get('class'))} (优先级: {obj.get('rank')})")

        # 2. 移动到初始位置
        if not dry_run:
            print("\n[步骤2] 移动到初始位置...")
            move_home()

        # 3. 逐个抓取放置
        success_count = 0
        fail_count = 0

        for i, obj in enumerate(objects):
            obj_class = obj.get('class', '')
            obj_label = obj.get('label', TYPE_LABELS.get(obj_class, obj_class))

            print(f"\n[步骤{3+i}] 处理 {obj_label}...")

            # 3.1 获取抓取位置（已经在01_detect_and_sort.py中转换为机械臂坐标）
            grab_x = obj.get('arm_x', 0)
            grab_y = obj.get('arm_y', 0)
            grab_z = obj.get('arm_z', -31.2)

            grab_pos = [grab_x, grab_y, grab_z]

            # 3.2 获取放置位置
            place_zone = self.place_zones.get(obj_class, DEFAULT_PLACE_ZONES.get(obj_class))
            place_pos = [place_zone['x'], place_zone['y'], place_zone['z']]

            print(f"  抓取位置: {grab_pos}")
            print(f"  放置位置: {place_pos}")

            if dry_run:
                print(f"  [DRY RUN] 跳过实际执行")
                success_count += 1
                self.results.append({
                    "object": obj_class,
                    "label": obj_label,
                    "status": "dry_run"
                })
                continue

            # 3.3 执行抓取放置
            grab_place_result = self._grab_and_place(obj_class, grab_pos, place_pos)

            if grab_place_result.get('status') == 'ok':
                print(f"  ✓ {obj_label} 处理完成")
                success_count += 1
                self.results.append({
                    "object": obj_class,
                    "label": obj_label,
                    "status": "ok"
                })
            else:
                print(f"  ✗ {obj_label} 处理失败: {grab_place_result.get('message')}")
                fail_count += 1
                self.results.append({
                    "object": obj_class,
                    "label": obj_label,
                    "status": "error",
                    "message": grab_place_result.get('message', '未知错误')
                })

        # 4. 回到初始位置
        if not dry_run:
            print("\n[步骤最后] 回到初始位置...")
            move_home()

        # 输出结果
        return self._build_result(success_count, fail_count, self.results)

    def _detect_and_sort(self):
        """调用检测排序脚本"""
        return run_script(DETECT_SORT_SCRIPT)

    def _grab_and_place(self, obj_class, grab_pos, place_pos):
        """调用抓取放置脚本"""
        args = [
            "--obj", obj_class,
            "--grab-pos", ",".join([str(x) for x in grab_pos]),
            "--place", ",".join([str(x) for x in place_pos]),
            "--json"
        ]
        return run_script(GRAB_PLACE_SCRIPT, args)

    def _build_result(self, success_count, fail_count, details):
        """构建结果"""
        return {
            "total_objects": success_count + fail_count,
            "success_count": success_count,
            "fail_count": fail_count,
            "details": details,
            "status": "ok" if fail_count == 0 else "partial"
        }


# ==================== 主函数 ====================

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='家具整理 - 主流程')
    parser.add_argument('--dry-run', action='store_true',
                        help='只规划不执行（调试用）')
    parser.add_argument('--place-zone', type=str, default='',
                        help='自定义放置区域 x,y,width,height')
    parser.add_argument('--json', action='store_true',
                        help='JSON格式输出')

    args = parser.parse_args()

    # 解析自定义放置区域
    place_zones = None
    if args.place_zone:
        try:
            parts = [float(x) for x in args.place_zone.split(',')]
            x, y = parts[0], parts[1]
            # 简单实现：所有物品放在同一区域附近
            place_zones = {
                'cola': {'x': x, 'y': y + 50, 'z': -31.2},
                'hanbao': {'x': x, 'y': y, 'z': -31.2},
                'shutiao': {'x': x, 'y': y - 50, 'z': -31.2},
            }
        except ValueError:
            print(json.dumps({"error": "放置区域格式错误"}, ensure_ascii=False))
            sys.exit(1)

    # 创建整理器
    organizer = FurnitureOrganizer(place_zones)

    # 执行整理
    result = organizer.run(dry_run=args.dry_run)

    # 输出结果
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("\n" + "=" * 50)
        print("整理完成")
        print("=" * 50)
        print(f"总数: {result.get('total_objects', 0)}")
        print(f"成功: {result.get('success_count', 0)}")
        print(f"失败: {result.get('fail_count', 0)}")

        if result.get('fail_count', 0) > 0:
            print("\n失败详情:")
            for detail in result.get('details', []):
                if detail.get('status') == 'error':
                    print(f"  - {detail.get('label')}: {detail.get('message')}")


if __name__ == "__main__":
    main()
