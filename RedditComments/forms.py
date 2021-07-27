from django import forms
__author__  = 'Max Kernchen'
__version__ = '1.0.'
__email__   = 'max.f.kernchen@gmail.com'

""" forms.py - our only field is reddit_url is which on the index page.
"""
class RedditURL(forms.Form):
    reddit_url = forms.CharField(label='reddit_url', max_length=300)




