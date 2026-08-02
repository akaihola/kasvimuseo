"""Fixtures for the browser tests: the label editor, and the admin of 013.

These run on the **host's Python 3**, not in the application container: the
application is Django 1.5 on Python 2.7, and nothing that drives a current
browser supports that interpreter (issue 017). They talk to the server
``dev/kasvimuseo app browser-test`` starts, over HTTP, and import no part of
the application.

Two things are faked and nothing else. The page loads Vue, axios and
sanitize.css from ``unpkg.com`` and ``cdnjs.cloudflare.com``; every request to
either is answered from ``vendor/`` instead, so a test run needs no network and
cannot go red because a CDN did. And ``truncated_labels`` replaces the data
endpoint's response, which is the one condition (issue 044) that cannot be
produced by asking the real server nicely.
"""

import os
import re
import shlex
import subprocess
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright

VENDOR = Path(__file__).parent / 'vendor'

# What the page asks a CDN for, and the local copy that answers it. The
# versions match the URLs in ``reports/planting-labels.html``: Vue is pinned
# there (2.6.14), axios is not -- ``unpkg.com/axios`` is whatever is current --
# so this pins for the tests what production floats.
CDN_REPLACEMENTS = {
    'vue.min.js': ('application/javascript', 'vue.min.js'),
    'axios.min.js': ('application/javascript', 'axios.min.js'),
    'sanitize.min.css': ('text/css', 'sanitize.min.css'),
}

LABELS_URL = '/kasvimuseo/planting-labels/'
DATA_URL = '/kasvimuseo/planting-labels/data/'

# The account ``seed.py`` creates. Its password is not here and never in the
# repository: ``dev/kasvimuseo`` makes one per run (issues 050 and 052).
STAFF_USERNAME = 'puutarhuri'

# The desktop the mouse tests use. At issue 046's 50 % screen zoom it is five
# labels across, so the two this data has sit side by side with the empty part
# of the ``<ul>`` beside them -- which is where a number has to be dropped to
# make a new label.
DESKTOP = {'width': 1280, 'height': 900}

# The device issue 045 was reported from, laid out at the width its viewport
# tag now asks for: an iPad (7th generation) is 810 x 1080 CSS pixels, and
# landscape is the orientation a sheet is arranged in -- at issue 046's 50 %
# screen zoom it puts three labels across, so there is empty sheet beside the
# two this data has to drop a number onto.
IPAD_LANDSCAPE = {'width': 1080, 'height': 810}

# The device's own user agent, for the tests that are about the branch the
# template picks from it. ``fitTextToSpace`` reads ``navigator.userAgent``
# (issue 056), so without this Chromium takes the desktop path however tablet
# the rest of the emulation is.
#
# It is deliberately *not* on ``anonymous_touch_page``: the iOS half of the
# template is half CSS, and that half lives behind ``@supports
# (-webkit-touch-callout: none)``, which neither Playwright's Chromium nor its
# WebKit implements. Putting the user agent on the shared fixture would run
# every touch test down a code path only half of which the browser can apply,
# so the tests that measure layout would be measuring a mixture. The fixtures
# below keep the two emulated dimensions apart: ``touch_page`` is the finger,
# ``ipad_page`` is the user agent.
IPAD_USER_AGENT = (
    'Mozilla/5.0 (iPad; CPU OS 18_7 like Mac OS X) AppleWebKit/605.1.15'
    ' (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1')


def pytest_addoption(parser):
    parser.addoption('--headed', action='store_true',
                     help='show the browser instead of running it headless')


@pytest.fixture(scope='session')
def base_url():
    """Where ``dev/kasvimuseo app browser-test`` put the server."""
    url = os.environ.get('KASVIMUSEO_BROWSER_TEST_URL')
    if not url:
        pytest.fail('KASVIMUSEO_BROWSER_TEST_URL is unset -- run these through'
                    ' `dev/kasvimuseo app browser-test`, which starts the'
                    ' server they need.')
    return url.rstrip('/')


