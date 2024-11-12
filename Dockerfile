# Установка базового образа
FROM python:3.9

# Установка рабочей директории внутри контейнера
WORKDIR /app

# Копирование requirements.txt и установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование api.py внутрь контейнера
# COPY api/init_minio_and_dvc.sh .
COPY api/api.py .
COPY api/models.py .
COPY api/requests.py .
COPY api/utils.py .

# Запуск api.py
CMD python api.py
