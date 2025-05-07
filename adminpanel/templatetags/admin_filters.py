from django import template

register = template.Library()

@register.filter
def status_color(value):
    """Return a Bootstrap color class based on the value"""
    try:
        value = float(value)
        if value < 50:
            return 'success'
        elif value < 80:
            return 'warning'
        else:
            return 'danger'
    except (ValueError, TypeError):
        return 'secondary' 