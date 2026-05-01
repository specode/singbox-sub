FROM nginx:1.27-alpine

RUN mkdir -p /usr/share/nginx/empty /srv/sub-configs
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY configs/ /srv/sub-configs/

EXPOSE 80
