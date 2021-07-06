from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader
from django.contrib import messages
from django.contrib.sessions import middleware
from django.http import JsonResponse
from .forms import RedditURL
from . import comment_stream


"""
Method for loading the index page. Defined in URLS.py
param: request - request object that expects a response
"""
def index(request):
    return render(request, 'index.html')

"""
Method for loading the index page for a new stream, this page does not use any faded in elements. Defined in URLS.py
param: request - request object that expects a response
"""


def index_new_stream(request):
    return render(request, 'index_no_fade_in.html')


"""
Method for loading the comments page, will be used for both POST (original form submission) and GET 
(ajax in-page refresh request) requests. Defined in URLS.py
param: request - request object that expects a response
"""

def process_reddit_url(request):
    # if this is a POST request we need to process the form data
    comments = ['No Results Found']

    if request.method == 'POST':
        form = RedditURL(request.POST)

        if form.is_valid():
            comment_url = form.cleaned_data['reddit_url']
            # to persist the URL for future ajax calls.
            request.session['comment_url_cookie'] = comment_url
            # initialize the cookie for storing alreay loaded comments, will be populated in comment stream call
            request.session['loaded_comments_cookie'] = []
            comments = comment_stream.get_comments(comment_stream, form.cleaned_data['reddit_url'], request)

            # Comments is None if any exceptions occur on the PRAW side
            if comments is not None and len(comments) > 0:
                return render(request, 'comments.html', {'comments_template': comments})
            else:
                return render(request, 'index_no_fade_in.html', {'error': 'invalid url'})
        else:
            # form found to be not valid.
            return render(request, 'index_no_fade_in.html', {'error': 'invalid url'})
    # ajax call for refresh will be a GET request
    if request.method == 'GET':
        # pull session cookie for comment url
        comment_url_get = request.session['comment_url_cookie']
        if comment_url_get:
            comments = comment_stream.get_comments(comment_stream, comment_url_get.strip(), request)
            if(len(comments) > 0):
                return render(request, 'comment_body.html', {'comments_template': comments})
            else:
                return HttpResponse(status=204)





