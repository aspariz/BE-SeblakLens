FROM python:3.9-slim

# Atur direktori kerja di dalam container
WORKDIR /app

# Salin kebutuhan library dan instal
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Salin seluruh kode backend
COPY . .

# Jalankan Flask pada port 7860 (Port wajib untuk Hugging Face)
EXPOSE 7860
ENV PORT=7860

CMD ["python", "server.py"]