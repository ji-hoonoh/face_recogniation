# config.py
from dataclasses import dataclass

@dataclass
class Config:
    # === 경로 설정 ===
    # 주인님들 사진이 들어있는 폴더
    AUTH_FACES_DIR: str = "auth_faces" 
    # 학습된 얼굴 데이터가 저장될 파일 (확장자 pickle)
    ENCODINGS_SAVE_FILE: str = "encodings.pickle"
    SECRET_FILE: str = "secret.xlsx"
    
    # === 인식 설정 ===
    TOLERANCE: float = 0.4  # 엄격함 정도 (낮을수록 엄격)
    MODEL: str = "hog"       # "hog"(빠름/일반) 또는 "cnn"(느림/정확-GPU필요)
    
    # === 시스템 설정 ===
    PATIENCE_LIMIT: int = 2 #n번의 실패를 하면 화면 전환 회수
    CHECK_INTERVAL: int = 5  # 5프레임마다 인식 수행
    WINDOW_NAME: str = "Smart Security System"