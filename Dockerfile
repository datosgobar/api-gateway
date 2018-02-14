FROM python:3.6.4-alpine3.7

ARG requirements=requirements.txt

ENV BASE_DIR=/app/ \
    PYTHON_VENV_DIR=/app/venv/ \
    MEDIA_ROOT=/app/media/ \
    STATIC_ROOT=/app/static/ \
    APP_DIR=/app/code/ \
    APP_USER=webapp

RUN apk --no-cache add imagemagick zlib-dev jpeg-dev gcc build-base postgresql-dev && \
    mkdir $APP_DIR $MEDIA_ROOT $STATIC_ROOT -p && \
    addgroup -S $APP_USER && \
    adduser -D -H -S $APP_USER $APP_USER && \
    chown $APP_USER:$APP_USER -Rc $BASE_DIR

WORKDIR $APP_DIR
USER $APP_USER

COPY requirements requirements/
COPY requirements.txt manage.py $APP_DIR

RUN python -m venv $PYTHON_VENV_DIR && \
    source $PYTHON_VENV_DIR/bin/activate && \
    pip install --no-cache -r $requirements

COPY conf conf/
COPY api_management api_management/

EXPOSE 8080

CMD ${PYTHON_VENV_DIR}bin/python manage.py runserver 0.0.0.0:8080
