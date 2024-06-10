FROM python:3.9-slim

WORKDIR /app

COPY . /app

ENV PIP_ROOT_USER_ACTION=ignore

RUN python3 -m ensurepip

RUN python3 -m pip install --no-cache-dir -r requirements.txt

CMD ["python3", "main.py"]