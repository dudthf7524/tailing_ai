# /config/config.py

PORT = 8080
MODEL_PATH = "models/best.pt"
IMAGE_SIZE = 224
class_names = ["A1", "A2", "A3", "A4", "A5", "A6"]

# 사람 탐지 설정 - 224x224 작은 이미지에서도 탐지할 수 있도록 threshold 낮춤
PERSON_FILTER_ENABLED = True
PERSON_THRESHOLD = 0.3  # 기본 0.5에서 0.3으로 낮춤
PERSON_MODEL_PATH = "yolov8n.pt"