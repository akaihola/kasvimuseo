"""Django's ``admin_list``, with the field name in each cell's ``class``.

A copy-and-modify fork of ``django/contrib/admin/templatetags/admin_list.py``
carrying the patch from Django ticket #11195, which Django closed itself in
1.7 -- so this file is deleted at upgrade plan Stage 5, which is the ruling on
issue 034. Until then it is re-synced against Django's own copy at every stage
that moves the framework, because the delta below is small and everything
around it is Django's.

Synced against **Django 1.6** at Stage 3. What that stage brought, both in
``items_for_result`` and neither of them this project's idea:

* ``add_preserved_filters`` on the link out of each row. 1.6 introduced the
  ``_changelist_filters`` parameter that takes a changelist's filters through
  a change form and back; without this line the fork's changelists are the
  only ones in the admin that lose them.
* ``escapejs`` and explicit quotes in the ``dismissRelatedLookupPopup`` call,
  replacing ``repr(force_text(value))[1:]``. Only reachable from a raw-id
  popup, which no ``ModelAdmin`` here opens, but it is Django's fix rather
  than an option.

1.6 also started putting a ``column-<field>`` class on each header; it is kept
beside this fork's ``fieldname_<field>`` rather than replaced by it, so a
changelist rendered through this tag carries everything an unforked one does.
"""

from __future__ import unicode_literals

import datetime
from django.contrib.admin.templatetags.admin_list import (
    result_hidden_fields, result_headers, ResultList)
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
from django.contrib.admin.util import (
    lookup_field, display_for_field, display_for_value, label_for_field)
from django.contrib.admin.views.main import EMPTY_CHANGELIST_VALUE, ORDER_VAR
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.template import Library
from django.utils.encoding import smart_str, force_text, force_unicode
from django.utils.html import escapejs, format_html
from django.utils.safestring import mark_safe


register = Library()


def identifier_for_field(name, model, model_admin=None):
    attr = None
    try:
        field = model._meta.get_field_by_name(name)[0]
        return name
    except models.FieldDoesNotExist:
        if name == "__unicode__":
            return force_unicode(model._meta.module_name)
        elif name == "__str__":
            return smart_str(model._meta.module_name)
        else:
            if callable(name):
                attr = name
            elif model_admin is not None and hasattr(model_admin, name):
                attr = getattr(model_admin, name)
            elif hasattr(model, name):
                attr = getattr(model, name)
            else:
                message = "Unable to lookup '%s' on %s" % (name, model._meta.object_name)
                if model_admin:
                    message += " or %s" % (model_admin.__name__,)
                raise AttributeError(message)

            if hasattr(attr, "name"):
                label = attr.name
            elif callable(attr):
                if attr.__name__ == "<lambda>":
                    return "__lambda__"
                else:
                    return attr.__name__
    return '__unknown__'


def result_headers(cl):
    """
    Generates the list column headers.
    """
    ordering_field_columns = cl.get_ordering_field_columns()
    for i, field_name in enumerate(cl.list_display):
        text, attr = label_for_field(field_name, cl.model,
            model_admin = cl.model_admin,
            return_attr = True
        )
        if attr:
            # Potentially not sortable

            # if the field is the action checkbox: no sorting and special class
            if field_name == 'action_checkbox':
                yield {
                    "text": text,
                    "class_attrib": mark_safe(' class="action-checkbox-column"'),
                    "sortable": False,
                }
                continue

            admin_order_field = getattr(attr, "admin_order_field", None)
            if not admin_order_field:
                # Not sortable
                yield {"text": text,
                       "sortable": False,
                       "class_attrib": format_html(
                           ' class="column-{0} fieldname_{1}"',
                           field_name,
                           identifier_for_field(
                               field_name,
                               cl.model,
                               model_admin=cl.model_admin))}
                continue

        # OK, it is sortable if we got this far
        th_classes = ['sortable',
                      'column-{0}'.format(field_name),
                      'fieldname_{0}'.format(
                          identifier_for_field(field_name,
                                               cl.model,
                                               model_admin=cl.model_admin))]
        order_type = ''
        new_order_type = 'asc'
        sort_priority = 0
        sorted = False
        # Is it currently being sorted on?
        if i in ordering_field_columns:
            sorted = True
            order_type = ordering_field_columns.get(i).lower()
            sort_priority = list(ordering_field_columns).index(i) + 1
            th_classes.append('sorted %sending' % order_type)
            new_order_type = {'asc': 'desc', 'desc': 'asc'}[order_type]

        # build new ordering param
        o_list_primary = [] # URL for making this field the primary sort
        o_list_remove  = [] # URL for removing this field from sort
        o_list_toggle  = [] # URL for toggling order type for this field
        make_qs_param = lambda t, n: ('-' if t == 'desc' else '') + str(n)

        for j, ot in ordering_field_columns.items():
            if j == i: # Same column
                param = make_qs_param(new_order_type, j)
                # We want clicking on this header to bring the ordering to the
                # front
                o_list_primary.insert(0, param)
                o_list_toggle.append(param)
                # o_list_remove - omit
            else:
                param = make_qs_param(ot, j)
                o_list_primary.append(param)
                o_list_toggle.append(param)
                o_list_remove.append(param)

        if i not in ordering_field_columns:
            o_list_primary.insert(0, make_qs_param(new_order_type, i))


        yield {
            "text": text,
            "sortable": True,
            "sorted": sorted,
            "ascending": order_type == "asc",
            "sort_priority": sort_priority,
            "url_primary": cl.get_query_string({ORDER_VAR: '.'.join(o_list_primary)}),
            "url_remove": cl.get_query_string({ORDER_VAR: '.'.join(o_list_remove)}),
            "url_toggle": cl.get_query_string({ORDER_VAR: '.'.join(o_list_toggle)}),
            "class_attrib": format_html(' class="{0}"', ' '.join(th_classes))
                            if th_classes else '',
        }


