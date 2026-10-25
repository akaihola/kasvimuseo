"""Check catalogue requests from embedding pages without configuration attributes."""

from pathlib import Path

import pytest
from playwright.sync_api import expect

LOADER = (Path(__file__).resolve().parents[1] / 'kasvimuseo' / 'static' /
          'js' / 'kasvimuseo' / 'planted-species-iframe.js').read_text()


@pytest.fixture(autouse=True)
def seeded():
    """These routed pages need no application database."""


@pytest.mark.parametrize('embedding_origin,asset_origin,catalogue_origin', [
    ('http://localhost:8000', 'http://localhost:8000', 'http://localhost:8000'),
    ('https://plants.example.invalid', 'https://static.plants.example.invalid',
     'https://plants.example.invalid'),
    ('https://museum.example.invalid', 'https://static.plants.example.invalid',
     'https://plants.example.invalid'),
    ('https://museum.example.invalid', 'https://plants.example.invalid',
     'https://plants.example.invalid'),
    ('http://museum.example.invalid', 'https://static.plants.example.invalid:8443',
     'https://plants.example.invalid:8443'),
    ('https://museum.example.invalid', 'https://plants.static.example.invalid',
     'https://plants.static.example.invalid'),
    ('https://museum.example.invalid', 'https://static.static.plants.example.invalid',
     'https://static.plants.example.invalid'),
])
def test_catalogue_origin(browser, embedding_origin, asset_origin, catalogue_origin):
    script_url = asset_origin + '/static/js/kasvimuseo/planted-species-iframe.js?v=5'
    catalogue_url = catalogue_origin + '/kasvimuseo/planted-species/'
    with browser.new_context() as context:
        page = context.new_page()

        def respond(route):
            if route.request.url == script_url:
                route.fulfill(content_type='application/javascript', body=LOADER)
            elif route.request.url == embedding_origin + '/embed/':
                route.fulfill(content_type='text/html',
                              body=f'<script src="{script_url}"></script>')
            else:
                route.fulfill(content_type='text/html', body='Catalogue')

        context.route('**/*', respond)
        with page.expect_request(catalogue_url):
            page.goto(embedding_origin + '/embed/')
        expect(page.locator('#kasvit-iframe')).to_have_attribute('src', catalogue_url)
        assert page.locator('script').get_attribute('data-site-url') is None


# The pages of the message tests. A hostile window must not resize the frame,
# write into the page or scroll it (task 23).
CATALOGUE = 'https://plants.example.invalid'
ELSEWHERE = 'https://elsewhere.example.invalid'
EMBEDDING_URL = 'https://museum.example.invalid/embed/'
SCRIPT_URL = ('https://static.plants.example.invalid/static/js/kasvimuseo/'
              'planted-species-iframe.js')

# ``received`` counts the messages this page got, so a test knows when the
# loader has seen one. The spacer puts the frame below the first screen, so a
# scroll to the frame shows.
EMBEDDING_PAGE = f'''<!doctype html>
<script>
var received = 0;
addEventListener('message', function () {{ received += 1; }});
</script>
<iframe id="elsewhere" src="{ELSEWHERE}/"></iframe>
<iframe id="sibling" src="{CATALOGUE}/kasvimuseo/sibling/"></iframe>
<div style="height: 3000px"></div>
<script src="{SCRIPT_URL}"></script>
'''

MARKUP_NAME = '<img src="x" onerror="document.title = \'injected\'">Kurjenpolvi'
POST_TO_PARENT = "message => parent.postMessage(message, '*')"


@pytest.fixture
def context(browser):
    with browser.new_context() as context:
        def respond(route):
            url = route.request.url
            if url == SCRIPT_URL:
                route.fulfill(content_type='application/javascript', body=LOADER)
            elif url.startswith(EMBEDDING_URL):
                route.fulfill(content_type='text/html', body=EMBEDDING_PAGE)
            else:
                route.fulfill(content_type='text/html',
                              body='<!doctype html><title>Other</title>')

        context.route('**/*', respond)
        yield context


