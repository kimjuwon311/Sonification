import os
import random

# =========================
# 1. 샘플 파일명 파싱
# =========================
def parse_sample_filename(fname):
    """
    파일명 예시:
    cello_A2_1_mezzo-piano_non-vibrato.mp3
    """
    name = fname.replace(".mp3", "")
    parts = name.split("_")

    if len(parts) < 5:
        return None

    return {
        "instrument": parts[0],
        "pitch": parts[1],
        "dynamic": parts[3],
        "technique": parts[4],
    }

# =========================
# 2. 샘플 인덱스 생성 (폴더 구조 그대로 탐색)
# =========================
def build_samples_index(sample_dir):
    index = []

    for root, _, files in os.walk(sample_dir):
        for fname in files:
            if not fname.lower().endswith(".mp3"):
                continue

            info = parse_sample_filename(fname)
            if info is None:
                continue

            info["path"] = os.path.join(root, fname)
            index.append(info)

    return index

# =========================
# 3. 악기별 음역 정의
# =========================
INSTRUMENT_RANGES = {
    "violin": ["G3", "A3", "B3", "C4", "D4", "E4", "G5", "A5", "Gs6"],
    "viola":  ["C3", "D3", "E3", "F3", "G3", "A3", "C4", "D4"],
    "cello":  ["A2", "B2", "C3", "D3", "E3", "A3", "C4"],
    "flute":  ["C4", "D4", "E4", "G5", "A5"],
    "oboe":   ["C4", "D4", "E4", "G5"]
}

# =========================
# 4. psych → 음향 규칙
# =========================
def choose_instrument(warmth):
    if warmth > 0.4:
        return ["cello", "viola"]
    elif warmth < -0.4:
        return ["flute", "oboe"]
    return ["violin"]

PITCH_RANGES = {
    "low":  ["A2", "B2", "C3", "D3", "E3"],
    "mid":  ["A3", "B3", "C4", "D4", "E4"],
    "high": ["C5", "D5", "E5", "G5", "A5", "Gs6"]
}

def choose_pitch(valence):
    if valence > 0.4:
        return PITCH_RANGES["high"]
    elif valence < -0.4:
        return PITCH_RANGES["low"]
    return PITCH_RANGES["mid"]

def choose_dynamic(arousal):
    if arousal < 0.3:
        return ["piano", "mezzo-piano"]
    elif arousal < 0.6:
        return ["mezzo-forte"]
    return ["forte", "fortissimo"]

def choose_technique(complexity):
    if complexity < 0.3:
        return ["non-vibrato"]
    elif complexity < 0.6:
        return ["vibrato"]
    return ["tremolo", "col-legno"]

# =========================
# 5. 샘플 선택 (음역 필터 + fallback)
# =========================
def select_sample(psych, samples_index):
    instruments = choose_instrument(psych["warmth"])
    raw_pitches = choose_pitch(psych["valence"])
    dynamics = choose_dynamic(psych["arousal"])
    techniques = choose_technique(psych["complexity"])

    candidates = []

    for s in samples_index:
        if s["instrument"] not in instruments:
            continue

        # 🔑 악기 음역 기반 pitch 필터
        valid_pitches = [p for p in raw_pitches if p in INSTRUMENT_RANGES.get(s["instrument"], [])]
        if s["pitch"] not in valid_pitches:
            continue

        if s["dynamic"] not in dynamics:
            continue

        if s["technique"] not in techniques:
            continue

        candidates.append(s)

    # 🔹 fallback 1: pitch 조건 무시
    if not candidates:
        for s in samples_index:
            if s["instrument"] in instruments:
                candidates.append(s)

    # 🔹 fallback 2: instrument 조건까지 없으면 전체에서 랜덤
    if not candidates:
        candidates = samples_index.copy()

    return random.choice(candidates) if candidates else None
def hsv_to_psych(hsv):
    return {
        "warmth": (hsv["h"]/180)*2 - 1,
        "valence": hsv["s"]*2 - 1,
        "arousal": hsv["v"],
        "complexity": 0.5
    }


# =========================
# 6. 실행부
# =========================
if __name__ == "__main__":
    sample_dir = r"C:\Python Project_Folders\비책\samples"
    samples_index = build_samples_index(sample_dir)
    print(f"🎵 로드된 샘플 수: {len(samples_index)}")

    # 임시 psych 값 (CLIP에서 가져온 값)
    psych = {
        "warmth": -0.34,
        "valence": -0.45,
        "arousal": 0.73,
        "complexity": 0.52
    }

    selected = select_sample(psych, samples_index)

    if selected is None:
        print("❌ 조건에 맞는 샘플을 찾지 못했습니다. (불가능)")
    else:
        print("\n✅ 선택된 샘플")
        print("악기:", selected["instrument"])
        print("피치:", selected["pitch"])
        print("셈여림:", selected["dynamic"])
        print("주법:", selected["technique"])
        print("파일 경로:", selected["path"])
