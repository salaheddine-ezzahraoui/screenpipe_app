FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 1112

CMD ["gunicorn", "--bind", "0.0.0.0:1112", "--workers", "2", "app:app"]
