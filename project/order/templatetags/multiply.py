from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiply the value by the argument."""
    try:
        return float(value) * float(arg)
    except (TypeError, ValueError):
        return 0  # Return 0 in case of an error