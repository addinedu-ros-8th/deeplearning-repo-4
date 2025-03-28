import cv2
from ultralytics import YOLO

# 1) 객체 검출 모델 로드 (WO-01 등 검출)
det_model = YOLO("/home/ted/dev_ws/deeplearing_pj/runs/segment/train19/weights/best.pt")

# 2) 헬멧 검출 모델 로드 (헬멧 부분만 검출하도록 학습된 모델)
helmet_model = YOLO("/home/ted/dev_ws/deeplearing_pj/helmet_detection/yolov8n_helmet/weights/best.pt")

# 카메라 열기
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 첫 번째 모델로 전체 프레임에서 객체 검출
    results = det_model(frame)

    for result in results:
        for box in result.boxes:
            # bounding box 좌표 추출 (정수형)
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            class_idx = int(box.cls[0])
            class_name = result.names[class_idx]

            # WO-01인 경우 헬멧 검출 모델 적용
            if class_name == "WO-01":
                # WO-01 영역 crop
                crop_img = frame[y1:y2, x1:x2]
                if crop_img.size == 0:
                    continue

                # crop된 이미지에서 헬멧 검출 (헬멧 영역만 검출하도록 학습된 모델)
                helmet_results = helmet_model(crop_img)
                helmet_detected = False

                # 헬멧 검출 결과 처리
                for helmet_result in helmet_results:
                    for helmet_box in helmet_result.boxes:
                        # 헬멧 검출된 영역의 좌표 (crop 이미지 기준)
                        hx1, hy1, hx2, hy2 = map(int, helmet_box.xyxy[0])
                        helmet_class_idx = int(helmet_box.cls[0])
                        helmet_class_name = helmet_result.names[helmet_class_idx]

                        # 원본 이미지 좌표로 변환 (crop 시작점(x1,y1) offset 적용)
                        ox1, oy1, ox2, oy2 = x1 + hx1, y1 + hy1, x1 + hx2, y1 + hy2

                        # 헬멧 검출 영역 표시 (예: 빨간색 바운딩 박스)
                        cv2.rectangle(frame, (ox1, oy1), (ox2, oy2), (0, 0, 255), 2)
                        cv2.putText(frame, helmet_class_name, (ox1, oy1 - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
                        helmet_detected = True
                        break  # 첫 검출 결과만 사용
                    if helmet_detected:
                        break

                # 헬멧이 검출되지 않은 경우, WO-01 전체에 "No Helmet" 표시
                if not helmet_detected:
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)
                    cv2.putText(frame, "No Helmet", (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)
            else:
                # WO-01가 아닌 경우, 원래 검출된 클래스명과 함께 전체 객체 바운딩 박스 표시
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, class_name, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    cv2.imshow("Frame", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
