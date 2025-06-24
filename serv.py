from flask import Flask, request
import face_recognition
import cv2
import numpy as np
import os
import time
import mediapipe as mp
import threading

app = Flask(__name__)

# Estado global
modo_reconhecimento = False
autenticado = False
pessoa_reconhecida = None

# Carrega rostos conhecidos
known_face_encodings = []
known_face_names = []

print("Carregando rostos da pasta 'faces/'...")
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

# Inicializa MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=True, max_num_hands=1, min_detection_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

@app.route('/upload', methods=['POST'])
def upload():
    global modo_reconhecimento, autenticado, pessoa_reconhecida

    # Converte imagem recebida
    file_bytes = request.data
    np_arr = np.frombuffer(file_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    if img is None:
        return "Erro ao decodificar imagem", 400

    # Fase de reconhecimento facial
    if not autenticado:
        if modo_reconhecimento:
            print(">> Tentando reconhecer rosto...")
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            faces = face_recognition.face_encodings(img_rgb)
            for face in faces:
                matches = face_recognition.compare_faces(known_face_encodings, face)
                if True in matches:
                    idx = matches.index(True)
                    nome = known_face_names[idx]
                    autenticado = True
                    modo_reconhecimento = False
                    pessoa_reconhecida = nome
                    print(">>> Rosto reconhecido!")
                    print(f">>> Bem-vindo, {nome}!")
                    print(">>> Modo contínuo ativado.")
                    return f"Reconhecido: {nome}"
            return "Nao reconhecido"
        else:
            return "Aguardando modo reconhecimento"

    # Já autenticado – contagem de dedos
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    resultado = hands.process(img_rgb)

    dedos = 0
    if resultado.multi_hand_landmarks:
        lm = resultado.multi_hand_landmarks[0]
        dedos = contar_dedos(lm)
        mp_drawing.draw_landmarks(img, lm, mp_hands.HAND_CONNECTIONS)

    print(f"Dedos detectados: {dedos}")
    return str(dedos)

@app.route('/check', methods=['GET'])
def check():
    return "OK" if autenticado else "WAIT"

def contar_dedos(landmarks):
    lm = landmarks.landmark
    dedos = 0
    for tip, pip in zip([8,12,16,20], [6,10,14,18]):
        if lm[tip].y < lm[pip].y:
            dedos += 1
    if lm[4].x > lm[2].x:
        dedos += 1
    return dedos

# Thread principal de controle por terminal
def entrada_terminal():
    global modo_reconhecimento, autenticado, pessoa_reconhecida
    while True:
        input("Pressione ENTER para iniciar reconhecimento facial...\n")
        if not autenticado:
            modo_reconhecimento = True
            print(">>> Modo reconhecimento ativado. Aguardando imagem da ESP32...\n")
        else:
            print(f">>> {pessoa_reconhecida} já autenticado. Para reiniciar, reinicie o servidor.\n")

# Inicialização
if __name__ == "__main__":
    threading.Thread(target=entrada_terminal, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)
