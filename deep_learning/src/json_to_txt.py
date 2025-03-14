import json
import os
import glob

# 이미지 크기 (예: 1920x1080)
IMG_WIDTH, IMG_HEIGHT = 1920, 1080

def convert_bbox_to_yolo(bbox):
    """ 바운딩 박스를 YOLO 형식으로 변환 """
    x_min, y_min, x_max, y_max = bbox
    
    x_min, x_max = min(x_min, x_max), max(x_min, x_max)
    y_min, y_max = min(y_min, y_max), max(y_min, y_max)

    # 좌표 보정 (이미지 크기 내에서 제한)
    x_min = max(0, min(x_min, IMG_WIDTH))
    y_min = max(0, min(y_min, IMG_HEIGHT))
    x_max = max(0, min(x_max, IMG_WIDTH))
    y_max = max(0, min(y_max, IMG_HEIGHT))

    # 변환
    x_center = (x_min + x_max) / 2.0
    y_center = (y_min + y_max) / 2.0
    width = x_max - x_min
    height = y_max - y_min

    # 정규화
    x_center_norm = x_center / IMG_WIDTH
    y_center_norm = y_center / IMG_HEIGHT
    width_norm = width / IMG_WIDTH
    height_norm = height / IMG_HEIGHT

    return x_center_norm, y_center_norm, width_norm, height_norm

# 클래스 매핑
class_mapping = {
    "Y-09": 0, "Y-10": 1, "Y-11": 2,
    "Y-12": 3, "Y-33": 4, "Y-34": 5, 
    "Y-39": 6, "Y-40": 7, "N-09": 8,
    "N-10": 9, "N-11": 10, "N-12": 11,
    "N-33": 12, "N-34": 13, "N-39": 14,
    "N-40": 15, "WO-01": 16, "WO-03": 17,
    "WO-23": 18, "SO-20": 19, "SO-21": 20,
    "SO-24": 21, "SO-28": 22, "SO-40": 23
}

# JSON 파일 경로
json_path = "./datasets/safety/라벨링데이터/TS_Y-09/"
json_file_list = glob.glob(json_path + "*.json")
save_path = "./datasets/safety/train/labels/"

for json_file in json_file_list:
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    annotations = data["Learning_Data_Info."]["Annotations"]
    yolo_annotations = []

    for ann in annotations:
        ann_type = ann["type"]
        class_id = ann["class_ID"]

        if class_id not in class_mapping:
            continue

        label_index = class_mapping[class_id]

        if ann_type == "bbox":
            bbox = ann["value"]  # [x_min, y_min, x_max, y_max]
        elif ann_type == "polygon":
            coords = ann["value"]
            xs = coords[0::2]
            ys = coords[1::2]
            if not xs or not ys:
                continue
            bbox = [min(xs), min(ys), max(xs), max(ys)]
        else:
            continue

        # 변환 수행
        x_center, y_center, width, height = convert_bbox_to_yolo(bbox)

        # 변환된 좌표가 유효한지 확인
        if width <= 0 or height <= 0:
            print(f"⚠️ Warning: Skipping invalid bbox in {json_file}: {bbox}")
            continue

        yolo_annotations.append(f"{label_index} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}")

    # YOLO 라벨 파일 저장
    label_file = save_path + json_file[len(json_path):-4] + "txt"
    with open(label_file, 'w', encoding='utf-8') as f:
        for line in yolo_annotations:
            f.write(line + "\n")

    print(f"✅ YOLO 형식 라벨 저장 완료: {label_file}")
