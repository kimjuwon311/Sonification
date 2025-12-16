import torch
import clip
from PIL import Image

device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)

IMAGE_PATH = r"C:\Python Project_Folders\bichek\stanley-park-4539852_1280.jpg"

EMOTION_TEXTS = [
    "a calm image",
    "a peaceful image",
    "a gloomy image",
    "a tense image",
    "a joyful image",
    "an energetic image",
    "a cold image",
    "a warm image"
]

EMOTION_KEYS = [e.replace("a ", "").replace(" image", "") for e in EMOTION_TEXTS]

def get_clip_emotions(image_path=IMAGE_PATH):
    """이미지를 CLIP에 넣어 각 감정별 강도를 dict로 반환"""
    image = preprocess(Image.open(image_path).convert("RGB")).unsqueeze(0).to(device)
    text_tokens = clip.tokenize(EMOTION_TEXTS).to(device)

    with torch.no_grad():
        img_f = model.encode_image(image)
        txt_f = model.encode_text(text_tokens)
        sims = (img_f @ txt_f.T).softmax(dim=-1)[0]

    # 감정별 강도를 명시적으로 0~1 값으로 반환
    emotions_with_strength = {k: float(v) for k, v in zip(EMOTION_KEYS, sims.tolist())}
    return emotions_with_strength

# 예시 실행
if __name__ == "__main__":
    emotions = get_clip_emotions()
    for k,v in emotions.items():
        print(f"{k:10s}: {v:.3f}")

