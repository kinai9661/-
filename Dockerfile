FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir \
    gradio==4.38.1 \
    yt-dlp>=2025.0.0

COPY . .

EXPOSE 7860

CMD ["python", "app.py"]
