# Используем официальный Python образ
#Use slim version for a smaller image
FROM python:3.11

# Устанавливаем рабочую директорию
WORKDIR /usr/src/app

# Копируем зависимости (например, requirements.txt)
COPY requirements.txt ./

# Устанавливаем зависимости
RUN pip install --trusted-host pypi.python.org --no-cache-dir -r requirements.txt

RUN apt-get update && \
    apt-get install -y wget unzip && \
    wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt-get install -y ./google-chrome-stable_current_amd64.deb && \
    rm google-chrome-stable_current_amd64.deb && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Копируем весь код приложения
COPY . .

# Запускаем приложение
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
#CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "app.main:app", "--bind", "0.0.0.0:8000"]