@pytest.fixture(autouse=True)
def seeded():
    """Put the data back before every test.

    The editor's save replaces every label in the database with what is on the
    screen, so a test that saves would otherwise decide what the next one sees.
    ``dev/kasvimuseo app browser-seed`` is the same wipe-and-rebuild the run
    started with, and costs about a second.
    """
    command = os.environ.get('KASVIMUSEO_BROWSER_TEST_SEED')
    if not command:
        pytest.fail('KASVIMUSEO_BROWSER_TEST_SEED is unset -- run these'
                    ' through `dev/kasvimuseo app browser-test`.')
    subprocess.run(shlex.split(command), check=True,
                   stdout=subprocess.DEVNULL)


@pytest.fixture(scope='session')
def browser(request):
    """One Chromium for the whole session.

    ``PLAYWRIGHT_BROWSERS_PATH`` decides where it comes from; nothing here ever
    downloads one.
    """
    with sync_playwright() as playwright:
        instance = playwright.chromium.launch(
            headless=not request.config.getoption('--headed'))
        yield instance
        instance.close()


def offline_page(browser, **options):
    """A page with the CDN scripts served locally and console errors collected.

    A generator, so the two fixtures below are one-liners that differ only in
    the context they ask for.
    """
    context = browser.new_context(**options)

    def serve_locally(route):
        name = route.request.url.rsplit('/', 1)[-1]
        content_type, filename = CDN_REPLACEMENTS[name]
        route.fulfill(status=200,
                      content_type=content_type,
                      body=(VENDOR / filename).read_bytes())

    for name in CDN_REPLACEMENTS:
        context.route(re.compile(r'https://(unpkg\.com|cdnjs\.cloudflare\.com)'
                                 r'/.*/{0}$'.format(re.escape(name))),
                      serve_locally)

    errors = []
    page = context.new_page()
    page.on('console', lambda message: (errors.append(message.text)
                                        if message.type == 'error' else None))
    page.console_errors = errors
    yield page
    context.close()


@pytest.fixture
def anonymous_page(browser):
    """A mouse, at a desktop size, arriving with no session."""
    for page in offline_page(browser, viewport=DESKTOP):
        yield page


@pytest.fixture
def anonymous_touch_page(browser):
    """The iPad of issue 045, as far as Chromium can be one.

    ``has_touch`` is what makes the browser deliver ``pointerdown`` with
    ``pointerType: 'touch'`` and honour ``touch-action``; ``is_mobile`` is what
    makes it obey the page's viewport tag the way a tablet does. It is
    emulation, not the device: the engine is still Chromium, so this can show
    that the editor works without a mouse, and cannot show that iOS Safari
    agrees.
    """
    for page in offline_page(browser, viewport=IPAD_LANDSCAPE,
                             has_touch=True, is_mobile=True):
        yield page


@pytest.fixture
def anonymous_ipad_page(browser):
    """The tablet again, this time as the template's ``isIOS`` test sees it.

    Everything ``anonymous_touch_page`` emulates, plus ``IPAD_USER_AGENT``, so
    the label fitter takes the branch the device takes (issue 056). Still
    Chromium: the JavaScript half of that branch runs here, the CSS half
    cannot -- see ``IPAD_USER_AGENT``.
    """
    for page in offline_page(browser, viewport=IPAD_LANDSCAPE,
                             has_touch=True, is_mobile=True,
                             user_agent=IPAD_USER_AGENT):
        yield page


def log_in(page, base_url):
    """Through the admin's login form, as the gardener ``seed.py`` creates.

    The editor and its data endpoint are staff-only (issue 052), so this is
    what every test but the one about the gate itself needs. The password is
    made per run by ``dev/kasvimuseo`` and reaches both halves through the
    environment, so nothing here is a credential anybody could reuse.
    """
    password = os.environ.get('KASVIMUSEO_BROWSER_TEST_PASSWORD')
    if not password:
        pytest.fail('KASVIMUSEO_BROWSER_TEST_PASSWORD is unset -- run these'
                    ' through `dev/kasvimuseo app browser-test`.')
    page.goto(base_url + '/admin/')
    page.fill('#id_username', STAFF_USERNAME)
    page.fill('#id_password', password)
    page.click('input[type="submit"]')
    page.wait_for_selector('#id_username', state='detached')
    return page


