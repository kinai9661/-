FROM python:3.11-slim
LABEL "language"="python"
LABEL "framework"="gradio"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir \
gradio>=4.50.0,<5.0.0  \
yt-dlp>=2025.0.0  \
huggingface-hub>=0.19.0,<0.21.0  

COPY . .

EXPOSE 8080

CMD ["python", "app.py"]
