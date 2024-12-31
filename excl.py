import sqlite3
import pandas as pd

# Подключение к базе данных SQLite
db_path = "sensor_data.db"  # Укажите путь к вашей базе данных
excel_path = "sensor_data_bed_tv.xlsx"  # Укажите путь для сохранения файла

conn = sqlite3.connect(db_path)

# SQL-запрос
query = """
SELECT timestamp, location, temperature, humidity
FROM data
WHERE location IN ('Спальня кровать', 'Спальня телевизор')
"""
df = pd.read_sql_query(query, conn)

# Группировка данных
reshaped_data = []
timestamps = df['timestamp'].unique()

for ts in timestamps:
    subset = df[df['timestamp'] == ts]
    if len(subset['location'].unique()) == 2:  # Проверка двух локаций
        reshaped_row = {'timestamp': ts}
        for _, row in subset.iterrows():
            loc = row['location']
            reshaped_row[f"{loc} Temperature"] = row['temperature']
            reshaped_row[f"{loc} Humidity"] = row['humidity']
        reshaped_data.append(reshaped_row)

reshaped_df = pd.DataFrame(reshaped_data)

# Сохранение данных в Excel
reshaped_df.to_excel(excel_path, index=False)
conn.close()

print(f"Данные сохранены в файл: {excel_path}")
