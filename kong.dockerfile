FROM kong:0.12

ENV API_GATEWAY_PLUING_DIR=/api-gateway-httplog

RUN yum install git -y

RUN git clone https://github.com/datosgobar/api-gateway-httplog.git $API_GATEWAY_PLUING_DIR

ENV KONG_CUSTOM_PLUGINS=api-gateway-httplog

RUN luarocks install json-lua && \
    cd $API_GATEWAY_PLUING_DIR && luarocks make

