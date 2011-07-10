from django.template import Library

from ..models import LIGHTINGS_VERBOSE


register = Library()


@register.filter
def lighting_name(number):
    return LIGHTINGS_VERBOSE[number]
