ARG PYTHON_VERSION

#
# Compile custom uwsgi for web image
#
FROM python:${PYTHON_VERSION}-slim-bookworm as uwsgi-compile
ENV _UWSGI_VERSION 2.0.23
RUN apt-get update && apt-get --no-install-recommends install -y build-essential wget && rm -rf /var/lib/apt/lists/*
RUN wget -O uwsgi-${_UWSGI_VERSION}.tar.gz https://github.com/unbit/uwsgi/archive/${_UWSGI_VERSION}.tar.gz \
  && tar zxvf uwsgi-*.tar.gz \
  && UWSGI_BIN_NAME=/uwsgi make -C uwsgi-${_UWSGI_VERSION} \
  && rm -Rf uwsgi-*



#
# Build poetry and export compiled dependecines as plain requirements.txt
#
FROM python:${PYTHON_VERSION}-slim-bookworm as deps-compile

WORKDIR /
COPY poetry.lock pyproject.toml /
# Version is taken from poetry.lock, assuming it is generated with up-to-date version of poetry
RUN pip install --no-cache-dir poetry==$(cat poetry.lock |head -n1|awk -v FS='(Poetry |and)' '{print $2}')
RUN poetry export --format=requirements.txt > requirements.txt


FROM python:${PYTHON_VERSION}-slim-bookworm as base
LABEL maintainer="fedor@borshev.com"
RUN apt-get update \
 && apt-get -y install wget \
 && rm -rf /var/lib/apt/lists/*

ENV BOT_ENV production
ENV DATABASE_URL sqlite:///db/selfmailbot.sqlite
VOLUME /db
RUN pip install --no-cache-dir --upgrade pip
COPY --from=deps-compile /requirements.txt /
RUN pip install --no-cache-dir -r requirements.txt
WORKDIR /
COPY src /src

USER nobody

#
# Bot image
#
FROM base as bot
HEALTHCHECK CMD wget -q -O /dev/null http://localhost:8000/healthcheck || exit 1
CMD python -m src.bot


#
# Background processing image
#
FROM base as worker
HEALTHCHECK CMD celery -A src.celery inspect ping -d celery@$HOSTNAME
CMD celery -A src.celery worker -c ${CONCURENCY:-4} -n "${celery}@%h" --max-tasks-per-child ${MAX_REQUESTS_PER_CHILD:-50} --time-limit ${TIME_LIMIT:-900}


#
# Web image
#
FROM base as web
COPY --from=uwsgi-compile /uwsgi /usr/local/bin/
HEALTHCHECK CMD wget -q -O /dev/null http://localhost:8000/healthcheck/ || exit 1
CMD uwsgi --master --http :8000 --module src.web:app

