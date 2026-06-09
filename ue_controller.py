import unreal

try:
    unreal.unregister_slate_post_tick_callback(handle)
except:
    pass

SENSOR_FILE  = r'C:\Users\공간지능연구실\Documents\Unreal Projects\FactoryEnvironmentCollect 5.7 - 7\Content\sensor_data.txt'
ACTOR_PREFIX = 'FX_capstone'
THRESHOLD    = 400

was_above         = False
target_components = []
cached_world      = None

def find_all_in_world(world):
    if world is None:
        return []
    comps = []
    actors = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.NiagaraActor)
    for actor in actors:
        if actor.get_actor_label().startswith(ACTOR_PREFIX):
            comp = actor.get_component_by_class(unreal.NiagaraComponent)
            if comp:
                comps.append(comp)
                unreal.log(f"[Init] 타겟 발견: {actor.get_actor_label()}")
    return comps

def set_all(active):
    for comp in target_components:
        if active:
            comp.set_visibility(True, True)
            comp.activate(reset=True)
        else:
            comp.deactivate()
            comp.set_visibility(False, True)

def tick(delta):
    global was_above, target_components, cached_world

    ue_sub        = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    current_world = ue_sub.get_game_world() or ue_sub.get_editor_world()

    if current_world != cached_world:
        target_components = []
        cached_world      = current_world
        was_above         = False
        unreal.log("[World] 월드 전환 감지 → 액터 재탐색")

    if not target_components:
        target_components = find_all_in_world(current_world)
        if not target_components:
            unreal.log_warning(f"[Init] '{ACTOR_PREFIX}' 액터를 찾지 못했습니다.")
            return
        unreal.log(f"[Init] 총 {len(target_components)}개 액터 등록 완료")

    try:
        with open(SENSOR_FILE, 'r') as f:
            data = f.read().strip()
        parts = data.split(',')
        if len(parts) < 2:
            return
        value = int(parts[0])
        above = value >= THRESHOLD

        if above and not was_above:
            set_all(True)
            unreal.log(f"[Particle ON]  Sensor: {value} / {len(target_components)}개 활성화")
            was_above = True
        elif not above and was_above:
            set_all(False)
            unreal.log(f"[Particle OFF] Sensor: {value} / {len(target_components)}개 비활성화")
            was_above = False

    except Exception as e:
        unreal.log_warning(f"[ERROR] {e}")

handle = unreal.register_slate_post_tick_callback(tick)
unreal.log("모니터링 시작!")
