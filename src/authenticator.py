# authenticator.py
import face_recognition
import cv2
import os
import numpy as np

class FaceAuthenticator:
    """
    얼굴 인식 및 인증을 전담하는 클래스입니다.
    이미지 로드, 인코딩 변환, 얼굴 비교 기능을 수행합니다.
    """
    def __init__(self, config):
        self.config = config
        self.authorized_encoding = None # 주인 얼굴 데이터 저장소
        self._load_authorized_face()    # 시작하자마자 얼굴 학습 시작

    def _load_authorized_face(self):
        """설정된 이미지 파일에서 얼굴을 읽어와 인코딩(수치화)합니다."""
        if not os.path.exists(self.config.AUTH_IMAGE_FILE):
            print(f"[오류] {self.config.AUTH_IMAGE_FILE} 파일이 없습니다.")
            return

        try:
            # 파일을 이미지로 로드
            image = face_recognition.load_image_file(self.config.AUTH_IMAGE_FILE)
            # 얼굴 특징 추출 (128차원 벡터)
            encodings = face_recognition.face_encodings(image)
            
            if encodings:
                self.authorized_encoding = encodings[0]
                print(f"[시스템] 얼굴 학습 완료. (허용 오차: {self.config.TOLERANCE})")
            else:
                print("[오류] 사진에서 얼굴을 찾을 수 없습니다. 정면 사진을 사용해주세요.")
        except Exception as e:
            print(f"[오류] 얼굴 로딩 중 에러 발생: {e}")

    def verify_frame(self, frame):
        """
        카메라 프레임을 받아 주인이 맞는지 검사합니다.
        
        Returns:
            is_match (bool): 주인 여부
            distance (float): 얼굴 차이 점수 (낮을수록 닮음)
            status (str): 현재 상태 메시지
        """
        # 학습된 얼굴이 없으면 무조건 실패 처리
        if self.authorized_encoding is None:
            return False, 1.0, "학습 데이터 없음"

        # [최적화] 전체 이미지를 쓰면 느리므로 1/4 크기로 줄여서 검사
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        
        # [중요] OpenCV는 BGR(파랑,초록,빨강) 순서지만, face_recognition은 RGB를 씁니다.
        # 색상 순서를 바꿔줘야 정확도가 올라갑니다.
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        # 현재 화면에서 얼굴 위치 찾기
        face_locations = face_recognition.face_locations(rgb_small_frame)
        # 찾은 얼굴을 수치 데이터로 변환
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        # 얼굴이 하나도 안 보일 경우
        if not face_locations:
            return False, 1.0, "얼굴 없음"

        # 화면에 잡힌 얼굴들과 주인 얼굴 비교
        min_distance = 1.0
        is_match = False
        
        for face_encoding in face_encodings:
            # 주인 얼굴과 현재 얼굴의 거리(차이) 계산
            distance = face_recognition.face_distance([self.authorized_encoding], face_encoding)[0]
            
            # 가장 주인과 닮은 얼굴의 점수 저장
            if distance < min_distance:
                min_distance = distance
            
            # 오차가 허용치보다 작으면 주인으로 인정
            if distance < self.config.TOLERANCE:
                is_match = True
                break # 주인을 찾았으니 더 볼 필요 없음

        status = "주인님 확인" if is_match else f"외부인({min_distance:.2f})"
        return is_match, min_distance, status