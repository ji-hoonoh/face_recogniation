# config.py
from dataclasses import dataclass

@dataclass
class Config:
    """
    프로젝트의 모든 설정값을 관리하는 클래스입니다.
    현업에서는 하드코딩(숫자를 코드에 직접 박는 것)을 피하고
    이렇게 설정 파일로 분리하여 관리합니다.
    """
    # === 파일 경로 설정 ===
    AUTH_IMAGE_FILE: str = "me_camera.jpg"  # 주인 얼굴 사진 파일명
    SECRET_FILE: str = "secret.xlsx"        # 실행할 보안 파일명
    
    # === 보안 민감도 설정 ===
    # 이 값이 낮을수록 엄격하게 검사합니다. (0.4 ~ 0.5 추천)
    TOLERANCE: float = 0.50
    
    # === 시스템 설정 ===
    # 얼굴 인식을 몇 번 실패해야 잠글지 결정 (너무 낮으면 깜빡임에 잠길 수 있음)
    PATIENCE_LIMIT: int = 20
    
    # 몇 프레임마다 얼굴 인식을 수행할지 (1이면 매 프레임, 숫자가 높으면 성능 향상)
    CHECK_INTERVAL: int = 3
    
    # 프로그램 창 이름
    WINDOW_NAME: str = "Smart Security Curtain"