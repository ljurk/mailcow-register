FROM python:3.9-alpine

WORKDIR /opt/mailcow-registration
EXPOSE 5000

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt


ENV MAILCOW_HOST=https://mail.303v.cf \
    MAILCOW_API_PATH=/api/v1/ \
    API_TOKEN= \
    REGISTER_DOMAIN=303v.cf \
    REGISTER_QUOTA=1024 \
    REGISTER_DEFAULT_TOKEN_LENGTH=64 \
    REDIS_HOST=redis \
    REDIS_PORT=6379

COPY app.py .
COPY forms/ ./forms
COPY templates/ ./templates

CMD ["python", "app.py"]
