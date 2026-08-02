# -*- coding: utf-8 -*-
"""The two admin changelist features issue 013's ``FIXME`` comments deny.

``kasvimuseo/tests/test_admin_changelist.py`` and ``test_admin_forms.py``
already drive both of them through the test client, so what is left to check is
the half a test client cannot see: Grappelli replaces two of the admin's own
controls with JavaScript, and neither the filter pulldown nor the action
dropdown does anything until that JavaScript runs.

The answer is that both work, which is why the comments are gone. The
interesting part is *how* the action runs, since it is why somebody once wrote
that action selection does not work: Grappelli's ``actions.js`` (its own copy,
shadowing Django's -- see the ``GRAPPELLI CUSTOM: submit on select`` comment in
it) deletes the "Go" button and submits the form when the dropdown changes
instead. There is no button to press, so an action looks inert until you notice
it has already run.
"""

CHANGELIST = '/admin/kasvimuseo/species/'

# ``seed.py``: kevätesikko is the one Yrtti (type 3), the other two are the
# factory's default Perenna (type 2).
YRTTI = '?type__exact=3'


def species_names(page):
    """The ``name_fi`` column, in the order the changelist lists it."""
    return page.eval_on_selector_all('td.fieldname_name_fi',
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


def test_species_changelist_action_runs_from_the_dropdown(page, base_url):
    """``# FIXME: action selection doesn't work in admin!``, twice over.

    "Create Species Sheets" is ``planted_species_report``, which redirects to
    the printable report keyed by the selected species' ``LajiNro``. Here that
    is kevätesikko, whose ``external_id`` ``seed.py`` sets to 2.
    """
    page.goto(base_url + CHANGELIST + YRTTI)
    page.check('tr input.action-select')

    # Nothing on the page submits it: Grappelli's actions.js drops the "Go"
    # button and hangs the submit on the dropdown's ``change`` instead, so this
    # assertion is the reason the feature looks broken to a reader.
    assert page.eval_on_selector_all(
        '#grp-changelist-form button, #grp-changelist-form input[type=submit]',
        'found => found.length') == 0

    page.select_option('select[name=action]', 'planted_species_report')
    page.wait_for_url(base_url + '/kasvimuseo/planted-species-printable/2/')

    assert 'kevätesikko' in page.content()
    assert page.console_errors == []
