FROM python:3.7.17-alpine3.18 AS base

FROM base AS builder

RUN mkdir /install

RUN apk add gcc jpeg-dev musl-dev postgresql-dev zlib-dev
ENV LIBRARY_PATH=/lib:/usr/lib
ENV PYTHONPATH=/install/lib/python3.7/site-packages

# Keep legacy source builds compatible with sortedm2m 1.3.3.
RUN pip install --no-cache-dir pip==23.1.2 setuptools==57.5.0 wheel==0.41.3

COPY requirements /kasvimuseo/requirements
# Install the runtime lock before the application package.
RUN pip install --prefix=/install -r /kasvimuseo/requirements/production.txt

# Check Finnish Django catalogs in the installation prefix.
# Issue 040 records why these files need a build check.
RUN set -e; \
    prefix=/install; \
    pkg=$prefix/lib/python3.7/site-packages/django; \
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
# `setup.py`'s `package_data` names `kasvimuseo`'s and `jqm`'s templates and
# static files and nothing else; everything else non-Python this project ships
# -- `ylaneenkasvit/templates/`, and both packages' `locale/` -- reaches an
# install only through `include_package_data`, which reads this file. Without
# it in the build context the installed package had no `base.html`, so every
# page extending it was a 500 in this image, and no Finnish catalog of the
# project's own either (issue 058). The Ansible install never saw this: it
# builds from a git checkout, where the file is beside `setup.py`.
COPY MANIFEST.in /kasvimuseo/MANIFEST.in
COPY kasvimuseo /kasvimuseo/kasvimuseo
COPY ylaneenkasvit /kasvimuseo/ylaneenkasvit
# The vendored django-jqm (issue 031). It is a third package rather than part
# of either of the two above because it stayed an app: `'jqm'` is in
# `INSTALLED_APPS`, and that is what makes the template loader and the
# staticfiles finder look inside it.
COPY jqm /kasvimuseo/jqm
RUN pip install --prefix=/install /kasvimuseo

# The same idiom as the Django block above, for this project's own files
# (issue 058). Nothing fails until a page is rendered: a missing `base.html` is
# a 500 on every page that extends it, and a missing catalog is an English
# string on a Finnish-only application. Reordering or trimming the `COPY` lines
# above is what drops them, which is why this stands in the build rather than
# in the suite -- the suite runs against the working tree, where these files
# are always there.
#
# All but the last arrive through MANIFEST.in. The last arrives through
# `setup.py`'s `package_data`, whose globs match one path segment each, so a
# file a level deeper than the existing entries is silently not installed --
# and it is one grappelli 2.5 requests on every admin page (upgrade plan Stage
# 3), so dropping it is a 404 per page and an English date picker.
RUN set -e; \
    site=/install/lib/python3.7/site-packages; \
    for f in ylaneenkasvit/templates/base.html \
             ylaneenkasvit/templates/404.html \
             ylaneenkasvit/templates/500.html \
             ylaneenkasvit/templates/grappelli/dashboard/modules/link_list.html \
             ylaneenkasvit/locale/fi/LC_MESSAGES/django.mo \
             kasvimuseo/locale/fi/LC_MESSAGES/django.mo \
             kasvimuseo/static/grappelli/jquery/i18n/ui.datepicker-fi.js; do \
        test -r "$site/$f" || { \
            echo "issue 058: $site/$f is missing from the installed package." \
                 "MANIFEST.in is the only thing that puts it there, so check" \
                 "that it is still COPYed into /kasvimuseo above and still" \
                 "names this file" >&2; \
            exit 1; \
        }; \
    done

FROM python:3.7.17-alpine3.18
RUN apk add libjpeg-turbo libpq && rm -rf /var/cache/apk
COPY --from=builder /install /usr/local
CMD ["manage", \
     "runserver", \
     "--settings=ylaneenkasvit.ylaneenkasvit_settings", \
     "--verbosity=3", \
     "0.0.0.0:8000"]
EXPOSE 8000
