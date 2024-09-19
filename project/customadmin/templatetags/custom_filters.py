from django import template

register = template.Library()

@register.filter
def is_active(request, url_segment):
    """
    Check if the current request path matches the URL segment
    or contains it with a trailing slash.
    """
    print('request.path.startswith(url_segment): ', url_segment)
    if hasattr(request, 'path'):
        return request.path.startswith(url_segment)
    return False

@register.filter
def is_active_common(request, url_segment):
    """
    Check if the current request path matches the URL segment
    or contains it with a trailing slash.
    """
    if hasattr(request, 'path'):
        return url_segment in request.path
    return False