def frame_of(page, selector):
    return page.locator(selector).element_handle().content_frame()


def from_frame(selector, navigate_to=None):
    """A sender that posts to the embedding page from one of its frames."""
    def open_page(context, url):
        page = context.new_page()
        page.goto(url)
        frame = frame_of(page, selector)
        if navigate_to:
            frame.goto(navigate_to)
        return page, lambda message: frame.evaluate(POST_TO_PARENT, message)
    return open_page


def from_opener(context, url):
    """A page on another origin opens the embedding page and posts to it."""
    opener = context.new_page()
    opener.goto(ELSEWHERE + '/')
    with context.expect_page() as popup:
        opener.evaluate('url => { window.embedding = open(url); }', url)
    page = popup.value
    page.wait_for_load_state()
    return page, lambda message: opener.evaluate(
        "message => embedding.postMessage(message, '*')", message)


HOSTILE_SENDERS = {
    'frame-on-another-origin': from_frame('#elsewhere'),
    'other-frame-on-catalogue-origin': from_frame('#sibling'),
    'catalogue-frame-after-navigation': from_frame('#kasvit-iframe',
                                                   ELSEWHERE + '/moved/'),
    'opener-on-another-origin': from_opener,
}


def page_state(page):
    """The markup with the frame height and debug box, the title, the scroll."""
    return page.evaluate(
        '() => [document.documentElement.outerHTML, document.title,'
        ' window.scrollX, window.scrollY]')


def post_and_wait(page, send, message):
    send(message)
    page.wait_for_function('received > 0')


@pytest.mark.parametrize('query', ['', '?debug=1'], ids=['plain', 'debug'])
@pytest.mark.parametrize('open_page', HOSTILE_SENDERS.values(),
                         ids=HOSTILE_SENDERS.keys())
def test_message_from_another_window_changes_nothing(context, open_page, query):
    page, send = open_page(context, EMBEDDING_URL + query)
    before = page_state(page)
    post_and_wait(page, send, {'plantedSpeciesIframeHeight': '1234px',
                               'plantedSpeciesIframePlantName': MARKUP_NAME})
    assert page_state(page) == before


@pytest.mark.parametrize('height', ['1234px', '100000px'])
def test_catalogue_frame_sets_the_height(context, height):
    page, send = from_frame('#kasvit-iframe')(context, EMBEDDING_URL)
    send({'plantedSpeciesIframeHeight': height,
          'plantedSpeciesIframePlantName': 'Kurjenpolvi'})
    frame = page.locator('#kasvit-iframe')
    expect(frame).to_have_css('height', height)
    # The loader scrolls the embedding page to the top of the frame.
    assert abs(frame.evaluate('frame => frame.getBoundingClientRect().top')) < 1


@pytest.mark.parametrize('height', [
    '1234', '12.5px', '-5px', '100001px', '50vh', ' 1234px', '1234px ',
    '1234px; background: red', 1234, ['1234px'], None,
])
def test_catalogue_frame_height_must_be_whole_pixels(context, height):
    page, send = from_frame('#kasvit-iframe')(context, EMBEDDING_URL + '?debug=1')
    before = page_state(page)
    post_and_wait(page, send, {'plantedSpeciesIframeHeight': height,
                               'plantedSpeciesIframePlantName': 'Kurjenpolvi'})
    assert page_state(page) == before


def test_debug_mode_shows_markup_in_a_plant_name_as_text(context):
    page, send = from_frame('#kasvit-iframe')(context, EMBEDDING_URL + '?debug=1')
    send({'plantedSpeciesIframeHeight': '1234px',
          'plantedSpeciesIframePlantName': MARKUP_NAME})
    debug = page.locator('#planted-species-iframe-debug')
    expect(debug).to_have_text(MARKUP_NAME + '/1234px')
    expect(debug.locator('img')).to_have_count(0)
    expect(page.locator('#kasvit-iframe')).to_have_css('height', '1234px')
    assert page.title() != 'injected'
