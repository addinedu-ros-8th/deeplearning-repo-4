import cv2
from ultralytics import YOLO




model = YOLO('/home/ted/dev_ws/deeplearing_pj/runs/segment/train19/weights/best.pt')  # best.pt가 저장된 위치

# 웹캠 열기 (기본 카메라 사용)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("웹캠을 열 수 없습니다.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("프레임을 받아올 수 없습니다.")
        break

    results = model(frame)
    annotated_frame = results[0].plot()
    cv2.imshow("Real-time Inference", annotated_frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 리소스 해제
cap.release()
cv2.destroyAllWindows()
