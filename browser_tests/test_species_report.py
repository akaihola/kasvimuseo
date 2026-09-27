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
