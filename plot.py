import pandas as pd
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
import matplotlib.dates as mdates

# Загрузка данных из Excel
excel_path = "sensor_data_bed_tv.xlsx"  # Укажите путь к вашему файлу
df = pd.read_excel(excel_path)

# Конвертация timestamp в формат datetime
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Установка timestamp как индекса
df.set_index('timestamp', inplace=True)

# Ресемплирование с шагом в 15 минут и усреднение
resampled_df = df.resample('15min').mean()

# Сглаживание данных
for column in resampled_df.columns:
    resampled_df[column] = gaussian_filter1d(resampled_df[column], sigma=2)

# Построение графика с двумя осями
fig, ax1 = plt.subplots(figsize=(14, 8))

# Графики влажности (левая шкала)
ax1.plot(resampled_df.index, resampled_df['Спальня телевизор Humidity'], label="Влажность: Спальня (Датчик 1)", color='blue')
ax1.plot(resampled_df.index, resampled_df['Спальня кровать Humidity'], label="Влажность: Спальня (Датчик 2)", color='green')
ax1.set_xlabel("Timestamp")
ax1.set_ylabel("Humidity (%)", color='blue')
ax1.tick_params(axis='y', labelcolor='blue')
ax1.grid(True, which='major', linestyle='--', linewidth=0.5)  # Основная сетка

# Установка шага меток для временной оси раз в час
ax1.xaxis.set_major_locator(mdates.HourLocator(interval=1))  # Шаг в 1 час
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))  # Формат отображения времени

# Графики температуры (правая шкала)
ax2 = ax1.twinx()
ax2.plot(resampled_df.index, resampled_df['Спальня телевизор Temperature'], label="Температура: Спальня (Датчик 1)", color='red', linestyle='--')
ax2.plot(resampled_df.index, resampled_df['Спальня кровать Temperature'], label="Температура: Спальня (Датчик 2)", color='orange', linestyle='--')
ax2.set_ylabel("Temperature (°C)", color='red')
ax2.tick_params(axis='y', labelcolor='red')

# Настройка шкалы температуры
ax2.set_ylim(25.0, 42.5)  # Лимиты шкалы
ax2.set_yticks([round(x, 1) for x in list(range(25, 43))])  # Метки с шагом 0.5

# Легенда
lines_1, labels_1 = ax1.get_legend_handles_labels()
lines_2, labels_2 = ax2.get_legend_handles_labels()
plt.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left')

# Настройка графика
plt.title("Влажность и Температура: Спальня (15-минутный шаг, сглаженные данные)")
plt.xticks(rotation=45)
plt.tight_layout()

# Сохранение графика
plt.savefig("bed_tv_temp_humidity_custom_axis_graph.png")
plt.show()
