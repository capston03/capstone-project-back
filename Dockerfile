FROM python:3.8-slim
COPY src /app
WORKDIR /app
RUN ls -al /app/*
RUN pip install -r docker/requirements.txt
CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0"]
