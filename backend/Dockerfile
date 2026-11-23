FROM python:3.12-alpine
WORKDIR /app

COPY requirements.txt /app/
RUN pip install -r requirements.txt

COPY backend/ /app/backend

EXPOSE 6500

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "6500"]