FROM eclipse-temurin:8-jre-jammy

RUN /bin/cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo 'Asia/Shanghai' >/etc/timezone

COPY ./target/ts-price-service-1.0.jar /app/ts-price-service.jar
CMD ["java", "-Xmx200m", "-jar", "/app/ts-price-service.jar"]

EXPOSE 16579