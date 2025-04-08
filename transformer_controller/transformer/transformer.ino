#include <Arduino_FreeRTOS.h>
#include <semphr.h> 
const int A_1A = 2;
const int A_1B = 3;
const int B_1A = 4;
const int B_1B = 5;
SemaphoreHandle_t xSerialSemaphore;

uint8_t status = 0b00000000; // bit 2, 1
void forward();
void backward();
void turnRight();
void turnLeft();
void stop();

void setup() {
  Serial.begin(115200);
  pinMode(A_1A, OUTPUT);
  pinMode(A_1B, OUTPUT);
  pinMode(B_1A, OUTPUT);
  pinMode(B_1B, OUTPUT);

  xTaskCreate(receiveDataFromHead, "ReceiveDataTask", 4096, NULL, 1, NULL);

}

void loop() {
  forward();
}

void forward() {
  digitalWrite(A_1A, HIGH);
  digitalWrite(A_1B, LOW);
  digitalWrite(B_1A, HIGH);
  digitalWrite(B_1B, LOW);
}

void backward() {
  digitalWrite(A_1A, LOW);
  digitalWrite(A_1B, HIGH);
  digitalWrite(B_1A, LOW);
  digitalWrite(B_1B, HIGH);
}

void turnRight() {
  digitalWrite(A_1A, LOW);
  digitalWrite(A_1B, HIGH);
  digitalWrite(B_1A, HIGH);
  digitalWrite(B_1B, LOW);
}

void turnLeft() {
  digitalWrite(A_1A, HIGH);
  digitalWrite(A_1B, LOW);
  digitalWrite(B_1A, LOW);
  digitalWrite(B_1B, HIGH);
}

void stop() {
  digitalWrite(A_1A, LOW);
  digitalWrite(A_1B, LOW);
  digitalWrite(B_1A, LOW);
  digitalWrite(B_1B, LOW);
}

void receiveDataFromHead(void* params) {
  uint8_t buffer[1024];  // 수신 버퍼
  uint8_t lengthBytes[4]; // 길이 저장 버퍼
  uint32_t length = 0;
  int received = 0;
  int state = 0; // 0: 길이 수신, 1: 데이터 수신
  unsigned long lastReceiveTime = 0;
  const unsigned long timeout = 500; // 500ms 타임아웃

  while (true) {
    if (state == 0) { 
      if (Serial.available() >= 4) {
        Serial.readBytes(lengthBytes, 4);
        memcpy(&length, lengthBytes, 4); 
        received = 0;
        lastReceiveTime = millis();  
        state = 1; 
      }
    } 
    
    if (state == 1) {
      while (Serial.available() > 0 && received < length) {
        buffer[received++] = Serial.read();
        lastReceiveTime = millis();
      }

      if (received >= length) {  // 📌 패킷 완전 수신
        uint8_t header = buffer[0];

        if (header == 0x20) {
          uint8_t targetStatus = buffer[2];
          if ((targetStatus >> 1) & 1 == 1) {
            forward();
            status = 0b00000010;
          } else {
            stop();
            status = 0b00000000;
          }
          
          status = 0b00000010 & targetStatus;
          uint8_t response[7];
          uint32_t resLength = 3;
          memcpy(response, &resLength, 4);
          response[4] = 0x51;
          response[5] = 1;
          response[6] = status;
          Serial.write(response, 7);
        }
        state = 0; 
      }
    }

    if (millis() - lastReceiveTime > timeout) {
      state = 0;
      received = 0;
    }

    vTaskDelay(10);
  }
}
