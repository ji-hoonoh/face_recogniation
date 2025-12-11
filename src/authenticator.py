# authenticator.py
import face_recognition
import pickle
import os
import cv2
import numpy as np

class FaceAuthenticator:
    def __init__(self, config):
        self.config = config
        self.data = {"encodings": [], "names": []}
        self._load_encodings()

    def _load_encodings(self):
        # (이전과 동일하므로 생략)
        if not os.path.exists(self.config.ENCODINGS_SAVE_FILE):
            print(f"[경고] {self.config.ENCODINGS_SAVE_FILE} 파일이 없습니다.")
            return
        with open(self.config.ENCODINGS_SAVE_FILE, "rb") as f:
            self.data = pickle.load(f)

    def process_frame(self, frame):
        """
        Returns:
            results (list): 얼굴 박스 정보들
            auth_count (int): 인식된 주인 수
            unknown_count (int): 인식된 외부인 수
        """
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_small, model=self.config.MODEL)
        face_encodings = face_recognition.face_encodings(rgb_small, face_locations)

        results = []
        auth_count = 0      # 주인님 숫자
        unknown_count = 0   # 외부인 숫자

        for loc, encoding in zip(face_locations, face_encodings):
            top, right, bottom, left = loc
            pos = (top*4, right*4, bottom*4, left*4)
            
            name = "Unknown"
            is_authorized = False
            distance = 1.0

            if self.data["encodings"]:
                distances = face_recognition.face_distance(self.data["encodings"], encoding)
                min_distance_idx = np.argmin(distances)
                min_distance = distances[min_distance_idx]
                distance = min_distance

                if min_distance < self.config.TOLERANCE:
                    name = self.data["names"][min_distance_idx]
                    is_authorized = True
            
            # === [수정된 부분] 숫자 카운팅 ===
            if is_authorized:
                auth_count += 1
            else:
                unknown_count += 1  # 외부인 발견!

            results.append({
                "pos": pos,
                "name": f"{name} ({distance:.2f})",
                "authorized": is_authorized
            })

        # True/False 대신 구체적인 숫자를 반환합니다.
        return results, auth_count, unknown_count