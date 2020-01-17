import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from seleniumbase import BaseCase


@pytest.fixture
def species_index(logged_in: BaseCase) -> BaseCase:
    logged_in.open('http://localhost:8000/admin/kasvimuseo/species/')
    index = logged_in
    assert index.get_current_url() == 'http://localhost:8000/admin/kasvimuseo/species/'
    return index


def test_species_index(species_index: BaseCase):
    table = species_index.get_element('#result_list')
    assert isinstance(table, WebElement)
    headers = table.find_elements_by_xpath('thead//th')
    assert [h.text for h in headers] ==  [
        '', 'Edit', 'LajiNro', 'SuomalainenNimi', 'Sukunimi', 'Ryhmä', 'Laji',
        'Subspecies', 'Lajike', 'Cultivation history', 'Type', 'Korkeuscm',
        'Leveyscm', 'Taimiväli', 'Kukinnanväri', 'Flowering time',
        'Light requirement', 'Kasvualusta', 'Additional information', 'Photo']
    species_index.assert_text(
        'Aaprottimaruna Ihantoja 02',
        '#results_list tbody tr:first-child td:last-child')


def test_species_detail(species_index: BaseCase):
    species_index.click('(all) species', By.LINK_TEXT)

