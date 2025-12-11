# ui.py
import cv2
import numpy as np

class SecurityUI:
    """
    화면 출력(Display)을 전담하는 클래스입니다.
    일반 모드와 잠금 모드 화면을 그리고, 윈도우 창 속성을 제어합니다.
    """
    def __init__(self, config):
        self.config = config
        # OpenCV 윈도우 생성 (크기 조절 가능 모드)
        cv2.namedWindow(self.config.WINDOW_NAME, cv2.WINDOW_NORMAL)

    def set_fullscreen(self, enable: bool):
        """윈도우를 전체화면으로 만들거나 원래대로 돌립니다."""
        if enable:
            cv2.setWindowProperty(self.config.WINDOW_NAME, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            # 창을 항상 최상위로 올림 (다른 작업 못하게)
            cv2.setWindowProperty(self.config.WINDOW_NAME, cv2.WND_PROP_TOPMOST, 1)
        else:
            cv2.setWindowProperty(self.config.WINDOW_NAME, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(self.config.WINDOW_NAME, 320, 240) # 작은 크기로 복귀

    def _create_lock_screen(self, width, height):
        """검은색 보안 배경 이미지를 생성합니다."""
        # 검은색 배경 생성 (Height, Width, 3채널)
        screen = np.full((height, width, 3), (0, 0, 0), dtype=np.uint8)
        
        # 경고 문구 작성
        cv2.putText(screen, "SECURITY MODE", (width//2 - 180, height // 2 - 20), 
                    cv2.FONT_HERSHEY_DUPLEX, 1.2, (0, 0, 255), 2)
        cv2.putText(screen, "Look at camera to unlock", (width//2 - 150, height // 2 + 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (150, 150, 150), 1)
        return screen

    def draw_frame(self, frame, is_locked):
        """
        현재 상태(잠금/해제)에 따라 적절한 화면을 그려서 보여줍니다.
        """
        h, w, _ = frame.shape

        if is_locked:
            # 1. 잠금 모드: 검은 화면 + 구석에 작은 카메라
            display = self._create_lock_screen(w, h)
            
            # 카메라 화면을 작게 줄여서 우측 하단에 배치
            small_cam = cv2.resize(frame, (0,0), fx=0.3, fy=0.3)
            # 좌표 계산: 전체 높이 - 작은화면 높이
            display[h-small_cam.shape[0]:h, w-small_cam.shape[1]:w] = small_cam
        else:
            # 2. 해제 모드: 카메라 화면 + 초록색 테두리
            display = cv2.resize(frame, (320, 240))
            cv2.rectangle(display, (0,0), (320,240), (0,255,0), 5)

        # 화면 출력
        cv2.imshow(self.config.WINDOW_NAME, display)