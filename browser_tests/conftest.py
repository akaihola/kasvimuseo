"""Fixtures for the label editor's browser tests.

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


@pytest.fixture
def anonymous_page(browser, base_url):
    """A page with the CDN scripts served locally and console errors collected.

    The viewport is 1280x900: at issue 046's 50 % screen zoom that is five
    labels across, so the two this data has sit side by side with the empty
    part of the ``<ul>`` beside them -- which is where a number has to be
    dropped to make a new label.
    """
    context = browser.new_context(viewport={'width': 1280, 'height': 900})

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
def page(anonymous_page, base_url):
    """The same page, logged in as the gardener ``seed.py`` creates.

    The editor and its data endpoint are staff-only (issue 052), so this is
    what every test but the one about the gate itself needs. The password is
    made per run by ``dev/kasvimuseo`` and reaches both halves through the
    environment, so nothing here is a credential anybody could reuse.
    """
    password = os.environ.get('KASVIMUSEO_BROWSER_TEST_PASSWORD')
    if not password:
        pytest.fail('KASVIMUSEO_BROWSER_TEST_PASSWORD is unset -- run these'
                    ' through `dev/kasvimuseo app browser-test`.')
    anonymous_page.goto(base_url + '/admin/')
    anonymous_page.fill('#id_username', STAFF_USERNAME)
    anonymous_page.fill('#id_password', password)
    anonymous_page.click('input[type="submit"]')
    anonymous_page.wait_for_selector('#id_username', state='detached')
    return anonymous_page


@pytest.fixture
def editor(page, base_url):
    """The label editor, loaded, with its labels drawn.

    ``page`` has been through the admin's login form, which is what the editor
    now requires (issue 052). It used to stop at ``/admin/`` for a different
    reason -- to borrow the ``csrftoken`` cookie the editor set none of -- and
    that half is gone: the page issues its own.
    """
    page.goto(base_url + LABELS_URL)
    page.wait_for_selector('#labels li')
    return page


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


def drag(page, source, target_x, target_y):
    """Drag ``source`` to a point, as HTML5 drag and drop.

    Playwright synthesises ``dragstart`` / ``dragenter`` / ``dragover`` /
    ``drop`` from these mouse movements the way a mouse does. Two moves rather
    than one: the first is what starts the drag, and the editor's handlers run
    on entering, so a single jump can land without ever having entered.
    """
    box = source.bounding_box()
    page.mouse.move(box['x'] + box['width'] / 2, box['y'] + box['height'] / 2)
    page.mouse.down()
    page.mouse.move(target_x, target_y, steps=8)
    page.mouse.move(target_x, target_y, steps=2)
    page.mouse.up()


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
