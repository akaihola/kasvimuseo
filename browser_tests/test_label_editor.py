# -*- coding: utf-8 -*-
"""What the label editor does, as opposed to what it serves.

``reports/planting-labels.html`` is a Vue application; the Django side of it --
the JSON endpoint, the POST round trip, the page's server contract -- is
covered by ``kasvimuseo/tests/test_views.py`` and ``test_templates.py``. These
are the behaviours that only exist in a browser: the drag that regroups museum
numbers, the save that replaces every label with what is on the screen, the
per-label photo, and the print toggle.

The data is ``browser_tests/seed.py``: ``valkonarsissi`` with museum numbers 11
and 12 and two photos, ``kevätesikko`` with 21 and one photo, and a third
species planted only in a private bed, which must never appear.

The names below are the ones the JSON carries. The sheet shows them in capitals
because ``h1`` is ``text-transform: uppercase``; nothing in the document is.
"""

import re

from conftest import DATA_URL, LABELS_URL, drag, labels, save

NARSISSI = 'valkonarsissi'
ESIKKO = 'kevätesikko'


def named(page, name):
    """The one label for ``name``. Only used where there is exactly one."""
    matches = [label for label in labels(page) if label['name'] == name]
    assert len(matches) == 1, '{0} labels named {1}'.format(len(matches), name)
    return matches[0]


def number(page, museum_number):
    """The draggable museum number ``museum_number``, wherever it now sits."""
    return page.locator('#labels li .observation-id').filter(
        has_text=re.compile(r'^\s*{0}\s*$'.format(museum_number))).first


def empty_space(page):
    """A point inside ``#labels`` that is not on a label.

    ``dragEnterBackground`` only fires for ``event.target.id === 'labels'``, so
    "the background" is the part of the ``<ul>`` beside the labels, not the
    page around it.
    """
    box = page.locator('#labels').bounding_box()
    last = page.locator('#labels li').last.bounding_box()
    right_edge = box['x'] + box['width']
    return ((last['x'] + last['width'] + right_edge) / 2,
            last['y'] + last['height'] / 2)


def test_the_sheet_draws_one_label_per_species_with_its_museum_numbers(editor):
    """Sorted, because the order the server sends them in is not.

    ``get_labels_data`` calls ``sorted()`` on ``Observation`` instances, which
    define no ordering, so Python 2 falls back to comparing them by identity
    and a label's numbers arrive in whatever order the objects happen to sit
    in. The editor's own ``insort`` puts them in numerical order the moment one
    is dragged, so the same label can print "12 11" and then "11 12". Reported
    in ``docs/issues/incoming.rst``; this test asserts what the page must do
    either way rather than pinning an arbitrary order.
    """
    assert [(label['name'], sorted(label['ids'])) for label in labels(editor)] \
        == [(ESIKKO, ['21']), (NARSISSI, ['11', '12'])]


def test_a_species_planted_only_in_a_private_bed_gets_no_label(editor):
    assert 'sinivuokko' not in [label['name'] for label in labels(editor)]


def test_dragging_a_number_onto_the_background_splits_the_label(editor):
    """The editor's reason to exist: two plantings, two labels to print.

    Issue 045's large half rewrites this interaction for touch, and this is the
    assertion that would catch the rewrite breaking it for a mouse.
    """
    drag(editor, number(editor, 11), *empty_space(editor))

    assert [(label['name'], label['ids']) for label in labels(editor)] == [
        (ESIKKO, ['21']), (NARSISSI, ['12']), (NARSISSI, ['11'])]


def test_dragging_a_number_onto_a_label_of_the_same_species_merges_them(
        editor):
    """And the label left holding nothing goes away, rather than printing
    blank."""
    drag(editor, number(editor, 11), *empty_space(editor))
    assert len(labels(editor)) == 3

    target = editor.locator('#labels li').nth(1).bounding_box()
    drag(editor, number(editor, 11),
         target['x'] + target['width'] / 2, target['y'] + 20)

    assert [(label['name'], label['ids']) for label in labels(editor)] == [
        (ESIKKO, ['21']), (NARSISSI, ['11', '12'])]


def test_saving_posts_the_sheet_and_the_reload_shows_it_back(editor):
    """The save cycle, which is the dangerous one.

    ``PlantedSpeciesLabelsApi.post`` deletes every label and recreates it from
    what is submitted (issues 010, 039), so what the button sends is the whole
    of the state, and a reload has to agree with it.
    """
    drag(editor, number(editor, 11), *empty_space(editor))

    posted = save(editor)

    assert [item['external_ids'] for item in posted
            if item['name_fi'] == NARSISSI] == [[12], [11]]
    editor.reload()
    editor.wait_for_selector('#labels li')
    assert sorted((label['name'], tuple(label['ids']))
                  for label in labels(editor)) == [
        (ESIKKO, ('21',)), (NARSISSI, ('11',)), (NARSISSI, ('12',))]


