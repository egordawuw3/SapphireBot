FROM python:3.9-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    python3-dev \
    portaudio19-dev \
    build-essential \
    libportaudio2 \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Копирование файлов проекта
COPY requirements.txt .

# Установка Python зависимостей пошагово
RUN pip install --no-cache-dir wheel setuptools
RUN pip install --no-cache-dir PyNaCl
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]