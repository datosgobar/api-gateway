FROM kong:0.13

ENV API_GATEWAY_PLUING_DIR=/api-gateway-httplog \
    API_GATEWAY_PLUING_BRANCH=master \
    KONG_CUSTOM_PLUGINS=api-gateway-httplog \
    KONG_PROXY_ACCESS_LOG=/dev/stdout \
    KONG_ADMIN_ACCESS_LOG=/dev/stdout \
    KONG_PROXY_ERROR_LOG=/dev/stderr \
    KONG_ADMIN_ERROR_LOG=/dev/stderr


RUN apk add --no-cache git && \
    git clone https://github.com/datosgobar/api-gateway-httplog.git $API_GATEWAY_PLUING_DIR && \
    luarocks install json-lua && \
    cd $API_GATEWAY_PLUING_DIR && luarocks make && \
    apk del --no-cache git
