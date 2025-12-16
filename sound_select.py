import os
import random

# 1. 샘플 파일명 파싱
def parse_sample_filename(fname):
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

def hsv_to_psych(hsv):
    # h: 0~180, s: 0~1, v:0~1
    return {
        "warmth": (hsv["h"] / 180) * 2 - 1,
        "valence": hsv["s"] * 2 - 1,
        "arousal": hsv["v"],
        "complexity": 0.5
    } 

# 2. 샘플 인덱스 생성
def build_samples_index(sample_dir):
    index = []
    for root, _, files in os.walk(sample_dir):
        for fname in files:
            if fname.lower().endswith(".mp3"):
                info = parse_sample_filename(fname)
                if info:
                    info["path"] = os.path.join(root, fname)
                    index.append(info)
    return index

# 3. 악기 음역
INSTRUMENT_RANGES = {
    "violin": ["G3","A3","B3","C4","D4","E4","G5","A5","Gs6"],
    "viola":  ["C3","D3","E3","F3","G3","A3","C4","D4"],
    "cello":  ["A2","B2","C3","D3","E3","A3","C4"],
    "flute":  ["C4","D4","E4","G5","A5"],
    "oboe":   ["C4","D4","E4","G5"]
}

# 4. CLIP 감정 → psych
def clip_to_psych(emotions):
    psych = {
        "warmth": emotions.get("warm",0) - emotions.get("cold",0),
        "valence": emotions.get("joyful",0) - emotions.get("gloomy",0),
        "arousal": emotions.get("energetic",0) + emotions.get("tense",0)
                   - emotions.get("calm",0) - emotions.get("peaceful",0),
        "complexity": 0.5
    }
    for k in psych:
        psych[k] = max(-1, min(1, psych[k]))
    return psych

# 5. psych → 음향 규칙
def choose_instrument(warmth):
    if warmth > 0.4: return ["cello","viola"]
    if warmth < -0.4: return ["flute","oboe"]
    return ["violin"]

PITCH_RANGES = {
    "low": ["A2","B2","C3","D3","E3"],
    "mid": ["A3","B3","C4","D4","E4"],
    "high": ["C5","D5","E5","G5","A5","Gs6"]
}

def choose_pitch(valence):
    if valence > 0.4: return PITCH_RANGES["high"]
    if valence < -0.4: return PITCH_RANGES["low"]
    return PITCH_RANGES["mid"]

def choose_dynamic(arousal):
    if arousal < 0.3: return ["piano","mezzo-piano"]
    if arousal < 0.6: return ["mezzo-forte"]
    return ["forte","fortissimo"]

def choose_technique(complexity):
    if complexity < 0.3: return ["non-vibrato"]
    if complexity < 0.6: return ["vibrato"]
    return ["tremolo","col-legno"]

# 6. 샘플 선택
def select_sample(psych, samples_index):
    instruments = choose_instrument(psych["warmth"])
    pitches = choose_pitch(psych["valence"])
    dynamics = choose_dynamic(psych["arousal"])
    techniques = choose_technique(psych["complexity"])

    candidates = []
    for s in samples_index:
        if s["instrument"] not in instruments: continue
        if s["pitch"] not in INSTRUMENT_RANGES.get(s["instrument"], []): continue
        if s["pitch"] not in pitches: continue
        if s["dynamic"] not in dynamics: continue
        if s["technique"] not in techniques: continue
        candidates.append(s)

    if not candidates:
        candidates = samples_index

    selected = random.choice(candidates) if candidates else None

    if selected:
        log = (f"🎵 Selected | {selected['instrument']} / {selected['pitch']} / "
               f"{selected['dynamic']} / {selected['technique']}")
    else:
        log = "No sample selected"

    return selected, log

# 7. 실행 예시
if __name__ == "__main__":
    sample_dir = r"C:\Python Project_Folders\bichek\samples"
    samples_index = build_samples_index(sample_dir)
    print(f"Loaded samples: {len(samples_index)}")

    # CLIP → emotions dict 예시 (나중에 CLIP.py에서 가져오기)
    emotions = {
        "calm": 0.446,
        "peaceful": 0.385,
        "gloomy": 0.002,
        "tense": 0.032,
        "joyful": 0.043,
        "energetic": 0.034,
        "cold": 0.010,
        "warm": 0.048
    }

    psych = clip_to_psych(emotions)
    sample, log = select_sample(psych, samples_index)
    print(log)

