FROM python:3.12-alpine
WORKDIR /app

RUN addgroup -g 1000 -S snake && adduser -u 1000 -S snake -G snake

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=snake:snake backend /app/backend

USER snake

EXPOSE 6500

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "6500"]