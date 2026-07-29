# -*- encoding: utf-8 -*-
"""Serving uploaded media from this project, with a remote fallback.

Production serves ``MEDIA_ROOT`` from a separate host and sets ``MEDIA_URL`` to
it, so none of this runs there: ``ylaneenkasvit/urls.py`` only adds the route
when ``MEDIA_URL`` is a local path.

Development is the case this exists for. Pointing ``MEDIA_URL`` at the
production media host makes every photo URL name production, which breaks the
photos that exist only locally -- anything uploaded in the development admin,
and every derived size photologue generates into ``cache/`` -- and requires the
browser's machine, not just the server's, to reach the public internet. Serving
the local files instead would mean downloading all 260 MB of them before any
photo appears at all.

So: serve what is there, and redirect the rest to ``MEDIA_FALLBACK_URL``. Both
halves are needed, which is what :doc:`issue 048
</issues/048-the-dev-server-loads-photos-from-the-production-media-host>`
records.
"""

from django.conf import settings
from django.http import Http404, HttpResponseRedirect
from django.utils.http import urlquote
from django.views.static import serve


def serve_media(request, path):
    """Serve ``path`` from ``MEDIA_ROOT``, or redirect to the fallback host.

    ``django.views.static.serve`` does the work and the path sanitising -- it
    strips ``..`` before touching the disk -- and raises ``Http404`` both for a
    missing file and for a directory. Either way the file is not here, so the
    fallback host is asked for it. Without ``MEDIA_FALLBACK_URL`` the 404 is
    the answer.
    """
    try:
        return serve(request, path, document_root=settings.MEDIA_ROOT)
    except Http404:
        if not settings.MEDIA_FALLBACK_URL:
            raise
        return HttpResponseRedirect(
            settings.MEDIA_FALLBACK_URL + urlquote(path))
