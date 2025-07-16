FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Install Playwright dependencies
RUN apt-get update && \
    apt-get install -y wget gnupg curl ca-certificates fonts-liberation libnss3 libatk-bridge2.0-0 libxss1 libasound2 libxcomposite1 libxrandr2 libgtk-3-0 libgbm1 libxdamage1 libxext6 libxfixes3 && \
    pip install playwright && playwright install chromium

COPY . .

EXPOSE 8000

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]