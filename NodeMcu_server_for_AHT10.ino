#include <ESP8266WiFi.h>
#include <Adafruit_AHTX0.h>

// Настройки Wi-Fi
const char* ssid = "";         // Имя вашей Wi-Fi сети
const char* password = "";   // Пароль Wi-Fi сети

// Создание объекта для работы с AHT10
Adafruit_AHTX0 aht;

// Настройки веб-сервера
WiFiServer server(80);

// Переменная для отслеживания состояния сенсора
bool sensor_connected = false;

void setup() {
  Serial.begin(9600);
  Serial.println("Starting NodeMCU...");

  // Подключение к Wi-Fi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("\nConnected to Wi-Fi!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  // Запуск веб-сервера
  server.begin();

  // Инициализация AHT10
  if (!aht.begin()) {
    Serial.println("AHT10 sensor not found. Running in degraded mode.");
    sensor_connected = false;
  } else {
    Serial.println("AHT10 sensor initialized successfully.");
    sensor_connected = true;
  }
}

void loop() {
  // Проверка подключения клиента
  WiFiClient client = server.available();
  if (!client) {
    return;
  }

  Serial.println("New client connected");
  client.setTimeout(5); // Таймаут на чтение данных

  // Чтение HTTP-запроса клиента
  String request = client.readStringUntil('\r');
  client.flush();
  Serial.println("Client request:");
  Serial.println(request);

  // Переменные для хранения данных
  float temp = 0.0;
  float hum = 0.0;

  // Считывание данных с AHT10 (если подключён)
  if (sensor_connected) {
    sensors_event_t humidity, tempEvent;
    aht.getEvent(&humidity, &tempEvent); // Получение данных с датчика

    temp = tempEvent.temperature;
    hum = humidity.relative_humidity;

    // Проверка на корректность данных
    if (isnan(temp) || isnan(hum)) {
      Serial.println("Failed to read from AHT10 sensor!");
      temp = 0.0;
      hum = 0.0;
    }
  } else {
    Serial.println("Sensor not connected. Returning default values.");
  }

  // Формирование JSON-ответа
  String response = "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n";
  response += "{\"sensor_connected\":";
  response += sensor_connected ? "true" : "false";
  response += ",\"temperature\":";
  response += String(temp, 2); // Два знака после запятой
  response += ",\"humidity\":";
  response += String(hum, 2);
  response += "}";

  // Отправка ответа клиенту
  client.print(response);
  Serial.println("Response sent");

  // Закрытие соединения
  client.stop();
  Serial.println("Client disconnected");
}