def items_for_result(cl, result, form):
    """
    Generates the actual list of data.

    This is the version which adds field names as cell classes, taken from
    http://code.djangoproject.com/ticket/11195
    """
    first = True
    pk = cl.lookup_opts.pk.attname
    for field_name in cl.list_display:
        row_classes = ['fieldname_%s' % identifier_for_field(
            field_name, cl.model, model_admin=cl.model_admin)]
        try:
            f, attr, value = lookup_field(field_name, result, cl.model_admin)
        except ObjectDoesNotExist:
            result_repr = EMPTY_CHANGELIST_VALUE
        else:
            if f is None:
                if field_name == 'action_checkbox':
                    row_classes.append('action-checkbox')
                allow_tags = getattr(attr, 'allow_tags', False)
                boolean = getattr(attr, 'boolean', False)
                if boolean:
                    allow_tags = True
                result_repr = display_for_value(value, boolean)
                # Strip HTML tags in the resulting text, except if the
                # function has an "allow_tags" attribute set to True.
                if allow_tags:
                    result_repr = mark_safe(result_repr)
                if isinstance(value, (datetime.date, datetime.time)):
                    row_classes.append('nowrap')
            else:
                if isinstance(f.rel, models.ManyToOneRel):
                    field_val = getattr(result, f.name)
                    if field_val is None:
                        result_repr = EMPTY_CHANGELIST_VALUE
                    else:
                        result_repr = field_val
                else:
                    result_repr = display_for_field(value, f)
                if isinstance(f, (models.DateField, models.TimeField, models.ForeignKey)):
                    row_classes.append('nowrap')
        if force_text(result_repr) == '':
            result_repr = mark_safe('&nbsp;')
        row_class = mark_safe(' class="%s"' % ' '.join(row_classes))
        # If list_display_links not defined, add the link tag to the first field
        if (first and not cl.list_display_links) or field_name in cl.list_display_links:
            table_tag = {True:'th', False:'td'}[first]
            first = False
            url = cl.url_for_result(result)
            url = add_preserved_filters({'preserved_filters': cl.preserved_filters, 'opts': cl.opts}, url)
            # Convert the pk to something that can be used in Javascript.
            # Problem cases are long ints (23L) and non-ASCII strings.
            if cl.to_field:
                attr = str(cl.to_field)
            else:
                attr = pk
            value = result.serializable_value(attr)
            result_id = escapejs(value)
            yield format_html('<{0}{1}><a href="{2}"{3}>{4}</a></{5}>',
                              table_tag,
                              row_class,
                              url,
                              format_html(' onclick="opener.dismissRelatedLookupPopup(window, &#39;{0}&#39;); return false;"', result_id)
                                if cl.is_popup else '',
                              result_repr,
                              table_tag)
        else:
            # By default the fields come from ModelAdmin.list_editable, but if we pull
            # the fields out of the form instead of list_editable custom admins
            # can provide fields on a per request basis
            if (form and field_name in form.fields and not (
                    field_name == cl.model._meta.pk.name and
                        form[cl.model._meta.pk.name].is_hidden)):
                bf = form[field_name]
                result_repr = mark_safe(force_text(bf.errors) + force_text(bf))
            yield format_html('<td{0}>{1}</td>', row_class, result_repr)
    if form and not form[cl.model._meta.pk.name].is_hidden:
        yield format_html('<td>{0}</td>', force_text(form[cl.model._meta.pk.name]))


def results(cl):
    if cl.formset:
        for res, form in zip(cl.result_list, cl.formset.forms):
            yield ResultList(form, items_for_result(cl, res, form))
    else:
        for res in cl.result_list:
            yield ResultList(None, items_for_result(cl, res, None))


@register.inclusion_tag("admin/change_list_results.html")
def result_list_with_fieldnames_in_classes(cl):
    """
    Displays the headers and data list together
    """
    headers = list(result_headers(cl))
    num_sorted_fields = 0
    for h in headers:
        if h['sortable'] and h['sorted']:
            num_sorted_fields += 1
    return {'cl': cl,
            'result_hidden_fields': list(result_hidden_fields(cl)),
            'result_headers': headers,
            'num_sorted_fields': num_sorted_fields,
            'results': list(results(cl))}
