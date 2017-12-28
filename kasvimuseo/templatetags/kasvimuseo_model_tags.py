from django.template import Library


register = Library()


@register.filter
def nicknames(observations):
    return [observation.nickname
            for observation in observations.exclude(nickname__exact='')]


@register.filter
def external_ids(observations):
    return sorted(observation.external_id for observation in observations)
