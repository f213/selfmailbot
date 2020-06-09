FROM python:3.7-slim
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && \
  apt-get --no-install-recommends --assume-yes install build-essential
RUN pip install uwsgi

COPY . /srv
WORKDIR /