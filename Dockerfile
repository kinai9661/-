FROM python:3.11-slim
LABEL "language"="python"
LABEL "framework"="gradio"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir \
gradio==4.38.1 \  
huggingface_hub==0.23.5 \  
yt-dlp>=2025.0.0 \  
requests>=2.28.0 \ 
COPY . .

EXPOSE 8080

CMD ["python", "app.py"]
