FROM python:3.13

# Устанавливаем рабочую директорию
WORKDIR /app

# Скопируем список зависимостей и установим их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Скопируем весь код внутрь контейнера
COPY . .

# Запустим uvicorn, FastAPI-приложение "main:app"
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9000"]
