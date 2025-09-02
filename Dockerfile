FROM python:3.11-slim

# ffmpeg for merging mp4
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

# cookies mount point
RUN mkdir -p /app/data

ENV PORT=8000
EXPOSE 8000
CMD ["gunicorn","--workers","2","--threads","4","--timeout","300","app:app","--bind","0.0.0.0:8000"]
