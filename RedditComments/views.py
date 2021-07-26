from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader
from django.contrib import messages
from django.contrib.sessions import middleware
from django.http import JsonResponse
from .forms import RedditURL
from . import comment_stream
from . import active_submissions
from RedditComments.models import ActiveSubmissions
import logging
logger = logging.getLogger(__name__)




"""
Method for loading the index page. Defined in URLS.py
param: request - request object that expects a response
"""
def index(request):
    return render(request, 'index.html', {'active_submissions_template':
                                              active_submissions.query_active_submissions()})

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
            submission_id = comment_stream.parse_submission_id(comment_url)
            logger.info('Starting new stream for sub_id=' + submission_id)

            request.session['submission_id'] = submission_id
            # initialize the cookie for storing alreay loaded comments, will be populated in comment stream call
            request.session['loaded_comments_cookie'] = []
            comments = comment_stream.get_comments(submission_id, request)

            # Comments is None if any exceptions occur on the PRAW side
            if comments is not None and len(comments) > 0:
                return render(request, 'comments.html', {'comments_template':
                comments,'title_template':comment_stream.get_submission_title(submission_id),
                'post_url_template':comment_stream.get_submission_permalink(submission_id)})
            else:
                return render(request, 'index.html', {'error': 'invalid url', 'active_submissions_template':
                                              active_submissions.query_active_submissions()})
        else:
            # form found to be not valid.
            return render(request, 'index.html', {'error': 'invalid url', 'active_submissions_template':
                                              active_submissions.query_active_submissions()})
    # ajax call for refresh will be a GET request
    if request.method == 'GET':
        # pull session cookie for comment url
        submission_id_get = request.session['submission_id']
        if submission_id_get:
            comments = comment_stream.get_comments(submission_id_get, request)
            if(comments is not None and len(comments) > 0):
                return render(request, 'comment_body.html', {'comments_template': comments})
            else:
                return HttpResponse(status=204)





