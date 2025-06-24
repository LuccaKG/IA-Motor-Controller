#include <Arduino.h>
#include "esp_camera.h"
#include <WiFi.h>
#include <HTTPClient.h>

// ==== Wi-Fi ====
const char* ssid = "<YOUR_WIFI_NAME>";
const char* password = "<YOUR_WIFI_PASSWORD>";

// ==== IP do servidor Flask ====
const char* serverURL = "http://<SERVER_IP>:5000/upload";

// ==== Configuração da câmera AI Thinker ====
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27
#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

// ==== Motor A ====
int motor1Pin1 = 13;
int motor1Pin2 = 15;
int enable1Pin = 14;

// PWM properties
const int freq = 30000;
const int pwmChannel = 0;
const int pwmResolution  = 8;

// Controle de parada
int contadorZeros = 0;
int velocidadeAtual = 0;

// Variável para velocidade
int dutyCycle = 0;

void setup() {
  Serial.begin(9600);

  // Wi-Fi
  WiFi.begin(ssid, password);
  Serial.print("Conectando ao Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWi-Fi conectado!");
  Serial.print("IP local: ");
  Serial.println(WiFi.localIP());

  // Configura motor
  pinMode(motor1Pin1, OUTPUT);
  pinMode(motor1Pin2, OUTPUT);
  pinMode(enable1Pin, OUTPUT);
  ledcAttachChannel(enable1Pin, freq, pwmResolution, pwmChannel);

  // Configura câmera
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  config.frame_size = FRAMESIZE_VGA;
  config.jpeg_quality = 15;
  config.fb_count = 1;

  if (esp_camera_init(&config) != ESP_OK) {
    Serial.println("Erro ao inicializar a câmera");
    while(true) delay(1000);
  }

  pararMotor();
}

void loop() {
  camera_fb_t *fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("Falha ao capturar imagem");
    delay(2000);
    return;
  }

  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverURL);
    http.addHeader("Content-Type", "image/jpeg");

    int httpResponseCode = http.POST(fb->buf, fb->len);
    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.print("Servidor respondeu: ");
      Serial.println(response);

      int dedos = response.toInt();
      if (dedos > 0) {
        contadorZeros = 0;  // Zera contador de zeros
        velocidadeAtual = mapearDedosParaVelocidade(dedos);

        Serial.print("Dedos detectados: ");
        Serial.println(dedos);
        Serial.print("Velocidade PWM: ");
        Serial.println(velocidadeAtual);

        moverFrente(velocidadeAtual);
      } 
      else {
        contadorZeros++;
        Serial.print("Zero detectado. Contador: ");
        Serial.println(contadorZeros);

        if (contadorZeros >= 10) {
          pararMotor();
          velocidadeAtual = 0;
          Serial.println("Parando motor após 10 zeros consecutivos.");
        } 
        else {
          moverFrente(velocidadeAtual);
          Serial.println("Mantendo última velocidade.");
        }
      }
    } else {
      Serial.print("Erro HTTP: ");
      Serial.println(httpResponseCode);
      pararMotor();
    }
    http.end();
  } else {
    Serial.println("Wi-Fi desconectado");
    pararMotor();
  }

  esp_camera_fb_return(fb);
  delay(2000);
}

void moverFrente(int velocidade) {
  digitalWrite(motor1Pin1, HIGH);
  digitalWrite(motor1Pin2, LOW);
  ledcWrite(enable1Pin, velocidade);
}

void pararMotor() {
  digitalWrite(motor1Pin1, LOW);
  digitalWrite(motor1Pin2, LOW);
  ledcWrite(enable1Pin, 0);
}

int mapearDedosParaVelocidade(int dedos) {
  if (dedos < 1) dedos = 1;
  if (dedos > 5) dedos = 5;

  int dutyMin = 80;
  int dutyMax = 255;

  return map(dedos, 1, 5, dutyMin, dutyMax);
}
