FROM mdillon/postgis:10-alpine

COPY ylaneenkasvit.sql /docker-entrypoint-initdb.d/ylaneenkasvit.sql
ENV PGDATA /var/lib/postgresql/integration-test-data
RUN /docker-entrypoint.sh -V
