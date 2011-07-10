from django.template import Library

from ..models import LIGHTINGS_VERBOSE


register = Library()


@register.filter
def lighting_name(number):
    if number:
        return dict(LIGHTINGS_VERBOSE)[number]
    return u''
