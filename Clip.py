import torch
import clip
from PIL import Image

# 1️⃣ 디바이스 설정
device = "cuda" if torch.cuda.is_available() else "cpu"

# 2️⃣ CLIP 모델 로드 (가볍고 안정적인 버전)
model, preprocess = clip.load("ViT-B/32", device=device)

# 3️⃣ 이미지 로드
image = preprocess(
    Image.open(r"C:\Users\sk926\Downloads\stanley-park-4539852_1280.jpg").convert("RGB")
).unsqueeze(0).to(device)

# 4️⃣ 감정 텍스트 후보
emotion_texts = [
    "a calm image",
    "a peaceful image",
    "a gloomy image",
    "a tense image",
    "a joyful image",
    "an energetic image",
    "a cold image",
    "a warm image"
]

text_tokens = clip.tokenize(emotion_texts).to(device)

# 5️⃣ 특징 추출 & 유사도 계산
with torch.no_grad():
    image_features = model.encode_image(image)
    text_features = model.encode_text(text_tokens)

    # cosine similarity
    similarity = (image_features @ text_features.T).softmax(dim=-1)

# 6️⃣ 결과 출력
print("=== Emotion Similarity Scores ===")
for emotion, score in zip(emotion_texts, similarity[0]):
    print(f"{emotion:20s}: {score.item():.3f}")

scores = list(zip(emotion_texts, similarity[0].tolist()))
scores.sort(key=lambda x: x[1], reverse=True)

summary = ", ".join([e.replace("a ", "").replace(" image", "") for e, _ in scores[:3]])
print("Emotion Summary:", summary)

