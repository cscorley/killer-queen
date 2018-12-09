from django.template import Library

register = Library()

@register.filter
def divide(value, arg):
    try:
        if arg:
            return value / arg
        else:
            return value
    except (ValueError, ZeroDivisionError):
        return None
