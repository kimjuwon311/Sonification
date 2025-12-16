import matplotlib.pyplot as plt
import numpy as np
import cv2
import json
import mplcursors
import pygame
from sound_select import build_samples_index, select_sample, hsv_to_psych
from Clip import get_clip_emotions, IMAGE_PATH

# 0. 샘플 로드
sample_dir = r"samples"
samples_index = build_samples_index(sample_dir)

# 1. 이미지 + JSON 로드
img = cv2.cvtColor(cv2.imread(IMAGE_PATH), cv2.COLOR_BGR2RGB)
h, w, _ = img.shape
with open("image_clusters_full.json","r") as f:
    cluster_data = json.load(f)

label_map = np.zeros((h,w), dtype=np.uint8)
for c in cluster_data:
    for x,y in c["pixels"]:
        label_map[y,x] = c["cluster"]

# 2. 클러스터 영역 시각화
colors = np.array([[255,0,0],[0,255,0],[0,0,255],[255,255,0],[0,255,255]],dtype=np.uint8)
overlay = np.zeros_like(img)
for i in range(len(cluster_data)):
    overlay[label_map==i] = colors[i]
combined = cv2.addWeighted(img,0.6,overlay,0.4,0)

# 3. mp3 재생 초기화
pygame.init()
def play_mp3(file_path):
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()

# 4. CLIP 감정
clip_emotions = get_clip_emotions()

# 5. hover 이벤트 + 클러스터 샘플 캐싱
cluster_to_sample = {}
def get_hsv_info(x,y):
    cluster_idx = label_map[y,x]
    c = cluster_data[cluster_idx]
    return f"Cluster: {cluster_idx}\nH:{c['h']:.1f}, S:{c['s']:.2f}, V:{c['v']:.2f}"

fig,ax = plt.subplots()
im = ax.imshow(combined)
cursor = mplcursors.cursor(im,hover=True)

@cursor.connect("add")
def on_hover(sel):
    x, y = int(sel.target[0] + 0.5), int(sel.target[1] + 0.5)
    cluster_idx = label_map[y, x]

    if cluster_idx not in cluster_to_sample:
        c = cluster_data[cluster_idx]
        psych = hsv_to_psych(c)

        # CLIP 감정 결합
        psych["valence"] += clip_emotions.get("joyful", 0) - clip_emotions.get("gloomy", 0)
        psych["arousal"] += clip_emotions.get("energetic", 0) + clip_emotions.get("tense", 0)
        psych["warmth"] += clip_emotions.get("warm", 0) - clip_emotions.get("cold", 0)
        for k in psych:
            psych[k] = max(-1, min(1, psych[k]))

        cluster_to_sample[cluster_idx] = select_sample(psych, samples_index)

    sample = cluster_to_sample[cluster_idx]
    if isinstance(sample, tuple):
        sample = sample[0]
    if not sample:
        return

    if not pygame.mixer.music.get_busy():
        play_mp3(sample["path"])

    sel.annotation.set_text(get_hsv_info(x, y))


plt.axis('off')
plt.show()
pygame.quit()

