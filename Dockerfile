FROM alpine:3.7

ARG requirements=requirements.txt

ENV TZ=America/Argentina/Buenos_Aires \
    BASE_DIR=/app/ \
    PYTHON_VENV_DIR=/app/venv/ \
    MEDIA_ROOT=/app/media/ \
    STATIC_ROOT=/app/static/ \
    APP_DIR=/app/code/ \
    APP_USER=webapp \
    DJANGO_SETTINGS_MODULE=conf.settings.production

WORKDIR $APP_DIR

COPY requirements/ requirements/
COPY requirements.txt manage.py $APP_DIR

RUN apk add --no-cache python3 imagemagick zlib-dev jpeg-dev build-base postgresql-dev && \
    apk add --no-cache git gcc python3-dev libc-dev --virtual build && \
    mkdir $APP_DIR $MEDIA_ROOT $STATIC_ROOT -p && \
    addgroup -S $APP_USER && \
    adduser -D -H -S $APP_USER $APP_USER && \
    chown $APP_USER:$APP_USER -Rc $BASE_DIR && \
    chmod 777 $MEDIA_ROOT && \
    python3 -m pip install --no-cache -r $requirements && \
    apk del --no-cache build

USER $APP_USER

COPY conf conf/
COPY api_management api_management/

EXPOSE 8080

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8080"]
