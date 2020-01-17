FROM python:2.7-alpine AS base

FROM base AS builder

RUN mkdir /install

RUN apk add gcc jpeg-dev musl-dev postgresql-dev python-dev zlib-dev
ENV LIBRARY_PATH=/lib:/usr/lib
ENV PYTHONPATH=/install/lib/python2.7/site-packages

COPY requirements /kasvimuseo/requirements
RUN pip install --install-option="--prefix=/install" -r /kasvimuseo/requirements/production.txt

COPY setup.py /kasvimuseo/setup.py
COPY kasvimuseo /kasvimuseo/kasvimuseo
COPY ylaneenkasvit /kasvimuseo/ylaneenkasvit
RUN pip install --install-option="--prefix=/install" /kasvimuseo

FROM python:2.7-alpine
RUN apk add libjpeg-turbo libpq && rm -rf /var/cache/apk
COPY --from=builder /install /usr/local
CMD ["manage", \
     "runserver", \
     "--settings=ylaneenkasvit.ylaneenkasvit_settings", \
     "--verbosity=3", \
     "0.0.0.0:8000"]
EXPOSE 8000
