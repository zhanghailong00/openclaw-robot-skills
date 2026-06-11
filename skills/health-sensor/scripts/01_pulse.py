#!/usr/local/miniconda3/bin/python
"""
心率血氧传感器脚本

功能：读取 MAX30102 脉搏传感器的心率（BPM）和血氧（SpO2）
硬件：智慧医疗场景板上的 MAX30102 传感器（I2C 地址 0x57）
原理：通过红外和红色 LED 反射光计算心率和血氧饱和度
注意：需要将手指放在传感器上，等待数据采集完成

用法：
  python3 01_pulse.py                    # 读取一次（默认采集 5 秒）
  python3 01_pulse.py --duration 10     # 采集 10 秒数据

输出：JSON 格式
"""
import sys, os, json, argparse, time
import numpy as np

# 加载传感器驱动
sys.path.insert(0, "/home/HwHiAiUser/.openclaw/workspace/python_sensor/MAX30102")
from max30102 import MAX30102

# 采样率和缓冲区大小
SAMPLE_FREQ = 25
BUFFER_SIZE = 100

# 命令行参数解析
parser = argparse.ArgumentParser(description="心率血氧传感器")
parser.add_argument("--duration", type=int, default=5,
                    help="数据采集时长（秒），默认 5")
args = parser.parse_args()


def find_peaks(x, size, min_height, min_dist, max_num):
    """寻找波谷（信号取反后的峰值）"""
    # 寻找大于 min_height 的峰值
    n_peaks = 0
    ir_valley_locs = []
    i = 0
    while i < size - 1:
        if x[i] > min_height and x[i] > x[i-1]:
            n_width = 1
            while i + n_width < size - 1 and x[i] == x[i+n_width]:
                n_width += 1
            if x[i] > x[i+n_width] and n_peaks < max_num:
                ir_valley_locs.append(i)
                n_peaks += 1
                i += n_width + 1
            else:
                i += n_width
        else:
            i += 1

    # 消除间隔太近的峰值
    sorted_indices = sorted(ir_valley_locs, key=lambda idx: x[idx], reverse=True)
    n_peaks = len(sorted_indices)
    i = -1
    while i < n_peaks:
        old_n_peaks = n_peaks
        n_peaks = i + 1
        j = i + 1
        while j < old_n_peaks:
            n_dist = (sorted_indices[j] - sorted_indices[i]) if i != -1 else (sorted_indices[j] + 1)
            if n_dist > min_dist or n_dist < -1 * min_dist:
                sorted_indices[n_peaks] = sorted_indices[j]
                n_peaks += 1
            j += 1
        i += 1

    sorted_indices[:n_peaks] = sorted(sorted_indices[:n_peaks])
    return sorted_indices, n_peaks


def calc_hr(ir_data):
    """从 IR 数据计算心率"""
    ir_mean = int(np.mean(ir_data))
    x = -1 * (np.array(ir_data) - ir_mean)

    # 均值滤波
    ma_size = 4
    for i in range(x.shape[0] - ma_size):
        x[i] = np.sum(x[i:i+ma_size]) / ma_size

    # 计算阈值
    n_th = int(np.mean(x))
    n_th = max(30, min(60, n_th))

    # 寻找波谷
    ir_valley_locs, n_peaks = find_peaks(x, BUFFER_SIZE, n_th, min_dist=4, max_num=15)

    if n_peaks >= 2:
        peak_interval_sum = 0
        for i in range(1, n_peaks):
            peak_interval_sum += (ir_valley_locs[i] - ir_valley_locs[i-1])
        peak_interval_sum = int(peak_interval_sum / (n_peaks - 1))
        hr = int(SAMPLE_FREQ * 60 / peak_interval_sum)
        return True, hr
    else:
        return False, -999


try:
    # 初始化传感器
    sensor = MAX30102()
    flag_finger = False
    ir_data = []
    red_data = []
    bpms = []

    start_time = time.time()
    while time.time() - start_time < args.duration:
        num_bytes = sensor.get_data_present()
        if num_bytes > 0:
            while num_bytes > 0:
                red, ir = sensor.read_fifo()
                num_bytes -= 1
                ir_data.append(ir)
                red_data.append(red)

                while len(ir_data) > BUFFER_SIZE:
                    ir_data.pop(0)
                    red_data.pop(0)

                if len(ir_data) == BUFFER_SIZE:
                    if np.mean(ir_data) < 50000 and np.mean(red_data) < 50000:
                        flag_finger = False
                    else:
                        flag_finger = True
                        hr_valid, hr = calc_hr(red_data)
                        if hr_valid:
                            bpms.append(hr)
                        while len(bpms) > 4:
                            bpms.pop(0)

        time.sleep(1)

    sensor.shutdown()

    if not flag_finger:
        result = {
            "success": True,
            "finger_detected": False,
            "message": "未检测到手指，请将手指放在传感器上"
        }
    elif len(bpms) > 0:
        hr_mean = np.mean(bpms)
        result = {
            "success": True,
            "finger_detected": True,
            "heart_rate_bpm": round(float(hr_mean), 1),
            "samples": len(bpms)
        }
    else:
        result = {
            "success": True,
            "finger_detected": True,
            "message": "数据不足，无法计算心率"
        }

    print(json.dumps(result, ensure_ascii=False))

except Exception as e:
    print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False))
    sys.exit(1)
