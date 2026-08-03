# -*- encoding: utf-8 -*-
"""Logging a development browser in from the shell, without the login form.

``dev/kasvimuseo db restore`` replaces the local database with production's,
and that includes ``auth_user`` and ``django_session``: every password becomes
production's, which nobody here is supposed to know (issues 049 and 050), and
the session the browser was carrying is gone with the rows it pointed at. So
the first thing after a restore was always the same detour -- ``changepassword``
in the container, then the admin's login form -- and it happened again after
every restore. ``db development`` (issue 067) removes the first half by
rewriting the dump's passwords to a known one; the form, and a dump restored as
it came, are what is left.

Django ships no management command for this and no command could be the whole
answer: what logs a browser in is a ``sessionid`` cookie *in that browser*, and
a process in a container has no way to put one there. A URL can. This is that
URL, which is what :doc:`issue 068
</issues/068-logging-in-after-a-restore-needs-a-password-nobody-has>` records::

    $ xdg-open http://localhost:8000/dev-login/akaihola/

It exists only when ``settings.DEV_LOGIN`` is on. ``common_settings`` reads
that from ``KASVIMUSEO_DEV_LOGIN`` and defaults it off, ``dev/kasvimuseo``
turns it on for the containers it starts, and nothing else does -- so the
route is absent from a deployment, from the test suite, and from any server
started by hand without the variable. ``ylaneenkasvit/urls.py`` does not
register it in that case, and the view refuses as well: two gates rather than
one, because the URLconf's is the one a future ``include()`` could route
around.

What the setting is *not* is a second ``DEBUG``. Issue 051 is production
running with ``DEBUG`` on behind an untracked ``local_settings.py``, and a
gate that reads ``settings.DEBUG`` would have been open there. This one is a
variable that only the development harness sets.
"""

from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.views.decorators.cache import never_cache


@never_cache
def dev_login(request, username):
    """Log ``username`` in and hand the browser the admin.

    ``login`` wants the backend that authenticated the user, and nothing
    authenticated this one -- that is the point -- so the first entry of
    ``AUTHENTICATION_BACKENDS`` is named instead. It is Django's
    ``ModelBackend``, the same one the login form would have used, and the
    dotted path it writes into the session is what ``get_user`` reads back on
    the next request.

    An inactive account is refused, because ``login`` itself does not check:
    ``ModelBackend`` is where the login form's rejection happens, and skipping
    the form skips that too.
    """
    if not settings.DEV_LOGIN:
        raise Http404('DEV_LOGIN is off')
    try:
        user = User.objects.get(username=username, is_active=True)
    except User.DoesNotExist:
        raise Http404('No active user named {0!r}'.format(username))
    user.backend = settings.AUTHENTICATION_BACKENDS[0]
    login(request, user)
    return HttpResponseRedirect(reverse('admin:index'))
