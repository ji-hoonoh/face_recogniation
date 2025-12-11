# main.py
import cv2
import os
from config import Config
from authenticator import FaceAuthenticator
from ui import SecurityUI

class SecuritySystem:
    def __init__(self):
        self.config = Config()
        self.auth = FaceAuthenticator(self.config)
        self.ui = SecurityUI(self.config)
        self.cap = cv2.VideoCapture(0)
        
        self.is_locked = True
        self.fail_count = 0
        
        self.last_results = []
        # 저장 변수 변경 (숫자를 기억)
        self.last_auth_count = 0
        self.last_unknown_count = 0

        if os.path.exists(self.config.SECRET_FILE):
             try: os.startfile(self.config.SECRET_FILE)
             except: pass

    def run(self):
        frame_count = 0
        print("=== 보안 시스템 시작 ===")

        while True:
            ret, frame = self.cap.read()
            if not ret: break
            frame_count += 1

            # === 주기적 검사 ===
            if frame_count % self.config.CHECK_INTERVAL == 0:
                # 결과와 숫자를 받아옴
                results, auth_count, unknown_count = self.auth.process_frame(frame)
                
                self.last_results = results
                self.last_auth_count = auth_count
                self.last_unknown_count = unknown_count

                # === [핵심 로직 변경] ===
                if unknown_count > 0:
                    # 1. 외부인이 보이면 즉시 실패 카운트 증가 (심지어 주인이 옆에 있어도!)
                    self.fail_count += 1
                    print(f"\r[경고] 외부인 감지! ({self.fail_count}/{self.config.PATIENCE_LIMIT})", end="")

                elif auth_count > 0:
                    # 2. 외부인은 없고, 주인만 있다 -> 통과
                    self.fail_count = 0
                    if self.is_locked:
                        print(f"\n[해제] 환영합니다.")
                        self.ui.set_fullscreen(False)
                        self.is_locked = False
                
                else:
                    # 3. 아무도 없다 -> 실패 카운트 증가 (자리를 비움)
                    self.fail_count += 1
                    print(f"\r[대기] 사용자 부재 ({self.fail_count}/{self.config.PATIENCE_LIMIT})", end="")

                # 실패가 한계치를 넘으면 잠금
                if self.fail_count > self.config.PATIENCE_LIMIT and not self.is_locked:
                    print("\n[잠금] 보안 모드 전환")
                    self.ui.set_fullscreen(True)
                    self.is_locked = True

            # 화면 그리기 (주기적 검사 결과 사용)
            self.ui.update_display(frame, self.last_results, self.is_locked)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    SecuritySystem().run()