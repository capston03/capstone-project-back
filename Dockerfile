FROM python:3.8-slim

COPY ./src/ /app

RUN pip3 install flask

WORKDIR /app

CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0"]
