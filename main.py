import subprocess
import sqlite3
import time
import json
from datetime import datetime, timedelta

# IP адреса ваших датчиков
SENSORS = {
    "Спальня кровать": "http://192.168.1.107",
    "Спальня телевизор": "http://192.168.1.113",
}

# Инициализация базы данных SQLite
def init_db():
    conn = sqlite3.connect("sensor_data.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME,
                        location TEXT,
                        temperature REAL,
                        humidity REAL)''')
    conn.commit()
    conn.close()

# Сохранение данных в базу
def save_to_db(location, temperature, humidity):
    conn = sqlite3.connect("sensor_data.db")
    cursor = conn.cursor()
    adjusted_time = datetime.utcnow() + timedelta(hours=5)  # Добавляем 5 часов к UTC
    cursor.execute("INSERT INTO data (timestamp, location, temperature, humidity) VALUES (?, ?, ?, ?)", 
                   (adjusted_time.strftime('%Y-%m-%d %H:%M:%S'), location, temperature, humidity))
    conn.commit()
    conn.close()

# Получение данных через curl
def get_data(sensor_name, sensor_url):
    try:
        result = subprocess.run(
            ["curl", "-s", sensor_url],  # -s отключает прогресс-бар
            capture_output=True,
            text=True,
            timeout=10
        )
        response = result.stdout.strip()
        # Парсим JSON
        data = json.loads(response)
        return sensor_name, data["temperature"], data["humidity"]
    except json.JSONDecodeError:
        print(f"Failed to decode JSON response from {sensor_name}.")
    except subprocess.TimeoutExpired:
        print(f"Connection to {sensor_name} timed out.")
    except Exception as e:
        print(f"An error occurred with {sensor_name}: {e}")
    return sensor_name, None, None

# Основной цикл
if __name__ == "__main__":
    init_db()
    print("Starting data collection...")
    try:
        while True:
            for sensor_name, sensor_url in SENSORS.items():
                location, temp, hum = get_data(sensor_name, sensor_url)
                if temp is not None and hum is not None:
                    print(f"[{location}] Temperature: {temp}°C, Humidity: {hum}%")
                    save_to_db(location, temp, hum)
                else:
                    print(f"Failed to get data from {location}.")
            time.sleep(60)  # 1 минута между опросами всех датчиков
    except KeyboardInterrupt:
        print("Exiting data collection...")
