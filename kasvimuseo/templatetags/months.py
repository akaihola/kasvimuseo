from django.template import Library

from ..models import MONTHS


register = Library()


@register.filter
def month_name(number):
    if number:
        return MONTHS[number]
    return u''
