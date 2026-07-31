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

import pytest

from conftest import (DATA_URL, LABELS_URL, centre, drag, labels, save,
                      touch_drag)

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
    """In numerical order, which is issue 053.

    ``get_labels_data`` used to call ``sorted()`` on the ``Observation``
    instances themselves, which on Python 2 compares them by address, so a
    label's numbers arrived in whatever order the objects happened to sit in.
    The editor's own ``insort`` puts them in numerical order the moment one is
    dragged, so the same label could print "12 11" and then "11 12". This
    version of the test is the one the server can now be held to; the order
    itself is pinned more cheaply in
    ``kasvimuseo/tests/test_views.py::test_labels_api_get_orders_the_museum_numbers_on_a_label``.
    """
    assert [(label['name'], label['ids']) for label in labels(editor)] \
        == [(ESIKKO, ['21']), (NARSISSI, ['11', '12'])]


def test_a_species_planted_only_in_a_private_bed_gets_no_label(editor):
    assert 'sinivuokko' not in [label['name'] for label in labels(editor)]


def test_label_text_fits_and_stays_stable_during_layout_passes(editor):
    """fitty must resize desktop labels without an unbounded feedback loop."""
    editor.wait_for_function("""() =>
        document.querySelector('#labels li h1').style.fontSize
    """)
    editor.evaluate("""() => {
        document.querySelector('#labels li h1').textContent =
            'A name long enough that fitty must make it substantially smaller';
    }""")
    editor.wait_for_function("""() =>
        parseFloat(document.querySelector('#labels li h1').style.fontSize) < 40
    """)

    samples = []
    for _ in range(12):
        editor.evaluate("window.dispatchEvent(new Event('resize'))")
        editor.wait_for_timeout(150)
        samples.append(editor.evaluate("""() => {
        const el = document.querySelector('#labels li h1');
        return parseFloat(getComputedStyle(el).fontSize);
    }"""))
    assert max(samples) / min(samples) < 1.05


def test_ipad_label_text_keeps_the_result_after_fit_observer_is_removed(
        page, base_url):
    """iPad drops fitty's observer without undoing its fitted font size."""
    page.add_init_script("""
        Object.defineProperty(navigator, 'platform', {value: 'MacIntel'});
        Object.defineProperty(navigator, 'maxTouchPoints', {value: 5});
    """)

    def make_name_need_fitting(route):
        response = route.fetch()
        data = response.json()
        for label in data['object_list']:
            label['name_fi'] = (
                'A name long enough that fitty must make it substantially smaller')
        route.fulfill(response=response, json=data)

    page.route('**' + DATA_URL, make_name_need_fitting)
    page.goto(base_url + LABELS_URL)
    page.wait_for_selector('#labels li')
    page.wait_for_function("""() => {
        const el = document.querySelector('#labels li h1');
        return parseFloat(el.style.getPropertyValue('--fit-screen-size')) < 40;
    }""")
    fitted = page.evaluate("""() =>
        parseFloat(document.querySelector('#labels li h1').style
            .getPropertyValue('--fit-screen-size'))
    """)
    printed = page.evaluate("""() =>
        parseFloat(document.querySelector('#labels li h1').style
            .getPropertyValue('--fit-print-size'))
    """)
    assert printed == fitted * 2

    chooser = page.locator('#labels li', has=page.locator(
        '.photo-chooser.next')).first
    if 'vertical' in (chooser.get_attribute('class') or ''):
        chooser.locator('.photo-chooser.next').click()
        page.wait_for_function("""el => el.classList.contains('horizontal')""",
                               arg=chooser.element_handle())
    horizontal_size = chooser.locator('h1').evaluate("""el =>
        parseFloat(el.style.getPropertyValue('--fit-screen-size'))
    """)
    chooser.locator('.photo-chooser.next').click()
    page.wait_for_function("""el => el.classList.contains('vertical')""",
                           arg=chooser.element_handle())
    page.wait_for_function("""([el, oldSize]) =>
        parseFloat(el.querySelector('h1').style
            .getPropertyValue('--fit-screen-size')) < oldSize
    """, arg=[chooser.element_handle(), horizontal_size])

    for _ in range(12):
        page.evaluate("window.dispatchEvent(new Event('resize'))")
        page.wait_for_timeout(150)

    assert page.evaluate("""() =>
        parseFloat(document.querySelector('#labels li h1').style
            .getPropertyValue('--fit-screen-size'))
    """) == fitted


