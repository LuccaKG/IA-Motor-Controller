
# 🤖 ESP32-CAM + Flask | Face Recognition + Finger Counting + Motor Control

This project integrates an **ESP32-CAM** with a **Flask server** to perform:

- 🔐 **Face recognition** for authentication.
- ✋ **Finger counting** using computer vision (MediaPipe).
- 🚗 **DC motor control** (L298N module) — the number of detected fingers determines the motor speed.

---

## 📜 Description

- The system starts in **face recognition mode**.
- Once an authorized face is detected, it switches to **finger counting mode**.
- The number of fingers shown controls the motor speed.
- The motor continues running until **zero fingers are detected 10 consecutive times**, preventing sudden stops due to false negatives.

---

## 🧠 Technologies and Libraries

### 🚩 ESP32-CAM (Arduino C++)
- Wi-Fi connection
- Image capture
- HTTP communication
- DC motor control with PWM (L298N module)

### 🐍 Python (Flask Server)
- **face_recognition** – Face recognition
- **MediaPipe** – Hand detection and finger counting
- **OpenCV (cv2)** – Image processing
- **NumPy** – Array handling
- **Flask** – HTTP server

---

## 🚀 Installation and Setup

### 📲 ESP32-CAM

1. Open Arduino IDE.
2. Install **ESP32 Board Support** via Board Manager.
3. Install libraries:
   - `WiFi.h`
   - `esp_camera.h`
   - `HTTPClient.h`
4. Edit the code to include your Wi-Fi credentials and server IP:

```cpp
const char* ssid = "<YOUR_WIFI_NAME>";
const char* password = "<YOUR_WIFI_PASSWORD>";
const char* serverURL = "http://<SERVER_IP>:5000/upload";
```

### 🔍 How to Get These Values

| Variable    | How to Obtain                                                                 |
| ------------| ------------------------------------------------------------------------------ |
| `<YOUR_WIFI_NAME>` | Your Wi-Fi name (SSID). If using mobile hotspot, check your phone's hotspot name. |
| `<YOUR_WIFI_PASSWORD>` | Your Wi-Fi password or mobile hotspot password.                        |
| `<SERVER_IP>` | Your computer's local IP address. Run `ipconfig` (Windows) or `ifconfig` (Linux/macOS) and look for your Wi-Fi IPv4 Address. Example: `192.168.1.100` |

> ⚠️ **Important:**  
> Make sure both the ESP32 and the Flask server are connected to the **same network** (either home Wi-Fi or mobile hotspot).

5. Upload the code to the ESP32-CAM.

---

### 💻 Flask Server (Python)

1. Create a virtual environment (optional but recommended):

```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On Linux/macOS
source venv/bin/activate
```

2. Install dependencies:

```bash
pip install flask face_recognition opencv-python mediapipe numpy
```

3. Create a folder named `faces` in the same directory as `serv.py`.
4. Add face images of authorized users in the `faces` folder. Use the filename format:

```
first_last.jpg
```

Example:
- `john_smith.jpg` → Name displayed: **John Smith**

5. Run the server:

```bash
python serv.py
```

---

## 📂 Project Structure

```
📁 Fingers-Recognizer/
├── faces/                            # Folder with authorized face images
│   ├── john_smith.jpg
│   └── mary_doe.png
├── Client/                           # ESP32-CAM code
│   └── Client.ino
├── serv.py                           # Flask server
├── README.md                         # This file
```

---

## 🔗 Server Endpoints

| Route        | Method | Description                                  |
| -------------|--------|----------------------------------------------|
| `/upload`    | POST   | Receives image from ESP32 (JPEG)             |
| `/check`     | GET    | Returns `OK` if authenticated, `WAIT` if not |

---

## ⚙️ System Workflow

1. Start the server and ESP32.
2. In the server terminal, press `ENTER` to activate **face recognition mode**.
3. Point the authorized face to the ESP32-CAM.
4. After authentication:
   - The server switches to **finger counting mode**.
   - The number of detected fingers controls the motor speed.

| Fingers | Motor Speed (PWM)         |
|---------|----------------------------|
| 1       | Slow                       |
| 5       | Fast                       |

5. The motor only stops after detecting **zero fingers 10 consecutive times**, preventing accidental stops.

---

## ⚡Schematic

![ESP32_1_DC_Motor_bb](https://github.com/user-attachments/assets/b9ff92eb-317b-4b2f-8250-81defeb029f0)

---

## 🎥 Demonstration

https://github.com/user-attachments/assets/f94a751c-20c3-4c6b-87f6-7b4729b535e2

**Note:** It was not possible to record a video of the motor in operation due to limitations in the recording setup. Additionally, the finger recognition is not performing at its full potential due to limitations of the camera and the frame rate at which the ESP32 transmits images to the server.

---
## 🚧 Important Notes

- ✅ Works on both Wi-Fi networks and mobile hotspots (as long as ESP32 and server are on the same network).
- ⚠️ No HTTP authentication implemented — avoid exposing to public networks.
- 🌞 Detection accuracy depends on lighting and camera positioning.

---

## 🏗️ Future Improvements

- 🔐 Add secure API authentication.
- 🌐 Create a web dashboard.
- ☁️ Enable cloud-based logging or control.

---

## ☕ License

This project is free to use and modify. If you use it, please give credit to this repository.

---

## ⭐ If you like this project, give it a star on GitHub! ⭐
