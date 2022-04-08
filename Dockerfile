FROM python:3.8-slim
COPY src /app
COPY docker /docker
RUN pip3 install -r docker/requirements.txt
WORKDIR /app

CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0"]
