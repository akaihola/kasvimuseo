FROM python:2.7-alpine AS base

FROM base AS builder

RUN mkdir /install

RUN apk add gcc jpeg-dev musl-dev postgresql-dev python-dev zlib-dev
ENV LIBRARY_PATH=/lib:/usr/lib
ENV PYTHONPATH=/install/lib/python2.7/site-packages

COPY requirements /kasvimuseo/requirements
# This resolves rather than passing --no-deps, unlike dev/Containerfile, and
# since issue 027 that no longer decides anything: production.txt names every
# runtime package including Pillow, and the two mechanisms were measured to
# install the same nine packages -- ten until issue 031 vendored `django-jqm`
# into `jqm/`, which this image now gets from the COPY below rather than from a
# GitHub URL, so this is the last pip line here that ever reached the network
# for anything but PyPI. Pillow used to be chosen here by whatever pip
# found, held below 10 only by the base image -- Pillow 7.0 dropped Python 2.7,
# and issue 028 is the AttributeError that waits above 9.5.0. It is pinned in
# the file now, so this image stops depending on that accident.
RUN pip install --install-option="--prefix=/install" -r /kasvimuseo/requirements/production.txt

# Django 1.5.1 lists its locale catalogs, fixtures and project_template in
# setup.py's `data_files` rather than `package_data`, and where those end up
# depends on how pip installs it (issue 040). `--install-option` above makes pip
# run the sdist's `setup.py install`, and that setup.py redirects the `data`
# install scheme to `purelib`, so here they land inside the package and the
# admin is Finnish. A wheel ignores that redirection and drops them in
# $prefix/django instead, which is what happens in dev/Containerfile. Handle
# both, in the builder stage so it survives the COPY --from=builder below, and
# fail the build rather than shipping an English admin if neither holds.
RUN set -e; \
    prefix=/install; \
    pkg=$prefix/lib/python2.7/site-packages/django; \
    if [ -d "$prefix/django" ]; then \
        cp -a "$prefix/django"/. "$pkg"/; \
        rm -rf "$prefix/django"; \
    fi; \
    for mo in conf/locale/fi contrib/admin/locale/fi; do \
        test -f "$pkg/$mo/LC_MESSAGES/django.mo" || { \
            echo "issue 040: $pkg/$mo/LC_MESSAGES/django.mo is missing and" \
                 "there is no $prefix/django to take it from -- find where" \
                 "pip put Django's data_files" >&2; \
            exit 1; \
        }; \
    done

COPY setup.py /kasvimuseo/setup.py
COPY kasvimuseo /kasvimuseo/kasvimuseo
COPY ylaneenkasvit /kasvimuseo/ylaneenkasvit
# The vendored django-jqm (issue 031). It is a third package rather than part
# of either of the two above because it stayed an app: `'jqm'` is in
# `INSTALLED_APPS`, and that is what makes the template loader and the
# staticfiles finder look inside it.
COPY jqm /kasvimuseo/jqm
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
