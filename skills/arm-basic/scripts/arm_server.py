#!/usr/bin/env python3
"""机械臂常驻服务：保持串口连接，收到 socket 指令立刻执行。
启动后监听 127.0.0.1:9999，响应时间 < 0.5 秒。

用法：python3 arm_server.py
"""
import sys, json, socket
sys.path.insert(0, "/home/HwHiAiUser/arm_voice_soft")
sys.path.insert(0, "/home/HwHiAiUser/arm_voice_soft/utils_arm")

from arm4dof import Arm4DoF

print("正在连接机械臂...")
arm = Arm4DoF(device="/dev/ttyUSB1", is_init_pose=False)
print("机械臂已连接")

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(("127.0.0.1", 9999))
server.listen(1)
print("服务已启动，监听 127.0.0.1:9999")

while True:
    conn, _ = server.accept()
    data = conn.recv(4096).decode()
    try:
        cmd = json.loads(data)
        action = cmd.get("action")

        if action == "open":
            arm.gripper_open(degrees=cmd.get("degrees", 45), t=cmd.get("t", 0.5))
            angle = arm.get_raw_angle_list()[4]
            result = {"success": True, "action": "open", "angle": round(float(angle), 1)}

        elif action == "close":
            arm.gripper_close(t=cmd.get("t", 0.5))
            angle = arm.get_raw_angle_list()[4]
            result = {"success": True, "action": "close", "angle": round(float(angle), 1)}

        elif action == "move":
            arm.move([cmd["x"], cmd["y"], cmd["z"]], t=cmd.get("t", 0.75), wait=True)
            pose = arm.get_tool_pose()
            result = {"success": True, "actual": {
                "x": round(float(pose[0]), 1),
                "y": round(float(pose[1]), 1),
                "z": round(float(pose[2]), 1)
            }}

        elif action == "status":
            thetas = arm.get_thetas()
            pose = arm.get_tool_pose()
            result = {"success": True, "joints": [round(float(t), 4) for t in thetas],
                      "pose": [round(float(p), 1) for p in pose]}

        elif action == "homing":
            arm.init_pose(t=cmd.get("t", 0.75))
            result = {"success": True}

        else:
            result = {"success": False, "error": f"未知动作: {action}"}

        conn.send(json.dumps(result, ensure_ascii=False).encode())

    except Exception as e:
        conn.send(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False).encode())
    finally:
        conn.close()
