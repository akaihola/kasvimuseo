# -*- coding: utf-8 -*-
"""Choosing between species that share a Finnish name.

``Species.name_fi`` carries no unique constraint, so a photo whose title names
a species can match more than one of them. Issue 002 made that case skip the
auto-attach rather than raise; this module is the refinement that tries to
narrow the match down to one first, and only skips when it cannot.

The narrowing is evidence about which of the namesakes is the plant actually
standing in the garden, applied as a cascade:

1. it has been observed at all;
2. one of those observations has a planting that has not been removed;
3. it has labels;
4. of the survivors, the one whose living plantings were cared for most
   recently;
5. of the survivors, the one whose own names -- and the names of the places its
   observations come from -- best match the photo's file name;
6. failing all that, the one that has no photo yet.

Steps 1 to 3 are filters, and a filter that would leave nothing is skipped
rather than applied: absent evidence is not evidence against. Steps 4 to 6
rank, and the first of them that separates the field decides.

The last step attaches a photo on a resemblance, so it can be wrong where the
code it replaces merely did nothing. Two things bound that: a candidate has to
clear ``MATCH_THRESHOLD`` on a field before that field counts for it at all,
and the winner has to beat the runner-up by ``WINNING_MARGIN``. Anything less
conclusive than that returns ``None`` and the photo stays unattached, which is
the behaviour issue 002 settled on.

Nothing here imports ``kasvimuseo.models`` -- that module imports this one --
so the species arrive as a queryset and everything else is reached through it.

Not to be confused with ``kasvimuseo.photos``, which matches the same two
things in the other direction, by title rather than by file name, for the
public site. Issue 003 is about the case-folding the two do differently, and
touches both.
"""

from __future__ import unicode_literals

import difflib
import re
import unicodedata

from django.db.models import Max

#: How alike a candidate's field and a piece of the file name have to be before
#: that field is counted as naming the candidate. Ratios below this are noise:
#: two unrelated Finnish plant names routinely score around 0.5.
MATCH_THRESHOLD = 0.85

#: How far ahead of the runner-up the winner has to be. Scores are sums of
#: ratios, so a lead this small means the two are corroborated by the same
#: number of fields and the photo does not tell them apart.
WINNING_MARGIN = 0.05

#: Longest run of file name words compared as one string, so that a two-word
#: place name still matches the file name it was written into.
MAX_WINDOW = 4

_SEPARATORS = re.compile(r'[^0-9a-z]+')


def normalize(text):
    """Split ``text`` into lowercase, unaccented, alphanumeric words.

    Total by construction: anything it cannot make sense of becomes no words.
    ``ä`` and ``ö`` decompose to ``a`` and ``o``, which is what a file name
    written on a Finnish keyboard and one written on somebody's phone have in
    common.
    """
    if not text:
        return []
    if isinstance(text, bytes):
        text = text.decode('utf-8', 'ignore')
    decomposed = unicodedata.normalize('NFKD', text)
    unaccented = ''.join(character for character in decomposed
                         if not unicodedata.combining(character))
    return [word for word in _SEPARATORS.split(unaccented.lower()) if word]


def filename_targets(filename):
    """Return the strings a candidate's fields are compared against.

    Every run of up to ``MAX_WINDOW`` consecutive words of the file name, joined
    up, plus the whole name joined up. The runs are what let ``Iso Mattila``
    match ``narsissi-iso-mattila.jpg``: as separate words neither half of the
    place name resembles it, and as one string the file name is too long.
    """
    words = normalize(_basename(filename))
    targets = set()
    for start in range(len(words)):
        for end in range(start + 1, min(start + MAX_WINDOW, len(words)) + 1):
            targets.add(''.join(words[start:end]))
    targets.add(''.join(words))
    targets.discard('')
    return targets


def _basename(filename):
    if not filename:
        return ''
    tail = filename.replace('\\', '/').rsplit('/', 1)[-1]
    return tail.rsplit('.', 1)[0] if '.' in tail else tail


def best_ratio(value, targets):
    """How well ``value`` matches the closest of ``targets``, from 0 to 1."""
    words = normalize(value)
    if not words or not targets:
        return 0.0
    joined = ''.join(words)
    return max(difflib.SequenceMatcher(None, joined, target).ratio()
               for target in targets)


