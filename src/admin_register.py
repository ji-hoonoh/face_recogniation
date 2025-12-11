# admin_register.py
import face_recognition
import pickle
import os
import cv2
from config import Config

def register_faces():
    conf = Config()
    
    # 1. 사진 폴더가 없으면 생성
    if not os.path.exists(conf.AUTH_FACES_DIR):
        os.makedirs(conf.AUTH_FACES_DIR)
        print(f"[알림] '{conf.AUTH_FACES_DIR}' 폴더를 생성했습니다.")
        print(f"이 폴더 안에 승인할 사람들의 사진(jpg, png)을 넣어주세요.")
        return

    known_encodings = []
    known_names = []

    # 2. 폴더 내의 이미지 파일들을 스캔
    print(f"[시스템] '{conf.AUTH_FACES_DIR}' 폴더에서 얼굴 학습을 시작합니다...")
    
    for filename in os.listdir(conf.AUTH_FACES_DIR):
        if not filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            continue

        image_path = os.path.join(conf.AUTH_FACES_DIR, filename)
        name = os.path.splitext(filename)[0] # 파일명(확장자 제외)을 이름으로 사용

        try:
            # 이미지 로드 (OpenCV로 읽어서 RGB 변환이 더 안정적일 때가 많음)
            image = face_recognition.load_image_file(image_path)
            
            # 얼굴 찾기
            boxes = face_recognition.face_locations(image, model=conf.MODEL)
            encodings = face_recognition.face_encodings(image, boxes)

            if len(encodings) > 0:
                # 첫 번째 발견된 얼굴을 등록
                known_encodings.append(encodings[0])
                known_names.append(name)
                print(f"  [+] 등록 완료: {name}")
            else:
                print(f"  [!] 얼굴 감지 실패: {filename} (정면 사진을 써주세요)")

        except Exception as e:
            print(f"  [Error] 처리 중 오류 발생 ({filename}): {e}")

    # 3. 데이터 저장 (Pickle)
    data = {"encodings": known_encodings, "names": known_names}
    
    with open(conf.ENCODINGS_SAVE_FILE, "wb") as f:
        pickle.dump(data, f)
    
    print(f"\n[완료] 총 {len(known_names)}명의 얼굴 데이터가 '{conf.ENCODINGS_SAVE_FILE}'에 저장되었습니다.")

if __name__ == "__main__":
    register_faces()