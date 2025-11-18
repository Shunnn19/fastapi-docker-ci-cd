FROM python:3.10

WORKDIR /app
COPY . .
RUN pip install fastapi uvicorn[standard] sqlalchemy "pydantic[email]"


EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
