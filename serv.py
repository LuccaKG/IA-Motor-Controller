from flask import Flask, request
import face_recognition
import cv2
import numpy as np
import os
import time
import mediapipe as mp
import threading

app = Flask(__name__)

# Global state
recognition_mode = False
authenticated = False
recognized_person = None

# Load known faces
known_face_encodings = []
known_face_names = []

print("Loading faces from 'faces/' folder...")
for filename in os.listdir("faces"):
    if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        path = os.path.join("faces", filename)
        img = face_recognition.load_image_file(path)
        enc = face_recognition.face_encodings(img)
        if enc:
            known_face_encodings.append(enc[0])
            name = os.path.splitext(filename)[0].replace("_", " ").title()
            known_face_names.append(name)
            print(f" - {name}")

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=True, max_num_hands=1, min_detection_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

@app.route('/upload', methods=['POST'])
def upload():
    global recognition_mode, authenticated, recognized_person

    # Convert received image
    file_bytes = request.data
    np_arr = np.frombuffer(file_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    if img is None:
        return "Error decoding image", 400

    # Facial recognition phase
    if not authenticated:
        if recognition_mode:
            print(">> Trying to recognize face...")
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            faces = face_recognition.face_encodings(img_rgb)
            for face in faces:
                matches = face_recognition.compare_faces(known_face_encodings, face)
                if True in matches:
                    idx = matches.index(True)
                    name = known_face_names[idx]
                    authenticated = True
                    recognition_mode = False
                    recognized_person = name
                    print(">>> Face recognized!")
                    print(f">>> Welcome, {name}!")
                    print(">>> Continuous mode activated.")
                    return f"Recognized: {name}"
            return "Not recognized"
        else:
            return "Waiting for recognition mode"

    # Already authenticated – finger counting
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result = hands.process(img_rgb)

    fingers = 0
    if result.multi_hand_landmarks:
        lm = result.multi_hand_landmarks[0]
        fingers = count_fingers(lm)
        mp_drawing.draw_landmarks(img, lm, mp_hands.HAND_CONNECTIONS)

    print(f"Fingers detected: {fingers}")
    return str(fingers)

@app.route('/check', methods=['GET'])
def check():
    return "OK" if authenticated else "WAIT"

def count_fingers(landmarks):
    lm = landmarks.landmark
    fingers = 0
    for tip, pip in zip([8, 12, 16, 20], [6, 10, 14, 18]):
        if lm[tip].y < lm[pip].y:
            fingers += 1
    if lm[4].x > lm[2].x:
        fingers += 1
    return fingers

# Terminal thread for manual control
def terminal_input():
    global recognition_mode, authenticated, recognized_person
    while True:
        input("Press ENTER to start face recognition...\n")
        if not authenticated:
            recognition_mode = True
            print(">>> Recognition mode activated. Waiting for ESP32 image...\n")
        else:
            print(f">>> {recognized_person} already authenticated. To restart, reboot the server.\n")

# Initialization
if __name__ == "__main__":
    threading.Thread(target=terminal_input, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)
