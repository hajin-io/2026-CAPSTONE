import unreal

try:
    unreal.unregister_slate_post_tick_callback(handle)
except:
    pass

# ── 설정 ──────────────────────────────────────────────────────────────────────
SENSOR_FILE = r'C:\Users\공간지능연구실\Documents\Unreal Projects\FactoryEnvironmentCollect 5.7\Content\sensor_data.txt'

# 센서 ID → 액터 라벨 매핑
SENSOR_ACTOR_MAP = {
    1: 'FX_capstone',
    2: 'FX_capstone2',
    3: 'FX_capstone3',
}

# 센서별 히스테리시스 임계값 (ON_THRESHOLD 이상이면 켜짐, OFF_THRESHOLD 이하면 꺼짐)
# 기본값: baseline ~269 / 가스: ~338
# 2번:   baseline ~561 / 가스: ~900
# 3번:   baseline ~554 / 가스: ~890
SENSOR_THRESHOLD = {
    1: {'on': 310, 'off': 280},
    2: {'on': 850, 'off': 800},
    3: {'on': 850, 'off': 800},
}
# ─────────────────────────────────────────────────────────────────────────────

# 런타임 상태
sensor_components = {sid: None  for sid in SENSOR_ACTOR_MAP}  # sid → ParticleSystemComponent
was_above         = {sid: False for sid in SENSOR_ACTOR_MAP}  # sid → bool
cached_world      = None

def find_components(world):
    """월드 내에서 SENSOR_ACTOR_MAP에 정의된 액터들을 탐색해 컴포넌트 딕셔너리 반환"""
    if world is None:
        return {sid: None for sid in SENSOR_ACTOR_MAP}
    result = {sid: None for sid in SENSOR_ACTOR_MAP}
    label_to_sid = {label: sid for sid, label in SENSOR_ACTOR_MAP.items()}
    actors = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Emitter)
    for actor in actors:
        label = actor.get_actor_label()
        if label in label_to_sid:
            comp = actor.get_component_by_class(unreal.ParticleSystemComponent)
            if comp:
                sid = label_to_sid[label]
                result[sid] = comp
                unreal.log(f"[Init] Sensor {sid} ← {label}")
    return result

def set_particle(comp, active):
    if active:
        comp.set_visibility(True, True)
        comp.activate(reset=True)
    else:
        comp.deactivate()
        comp.set_visibility(False, True)

def tick(delta):
    global sensor_components, was_above, cached_world

    ue_sub        = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    current_world = ue_sub.get_game_world() or ue_sub.get_editor_world()

    # 월드 전환 감지 → 재탐색
    if current_world != cached_world:
        sensor_components = {sid: None  for sid in SENSOR_ACTOR_MAP}
        was_above         = {sid: False for sid in SENSOR_ACTOR_MAP}
        cached_world      = current_world
        unreal.log("[World] 월드 전환 감지 → 액터 재탐색")

    # 미등록 컴포넌트 있으면 탐색
    if any(c is None for c in sensor_components.values()):
        sensor_components = find_components(current_world)
        found = [sid for sid, c in sensor_components.items() if c is not None]
        if not found:
            unreal.log_warning("[Init] 등록된 액터를 찾지 못했습니다. 아웃라이너 라벨을 확인하세요.")
            return
        unreal.log(f"[Init] {len(found)}개 액터 등록 완료: {found}")

    # 파일 읽기
    try:
        with open(SENSOR_FILE, 'r') as f:
            lines = f.read().strip().splitlines()
    except Exception as e:
        unreal.log_warning(f"[ERROR] 파일 읽기 실패: {e}")
        return

    # 각 줄: "sensor_id,value,level"
    for line in lines:
        parts = line.split(',')
        if len(parts) < 2:
            continue
        try:
            sid   = int(parts[0])
            value = int(parts[1])
        except ValueError:
            continue

        if sid not in sensor_components:
            continue
        comp = sensor_components[sid]
        if comp is None:
            continue

        th = SENSOR_THRESHOLD.get(sid, {'on': 400, 'off': 350})
        if value >= th['on'] and not was_above[sid]:
            set_particle(comp, True)
            unreal.log(f"[ON]  Sensor {sid} ({SENSOR_ACTOR_MAP[sid]}): {value}")
            was_above[sid] = True
        elif value <= th['off'] and was_above[sid]:
            set_particle(comp, False)
            unreal.log(f"[OFF] Sensor {sid} ({SENSOR_ACTOR_MAP[sid]}): {value}")
            was_above[sid] = False

handle = unreal.register_slate_post_tick_callback(tick)
unreal.log("모니터링 시작! (3-sensor mode)")
