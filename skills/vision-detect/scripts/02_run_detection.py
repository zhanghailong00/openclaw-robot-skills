#!/usr/bin/env python3
"""拍照 -> 去畸变 -> YOLO 推理 -> JSON 输出"""
import sys, os, json

sys.path.insert(0, "/home/HwHiAiUser/arm_voice_soft")
sys.path.insert(0, "/home/HwHiAiUser/arm_voice_soft/camera_utils")
sys.path.insert(0, "/home/HwHiAiUser/arm_voice_soft/yolo_utils")
sys.path.insert(0, "/usr/local/Ascend/thirdpart/aarch64/acllite")
sys.path.insert(0, "/usr/local/Ascend/ascend-toolkit/latest/python/site-packages")

import numpy as np
from camera import Camera

YOLO_PKG = os.path.join(os.environ.get("HOME", ""), "arm_voice_soft", "yolo_utils", "yolo11.py")
OM_PATH = os.path.join(os.environ.get("HOME", ""), "arm_voice_soft", "model", "yolo11.om")

CLASSES = ["hanbao", "cola", "panzi", "shutiao"]
LABELS_CN = ["汉堡", "可乐", "盘子", "薯条"]


def to_native(v):
    if isinstance(v, (np.float32, np.float64)):
        return float(v)
    if isinstance(v, (np.int32, np.int64, np.uint8, np.uint16)):
        return int(v)
    return v


def main():
    # 1. 拍照 + 去畸变
    cam = Camera()
    cam.load_cam_calib_data()
    cap = cam.get_video_capture()
    
    import time
    time.sleep(0.3)
    cam.empty_cache()
    ret, frame = cap.read()
    cap.release()
    cam.release()
    
    if not ret:
        print(json.dumps({"status": "error", "message": "拍照失败"}))
        sys.exit(1)
    
    image = cam.remove_distortion(frame)
    
    # 2. YOLO 推理
    try:
        sys.path.insert(0, os.path.dirname(YOLO_PKG))
        from yolo11 import init_resource, init_om_model, detect, release_resource
        init_resource()
        init_om_model(OM_PATH)
        _, predbox = detect(image)
        release_resource()
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))
        sys.exit(1)
    
    # 3. 输出
    detections = []
    if predbox:
        for box in predbox:
            cx = round(to_native((box.xmin + box.xmax) / 2), 1)
            cy = round(to_native((box.ymin + box.ymax) / 2), 1)
            detections.append({
                "class": CLASSES[box.classId],
                "label": LABELS_CN[box.classId],
                "confidence": round(to_native(box.score), 3),
                "cx": cx,
                "cy": cy,
                "xmin": round(to_native(box.xmin), 1),
                "ymin": round(to_native(box.ymin), 1),
                "xmax": round(to_native(box.xmax), 1),
                "ymax": round(to_native(box.ymax), 1),
            })
    
    result = {"detections": detections, "count": len(detections), "status": "ok"}
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
