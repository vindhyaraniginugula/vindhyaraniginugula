#FROM python:3.11-slim
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .

#RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 80
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
