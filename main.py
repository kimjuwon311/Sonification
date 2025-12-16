import matplotlib.pyplot as plt
import numpy as np
import cv2
import json
import mplcursors
import pygame
from sound_select import build_samples_index, select_sample, hsv_to_psych

# =========================
# 0. 샘플 인덱스 로드
# =========================
sample_dir = r"samples"
samples_index = build_samples_index(sample_dir)

# =========================
# 1. 이미지 및 JSON 로드
# =========================
img_path = r"C:\Users\sk926\Downloads\stanley-park-4539852_1280.jpg"
img = cv2.cvtColor(cv2.imread(img_path), cv2.COLOR_BGR2RGB)
h, w, _ = img.shape

with open("image_clusters_full.json", "r") as f:
    cluster_data = json.load(f)

# label_map 생성
label_map = np.zeros((h, w), dtype=np.uint8)
for c in cluster_data:
    for x, y in c["pixels"]:
        label_map[y, x] = c["cluster"]

# =========================
# 2. 클러스터 영역 시각화
# =========================
colors = np.array([
    [255,0,0], [0,255,0], [0,0,255], [255,255,0], [0,255,255]
], dtype=np.uint8)

overlay = np.zeros_like(img)
for i in range(len(cluster_data)):
    overlay[label_map==i] = colors[i]

alpha = 0.4
combined = cv2.addWeighted(img, 1-alpha, overlay, alpha, 0)

# =========================
# 3. mp3 재생 초기화
# =========================
pygame.init()
def play_mp3(file_path):
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()

# =========================
# 4. hover 이벤트 + 클러스터별 샘플 캐싱
# =========================
cluster_to_sample = {}

def get_hsv_info(x, y):
    cluster_idx = label_map[y, x]
    c = cluster_data[cluster_idx]
    return f"Cluster: {cluster_idx}\nH: {c['h']:.1f}, S: {c['s']:.2f}, V: {c['v']:.2f}"

fig, ax = plt.subplots()
im = ax.imshow(combined)

cursor = mplcursors.cursor(im, hover=True)

@cursor.connect("add")
def on_hover(sel):
    x, y = int(sel.target[0]), int(sel.target[1])
    cluster_idx = label_map[y, x]

    # 클러스터 단위 샘플 캐싱
    if cluster_idx not in cluster_to_sample:
        c = cluster_data[cluster_idx]
        psych = hsv_to_psych(c)
        cluster_to_sample[cluster_idx] = select_sample(psych, samples_index)

    sample = cluster_to_sample[cluster_idx]

    # mp3 재생
    if sample:
        play_mp3(sample["path"])

    # HSV info 표시
    sel.annotation.set_text(get_hsv_info(x, y))

plt.axis('off')
plt.show()
pygame.quit()
