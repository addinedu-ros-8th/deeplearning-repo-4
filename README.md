
![제목을 입력해주세요_-001 (1)](https://github.com/user-attachments/assets/b2065a0f-8b31-4906-9bc5-95f4567c3903)

# 공사현장 안전감지 순찰로봇

## 👉 [통합 영상](https://youtu.be/33UZJujoVBs?si=Ll3DOmD68eE4wvqI)

## 👉 [발표 자료](https://docs.google.com/presentation/d/1dvwK7o6es8Wn-Mrr18u-DYbreAsfyP4J_0AuqXVFU0I/edit?usp=sharing)


## 1. 프로젝트 개요

### 1.1 프로젝트 소개
이 프로젝트는 안전 모니터링과 자율 주행 기능을 결합한  **Driving Robot** 시스템을 구축하는 것을 목표로 합니다. <br>
  공사현장에서 안전사고가 일어날 수 있는 상황을 판단하여, 공사감독자에게 전송하여 안전사고를 미리 대비하는 기능이 핵심입니다.



## 1.2 주제 선정 배경
<table align="center">
    <tr>
        <td align="center">
            <img src="https://github.com/user-attachments/assets/442625fc-3e16-403d-901d-c20a8ed1498b" alt="공사장 안전사고의 증가" height="200"/>
        </td>
        <td align="center">
            <img src="https://github.com/user-attachments/assets/8cf9a31e-0296-4919-b24c-8068743b46f2" alt="데이터 기반 안전 관리" height="200"/>
        </td>
        <td align="center">
            <img src="https://github.com/user-attachments/assets/af1c2b51-0979-482d-8249-5c560424cfa8" alt="인명 사고 예방" height="200"/>
        </td>
    </tr>
    <tr>
        <td align="center">
            <p><strong>공사장 안전사고의 증가</strong></p>
        </td>
        <td align="center">
            <p><strong>데이터 기반 안전 관리</strong></p>
        </td>
        <td align="center">
            <p><strong>인명 사고 예방</strong></p>
        </td>
    </tr>
</table>

### 공사장 안전사고 증가
- 최근 공사장에서의 안전사고가 꾸준히 증가하고 있으며, 특히 기본적인 안전수칙 미준수나 장비 착용 미비로 인한 인명 피해가 심각한 수준입니다.

### 데이터 기반 안전 관리
- 로봇이 수집한 영상/센서 데이터를 기반으로 **사고가 자주 발생하는 구역**이나 **위험 행동 패턴**을 분석할 수 있습니다. 또한 이런 데이터는 향후 **더 효율적인 안전 계획 수립**에 도움이 됩니다.

### 인명 사고 예방 : 
- 로봇이 사람 대신 근로자들의 **안전 장비 착용 여부와 화재장비**를 실시간 감지하면 **사고를 사전에 방지**할 수 있습니다.


## 1-3. 팀원 및 역할
| **이름**    | **담당 업무**                                                                                             |
|-------------|-----------------------------------------------------------------------------------------------------|
| **박정배**<br/>**(팀장)**  | • 주행기능 개발 <br/> • 하드웨어 설계                            |
| **김가은**  | • GUI 개발 <br/> • DB 설계          |
| **이태민**  | • 시스템 통합(Server) <br/> • 통신기능 개발   |
| **이우재**  | • 딥러닝 모델 개발  <br/> • 시스템 아케텍처 설계  |


## 1-4. 활용 기술
| **구분**          | **상세**                                                                                                  |
|:------------------:|---------------------------------------------------------------------------------------------------------|
| **개발환경**       | <img src="https://img.shields.io/badge/Ubuntu 24.04-E95420?style=for-the-badge&logo=Ubuntu&logoColor=white"/>  |
| **개발언어**       | <img src="https://img.shields.io/badge/Python 3.12-3776AB?style=for-the-badge&logo=Python&logoColor=white"/> |
| **UI**             | <img src="https://img.shields.io/badge/PYQT5-41CD52?style=for-the-badge&logo=cplusplus&logoColor=white"/> |
| **DBMS**           | <img src="https://img.shields.io/badge/MYSQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white"/> |
| **AI/DL**          | <img src="https://img.shields.io/badge/Tensorflow-FF6F00?style=for-the-badge&logo=Tensorflow&logoColor=white"/> <img src="https://img.shields.io/badge/Keras-D00000?style=for-the-badge&logo=keras&logoColor=white"/> <img src="https://img.shields.io/badge/Yolov8-F2E142?style=for-the-badge&logo=elegoo&logoColor=white"/> <img src="https://img.shields.io/badge/Mediapipe-0097A7?style=for-the-badge&logo=mediapipe&logoColor=white"/> |
| **협업 도구**      | <img src="https://img.shields.io/badge/jira-0052CC?style=for-the-badge&logo=jira&logoColor=white"/> <img src="https://img.shields.io/badge/confluence-172B4D?style=for-the-badge&logo=confluence&logoColor=white"/>  <img src="https://img.shields.io/badge/slack-4A154B?style=for-the-badge&logo=slack&logoColor=white"/> |
| **소스 버전 관리** | <img src="https://img.shields.io/badge/git-F05032?style=for-the-badge&logo=git&logoColor=white"/> |

# 2. 설계
## 2-1. 주요 기능

<img src="https://github.com/user-attachments/assets/0a17c591-875f-464d-85ed-c78fe6ad9a86" alt="주요 기능" width="1000"/>


## 2-2. 시스템 구성도

<img src="https://github.com/user-attachments/assets/c4cec64c-fce8-4333-8cac-4ac386ad375f" alt="시스템 구성도" width="1000"/>

## 2-3. Data Structure

<img src="https://github.com/user-attachments/assets/647de690-6a3f-4b6f-a3ca-f3c978d5c174" alt="data structure" width="1000"/>


## 2-4. 시퀀스 다이어그램

## 2-5. GUI

<img src="https://github.com/user-attachments/assets/02da4599-988c-46a1-89c2-c039d5b48128" alt="인명 사고 예방" width="1000"/>
<img src="https://github.com/user-attachments/assets/18becab3-9681-4e39-8ff9-65c0bbf207e2" alt="인명 사고 예방" width="1000"/>

## 2-5. 딥러닝 모델
## 데이터셋
### 데이터 셋: [AI-HUB 건설 현장 위험 상태 판단 데이터](https://www.aihub.or.kr/aihubdata/data/view.do?currMenu=115&topMenu=100&dataSetSn=71407)
### 전처리 과정: 정규화, 증강 등 전처리 방법

## 모델 아키텍처
- **모델 개요:** YOLO8n-seg, 
- **하이퍼파라미터:**
epochs: 100
patience: 100
batch: 16
imgsz: 640
optimizer: adam
- **특이사항:** 모델 개선을 위한 기법이나 추가 아이디어

# 3. 기능
## 3-1.
## 3-2.
## 3-3.



# 5. 결론

## 5-1. 통합 테스트 결과

## 5-2. 개발시 어려웠던 점과 해결방안

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
