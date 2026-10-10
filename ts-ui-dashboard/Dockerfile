FROM nginx:alpine

RUN /bin/cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo 'Asia/Shanghai' >/etc/timezone
COPY nginx.conf /etc/nginx/nginx.conf
COPY static /usr/share/nginx/html
EXPOSE 8080
