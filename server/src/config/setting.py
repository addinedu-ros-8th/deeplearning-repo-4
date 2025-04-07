from enum import *

class SocketIP(StrEnum):
    MAIN_SERVER_IP = "192.168.0.180"

    AI_SERVER_IP = "192.168.0.180"
    
class SocketPort(IntEnum):
    MAIN_GUI_PORT = 8080

    MAIN_VISION_PORT = 8081

    MAIN_AI_PORT = 8082

    AI_VISION_PORT = 8083
    
class EventType(StrEnum):
    장비위반 = "장비위반"
    용접위반 = "용접작업 위반"
    절삭위반 = "절삭작업 위반"
    사다리위반 = "사다리작업 위반"
    사고 = "사고"
    
class Equip(StrEnum):
    안전모 = "안전모"
    용접가면 = "용접가면"
    소화기 = "소화기"
    불티산방지막="불티산방지막"
    적재물 = "적재물"
    최상단밑단 = "최상단 밑단"
    
class Accident(StrEnum):
    감지 = "감지"
    쓰러짐 = "쓰러짐"
    화재 = "화재"
    
class Label(StrEnum):
    작업자 = "WO-01"
    사다리 = "WO-03"
    용접가면 = "WO-23"
    불티산방지막 = "SO-20"
    용접기 = "SO-24"
    원형톱 = "SO-28"
    소화기 = "SO-40"
    헬멧 = "helmet"

class Command(IntEnum):
    # getStream
    STOP_STREAM = 0x00
    START_STREAM = 0x01
    
    # sendStream
    SEND_STREAM = 0x10
    
    # setStatus
    SET_STATUS = 0x20
     
    # detect
    NOT_DETECT = 0x30
    DETECT = 0x31
    
    # getStatus
    GET_STATUS = 0x50
    RESPONSE_STATUS = 0x51
    
    # requestGrant
    REQUEST_GRANT = 0x40
    
class RobotID(IntEnum):
    ROBOT1 = 1
    ROBOT2 = 2
    
class Status(IntEnum):
    ERROR = 1 << 0
    DRIVE_MODE = 1 << 1
    CAMERA = 1 << 2
    BUZZER_MASK = 0b11 << 3
    BUZZER_SHIFT = 3