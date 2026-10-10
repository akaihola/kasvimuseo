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
