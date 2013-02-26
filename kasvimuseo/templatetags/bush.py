from django.template import Library

register = Library()


@register.filter
def bush_shadow(planting):
    reduction = min(planting.width, planting.depth)
    return (u'width: {width}em;'
            u'height: {depth}em;'
            u'left: {left}em;'
            u'top: {top}em;'
            u'box-shadow: 0px 0px {half_radius}em {half_radius}em rgba(0, 255, 0, 1);'
            .format(width=planting.width - reduction,
                    depth=planting.depth - reduction,
                    left=reduction / 2.0,
                    top=reduction / 2.0,
                    half_radius=reduction / 2.0))

