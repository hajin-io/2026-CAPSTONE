import serial
import time
import threading

# ── 설정 ──────────────────────────────────────────────────────────────────────
SENSORS = [
    {'id': 1, 'port': 'COM3', 'baud': 9600},
    {'id': 2, 'port': 'COM4', 'baud': 9600},
    {'id': 3, 'port': 'COM5', 'baud': 9600},
]
OUTPUT_FILE = r'C:\Users\공간지능연구실\Documents\Unreal Projects\FactoryEnvironmentCollect 5.7\Content\sensor_data.txt'
# ─────────────────────────────────────────────────────────────────────────────

# 센서별 최신값 공유 딕셔너리 (id → 정수값, 초기값 0)
latest = {s['id']: 0 for s in SENSORS}
lock   = threading.Lock()

def level_str(value):
    if   value >= 400: return "RED"
    elif value >= 200: return "GREEN"
    else:              return "BLUE"

def read_sensor(sensor):
    """각 COM 포트를 독립 스레드에서 읽어 latest 딕셔너리 갱신"""
    while True:
        try:
            ser = serial.Serial(sensor['port'], sensor['baud'], timeout=1)
            print(f"[Sensor {sensor['id']}] {sensor['port']} 연결됨")
            while True:
                line = ser.readline().decode('utf-8').strip()
                if line.isdigit():
                    val = int(line)
                    with lock:
                        latest[sensor['id']] = val
        except serial.SerialException as e:
            print(f"[Sensor {sensor['id']}] 포트 오류: {e} — 3초 후 재시도")
            time.sleep(3)
        except Exception as e:
            print(f"[Sensor {sensor['id']}] 오류: {e}")
            time.sleep(1)

def write_file():
    """0.1초마다 3개 센서 최신값을 파일에 3줄로 기록"""
    while True:
        with lock:
            snapshot = dict(latest)
        lines = []
        for sid, val in sorted(snapshot.items()):
            lines.append(f"{sid},{val},{level_str(val)}")
        content = "\n".join(lines)
        try:
            with open(OUTPUT_FILE, 'w') as f:
                f.write(content)
        except Exception as e:
            print(f"[File] 쓰기 오류: {e}")
        time.sleep(0.1)

# ── 실행 ──────────────────────────────────────────────────────────────────────
print("Bridge 시작. 3개 센서 모니터링 중...")
print(f"출력 파일: {OUTPUT_FILE}")

for s in SENSORS:
    t = threading.Thread(target=read_sensor, args=(s,), daemon=True)
    t.start()

# 메인 스레드는 파일 쓰기 담당 (블로킹)
write_file()
