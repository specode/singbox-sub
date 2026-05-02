FROM nginx:1.27-alpine

RUN mkdir -p /usr/share/nginx/empty /srv/sub-configs /srv/singbox-configs
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY configs/ /srv/sub-configs/
COPY singbox-configs/ /srv/singbox-configs/

EXPOSE 80
