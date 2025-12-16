import matplotlib.pyplot as plt
import numpy as np
import cv2
import json
import mplcursors

# JSON 로드 (cluster_data)
with open("image_clusters_full.json") as f:
    cluster_data = json.load(f)

# 이미지 로드
img_path = r"C:\Python Project_Folders\bichek\stanley-park-4539852_1280.jpg"
img = cv2.cvtColor(cv2.imread(img_path), cv2.COLOR_BGR2RGB)
h, w, _ = img.shape

# 클러스터별 색상 지정
colors = np.array([
    [255,0,0],
    [0,255,0],
    [0,0,255],
    [255,255,0],
    [0,255,255]
], dtype=np.uint8)

# label_map 생성
label_map = np.zeros((h,w), dtype=np.uint8)
for c in cluster_data:
    for x,y in c["pixels"]:
        label_map[y,x] = c["cluster"]

# 클러스터 영역 시각화 (원본 이미지 + 투명 오버레이)
overlay = np.zeros_like(img)
for i in range(len(cluster_data)):
    overlay[label_map==i] = colors[i]

alpha = 0.4
combined = cv2.addWeighted(img, 1-alpha, overlay, alpha, 0)

fig, ax = plt.subplots()
im = ax.imshow(combined)

# hover 시 HSV 표시
def get_hsv_info(x, y):
    cluster_idx = label_map[y, x]
    c = cluster_data[cluster_idx]
    return f"Cluster: {cluster_idx}\nH: {c['h']:.1f}, S: {c['s']:.2f}, V: {c['v']:.2f}"

cursor = mplcursors.cursor(im, hover=True)
@cursor.connect("add")
def on_hover(sel):
    x, y = int(sel.target[0]), int(sel.target[1])
    sel.annotation.set_text(get_hsv_info(x, y))

plt.axis('off')
plt.show()


