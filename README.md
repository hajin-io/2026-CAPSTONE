## UE5 실시간 센서 연동 파티클 제어

아두이노 센서 데이터를 실시간으로 읽어 Unreal Engine 5 씬의 Niagara 파티클 액터를 자동으로 ON/OFF 제어하는 시스템입니다.

---

## 시스템 구조

```
Arduino (시리얼 데이터)
    ↓ COM 포트 (9600 baud)
bridge.py  ── PC에서 실행 (VSCode 터미널)
    ↓ sensor_data.txt 파일에 저장
ue_controller.py  ── UE5 에디터 Python 콘솔에서 실행
    ↓ 센서값 400 이상/이하 경계에서
FX_capstone* 액터 전체 동시 ON/OFF
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

## 사전 준비

### 1. Python 패키지 설치
```bash
pip install pyserial
```

### 2. 아두이노 연결 확인
- 장치 관리자 → 포트(COM & LPT)에서 COM 번호 확인
- `bridge.py` 4번째 줄 `SERIAL_PORT` 값과 일치하는지 확인

### 3. UE5 프로젝트 설정
- 레벨에 Niagara 파티클 액터 배치 후 라벨을 `FX_capstone`으로 지정
- 여러 개 배치 시 UE5가 자동으로 `FX_capstone2`, `FX_capstone3`... 으로 넘버링
- Niagara 에셋의 **Loop Behavior** → `Infinite` 로 설정 후 컴파일/저장

---

## 실행 방법

### Step 1 — bridge.py 실행 (VSCode 터미널)

```bash
python "C:\Users\<사용자명>\Desktop\capstone\python_bridge\bridge.py"
```

정상 실행 시 터미널에 아래와 같이 출력됩니다:
```
Bridge 시작. 파일로 데이터 저장 중...
저장: 46,BLUE
저장: 210,GREEN
저장: 412,RED
```

### Step 2 — UE5 에디터에서 PIE 모드 진입

> **중요: 반드시 플레이(PIE) 모드에서 실행해야 합니다.**  
> 에디터 모드에서는 파티클 제어가 정상 동작하지 않습니다.

UE5 상단 툴바의 **플레이(▶) 버튼**을 눌러 PIE 모드 진입

### Step 3 — ue_controller.py 실행 (UE5 Output Log)

Output Log 하단 입력창 드롭다운을 `Python` 으로 변경 후 입력:

```python
exec(open(r"C:\Users\<사용자명>\Desktop\capstone\ue_controller.py").read())
```

> `r"..."` 앞의 `r` 은 반드시 포함해야 합니다. 없으면 경로의 `\` 문자가 오류를 일으킵니다.

정상 실행 시 Output Log에 출력:
```
모니터링 시작!
[World] 월드 전환 감지 → 액터 재탐색
[Init] 타겟 발견: FX_capstone
[Init] 타겟 발견: FX_capstone2
[Init] 총 2개 액터 등록 완료
```

---

## 동작 원리

| 센서값 | 레벨 | 파티클 상태 |
|--------|------|-------------|
| 400 이상 | RED | ON (activate) |
| 200 ~ 399 | GREEN | OFF (deactivate) |
| 200 미만 | BLUE | OFF (deactivate) |

에지 트리거 방식으로 동작합니다. 400 경계를 **넘는 순간** 1회, **내려오는 순간** 1회만 호출되어 매 프레임 파티클이 리셋되는 현상을 방지합니다.

Output Log 출력 예시:
```
[Particle ON]  Sensor: 412 / 2개 활성화
[Particle OFF] Sensor: 398 / 2개 비활성화
```

---

## 다른 컴퓨터에서 작업 시 수정 항목

### bridge.py
| 위치 | 항목 | 설명 |
|------|------|------|
| 4번 줄 | `SERIAL_PORT` | 아두이노 연결 포트 (예: `COM3`, `COM5`) |
| 6번 줄 | `OUTPUT_FILE` | sensor_data.txt 절대 경로 |

### ue_controller.py
| 위치 | 항목 | 설명 |
|------|------|------|
| 8번 줄 | `SENSOR_FILE` | sensor_data.txt 절대 경로 (`OUTPUT_FILE`과 동일해야 함) |
| 9번 줄 | `ACTOR_PREFIX` | 제어할 액터 라벨 접두사 (기본값: `FX_capstone`) |
| 10번 줄 | `THRESHOLD` | 파티클 활성화 임계값 (기본값: `400`) |

---

## 자주 발생하는 오류

**`ModuleNotFoundError: No module named 'serial'`**
→ `pip install pyserial` 실행

**`[Init] 'FX_capstone' 액터를 찾지 못했습니다.`**
→ UE5 아웃라이너에서 액터 라벨이 `FX_capstone`으로 정확히 지정되어 있는지 확인  
→ PIE 모드로 진입한 상태인지 확인

**`not enough values to unpack`**
→ bridge.py가 실행 중인지 확인  
→ sensor_data.txt 경로가 bridge.py와 ue_controller.py에서 동일한지 확인

**파티클이 켜지지 않음**
→ PIE 모드 진입 후 ue_controller.py를 실행했는지 확인 (에디터 모드에서는 동작 안 함)  
→ Niagara 에셋 Loop Behavior가 `Infinite`로 설정되어 있는지 확인
