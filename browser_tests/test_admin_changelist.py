# -*- coding: utf-8 -*-
"""These browser tests check the admin filter and action controls.

Grappelli opens the filter with JavaScript. Its action form requires the submit button.
The tests check both controls against the report and species data.
"""

CHANGELIST = '/admin/kasvimuseo/species/'

# ``seed.py``: kevätesikko is the one Yrtti (type 3), the other two are the
# factory's default Perenna (type 2).
YRTTI = '?type__exact=3'


def species_names(page):
    """The ``name_fi`` column, in the order the changelist lists it."""
    return page.eval_on_selector_all('td.field-name_fi',
                                     'cells => cells.map(c => c.textContent)')


def test_species_changelist_filter_narrows_the_rows(page, base_url):
    """``# FIXME: filtering doesn't work`` on ``SpeciesAdmin``.

    The sidebar filter is a pulldown Grappelli opens with JavaScript and a
    ``<select>`` whose ``change`` sets ``location.href``; a test client sees
    neither, only the ``?type__exact=`` link behind them.
    """
    page.goto(base_url + CHANGELIST)
    assert sorted(species_names(page)) == ['kevätesikko', 'sinivuokko',
                                           'valkonarsissi']

    content = page.query_selector('#grp-filters .grp-pulldown-content')
    assert not content.is_visible()
    page.click('#grp-filters .grp-pulldown-handler')
    assert content.is_visible()

    page.select_option('#grp-filters select.grp-filter-choice', YRTTI)
    page.wait_for_url(base_url + CHANGELIST + YRTTI)

    assert species_names(page) == ['kevätesikko']


def test_species_changelist_action_runs_from_the_submit_button(page, base_url):
    """``# FIXME: action selection doesn't work in admin!``, twice over.

    "Create Species Sheets" is ``planted_species_report``, which redirects to
    the printable report keyed by the selected species' ``LajiNro``. Here that
    is kevätesikko, whose ``external_id`` ``seed.py`` sets to 2.
    """
    page.goto(base_url + CHANGELIST + YRTTI)
    page.check('tr input.action-select')

    page.select_option('select[name=action]', 'planted_species_report')
    page.click('#grp-changelist-form button[name=index]')
    page.wait_for_url(base_url + '/kasvimuseo/planted-species-printable/2/')

    assert 'kevätesikko' in page.content()
    assert page.console_errors == []
