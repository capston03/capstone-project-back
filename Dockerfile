FROM python:3.11-rc-bullseye
COPY src /app
COPY docker /docker
RUN pip3 install -r docker/requirements.txt
RUN python3 --version
WORKDIR /app

CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0"]