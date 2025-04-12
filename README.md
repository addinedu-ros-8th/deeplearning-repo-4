
![제목을 입력해주세요_-001 (1)](https://github.com/user-attachments/assets/b2065a0f-8b31-4906-9bc5-95f4567c3903)

# 공사현장 안전감지 순찰로봇

## 👉 [통합 영상](https://youtu.be/Cz_f8TSdo1w)

## 👉 [발표 자료](https://docs.google.com/presentation/d/1E1gCpSgeWy28GYIsga0qjuvy6-IceTNsRVZ3a80uXaQ/edit?usp=sharing)


## 1. 프로젝트 개요

### 1.1 프로젝트 소개
이 프로젝트는 안전 모니터링과 자율 주행 기능을 결합한  **Driving Robot** 시스템을 구축하는 것을 목표로 합니다. <br>
  공사현장에서 안전사고가 일어날 수 있는 상황을 판단하여, 안전관리자에게 전송하여 안전사고를 미리 대비하는 기능이 핵심입니다.



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

## 1-5. 합업둘

### Jira
[jara.webm](https://github.com/user-attachments/assets/afcca6c6-6cfc-4628-bf21-e0afef050549)

### Confluence
<img src="https://github.com/user-attachments/assets/961891e8-fdac-4022-8efa-41a84195af33" width="1000" />


# 2. 설계
## 2-1. Main Function

<img src="https://github.com/user-attachments/assets/0a17c591-875f-464d-85ed-c78fe6ad9a86" alt="주요 기능" width="1000"/>


## 2-2. System Architecture

<img src="https://github.com/user-attachments/assets/c4cec64c-fce8-4333-8cac-4ac386ad375f" alt="시스템 구성도" width="1000"/>

## 2-3. Data Structure

<img src="https://github.com/user-attachments/assets/647de690-6a3f-4b6f-a3ca-f3c978d5c174" alt="data structure" width="1000"/>

## 2-4. Interface Specification
<img src="https://github.com/user-attachments/assets/330336c1-3872-42d0-b24d-441440afe9ee" alt="data structure" width="1000"/>

## 2-5. Sequence Diagram

### Streaming 
<img src="https://github.com/user-attachments/assets/3322af13-384e-49f9-bcc2-b57a3d09bfdd" width="1000"/>

### Detect 
<img src="https://github.com/user-attachments/assets/be06ab33-7ab8-440c-a4f7-29d6a8a34ed0" width="1000"/>

### Control Driving 
<img src="https://github.com/user-attachments/assets/61263244-34b0-4742-8d3a-9083549423cc" width="1000"/>


## 2-6. GUI

<img src="https://github.com/user-attachments/assets/02da4599-988c-46a1-89c2-c039d5b48128" alt="인명 사고 예방" width="1000"/>
<img src="https://github.com/user-attachments/assets/18becab3-9681-4e39-8ff9-65c0bbf207e2" alt="인명 사고 예방" width="1000"/>

## 2-7. Hardware Design
<img src="https://github.com/user-attachments/assets/c962944d-6e21-4f0a-8eaf-37c702a8c7fd" alt="인명 사고 예방" width="1000"/>


## 2-7. Deeplearning

### 2-7-1 Data Set  [AI-HUB 건설 현장 위험 상태 판단 데이터](https://www.aihub.or.kr/aihubdata/data/view.do?currMenu=115&topMenu=100&dataSetSn=71407)

### 2-7-2 Model
<img src="https://github.com/user-attachments/assets/ca8f9120-6a9f-428c-bbde-07ec78e12d32" alt="2-7-2 Model 1" width="1000"/>
<img src="https://github.com/user-attachments/assets/ceaab821-f3d6-4ad8-8600-c3ac949616f0" alt="2-7-2 Model 2" width="1000"/>

### 2-7-3 Accuracy
<img src="https://github.com/user-attachments/assets/fa8a7929-3a60-4a6c-8ca2-b0d75dddb186" alt="2-7-3 Accuracy 1" width="1000"/>
<img src="https://github.com/user-attachments/assets/57c72927-7d57-4f23-9b9f-762c5d9901aa" alt="2-7-3 Accuracy 2" width="1000"/>

### 2-7-4 Improve Performance

### 2-7-4-1 Preprocessing
<img src="https://github.com/user-attachments/assets/7e1db354-5918-42b6-9266-7a8535ce58b4" alt="2-7-4-1 Preprocessing" width="1000"/>

### 2-7-4-2 Augmentation
<img src="https://github.com/user-attachments/assets/799b3e16-b430-43c5-a08a-451878e2f698" alt="2-7-4-2 Augmentation" width="1000"/>

### 2-7-4-2 Optimizer
<img src="https://github.com/user-attachments/assets/1a086f8f-b0b1-48cf-95d0-72a0cee62cff" alt="2-7-4-2 Optimizer" width="1000"/>

### 2-8 Class Diagram 
<img src="https://github.com/user-attachments/assets/daafb111-dfc0-44ba-9a2d-eca1654cc3d5" alt="2-8 Class Diagram" width="1000"/>

# 3. 기능
## 3-1. 상황인식기능
<img src="https://github.com/user-attachments/assets/37a36a38-4d1a-4333-ba73-279823dedd62" alt="인명 사고 예방" width="1000"/>
<img src="https://github.com/user-attachments/assets/1f131c3e-aa18-49be-b930-0d068a95d2ee" alt="인명 사고 예방" width="1000"/>


## 3-2. 주행기능
[Screencast from 2025-04-12 13-40-32.webm](https://github.com/user-attachments/assets/43b94c77-00af-4192-88b6-11bfb2643306)


## 3-3. GUI알림기능
[Screencast from 2025-04-12 13-42-28.webm](https://github.com/user-attachments/assets/c532bbc9-c1cf-456c-a42c-e0ef26ae8465)

# 4. 결론
설계 단계에서 전체 시스템을 기능 단위로 명확히 모듈화하여 세분화하였으며, 특히 서버를 AI 서버와 Main 서버로 분리함으로써 시스템의 부하를 분산하고 통신 속도 개선에 기여하였다.
성능 향상을 위해 비동기 통신 구조를 적용하고, 멀티스레딩 및 큐 기반 병렬 처리 방식을 도입하여 데이터 처리 속도와 타이밍 문제를 효과적으로 개선하였다.
전체 코드를 기능별 클래스 구조로 모듈화함으로써 재사용성과 유지보수의 효율성을 높였다.
AI 모델의 실시간 처리 한계를 극복하기 위해, 분석 알고리즘을 체계화하고 처리 과정을 최적화하여 실시간성 확보에 성공하였다.

## 4-2. 아쉬운점과 한계점
Main 서버가 중단되었을 때 전체 시스템의 기능이 멈추는 구조적 한계가 있었으며, 이에 대한 자동 재연결 및 예외 처리 로직이 부족하였다.
일부 클래스에 기능이 과도하게 집중되어 있어, 역할 분리 및 클래스 세분화가 미흡하다는 점이 코드의 유지보수성과 확장성에 영향을 주었다.
Serial 통신에서 통신 속도가 빠를 경우, 기존의 데이터 길이 기반 프로토콜에서 동기화 문제가 발생하는 등 통신 안정성 측면에서 개선이 필요했다.
프로젝트 목적에 맞는 적절한 데이터셋 확보가 어려워, AI 모델 학습 및 테스트 과정에서 제약이 있었다.
기구 제작에 소요되는 시간이 예상보다 길어짐에 따라, 자동 주행 기능의 구현이 프로젝트 일정 내에 완료되지 못한 점이 아쉬움으로 남았다.

## 4-3. 개선점
초기 설계 단계에 더욱 집중하여, 시스템 전반의 Architecture를 명확하게 수립하고, 다양한 UML을 활용해 각 기능에 대한 설계를 구체화함으로써 프로젝트 진행 전 명확한 일정 및 역할 분담이 가능하도록 할 필요가 있다.
각 기능 구현 전 기술 검증을 세분화하여 수행하고, 다양한 예외 상황을 사전에 정의하여 오류 처리 및 예외 대응 로직을 강화함으로써 전체 시스템의 안정성과 신뢰성을 높여야 한다.
사용 가능한 외부 데이터에 대한 조사를 철저히 하고, 필요한 경우 직접 촬영 또는 수집을 통해 학습에 적합한 데이터셋을 확보할 수 있도록 사전 준비가 필요하다.
클래스 구조를 역할에 따라 명확히 분리하고, 단일 책임 원칙(SRP)을 적용하여 모듈화 수준을 높임으로써 유지보수성과 확장성을 개선해야 한다.
네트워크 불안정 상황에서도 시스템이 일정 수준의 기능을 유지할 수 있도록, 자동 재연결, 타임아웃 처리, 백업 서버 연결 등 예외 대응 방안을 구조에 포함해야 한다.
일정 지연 요소 중 하나였던 기구 제작이나 외부 의존 작업은 사전 테스트 및 시뮬레이션 기반 개발을 통해 병행 처리하거나, 기능 우선순위 기반으로 유연하게 프로젝트 범위를 조정할 필요가 있다.


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
