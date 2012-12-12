from django import template
register = template.Library()

@register.filter(name='get_attr')
def get_attr(obj, key):
	return obj.__dict__.get(key)

@register.filter(name='replace')
def get_attr(value, repl):
	return value.replace(repl, ' ')