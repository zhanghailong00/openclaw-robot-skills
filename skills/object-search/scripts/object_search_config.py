#!/usr/local/miniconda3/bin/python
"""
物体搜寻 Skill 统一配置文件

所有配置集中在此文件，修改配置只需改这个文件
"""

# ==================== 路径配置 ====================

# Python 解释器路径
PYTHON_PATH = "/usr/local/miniconda3/bin/python"

# 技能目录
SKILLS_DIR = "/home/HwHiAiUser/.openclaw/workspace/skills"

# 脚本路径
DETECT_SCRIPT = f"{SKILLS_DIR}/vision-detect/scripts/02_run_detection.py"
COORD_SCRIPT = f"{SKILLS_DIR}/coord-transform/scripts/02_convert.py"
ARRANGE_SCRIPT = f"{SKILLS_DIR}/furniture-organize/scripts/05_grab_avoid.py"

# ==================== 机械臂配置 ====================

# 安全位置（离开工作区，不遮挡摄像头）
SAFE_HEIGHT = 30        # 安全高度（mm）
SAFE_POS = [20, -130, 30]  # 安全位坐标

# ==================== 推倒配置 ====================

# 最大推倒次数
MAX_PUSH_COUNT = 5

# 推倒参数
ABOVE_HEIGHT = 100      # 物体上方高度（mm）
LEFT_DISTANCE = 20      # 向左移动距离（mm）
DOWN_HEIGHT = 70        # 下降高度（mm）
RIGHT_DISTANCE = 80     # 向右推倒距离（mm）

# ==================== 目标物品配置 ====================

# 目标物品（只有可乐、汉堡、薯条，盘子无法堆叠）
TARGET_ITEMS = {'cola', 'hanbao', 'shutiao'}

# 物品中文名称
TYPE_LABELS = {
    'cola': '可乐',
    'hanbao': '汉堡',
    'shutiao': '薯条',
    'panzi': '盘子',
}

# ==================== 放置区域配置 ====================

# 放置区域（根据实测物品位置）
PLACE_AREA = {
    'x_min': 78,    # X左边界
    'x_max': 183,   # X右边界
    'y_min': 10,    # Y下边界
    'y_max': 96,    # Y上边界
    'z': -31.2      # 放置高度
}

# 网格排列配置
GRID_COLS = 2  # 每行2个（增大间距）
GRID_ROWS = 3  # 最多3行

# ==================== 避障配置 ====================

# 障碍物半径（mm）
OBSTACLE_RADIUS = 30

# 最小安全距离（mm）
MIN_SAFE_DISTANCE = 50

# ==================== 已放置位置记录 ====================

# 已放置位置记录文件路径
PLACED_POSITIONS_FILE = f"{SKILLS_DIR}/furniture-organize/scripts/placed_positions.json"
