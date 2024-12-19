# ft_transcendence/srcs/services/auth/Dockerfile

# Используем официальный образ Python в качестве базового
FROM python:3.9

# Используем метки для обозначения проекта.
# LABEL project=fastpong

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файл requirements.txt в рабочую директорию
COPY requirements.txt .

# Устанавливаем зависимости из requirements.txt
RUN pip install -r requirements.txt

# Копируем все файлы и директории в рабочую директорию
COPY . .

# # Копируем скрипт wait-for-it.sh в рабочую директорию
# COPY wait-for-it.sh .

# # Устанавливаем права на выполнение скрипта wait-for-it.sh
# RUN chmod +x wait-for-it.sh

# # Выполняем миграции базы данных
# RUN python manage.py migrate

# # Собираем статические файлы
# RUN python manage.py collectstatic --noinput

# Команда для запуска сервера Django
CMD ["gunicorn", "--bind", "0.0.0.0:8888", "auth_service.wsgi:application"]
