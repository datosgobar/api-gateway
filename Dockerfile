FROM alpine:3.7

ARG requirements=requirements.txt

ENV BASE_DIR=/app/ \
    PYTHON_VENV_DIR=/app/venv/ \
    MEDIA_ROOT=/app/media/ \
    STATIC_ROOT=/app/static/ \
    APP_DIR=/app/code/ \
    APP_USER=webapp \
    DJANGO_SETTINGS_MODULE=conf.settings.production

WORKDIR $APP_DIR

COPY requirements/ requirements/
COPY requirements.txt manage.py $APP_DIR

RUN apk add --no-cache python3 imagemagick zlib-dev jpeg-dev gcc build-base postgresql-dev && \
    mkdir $APP_DIR $MEDIA_ROOT $STATIC_ROOT -p && \
    addgroup -S $APP_USER && \
    adduser -D -H -S $APP_USER $APP_USER && \
    chown $APP_USER:$APP_USER -Rc $BASE_DIR && \
    apk add --no-cache git gcc python3-dev libc-dev --virtual build && \
    python3 -m pip install --no-cache -r $requirements && \
    apk del --no-cache build

USER $APP_USER

COPY conf conf/
COPY api_management api_management/

EXPOSE 8080

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8080"]
