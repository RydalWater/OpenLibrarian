from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Custom filter to get a dictionary item by key in Django templates."""
    return dictionary.get(key, "")