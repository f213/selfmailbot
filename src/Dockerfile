FROM python:3.6-slim
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . /srv
WORKDIR /