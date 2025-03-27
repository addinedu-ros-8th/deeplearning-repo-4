
![제목을 입력해주세요_-001 (1)](https://github.com/user-attachments/assets/b2065a0f-8b31-4906-9bc5-95f4567c3903)

# 공사현장 안전감지 순찰로봇

## 👉 [통합 영상](https://youtu.be/33UZJujoVBs?si=Ll3DOmD68eE4wvqI)

## 👉 [발표 자료](https://docs.google.com/presentation/d/1dvwK7o6es8Wn-Mrr18u-DYbreAsfyP4J_0AuqXVFU0I/edit?usp=sharing)


## 1. 프로젝트 소개

### 1.1 목표
- AI기반 영상 분석을 통해 공사장의 위험 요소를 자동으로 감지하고, 이를 관리자에게 신속하게 전달하여 안전 관리를 돕는 서비스 개발

## 1.2 주제 선정 배경
![constrution](https://github.com/user-attachments/assets/30f03747-b251-4896-9a1f-d342b2cb2682)

### 공사 현장의 다양한 위험 요소 노출
- 작업자의 부주의나 관리자의 사각지대 때문에 사고로 이어질 가능성이 증가.

### 해결방안
- 인공지능 기술을 활용하여 영상 데이터를 분석하고, 위험 요소를 사전에 감지해 관리자에게 전달하는 시스템이 필요.


## 1-3. 팀원 및 역할
| **이름**    | **담당 업무**                                                                                             |
|-------------|-----------------------------------------------------------------------------------------------------|
| **박정배**<br/>**(팀장)**  | • 라인트레이싱 기능 개발 <br/> • 하드웨어 설계                            |
| **김가은**  | • GUI 개발 <br/> •           |
| **이태민**  | • 시스템 통합(Server) <br/> •                                           |
| **이우재**  | • 위험상황 탐지기능 개발  <br/> •  |


## 1-4. 활용 기술
| **구분**          | **상세**                                                                                                  |
|:------------------:|---------------------------------------------------------------------------------------------------------|
| **개발환경**       | <img src="https://img.shields.io/badge/Ubuntu 22.04-E95420?style=for-the-badge&logo=Ubuntu&logoColor=white"/> <img src="https://img.shields.io/badge/Amazon RDS-527FFF?style=for-the-badge&logo=amazonrds&logoColor=white"/> |
| **개발언어**       | <img src="https://img.shields.io/badge/Python 3.10-3776AB?style=for-the-badge&logo=Python&logoColor=white"/> |
| **UI**             | <img src="https://img.shields.io/badge/PYQT5-41CD52?style=for-the-badge&logo=cplusplus&logoColor=white"/> <img src="https://img.shields.io/badge/Figma-F24E1E?style=for-the-badge&logo=figma&logoColor=white"/> |
| **DBMS**           | <img src="https://img.shields.io/badge/MYSQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white"/> |
| **AI/DL**          | <img src="https://img.shields.io/badge/Tensorflow-FF6F00?style=for-the-badge&logo=Tensorflow&logoColor=white"/> <img src="https://img.shields.io/badge/Keras-D00000?style=for-the-badge&logo=keras&logoColor=white"/> <img src="https://img.shields.io/badge/Yolov8-F2E142?style=for-the-badge&logo=elegoo&logoColor=white"/> <img src="https://img.shields.io/badge/Mediapipe-0097A7?style=for-the-badge&logo=mediapipe&logoColor=white"/> |
| **API**            | <img src="https://img.shields.io/badge/KakaoTalk Message API-FFCD00?style=for-the-badge&logo=kakao&logoColor=black"/> <img src="https://img.shields.io/badge/USDA FoodData Central API-8DC63F?style=for-the-badge&logo=leaflet&logoColor=white"/> |
| **협업 도구**      | <img src="https://img.shields.io/badge/jira-0052CC?style=for-the-badge&logo=jira&logoColor=white"/> <img src="https://img.shields.io/badge/confluence-172B4D?style=for-the-badge&logo=confluence&logoColor=white"/>  <img src="https://img.shields.io/badge/slack-4A154B?style=for-the-badge&logo=slack&logoColor=white"/> |
| **소스 버전 관리** | <img src="https://img.shields.io/badge/git-F05032?style=for-the-badge&logo=git&logoColor=white"/> |

# 2. 설계
## 2-1. 주요 기능

## 2-2. 시스템 구성도
![sw_architecture drawio](https://github.com/user-attachments/assets/c4cec64c-fce8-4333-8cac-4ac386ad375f)

## 2-3. Data Structure
![TF_ERD drawio](https://github.com/user-attachments/assets/647de690-6a3f-4b6f-a3ca-f3c978d5c174)

## 2-4. 시퀀스 다이어그램

## 2-5. 사용자 시나리오

# 3. 기능
## 3-1.
## 3-2.
## 3-3.

# 4. 결론

## 4-1. 통합 테스트 결과

## 4-2. 개발시 어려웠던 점과 해결방안


## 특징 및 동기
프로젝트의 독창적인 점과 개발 동기를 설명합니다.
- 딥러닝 기술 선택 이유
- 적용 사례 및 기대 효과

## 데이터셋
사용한 데이터셋과 데이터 전처리 방법에 대해 기술합니다.
- **데이터 출처:** 공개 데이터셋 혹은 자체 수집 데이터
- **전처리 과정:** 정규화, 증강 등 전처리 방법

## 모델 아키텍처
모델의 구성 및 학습 전략을 소개합니다.
- **모델 개요:** 사용한 네트워크 구조 (CNN, RNN, Transformer 등)
- **하이퍼파라미터:** 학습률, 배치 사이즈, 에폭 등
- **특이사항:** 모델 개선을 위한 기법이나 추가 아이디어

## 설치 및 실행 방법
프로젝트를 로컬에서 실행할 수 있도록 환경 설정 및 실행 방법을 안내합니다.

```bash
# 1. 레포지토리 클론
git clone https://github.com/사용자명/프로젝트명.git
cd 프로젝트명

# 2. 가상환경 생성 및 활성화 (예: Python 가상환경)
python -m venv env
source env/bin/activate  # Windows는 env\Scripts\activate

# 3. 필요한 패키지 설치
pip install -r requirements.txt

# 4. 프로젝트 실행
python main.py
