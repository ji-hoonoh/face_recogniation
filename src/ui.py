# ui.py
import cv2
import numpy as np

class SecurityUI:
    def __init__(self, config):
        self.config = config
        cv2.namedWindow(self.config.WINDOW_NAME, cv2.WINDOW_NORMAL)
        self.green = (0, 255, 0)
        self.red = (0, 0, 255)

    def set_fullscreen(self, enable: bool):
        if enable:
            cv2.setWindowProperty(self.config.WINDOW_NAME, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            cv2.setWindowProperty(self.config.WINDOW_NAME, cv2.WND_PROP_TOPMOST, 1)
        else:
            cv2.setWindowProperty(self.config.WINDOW_NAME, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(self.config.WINDOW_NAME, 640, 480)

    def _draw_lock_screen(self, w, h):
        screen = np.full((h, w, 3), (0, 0, 0), dtype=np.uint8)
        cv2.putText(screen, "LOCKED", (w//2 - 100, h//2), cv2.FONT_HERSHEY_DUPLEX, 1.5, self.red, 2)
        return screen

    def update_display(self, frame, face_results, is_locked):
        """
        frame: 카메라 원본 이미지
        face_results: 얼굴 위치와 정보가 담긴 리스트
        is_locked: 현재 잠금 상태
        """
        display = frame.copy()
        h, w, _ = display.shape

        # === 1. 얼굴 박스 그리기 (잠금 여부 상관없이 항상 표시 or 잠금때만 표시 선택 가능) ===
        if not is_locked: # 해제 상태일 때 얼굴 박스 보여주기
            for face in face_results:
                top, right, bottom, left = face['pos']
                color = self.green if face['authorized'] else self.red
                
                # 박스 그리기
                cv2.rectangle(display, (left, top), (right, bottom), color, 2)
                
                # 이름(거리) 출력
                cv2.putText(display, face['name'], (left, top - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

        # === 2. 잠금 화면 처리 ===
        if is_locked:
            lock_bg = self._draw_lock_screen(w, h)
            # 잠금 화면 우측 하단에 카메라 화면 작게 띄우기 (PIP)
            small = cv2.resize(display, (0,0), fx=0.3, fy=0.3)
            sh, sw, _ = small.shape
            lock_bg[h-sh:h, w-sw:w] = small
            display = lock_bg
        else:
            # 해제 상태일 때 전체 테두리
            cv2.rectangle(display, (0,0), (w,h), self.green, 5)

        cv2.imshow(self.config.WINDOW_NAME, display)