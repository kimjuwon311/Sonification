import cv2
import numpy as np
from sklearn.cluster import KMeans
from PIL import Image
import json

# =========================
# 1. 이미지 로드
# =========================
img_path = r"C:\Users\sk926\Downloads\stanley-park-4539852_1280.jpg"
img = cv2.cvtColor(np.array(Image.open(img_path).convert("RGB")), cv2.COLOR_RGB2BGR)
h, w = img.shape[:2]

# RGB → HSV
hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
pixels = hsv_img.reshape(-1, 3)

# =========================
# 2. K-means 클러스터링
# =========================
n_clusters = 5
kmeans = KMeans(n_clusters=n_clusters, random_state=42)
labels = kmeans.fit_predict(pixels)
label_map = labels.reshape(h, w)  # 이미지 크기대로 2차원 맵

# =========================
# 3. 클러스터별 HSV 평균 + 픽셀 좌표
# =========================
cluster_data = []

for cluster_idx in range(n_clusters):
    ys, xs = np.where(label_map == cluster_idx)  # 클러스터 픽셀 좌표
    cluster_pixels = hsv_img[ys, xs]

    h_mean, s_mean, v_mean = cluster_pixels.mean(axis=0)
    cluster_entry = {
        "cluster": cluster_idx,
        "h": float(h_mean),
        "s": float(s_mean/255),  # 0~1 정규화
        "v": float(v_mean/255),
        "pixels": list(zip(xs.tolist(), ys.tolist()))  # (x, y) 좌표 리스트
    }
    cluster_data.append(cluster_entry)

# =========================
# 4. JSON 저장
# =========================
with open("image_clusters_full.json", "w") as f:
    json.dump(cluster_data, f, indent=2)

print("✅ 클러스터링 완료, image_clusters_full.json 생성됨")
print(f"클러스터 개수: {n_clusters}")
