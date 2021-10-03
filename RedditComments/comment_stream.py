from datetime import datetime
import configparser
import praw
import praw.config
import praw.exceptions
import praw.models.reddit.more
import prawcore.exceptions
import requests
from praw.models import MoreComments
from pathlib import Path
import os
__author__  = 'Max Kernchen'
__version__ = '1.0.'
__email__   = 'max.f.kernchen@gmail.com'

""" This module's main purpose is to retreive the latest comments from a submission, it is called often via ajax or the 
post request from our index form submission.
"""

def get_comments(submission_id, views_request, is_post):
    """ Method get_comments will take in a submission_id (6 character alphanumeric value) from views.py
        and find the submission/newest comments. These comments are then compared to already loaded comments
        stored in the session cookie. Any comments comments that different from the already loaded ones are returned to
        views.py in a formatted string.
        ----params-----
        @submission_id - the 6 char alphanumeric value that represents a submission
        @views_request - the request object from views.py, this is passed in to update the session cookie.
        @is_post       - the request is a POST so we will need additonal info returned in our dictionary

        @return a dictionary with comments sorted by newest, the title and permalink if this is a POST request
    """
    config = configparser.ConfigParser()
    config_dir = Path(os.getcwd() + '/RedditComments/praw.ini')
    config.read(config_dir)

    reddit_obj = praw.Reddit(client_id=config['bot1']['client_id'],
                             client_secret=config['bot1']['client_secret'],
                             user_agent=config['bot1']['user_agent'])

    try:
        submission = reddit_obj.submission(id=submission_id)
        # only get the newest comments
        submission.comment_sort = 'new'
        comment_list = list(submission.comments)
    except (praw.exceptions.PRAWException, prawcore.PrawcoreException,
            praw.exceptions.RedditAPIException) as e:
        # None is okay to return as views.py will handle this appropriately
        return None

    i = 0
    comments_sorted = []
    comments_cookie = []
    # get session cookie which stored the previous list of loaded comments
    already_loaded_comments = views_request.session['loaded_comments_cookie']
    for comment in comment_list:
        if isinstance(comment, MoreComments):
            # for now we are only streaming top-level comments, no replies
            continue
        comments_sorted.append(comment)
        # store just the comment id hex value to only load new comments between ajax calls
        comments_cookie.append(comment.id)

    comments_returned = []
    for comment in comments_sorted:
        i += 1
        # don't track deleted comments or comments which we've already loaded
        if(comment.author is not None and comment.id not in already_loaded_comments and not comment.stickied):
            comments_returned.append(comment.author.name + " - " +
                                     str(datetime.fromtimestamp(comment.created_utc)) + " - " +
                                     detect_hyper_link(comment.body))

    #update session cookie with newly streamed comments
    views_request.session['loaded_comments_cookie'] = comments_cookie
    # store results in a dictionary, if this is a POST request on initial form submission
    # include the title and permalink
    submission_comments_dict = {}
    if(is_post):
        submission_comments_dict['title'] = submission.subreddit_name_prefixed + ' | ' + submission.title
        submission_comments_dict['permalink'] = 'https://www.reddit.com' + submission.permalink
    submission_comments_dict['comments'] = comments_returned
    return submission_comments_dict

def parse_submission_id(comment_url):
    """ Simple helper method which will parse the full url of the reddit page and find the submission_id only
    This is useful as it allows the user to enter only the partial url or just the submission_id in the form.
     -----params----
    @comment_url - the url or submission id the user has passed into our form

    @return - just the parsed submission_id which we will store in a session cookie
    """
    index_start = comment_url.find('comments')
    # assume user has passed in just the 6 character submission id,
    # if it's incorrect it will be caught by try catch in get_comments
    if(index_start == -1):
        return comment_url
    # parse submission id which will start 9 characters after comments keyword in the url
    # and is always 6 characters in length
    else:
        return comment_url[index_start+9:index_start+15]


def detect_hyper_link(comment_text):
    """ Simple helper method which will parse each comment and find if it contains a hyperlink in the reddit format
       e.g. [URL NAME](www.url.com)
       -----params----
      @comment_text - text of the comment to check

      @return - the comment as is or parsed into an anchor tag for a hyperlink
      """
    open_bracket_index    = comment_text.find('[')
    closing_bracket_index = comment_text.find(']')
    opening_parentheses_index = comment_text.find('(')
    closing_parentheses_index = comment_text.find(')')
    # verify bracket and paranthese are in the right place
    if(open_bracket_index < closing_bracket_index and opening_parentheses_index < closing_parentheses_index and
    opening_parentheses_index > open_bracket_index and opening_parentheses_index > closing_bracket_index):
        anchor_text = '<a href="{0}">{1}</a>'
        comment_text = comment_text[0:open_bracket_index] + \
                       anchor_text.format(comment_text[opening_parentheses_index + 1:closing_parentheses_index],
                                          comment_text[open_bracket_index + 1:closing_bracket_index]) + \
                       comment_text[closing_parentheses_index + 1:len(comment_text) - 1]

    return comment_text
