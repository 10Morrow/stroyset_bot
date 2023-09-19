FROM python:3.9.2
WORKDIR /app
COPY . .
RUN pip3 install -r requirements.txt
RUN chmod 755 .


# Команда для запуска бота
CMD ["python3", "bot.py"]