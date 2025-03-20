import json
import cv2
import numpy as np
import matplotlib.pyplot as plt
import glob
# JSON 파일 경로
json_path = "./datasets/safety/라벨링데이터/TS_Y-39"
# 이미지 파일 경로
image_path = './datasets/safety/원천데이터/TS_Y-39'

image_files = glob.glob(image_path + "/*.jpg")
json_files = glob.glob(json_path + "/*.json")
image_files.sort()
json_files.sort()

prev_frame = 0
idx = 0

while True:
    # JSON 로드
    with open(json_files[idx], 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 이미지 로드 (OpenCV는 기본 BGR이므로 나중에 RGB로 변환)
    image = cv2.imread(image_files[idx])
    if image is None:
        raise FileNotFoundError(f"이미지 파일을 찾을 수 없습니다: {image}")
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    # Annotations 추출
    annotations = data["Learning_Data_Info."]["Annotations"]
    for ann in annotations:
        ann_type = ann["type"]
        coords = ann["value"]
        class_id = ann["class_ID"]
        if ann_type == "polygon":
            # 폴리곤인 경우 [x1, y1, x2, y2, ...] 형태이므로,
            # 2개씩 묶어서 (x, y) 좌표 리스트로 변환
            pts = [(coords[i], coords[i+1]) for i in range(0, len(coords), 2)]
            pts_np = np.array(pts, dtype=np.int32).reshape((-1, 1, 2))
            # 폴리곤 그리기
            cv2.polylines(image, [pts_np], isClosed=True, color=(255, 0, 0), thickness=3)
            # 첫 번째 점 근처에 클래스 ID 표시
            x_text, y_text = pts[0]
            cv2.putText(image, class_id, (int(x_text), int(y_text) - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        elif ann_type == "bbox":
            # bbox인 경우 [x_min, y_min, x_max, y_max]
            x_min, y_min, x_max, y_max = coords
            pt1 = (int(x_min), int(y_min))
            pt2 = (int(x_max), int(y_max))
            # 사각형 그리기
            cv2.rectangle(image, pt1, pt2, (0, 255, 0), 3)
            # 왼쪽 상단에 클래스 ID 표시
            cv2.putText(image, class_id, pt1,
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow("image", image)
    key = cv2.waitKey(0) & 0xFF
    if key == ord('w') and len(image_files) - 1 > idx:
        prev_frame = idx
        idx += 1
    elif key == ord('s') and idx > 0:
        prev_frame = idx
        idx -= 1
    elif key == ord('q'):
        break
        
cv2.destroyAllWindows()