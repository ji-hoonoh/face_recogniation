# main.py
import cv2
import os
from config import Config
from authenticator import FaceAuthenticator
from ui import SecurityUI

class SecuritySystem:
    """
    시스템 전체의 상태(State)를 관리하고 각 모듈을 조율하는 메인 컨트롤러입니다.
    """
    def __init__(self):
        # 1. 설정 로드
        self.config = Config()
        
        # 2. 각 전문가(모듈) 고용
        self.auth = FaceAuthenticator(self.config)
        self.ui = SecurityUI(self.config)
        
        # 3. 상태 변수 초기화
        self.cap = cv2.VideoCapture(0) # 카메라 연결
        self.is_locked = True          # 초기 상태는 '잠금'
        self.fail_count = 0            # 실패 횟수 누적
        
        # 비밀 엑셀 파일 열기 (파일이 있을 경우)
        if os.path.exists(self.config.SECRET_FILE):
            try:
                os.startfile(self.config.SECRET_FILE)
            except AttributeError:
                # mac/linux 호환성을 위해 예외처리 (윈도우가 아닐 경우 startfile 없음)
                pass

    def run(self):
        """프로그램의 메인 루프(반복문)입니다."""
        print("=== [시스템 가동] 실시간 보안 감시 시작 ===")
        frame_count = 0

        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("[오류] 카메라를 읽을 수 없습니다.")
                break
            
            frame_count += 1

            # === [핵심 로직] 주기적으로 얼굴 검사 수행 ===
            # 성능을 위해 매 프레임 검사하지 않고 CHECK_INTERVAL 마다 검사
            if frame_count % self.config.CHECK_INTERVAL == 0:
                is_owner, distance, msg = self.auth.verify_frame(frame)
                self._update_security_status(is_owner, distance, msg)

            # === [화면 갱신] UI 모듈에게 그림 그리기 요청 ===
            self.ui.draw_frame(frame, self.is_locked)
            
            # 'q' 키를 누르면 종료
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # 종료 시 자원 해제
        self.cap.release()
        cv2.destroyAllWindows()

    def _update_security_status(self, is_owner, distance, msg):
        """얼굴 인식 결과에 따라 잠금/해제 상태를 결정합니다."""
        
        if is_owner:
            # 주인이 확인되면 실패 카운트 초기화
            self.fail_count = 0
            
            # 잠겨있었다면 -> 해제
            if self.is_locked:
                print(f"\n[해제] 어서오세요! (오차: {distance:.2f})")
                self.ui.set_fullscreen(False) # 전체화면 해제
                self.is_locked = False
            else:
                # 이미 해제 상태라면 로그만 살짝 출력 (줄바꿈 없이)
                print(f"\r[O] 감시 중... 주인 확인됨 ({distance:.2f})   ", end="")
        
        else:
            # 주인이 아니면 실패 카운트 증가
            self.fail_count += 1
            print(f"\r[X] 경고! 인식 실패 ({self.fail_count}/{self.config.PATIENCE_LIMIT}) - {msg}    ", end="")
            
            # 인내심 한계를 넘었고, 현재 잠겨있지 않다면 -> 잠금!
            if self.fail_count > self.config.PATIENCE_LIMIT and not self.is_locked:
                print("\n\n[!!!] 보안 위협 감지! 시스템 잠금 발동! [!!!]\n")
                self.ui.set_fullscreen(True) # 전체화면 설정
                self.is_locked = True

if __name__ == "__main__":
    # 메인 실행부
    system = SecuritySystem()
    system.run()