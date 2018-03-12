from django.template import Library


register = Library()


@register.filter
def get_photo_orientation(photo, threshold=3.1/4.0):
    width, height = photo.get_display_size()
    aspect_ratio = float(width) / height
    return 'vertical' if aspect_ratio < threshold else 'horizontal'