@pytest.fixture
def page(anonymous_page, base_url):
    return log_in(anonymous_page, base_url)


@pytest.fixture
def touch_page(anonymous_touch_page, base_url):
    """The tablet, logged in: the gardener carrying it is staff too."""
    return log_in(anonymous_touch_page, base_url)


@pytest.fixture
def ipad_page(anonymous_ipad_page, base_url):
    """The same, for the tests that need the iPad's user agent as well."""
    return log_in(anonymous_ipad_page, base_url)


def open_editor(page, base_url):
    """The label editor, loaded, with its labels drawn.

    ``page`` has been through the admin's login form, which is what the editor
    now requires (issue 052). It used to stop at ``/admin/`` for a different
    reason -- to borrow the ``csrftoken`` cookie the editor set none of -- and
    that half is gone: the page issues its own.
    """
    page.goto(base_url + LABELS_URL)
    page.wait_for_selector('#labels li')
    return page


@pytest.fixture
def editor(page, base_url):
    return open_editor(page, base_url)


@pytest.fixture
def touch_editor(touch_page, base_url):
    return open_editor(touch_page, base_url)


def labels(page):
    """The sheet as the tests talk about it: one entry per label, in order."""
    return page.evaluate("""() => Array.from(
        document.querySelectorAll('#labels li')).map(li => ({
            species: li.dataset.speciesId,
            name: li.querySelector('h1').textContent.trim(),
            ids: Array.from(li.querySelectorAll('.observation-id'))
                      .map(p => p.textContent.trim()),
            photo: li.querySelector('.photo img').getAttribute('src'),
            hidden: li.classList.contains('hidden'),
        }))""")


def centre(source):
    box = source.bounding_box()
    return box['x'] + box['width'] / 2, box['y'] + box['height'] / 2


def drag(page, source, target_x, target_y, release=True):
    """Drag ``source`` to a point with the mouse.

    Since issue 045 the editor listens for ``pointerdown`` / ``pointermove`` /
    ``pointerup`` rather than the HTML5 drag events, and a mouse produces those
    too -- so this drives the same code path as ``touch_drag`` below, which is
    the point of the rewrite. It moves in steps because the gesture is not a
    drag until the pointer has travelled, and because the preview follows every
    move.

    ``release=False`` leaves the button down, for a test that wants to look at
    the page mid-drag; it is then on the caller to finish or abandon it.
    """
    page.mouse.move(*centre(source))
    page.mouse.down()
    page.mouse.move(target_x, target_y, steps=8)
    if release:
        page.mouse.up()


def touch_drag(page, source, target_x, target_y, release='touchEnd'):
    """The same drag by finger, and the reason this rewrite happened.

    Playwright's ``page.touchscreen`` can only tap, so the sequence is
    dispatched over CDP: ``Input.dispatchTouchEvent`` is what a real touch on
    an emulated touch screen goes through, so the browser does its own
    hit-testing, applies ``touch-action`` and decides for itself what the
    pointer events look like. Nothing here calls a handler directly.

    ``release`` is the event that ends it: ``'touchEnd'`` for a finger lifted,
    ``'touchCancel'`` for a gesture the system took away, or ``None`` to leave
    the finger down. Returns the function that ends it either way.
    """
    session = page.context.new_cdp_session(page)
    x, y = centre(source)

    def dispatch(kind, point=None):
        session.send('Input.dispatchTouchEvent',
                     {'type': kind,
                      'touchPoints': [] if point is None else [point]})

    dispatch('touchStart', {'x': x, 'y': y, 'id': 1})
    for step in range(1, 9):
        dispatch('touchMove', {'x': x + (target_x - x) * step / 8,
                               'y': y + (target_y - y) * step / 8,
                               'id': 1})
    if release:
        dispatch(release)
    return dispatch


def save(page):
    """Click Save and wait for the POST to come back, returning what it sent."""
    with page.expect_request(lambda request: request.url.endswith(DATA_URL)
                             and request.method == 'POST') as request_info:
        with page.expect_response(
                lambda response: response.url.endswith(DATA_URL)
                and response.request.method == 'POST') as response_info:
            page.click('#save')
    assert response_info.value.status == 200
    return request_info.value.post_data_json
