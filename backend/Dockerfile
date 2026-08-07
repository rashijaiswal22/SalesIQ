FROM python:3.10-slim

WORKDIR /app


ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get clean && \
    apt-get update -o Acquire::Retries=3 && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
