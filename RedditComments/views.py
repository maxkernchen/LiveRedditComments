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
__author__  = 'Max Kernchen'
__version__ = '1.0.'
__email__   = 'max.f.kernchen@gmail.com'


def index(request):
    """ Method for loading the index page. Defined in URLS.py
    Will load the active submissions by calling query_active_submissions in active_submissions module

    @return - a rendered page for our homepage index.html
    """
    return render(request, 'index.html', {'active_submissions_template':
                                              active_submissions.query_active_submissions()})

def process_reddit_url(request):
    """
    Method for loading the comments page, will be used for both POST (original form submission) and GET
    (ajax in-page refresh request) requests. Defined in URLS.py

    @return - a rendered page for /process_url or in case of errors /index.html with an error message
    """
    # if this is a POST request we need to process the form data
    comments = ['No Results Found']

    if request.method == 'POST':
        form = RedditURL(request.POST)

        if form.is_valid():
            comment_url = form.cleaned_data['reddit_url']
            submission_id = comment_stream.parse_submission_id(comment_url)
            logger.info('Starting new stream for sub_id=' + submission_id)

            # initialize the cookie for storing alreay loaded comments, will be populated in comment stream call
            request.session['loaded_comments_cookie'] = []
            submission_comments_dict = comment_stream.get_comments(submission_id, request, True)
            if(submission_comments_dict is None):
                return render(request, 'index.html', {'error': 'invalid url', 'active_submissions_template':
                    active_submissions.query_active_submissions()})
            submission_title = submission_comments_dict['title']
            submission_permalink = submission_comments_dict['permalink']
            comments = submission_comments_dict['comments']
            # Comments is None if any exceptions occur on the PRAW side
            if comments is not None  and submission_title is not None and \
                    submission_permalink is not None:
                return render(request, 'comments.html', {'comments_template':
                comments,'title_template':submission_title,
                'post_url_template':submission_permalink})
            else:
                # return with a error message defiend in the HTML template
                return render(request, 'index.html', {'error': 'invalid url', 'active_submissions_template':
                                              active_submissions.query_active_submissions()})
        else:
            # return with a error message defiend in the HTML template
            return render(request, 'index.html', {'error': 'invalid url', 'active_submissions_template':
                                              active_submissions.query_active_submissions()})
    # ajax call for refresh will be a GET request
    if request.method == 'GET':
        # pull session cookie for comment url
        submission_id_get = comment_stream.parse_ajax_submission_id(request.path)
        if submission_id_get:
            comments_dict = comment_stream.get_comments(submission_id_get, request, False)
            comment_list = comments_dict['comments']
            if(comment_list is not None and len(comment_list) > 0):
                return render(request, 'comment_body.html', {'comments_template': comment_list})
            else:
                # Status 204 is okay for ajax response as it will then just call again after the refresh rate.
                return HttpResponse(status=204)





