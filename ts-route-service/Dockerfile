FROM eclipse-temurin:8-jre-jammy

RUN /bin/cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo 'Asia/Shanghai' >/etc/timezone

COPY ./target/ts-route-service-1.0.jar /app/ts-route-service.jar
ENTRYPOINT ["java", "-Xmx200m", "-jar", "/app/ts-route-service.jar"]

EXPOSE 11178
