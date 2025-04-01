#include <Servo.h>

const int trigPin = 2;  // 초음파 센서 Trig 핀
const int echoPin = 3;  // 초음파 센서 Echo 핀
const int potPin = A0;  // 포텐쇼미터 핀
const int ESC_STOP = 1100;
const int ESC_MAX = 1150;
const int STOP_DISTANCE = 30;  // 30cm 이내 감지 시 정지

int escPin1 = 6;
int escPin2 = 5;
Servo esc1, esc2;
Servo servo1, servo2;

bool isMoving = false;  // 모터가 움직이고 있는지 상태 추적

void setup() {
  Serial.begin(115200);
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  
  esc1.attach(escPin1);
  esc2.attach(escPin2);
  servo1.attach(10);
  servo2.attach(9);

  // ESC 초기화 (최소 신호 먼저 보내기)
  esc1.writeMicroseconds(ESC_STOP);
  esc2.writeMicroseconds(ESC_STOP);
  delay(2000);  // ESC가 신호를 인식할 시간 대기

  servo1.write(90);
  servo2.write(90);
}

void loop() {
  // 시리얼 명령어 처리
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');  // 명령어 끝까지 읽기
    
    if (command == "0x20") { // 정지 명령
      Serial.println("[모터 정지]");
      esc1.writeMicroseconds(ESC_STOP);
      esc2.writeMicroseconds(ESC_STOP);
      isMoving = false;  // 모터 정지 상태로 설정
    }
    else if (command == "0x21") { // 이동 명령
      Serial.println("[모터 동작]");
      isMoving = true;  // 모터 동작 상태로 설정
    }
    else {
      Serial.println("Invalid command.");
    }
  }

  // 모터가 움직이는 동안 초음파 센서가 계속 거리 측정
  float distance = getDistance();  

  if (isMoving) {
    if (distance < STOP_DISTANCE) {
      Serial.println("Obstacle detected! Stopping automatically.");
      esc1.writeMicroseconds(ESC_STOP);
      esc2.writeMicroseconds(ESC_STOP);
      isMoving = false;  // 자동 정지
    } else {
      esc1.writeMicroseconds(ESC_MAX);  // 장애물이 없으면 계속 이동
      esc2.writeMicroseconds(ESC_MAX);
    }
  }

  // 포텐쇼미터로 서보모터 제어
  int potValue = analogRead(potPin);  // 포텐쇼미터 값 읽기 (0~1023)
  int angle = map(potValue, 0, 1023, 0, 180);  // 0~180도로 변환

  servo1.write(angle);
  servo2.write(angle);

  delay(20);  // ESC 주기를 고려하여 20ms 대기
}

// 초음파 거리 측정 함수
float getDistance() {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  long duration = pulseIn(echoPin, HIGH, 30000); // 30ms 타임아웃 추가
  float distance = duration * 0.0343 / 2;  // cm 단위로 변환 (0.0343cm per microsecond)
  
  // Serial.print("Distance (cm): ");
  // Serial.println(distance);
  return distance;
}
