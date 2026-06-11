# 2026 CAPSTONE — UE5 실시간 센서 연동 파티클 제어 시스템

아두이노 센서 데이터를 실시간으로 읽어 Unreal Engine 5 씬의 케스케이드 파티클 액터를 자동으로 ON/OFF 제어하는 디지털 트윈 시스템입니다.

---

## 시스템 구조

```
Arduino x3 (COM3 / COM4 / COM5)
    ↓ 각각 9600 baud 시리얼 송신
bridge.py  ── PC에서 실행 (멀티스레드, 3포트 동시 수신)
    ↓ sensor_data.txt 에 3줄 포맷으로 저장
ue_controller.py  ── UE5 에디터 Python 콘솔에서 실행
    ↓ 센서별 히스테리시스 임계값 기준으로
FX_capstone / FX_capstone2 / FX_capstone3 개별 ON/OFF
```

---

## 파일 구성

```
capstone/
├── python_bridge/
│   └── bridge.py         # 아두이노 시리얼 → 파일 변환 (외부 실행)
└── ue_controller.py      # UE5 내부 파티클 제어 스크립트
```

---

## 센서 포트 매핑

| COM 포트 | 센서 ID | UE 액터 |
|----------|---------|---------|
| COM3 | Sensor 1 | FX_capstone |
| COM4 | Sensor 2 | FX_capstone2 |
| COM5 | Sensor 3 | FX_capstone3 |

---

## 센서별 임계값 (히스테리시스)

센서마다 기본 출력값이 다르기 때문에 개별 임계값을 적용합니다.  
ON 임계값 이상이면 파티클 활성화, OFF 임계값 이하로 내려오면 비활성화됩니다.

| 센서 | 포트 | 기본값 | ON 임계값 | OFF 임계값 |
|------|------|--------|-----------|------------|
| 1 | COM3 | ~269 | 310 | 280 |
| 2 | COM4 | ~561 | 850 | 800 |
| 3 | COM5 | ~554 | 850 | 800 |

> 임계값 수정 시 `ue_controller.py` 상단 `SENSOR_THRESHOLD` 딕셔너리를 변경하세요.

---

## 사전 준비

### 1. Python 패키지 설치
```bash
pip install pyserial
```

### 2. 아두이노 연결 확인
- 장치 관리자 → 포트(COM & LPT)에서 COM 번호 확인
- `bridge.py` `SENSORS` 리스트의 포트 번호와 일치하는지 확인

### 3. UE5 프로젝트 설정
- 레벨에 케스케이드 파티클 액터 3개 배치
- 아웃라이너 라벨을 `FX_capstone`, `FX_capstone2`, `FX_capstone3`으로 지정
- Auto Activate 비활성화

---

## 실행 방법

### Step 1 — bridge.py 실행 (VSCode 터미널)

```bash
python "C:\Users\<사용자명>\Desktop\capstone\python_bridge\bridge.py"
```

정상 실행 시:
```
Bridge 시작. 3개 센서 모니터링 중...
[Sensor 1] COM3 연결됨
[Sensor 2] COM4 연결됨
[Sensor 3] COM5 연결됨
```

### Step 2 — UE5 에디터에서 PIE 모드 진입

> **중요: 반드시 플레이(PIE) 모드에서 실행해야 합니다.**

### Step 3 — ue_controller.py 실행 (UE5 Output Log)

1. UE5 하단 **Output Log** 패널 열기
   - 메뉴 → **창(Window) → Output Log** 또는 하단 탭에서 확인
2. Output Log 하단 입력창 왼쪽 드롭다운 클릭 → **Python** 선택
3. 아래 명령어 입력 후 엔터:

```python
exec(open(r"C:\Users\공간지능연구실\Desktop\capstone\ue_controller.py").read())
```

> `r"..."` 앞의 `r` 은 반드시 포함해야 합니다. 없으면 경로의 `\` 문자가 오류를 일으킵니다.

> 재실행 시 동일 명령어를 다시 입력하면 됩니다. 기존 콜백은 자동으로 해제됩니다.

정상 실행 시:
```
모니터링 시작! (3-sensor mode)
[Init] Sensor 1 ← FX_capstone
[Init] Sensor 2 ← FX_capstone2
[Init] Sensor 3 ← FX_capstone3
[Init] 3개 액터 등록 완료: [1, 2, 3]
```

---

## 동작 원리

히스테리시스 방식으로 동작합니다. ON 임계값을 초과하는 순간 파티클이 켜지고, OFF 임계값 이하로 내려오는 순간 꺼집니다. 경계를 넘는 순간에만 1회 호출되어 매 프레임 파티클이 리셋되는 현상을 방지합니다.

Output Log 출력 예시:
```
[ON]  Sensor 2 (FX_capstone2): 867
[OFF] Sensor 2 (FX_capstone2): 795
```

---

## 다른 컴퓨터에서 작업 시 수정 항목

### bridge.py
| 항목 | 설명 |
|------|------|
| `SENSORS` 리스트 `port` 값 | 아두이노 연결 포트 번호 |
| `OUTPUT_FILE` | sensor_data.txt 절대 경로 |

### ue_controller.py
| 항목 | 설명 |
|------|------|
| `SENSOR_FILE` | sensor_data.txt 절대 경로 (`OUTPUT_FILE`과 동일해야 함) |
| `SENSOR_ACTOR_MAP` | 센서 ID ↔ UE 액터 라벨 매핑 |
| `SENSOR_THRESHOLD` | 센서별 ON/OFF 임계값 |

---

## 자주 발생하는 오류

**`ModuleNotFoundError: No module named 'serial'`**
→ `pip install pyserial` 실행

**`[Init] 등록된 액터를 찾지 못했습니다.`**
→ UE5 아웃라이너에서 액터 라벨 확인
→ PIE 모드로 진입한 상태인지 확인

**`[ERROR] 파일 읽기 실패`**
→ bridge.py가 실행 중인지 확인
→ sensor_data.txt 경로가 bridge.py와 ue_controller.py에서 동일한지 확인

**파티클이 켜지지 않음**
→ PIE 모드 진입 후 ue_controller.py를 실행했는지 확인
→ 액터의 Auto Activate가 비활성화되어 있는지 확인
