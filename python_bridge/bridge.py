import serial
import time

SERIAL_PORT = 'COM3'
BAUD_RATE   = 9600
OUTPUT_FILE = r'C:\Users\공간지능연구실\Documents\Unreal Projects\FactoryEnvironmentCollect 5.7 - 7\Content\sensor_data.txt'

ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

print("Bridge 시작. 파일로 데이터 저장 중...")

while True:
    try:
        line = ser.readline().decode('utf-8').strip()
        if line.isdigit():
            value = int(line)
            if   value >= 400: level = "RED"
            elif value >= 200: level = "GREEN"
            else:              level = "BLUE"

            msg = f"{value},{level}"
            with open(OUTPUT_FILE, 'w') as f:
                f.write(msg)
            print(f"저장: {msg}")
    except Exception as e:
        print(f"에러: {e}")
    time.sleep(0.1)