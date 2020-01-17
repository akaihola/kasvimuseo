import pytest
from seleniumbase import BaseCase


@pytest.fixture(scope='session')
def logged_in():
    class BaseClass(BaseCase):
        def base_method():
            pass

    sb = BaseClass("base_method")
    sb.setUp()
    sb.open('http://localhost:8000/')
    assert sb.get_current_url() == 'http://localhost:8000/admin/'
    sb.assert_text('Username:')
    sb.assert_text('Password:')
    sb.update_text('#id_username', 'akaihola')
    sb.update_text('#id_password', '123')
    sb.slow_click('input[type=submit]')
    assert sb.get_current_url() == 'http://localhost:8000/admin/'
    yield sb
    sb.tearDown()
