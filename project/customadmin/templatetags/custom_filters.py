from django import template

register = template.Library()

@register.filter
def is_active(request, url_segment):
    """ Check if the current request path contains the URL segment """
    if hasattr(request, 'path'):
        return url_segment in request.path
    return False