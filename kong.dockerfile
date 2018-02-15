FROM kong:0.11

RUN yum install git -y

COPY deploy/roles/kong/files/httplog2-kong /httplog2-kong

ENV KONG_CUSTOM_PLUGINS=httplog2

RUN luarocks install json-lua && \
    cd /httplog2-kong && luarocks make