def test_dragging_a_number_onto_the_background_splits_the_label(editor):
    """The editor's reason to exist: two plantings, two labels to print.

    Since issue 045's large half this runs on pointer events rather than HTML5
    drag and drop, so it is the assertion that catches the rewrite breaking the
    interaction for a mouse -- which is the half of it a mouse can still see.
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


def test_a_number_dragged_off_the_sheet_and_released_stays_where_it_was(
        editor):
    """The mouse half of "nothing happens unless it lands somewhere".

    The Save button is over the page, not over the ``<ul>``, so a release there
    is a gesture that ended nowhere: no label takes the number, no label is
    created, and there is nothing to save either.
    """
    before = [(label['name'], label['ids']) for label in labels(editor)]

    drag(editor, number(editor, 11), *centre(editor.locator('#save')))

    assert [(label['name'], label['ids']) for label in labels(editor)] == before
    assert editor.locator('#save').is_disabled()


def test_a_number_moves_between_labels_by_touch(touch_editor):
    """The reported symptom, and the point of the rewrite (issue 045).

    Not one drag but two, because moving a number *between* labels needs a
    second label of the same species first, and splitting one off is how the
    editor makes it. Both are fingers on a touch screen with no mouse anywhere
    near: before the rewrite neither did anything at all, since iOS Safari
    generates no ``dragstart`` from touch and Chromium's touch emulation
    generates none either.
    """
    touch_drag(touch_editor, number(touch_editor, 11),
               *empty_space(touch_editor))

    assert [(label['name'], label['ids']) for label in labels(touch_editor)] \
        == [(ESIKKO, ['21']), (NARSISSI, ['12']), (NARSISSI, ['11'])]

    target = touch_editor.locator('#labels li').nth(1).bounding_box()
    touch_drag(touch_editor, number(touch_editor, 11),
               target['x'] + target['width'] / 2, target['y'] + 20)

    assert [(label['name'], label['ids']) for label in labels(touch_editor)] \
        == [(ESIKKO, ['21']), (NARSISSI, ['11', '12'])]


def test_a_tap_on_a_number_moves_nothing(touch_editor):
    """A finger is never quite still, so a tap has to be told from a drag.

    A press that wobbles a pixel is a tap, and the editor's ``dragMove``
    threshold is what says so; without it a tap could take the number with it
    and put it down somewhere else, which is worse than the defect this fixes.
    The other thing on a label to tap is the print toggle, right beside it.
    """
    before = [(label['name'], label['ids']) for label in labels(touch_editor)]

    touch_editor.touchscreen.tap(*centre(number(touch_editor, 11)))

    assert [(label['name'], label['ids'])
            for label in labels(touch_editor)] == before
    assert touch_editor.locator('#save').is_disabled()


def test_a_touch_gesture_the_system_takes_away_changes_nothing(touch_editor):
    """``pointercancel``: a call arrives, or the finger leaves the digitiser.

    The number has not been taken out of its label at any point during the
    drag -- the sheet is only rearranged on release -- so a cancelled gesture
    has nothing to undo, and this is the assertion that keeps it that way.
    """
    before = [(label['name'], label['ids']) for label in labels(touch_editor)]

    touch_drag(touch_editor, number(touch_editor, 11),
               *empty_space(touch_editor), release='touchCancel')

    assert [(label['name'], label['ids'])
            for label in labels(touch_editor)] == before
    assert touch_editor.locator('#save').is_disabled()
    assert touch_editor.locator('#drag-wrapper').is_hidden()


def test_the_drag_preview_follows_the_finger_at_the_screen_zoom(touch_editor):
    """Issue 046's 50 % zoom, read by the preview so it matches the grid.

    The finger covers the number it is moving, so the preview is the only
    feedback there is about where the number will land; drawn at any other
    scale it would be a label that does not fit the sheet under it. The
    computed ``transform`` is a matrix, which carries both the scale the
    stylesheet's ``--screen-scale`` asked for and where the preview was put.
    """
    x, y = empty_space(touch_editor)
    end = touch_drag(touch_editor, number(touch_editor, 11), x, y,
                     release=None)

    assert touch_editor.locator('#drag-wrapper').is_visible()
    assert [text.strip() for text in
            touch_editor.locator('#drag-wrapper .observation-id')
                        .all_text_contents()] == ['11']
    matrix = touch_editor.evaluate(
        """() => getComputedStyle(document.querySelector('#drag-wrapper'))
                     .transform""")
    scale_x, _, _, scale_y, left, top = [
        float(part) for part in matrix[len('matrix('):-1].split(',')]
    assert (scale_x, scale_y) == (0.5, 0.5)
    # 380 x 120 unscaled pixels into the label is where its numbers sit, so
    # that is the offset the preview is drawn at, at the same 50 %.
    assert (left, top) == pytest.approx((x - 380 * 0.5, y - 120 * 0.5),
                                        abs=0.01)

    end('touchEnd')
    assert len(labels(touch_editor)) == 3
    assert touch_editor.locator('#drag-wrapper').is_hidden()


def test_saving_after_a_touch_drag_persists_the_new_arrangement(touch_editor):
    """The dangerous cycle (issues 010, 044) reached the way the iPad reaches
    it.

    ``PlantedSpeciesLabelsApi.post`` deletes every label and recreates it from
    what is submitted, so a save is only ever as good as what the page holds:
    the button has to be enabled by the drag, send the whole sheet, and the
    reload has to agree with it.
    """
    assert touch_editor.locator('#save').is_disabled()

    touch_drag(touch_editor, number(touch_editor, 11),
               *empty_space(touch_editor))

    assert touch_editor.locator('#save').is_enabled()
    posted = save(touch_editor)

    assert [item['external_ids'] for item in posted
            if item['name_fi'] == NARSISSI] == [[12], [11]]
    touch_editor.reload()
    touch_editor.wait_for_selector('#labels li')
    assert sorted((label['name'], tuple(label['ids']))
                  for label in labels(touch_editor)) == [
        (ESIKKO, ('21',)), (NARSISSI, ('11',)), (NARSISSI, ('12',))]


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


def drop_csrf_cookie(page):
    """Expire the ``csrftoken`` cookie and leave the session alone.

    ``clear_cookies`` would take the session with it, which is a different
    failure -- that one is the 403 below.
    """
    page.evaluate("() => { document.cookie = "
                  "'csrftoken=; Max-Age=0; path=/'; }")
    assert 'csrftoken' not in [cookie['name']
                               for cookie in page.context.cookies()]


def test_the_page_issues_the_csrf_cookie_its_own_save_needs(page, base_url):
    """Issue 052: the editor no longer depends on some other page's cookie.

    ``save`` reads ``csrftoken`` out of ``document.cookie``, and the page used
    to render no token, so ``CsrfViewMiddleware`` set none: for a browser that
    had not been given one elsewhere, the read threw inside the click handler
    and the button did nothing and said nothing. The cookie is dropped here to
    reproduce exactly that -- a session that outlives it, or one refused and
    re-granted -- and the reload has to be enough to put it back.
    """
    page.goto(base_url + LABELS_URL)
    page.wait_for_selector('#labels li')
    drop_csrf_cookie(page)

    page.reload()
    page.wait_for_selector('#labels li')

    assert 'csrftoken' in [cookie['name'] for cookie in page.context.cookies()]

    page.locator('#labels li').first.locator('.remove svg').click()
    save(page)

    page.reload()
    page.wait_for_selector('#labels li')
    assert labels(page)[0]['hidden']
    assert [error for error in page.console_errors
            if 'TypeError' in error] == []


def test_saving_with_no_cookie_says_so_rather_than_nothing(page, base_url):
    """The failure mode left over: the cookie can still be absent.

    Cookies refused for the site, or a sheet left open past the cookie's life,
    and the request would be rejected whatever it sent. What issue 052 removes
    is the silence, not the dependency, so the button has to say why it did
    nothing.
    """
    page.goto(base_url + LABELS_URL)
    page.wait_for_selector('#labels li')
    page.locator('#labels li').first.locator('.remove svg').click()
    drop_csrf_cookie(page)

    alerts = []
    page.on('dialog', lambda dialog: (alerts.append(dialog.message),
                                      dialog.dismiss()))
    posts = []
    page.on('request', lambda request: posts.append(request)
            if request.method == 'POST' else None)
    page.click('#save')
    page.wait_for_timeout(500)

    assert posts == []
    assert len(alerts) == 1
    assert 'csrftoken' in alerts[0]
    assert [error for error in page.console_errors
            if 'TypeError' in error] == []


def test_the_editor_and_its_endpoint_are_staff_only(anonymous_page, base_url):
    """Issue 052's other half: not logged in, nothing to see and nothing to do.

    ``PlantedSpeciesLabelsApi.post`` deletes every label and rebuilds the table
    from the request body, and until this gate it ran for anyone who knew the
    URL. The page answers with the admin's login form -- Django 1.5 renders it
    at the requested URL with a 200 rather than redirecting -- and the endpoint
    answers 403, because a login page behind a 200 is what axios cannot tell
    from a saved sheet.
    """
    anonymous_page.goto(base_url + LABELS_URL)

    assert anonymous_page.locator('#labels li').count() == 0
    assert anonymous_page.locator('input[name="password"]').count() == 1

    assert anonymous_page.request.get(base_url + DATA_URL).status == 403

    # The POST carries the token the login page just handed this browser, so
    # ``CsrfViewMiddleware`` is satisfied and the 403 below is the staff check
    # refusing it rather than the CSRF check. That is the whole of what an
    # outsider had to do before this gate existed.
    token, = [cookie['value'] for cookie in anonymous_page.context.cookies()
              if cookie['name'] == 'csrftoken']
    refused = anonymous_page.request.post(
        base_url + DATA_URL, data=[], headers={'X-CSRFToken': token})

    assert refused.status == 403
    assert 'staff' in refused.text()


def test_a_save_the_server_refuses_says_so(page, base_url):
    """A session that expires under an open sheet must not fail quietly.

    The gate turns that into a 403, and a rejected save used to reach the
    console and nowhere else -- the same silence the missing token caused.
    """
    page.goto(base_url + LABELS_URL)
    page.wait_for_selector('#labels li')
    page.locator('#labels li').first.locator('.remove svg').click()
    page.route('**' + DATA_URL,
               lambda route: route.fulfill(status=403,
                                           content_type='text/plain',
                                           body='staff only')
               if route.request.method == 'POST' else route.fallback())

    alerts = []
    page.on('dialog', lambda dialog: (alerts.append(dialog.message),
                                      dialog.dismiss()))
    page.click('#save')
    page.wait_for_timeout(500)

    assert len(alerts) == 1
    assert '403' in alerts[0]
    assert page.locator('#save').is_enabled()


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