def candidate_strings(species):
    """Every name that could have been written into a photo's file name.

    The species' own botanical and Finnish names, and for each observation of
    it the nickname it goes by and where it came from -- photographs get named
    after the house they were taken at at least as often as after the plant.
    """
    values = [species.name_fi, species.genus, species.group, species.species,
              species.subspecies, species.variety]
    for observation in species.observation_set.select_related('origin').all():
        values.append(observation.nickname)
        origin = observation.origin
        if origin is not None:
            values.extend([origin.name, origin.alias, origin.village])
    seen = set()
    strings = []
    for value in values:
        key = ''.join(normalize(value))
        if key and key not in seen:
            seen.add(key)
            strings.append(value)
    return strings


def similarity_score(species, targets):
    """Sum of the ratios of the fields that name ``species`` in the file name.

    A sum rather than the best single ratio, so that a file name corroborated
    by two fields -- the plant and the house it came from -- beats one that
    only repeats the Finnish name both candidates already share.
    """
    total = 0.0
    for value in candidate_strings(species):
        ratio = best_ratio(value, targets)
        if ratio >= MATCH_THRESHOLD:
            total += ratio
    return total


def disambiguate(candidates, filename):
    """Return the one species ``filename``'s photo belongs to, or ``None``.

    ``None`` means the evidence does not separate the candidates, and the
    caller should leave every one of them alone.
    """
    narrowed = candidates
    for lookup in ({'observation__isnull': False},
                   {'observation__planting__removal_date__isnull': True},
                   {'label__isnull': False}):
        narrowed = _narrowed(narrowed, lookup)
    survivors = list(narrowed.distinct())
    if not survivors:
        return None
    if len(survivors) == 1:
        return survivors[0]
    return (_most_recently_cared(candidates.model, survivors)
            or _most_similar(survivors, filename_targets(filename))
            or _the_one_still_without_a_photo(survivors))


def _narrowed(queryset, lookup):
    """Apply ``lookup`` unless it would leave nothing to choose between."""
    narrowed = queryset.filter(**lookup).distinct()
    return narrowed if narrowed.exists() else queryset


def _most_recently_cared(model, survivors):
    """The survivor whose *living* plantings were cared for most recently.

    ``None`` when nothing was cared for, or when two were cared for on the same
    day.

    The query is built from scratch rather than from the narrowed queryset,
    and the removal date and the aggregate go in one ``filter()`` call. Both
    matter: each ``filter()`` call across a multi-valued relation joins the
    table again, so a query that has already been narrowed by removal date
    would end up aggregating over a *second*, unconstrained join and would
    happily answer with the date a plant was last cared for before it was dug
    up.
    """
    dates = dict(
        model._default_manager
        .filter(pk__in=[species.pk for species in survivors],
                observation__planting__removal_date__isnull=True)
        .annotate(last_care=Max('observation__planting__care__date'))
        .values_list('pk', 'last_care'))
    cared = [(dates[species.pk], species) for species in survivors
             if dates.get(species.pk) is not None]
    if not cared:
        return None
    latest = max(date for date, _species in cared)
    winners = [species for date, species in cared if date == latest]
    return winners[0] if len(winners) == 1 else None


def _the_one_still_without_a_photo(survivors):
    """The last resort: the namesake that has no photo yet.

    Since issue 042 a photo replaces the one a species already has, so having
    one is no longer a reason to be passed over -- but when nothing else
    separates two namesakes, the one with an empty slot is the better guess,
    and it keeps the behaviour that was there before 042 for the case that used
    to be the only one this receiver could reach.
    """
    photoless = [species for species in survivors if species.photo_id is None]
    return photoless[0] if len(photoless) == 1 else None


def _most_similar(survivors, targets):
    """The survivor the file name names, if it names one of them clearly."""
    scored = sorted(((similarity_score(species, targets), species)
                     for species in survivors),
                    key=lambda pair: pair[0],
                    reverse=True)
    best, runner_up = scored[0][0], scored[1][0]
    if best > 0 and best - runner_up >= WINNING_MARGIN:
        return scored[0][1]
    return None
