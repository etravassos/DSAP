from django import template
from random import randint
from django.utils.safestring import mark_safe
from django.contrib.staticfiles.storage import staticfiles_storage

register = template.Library()

@register.simple_tag
def random_intnumber(length=5):
    """
    Create a random integer with given length.
    For a length of 3 it will be between 100 and 999.
    For a length of 4 it will be between 1000 and 9999.
    """
    return randint(10**(length-1), (10**(length)-1))
    
@register.simple_tag
def javascript(filename, type='text/javascript'):
    """A simple shortcut to render a ``script`` tag to a static javascript file"""
    
    if '?' in filename and len(filename.split('?')) is 2:
        filename, params = filename.split('?')
        return mark_safe('<script type="{}" src="{}?{}"></script>'
                    .format(type, staticfiles_storage.url(filename), params))
    else:
        return mark_safe('<script type="{}" src="{}"></script>'
                    .format(type, staticfiles_storage.url(filename)))


@register.simple_tag
def js(filename, type='text/javascript'):
    """A simple shortcut"""
    
    return javascript(filename, type=type)


@register.simple_tag
def css(filename):
    """A simple shortcut to render a ``link`` tag to a static CSS file"""
    
    return mark_safe('<link rel="stylesheet" type="text/css" href="{}" />'
                .format(staticfiles_storage.url(filename)))