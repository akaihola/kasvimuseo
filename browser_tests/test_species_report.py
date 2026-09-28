import pytest


@pytest.mark.parametrize('species_id,orientation', [(1, 'vertical'),
                                                     (2, 'horizontal')])
def test_compact_photo_label_matches_photo_width(page, base_url, species_id,
                                                orientation):
    page.set_viewport_size({'width': 810, 'height': 1080})
    page.goto(f'{base_url}/kasvimuseo/planted-species-compact/{species_id}/')
    header = page.locator('.header')
    photo = page.locator('.header .photo img')

    assert f'header {orientation}' in header.get_attribute('class')
    assert header.evaluate('''node => {
        const header = node.getBoundingClientRect();
        return [header.left, header.right];
    }''') == photo.evaluate('''node => {
        const photo = node.getBoundingClientRect();
        return [photo.left, photo.right];
    }''')


def test_report_logout_ends_the_session(page, base_url):
    page.goto(f'{base_url}/kasvimuseo/planted-species/')
    with page.expect_response(lambda response: response.url.endswith('/accounts/logout/')) as logout:
        page.locator('.logout-button').click()

    assert logout.value.request.method == 'POST'
    assert logout.value.status == 200
    page.wait_for_url(f'{base_url}/accounts/logout/')
    assert 'Your account has been logged out.' in page.locator('body').inner_text()
    response = page.request.get(f'{base_url}/admin/', max_redirects=0)
    assert response.status == 302
    assert '/admin/login/' in response.headers['location']
