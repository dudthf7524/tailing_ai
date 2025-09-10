# /app/model.py
# from config import config
# import io
# from PIL import Image
# from ultralytics import YOLO

# MODEL_PATH = config.MODEL_PATH
# IMAGE_SIZE = config.IMAGE_SIZE
# model = YOLO(MODEL_PATH)
# class_names = config.class_names

# def classification(image_bytes: bytes):
#     try:
#         # 이미지 입력
#         image = Image.open(io.BytesIO(image_bytes))
#         # 예측
#         results = model(image, imgsz = IMAGE_SIZE, verbose=False)
#         result = results[0]
#         probs = result.probs
#         ans_idx = probs.top1
#         conf = probs.top1conf.item()
#         predicted_class_name = class_names[ans_idx]

#         return {
#             "predicted_class": predicted_class_name,
#             "confidence": f"{conf:.4f}",
#             "class_index": ans_idx,
#         }

#     except Exception as e:
#         print(f"Error : {e}")





# /app/model.py
from config import config
import io
from PIL import Image
from ultralytics import YOLO

# ---------- 기존 분류 모델 ----------
MODEL_PATH = config.MODEL_PATH
IMAGE_SIZE = config.IMAGE_SIZE
print(f"[INIT] Loading classification model from {MODEL_PATH}, IMAGE_SIZE={IMAGE_SIZE}")
model = YOLO(MODEL_PATH)
class_names = config.class_names
print(f"[INIT] Class names loaded: {class_names}")

# ---------- 사람 필터 설정(없으면 기본값) ----------
PERSON_FILTER_ENABLED = getattr(config, "PERSON_FILTER_ENABLED", True)
PERSON_THRESHOLD = float(getattr(config, "PERSON_THRESHOLD", 0.5))
PERSON_MODEL_PATH = getattr(config, "PERSON_MODEL_PATH", "yolov8n.pt")  # COCO 사전학습(detector)

print(f"[INIT] Loading person detector from {PERSON_MODEL_PATH}, threshold={PERSON_THRESHOLD}, enabled={PERSON_FILTER_ENABLED}")
person_detector = YOLO(PERSON_MODEL_PATH)

def is_person_image(image_bytes: bytes, threshold: float = PERSON_THRESHOLD) -> bool:
    """yolov8 detector로 person(cls=0) 존재 여부 확인"""
    print("[is_person_image] Called")
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        print(f"[is_person_image] Image opened successfully, size: {image.size}")
        # 224x224 작은 이미지도 처리할 수 있도록 imgsz를 더 작게 설정
        results = person_detector(image, imgsz=IMAGE_SIZE, verbose=False)
        print(f"[is_person_image] Detection results: {results}")
        boxes = getattr(results[0], "boxes", None)
        if boxes is None:
            print("[is_person_image] No boxes found")
            return False
        for b in boxes:
            cls_id = int(b.cls)
            conf = float(b.conf)
            print(f"[is_person_image] Found cls_id={cls_id}, conf={conf}")
            if cls_id == 0 and conf >= threshold:
                print("[is_person_image] Person detected!")
                return True
        print("[is_person_image] No person detected above threshold")
        return False
    except Exception as e:
        print(f"[is_person_image][ERROR] {e}")
        return False

def classification(image_bytes: bytes):
    print("[classification] Called")
    try:
        # 1) 사람 이미지 프리필터(차단)
        if PERSON_FILTER_ENABLED:
            print("[classification] Running person filter...")
            if is_person_image(image_bytes, PERSON_THRESHOLD):
                print("[classification] Person detected → Blocking classification")
                return {
                    "blocked": True,
                    "predicted_class": 0,
                    "confidence": "0.0",
                    "class_index": "X",
                }

        # 2) 분류 실행
        print("[classification] Running classification model...")
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        print("[classification] Image opened successfully for classification")
        results = model(image, imgsz=IMAGE_SIZE, verbose=False)
        print(f"[classification] Raw results: {results}")
        result = results[0]

        # YOLO 분류 결과 확률
        probs = getattr(result, "probs", None)
        print(f"[classification] Probs: {probs}")
        if probs is None:
            print("[classification][ERROR] probs is None")
            return {
                "blocked": False,
                "error": "No probabilities found in result. Check if MODEL_PATH is a classification model.",
            }

        ans_idx = int(probs.top1)
        conf = float(probs.top1conf.item()) if hasattr(probs, "top1conf") else float(probs.data[ans_idx].item())
        predicted_class_name = class_names[ans_idx] if class_names and ans_idx < len(class_names) else str(ans_idx)

        print(f"[classification] Predicted idx={ans_idx}, name={predicted_class_name}, conf={conf}")

        return {
            "blocked": False,
            "predicted_class": predicted_class_name,
            "confidence": f"{conf:.4f}",
            "class_index": ans_idx,
        }

    except Exception as e:
        print(f"[classification][ERROR] {e}")
        return {"error": str(e)}
