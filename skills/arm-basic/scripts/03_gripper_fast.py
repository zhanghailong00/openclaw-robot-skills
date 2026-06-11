#!/usr/local/miniconda3/bin/python
"""夹爪控制（通过常驻服务调用，响应 < 0.5 秒）

用法：
  python3 03_gripper_fast.py open
  python3 03_gripper_fast.py close

需要先启动 arm_server.py
"""
import sys, json, socket

action = sys.argv[1] if len(sys.argv) > 1 else "open"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("127.0.0.1", 9999))
s.send(json.dumps({"action": action}).encode())
result = s.recv(4096).decode()
s.close()
print(result)
