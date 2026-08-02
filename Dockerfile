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
# install the same set -- nine packages when that was measured, ten until issue
# 031 vendored `django-jqm`, and eleven since upgrade plan Stage 2 added
# photologue 2.8's own two. The vendored `django-jqm` goes
# into `jqm/`, which this image now gets from the COPY below rather than from a
# GitHub URL, so this is the last pip line here that ever reached the network
# for anything but PyPI. Pillow used to be chosen here by whatever pip
# found, held below 10 only by the base image -- Pillow 7.0 dropped Python 2.7,
# and issue 028 is the AttributeError that waits above 9.5.0. It is pinned in
# the file now, so this image stops depending on that accident.
RUN pip install --install-option="--prefix=/install" -r /kasvimuseo/requirements/production.txt

# Django 1.5.1 listed its locale catalogs, fixtures and project_template in
# setup.py's `data_files` rather than `package_data`, and where those ended up
# depended on how pip installed it (issue 040). `--install-option` above makes
# pip run the sdist's `setup.py install`, and 1.5.1's setup.py redirected the
# `data` install scheme to `purelib`, so they landed inside the package here
# and the admin was Finnish; a wheel ignored that redirection and dropped them
# in $prefix/django, which is what used to happen in dev/Containerfile.
#
# Django 1.5.12 -- upgrade plan Stage 1 -- makes both paths the same: it
# collects them as `package_data` and redirects nothing, so they are inside
# the package however pip is invoked. This block keeps handling both, in the
# builder stage so it survives the COPY --from=builder below, and still fails
# the build rather than shipping an English admin if neither holds.
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
RUN pip install --install-option="--prefix=/install" /kasvimuseo

# The same idiom as the Django block above, for this project's own files
# (issue 058). Every path here arrives through MANIFEST.in rather than through
# `package_data`, so nothing fails until a page is rendered: a missing
# `base.html` is a 500 on every page that extends it, and a missing catalog is
# an English string on a Finnish-only application. Reordering or trimming the
# `COPY` lines above is what drops them, which is why this stands in the build
# rather than in the suite -- the suite runs against the working tree, where
# these files are always there.
RUN set -e; \
    site=/install/lib/python2.7/site-packages; \
    for f in ylaneenkasvit/templates/base.html \
             ylaneenkasvit/templates/404.html \
             ylaneenkasvit/templates/500.html \
             ylaneenkasvit/templates/grappelli/dashboard/modules/link_list.html \
             ylaneenkasvit/locale/fi/LC_MESSAGES/django.mo \
             kasvimuseo/locale/fi/LC_MESSAGES/django.mo; do \
        test -r "$site/$f" || { \
            echo "issue 058: $site/$f is missing from the installed package." \
                 "MANIFEST.in is the only thing that puts it there, so check" \
                 "that it is still COPYed into /kasvimuseo above and still" \
                 "names this file" >&2; \
            exit 1; \
        }; \
    done

FROM python:2.7-alpine
RUN apk add libjpeg-turbo libpq && rm -rf /var/cache/apk
COPY --from=builder /install /usr/local
CMD ["manage", \
     "runserver", \
     "--settings=ylaneenkasvit.ylaneenkasvit_settings", \
     "--verbosity=3", \
     "0.0.0.0:8000"]
EXPOSE 8000