def test_the_chevrons_change_the_photo_of_that_label_only(editor):
    """Issue 039: the choice belongs to the label, and it is read back.

    Issue 037's line above the sheet promises exactly this, so the sentence is
    under test as much as the code.
    """
    before, esikko = named(editor, NARSISSI), named(editor, ESIKKO)

    editor.locator('#labels li', has_text=NARSISSI).locator(
        '.photo-chooser.next').click()

    chosen = named(editor, NARSISSI)['photo']
    assert chosen != before['photo']
    assert named(editor, ESIKKO)['photo'] == esikko['photo']

    save(editor)
    editor.reload()
    editor.wait_for_selector('#labels li')
    assert named(editor, NARSISSI)['photo'] == chosen
    assert named(editor, ESIKKO)['photo'] == esikko['photo']


def test_a_label_with_one_photo_gets_no_chevrons(editor):
    """They would walk in a circle of one, and the sheet is drawn small."""
    assert editor.locator('#labels li', has_text=ESIKKO).locator(
        '.photo-chooser').count() == 0
    assert editor.locator('#labels li', has_text=NARSISSI).locator(
        '.photo-chooser').count() == 2


def test_the_print_toggle_takes_a_label_out_of_the_print_run(editor):
    """Issue 047: clicking the printer flips the checkbox, which the
    ``<label for="remove">`` it replaced could not do."""
    assert not named(editor, NARSISSI)['hidden']

    editor.locator('#labels li', has_text=NARSISSI).locator(
        '.remove svg').click()

    assert named(editor, NARSISSI)['hidden']
    assert not named(editor, ESIKKO)['hidden']

    save(editor)
    editor.reload()
    editor.wait_for_selector('#labels li')
    assert named(editor, NARSISSI)['hidden']


def test_save_is_disabled_until_something_changes(editor):
    """Nothing to save is not the same as saving nothing, and saving nothing
    would delete every label."""
    assert editor.locator('#save').is_disabled()

    editor.locator('#labels li').first.locator('.remove svg').click()

    assert editor.locator('#save').is_enabled()


def test_saving_without_an_admin_cookie_does_nothing_and_says_nothing(
        page, base_url):
    """What the page does today for a browser that arrives straight at it.

    ``save`` reads the ``csrftoken`` cookie with ``match(...)[1]``, and this
    page sets no such cookie: it renders no ``{% csrf_token %}``, so
    ``CsrfViewMiddleware`` never puts one on the response. Staff reach the
    editor from the admin, where the login form does set it, which is why this
    has never been noticed. Reported in ``docs/issues/incoming.rst``; the
    assertions here are what the code does, so fixing it means changing them.
    """
    page.goto(base_url + LABELS_URL)
    page.wait_for_selector('#labels li')
    page.locator('#labels li').first.locator('.remove svg').click()

    posts = []
    page.on('request', lambda request: posts.append(request)
            if request.method == 'POST' else None)
    page.click('#save')
    page.wait_for_timeout(500)

    assert 'csrftoken' not in [cookie['name']
                               for cookie in page.context.cookies()]
    assert posts == []
    assert any('null' in error or 'undefined' in error
               for error in page.console_errors), page.console_errors


def test_a_truncated_response_leaves_the_editor_empty_rather_than_partial(
        page, base_url):
    """Issue 044, which is why the guard in ``created`` exists.

    axios parses a body that stops mid-string as a plain string rather than
    raising, so a truncated response arrived as a short list in an editor whose
    save deletes and recreates every label. The page must refuse it, say so,
    and offer nothing to save.
    """
    complete = page.request.get(base_url + DATA_URL).text()
    page.route('**' + DATA_URL,
               lambda route: route.fulfill(
                   status=200,
                   content_type='application/json',
                   body=complete[:len(complete) // 2]))
    alerts = []
    page.on('dialog', lambda dialog: (alerts.append(dialog.message),
                                      dialog.dismiss()))

    page.goto(base_url + LABELS_URL)
    page.wait_for_timeout(1000)

    assert page.locator('#labels li').count() == 0
    assert len(alerts) == 1
    assert 'not valid JSON' in alerts[0]
    assert page.locator('#save').is_disabled()
