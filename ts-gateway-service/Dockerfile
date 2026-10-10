FROM java:8-jre
FROM eclipse-temurin:8-jre-jammy

RUN /bin/cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo 'Asia/Shanghai' >/etc/timezone

ADD ./target/ts-gateway-service-1.0.jar /app/
CMD ["java", "-Xmx1024m",  "-jar", "/app/ts-gateway-service-1.0.jar"]
COPY ./target/ts-gateway-service-1.0.jar /app/ts-gateway-service.jar
CMD ["java", "-Xmx512m", "-jar", "/app/ts-gateway-service.jar"]

EXPOSE 18888 
EXPOSE 18888
