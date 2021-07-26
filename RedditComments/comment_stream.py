from datetime import datetime
import configparser
import praw
import praw.config
import praw.exceptions
import praw.models.reddit.more
import prawcore.exceptions
import requests
from praw.models import MoreComments
import os


"""
Method get_comments, this takes in a Reddit comment url string and passes it to the PRAW client.
Currently this returns only the parent comment, no child comments.
Also it includes the time the comment was posted. These comments are order by newest submission.
para - comment_url - string of the full Reddit URL pointing to the comment page of a post.
"""


def get_comments(submission_id, views_request):
    config = configparser.ConfigParser()
    config.read(os.getcwd() + '\RedditComments\praw.ini')
    reddit_obj = praw.Reddit(client_id=config['bot1']['client_id'],
                             client_secret=config['bot1']['client_secret'],
                             user_agent=config['bot1']['user_agent'])

    try:
        submission = reddit_obj.submission(id=submission_id)
        # only get the newest comments
        submission.comment_sort = 'new'
        comment_list = list(submission.comments)
    except (praw.exceptions.PRAWException, prawcore.PrawcoreException, praw.exceptions.RedditAPIException) as e:
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
                                     str(datetime.fromtimestamp(comment.created_utc)) + " - " + comment.body)

    views_request.session['loaded_comments_cookie'] = comments_cookie

    return comments_returned

def get_submission_title(submission_id):
    config = configparser.ConfigParser()
    config.read(os.getcwd() + '\RedditComments\praw.ini')
    reddit_obj = praw.Reddit(client_id=config['bot1']['client_id'],
                             client_secret=config['bot1']['client_secret'],
                             user_agent=config['bot1']['user_agent'])
    # no need to try catch since at this point we will know that the URL is valid
    submission = reddit_obj.submission(id=submission_id)
    return submission.subreddit_name_prefixed + ' | ' + submission.title

def get_submission_permalink(submission_id):
    config = configparser.ConfigParser()
    config.read(os.getcwd() + '\RedditComments\praw.ini')
    reddit_obj = praw.Reddit(client_id=config['bot1']['client_id'],
                             client_secret=config['bot1']['client_secret'],
                             user_agent=config['bot1']['user_agent'])
    # no need to try catch since at this point we will know that the URL is valid
    submission = reddit_obj.submission(id=submission_id)
    return 'https://reddit.com' + submission.permalink

def parse_submission_id(comment_url):
    index_start = comment_url.find('comments')
    # assume user has passed in just the 6 character submission id,
    # if it's incorrect it will be caught by try catch in get_comments
    if(index_start == -1):
        return comment_url
    # parse submission id which will start 9 characters after comments keyword in the url
    # and is always 6 characters in length
    else:
        return comment_url[index_start+9:index_start+15]


