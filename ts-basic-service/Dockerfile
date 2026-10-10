FROM eclipse-temurin:8-jre-jammy

RUN /bin/cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo 'Asia/Shanghai' >/etc/timezone

COPY ./target/ts-basic-service-1.0.jar /app/ts-basic-service.jar
CMD ["java", "-Xmx200m", "-jar", "/app/ts-basic-service.jar"]

EXPOSE 15680
