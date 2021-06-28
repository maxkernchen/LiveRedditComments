from datetime import datetime
import configparser
import praw
import praw.config
import praw.exceptions
import praw.models.reddit.more
from praw.models import MoreComments
import os


"""
Method get_comments, this takes in a Reddit comment url string and passes it to the PRAW client.
Currently this returns only the parent comment, no child comments. 
Also it includes the time the comment was posted. These comments are order by newest submission.
para - comment_url - string of the full Reddit URL pointing to the comment page of a post.
"""

def get_comments(self, comment_url):
    config = configparser.ConfigParser()
    config.read(os.getcwd() + '\RedditComments\praw.ini')
    reddit_obj = praw.Reddit(client_id = config['bot1']['client_id'],
                             client_secret = config['bot1']['client_secret'],
                             user_agent = config['bot1']['user_agent'])
    # get the submission from the link passed in
    try:
        submission = reddit_obj.submission(url=comment_url)
    except praw.exceptions.ClientException:
        # None is okay to return as views.py will handle this appropriately
        return None

    # only get newest comments
    i = 0
    submission.comment_sort = 'new'
    comment_list = list(submission.comments)
    comments_sorted = []
    for comment in comment_list:
        if isinstance(comment, MoreComments):
            # TODO Consider adding logic for loading more comments/replies
            #comments_sorted + (comment.comments(update=True))
            continue
        comments_sorted.append(comment)

    comments_returned = []

    for comment in comments_sorted:
        i += 1
        # don't track deleted comments
        if(comment.author is not None):
            comments_returned.append(comment.author.name + " - " +
                                     str(datetime.fromtimestamp(comment.created_utc)) + " - " + comment.body)

    # return the comments only
    # print("number of comments: ", i)

    return comments_returned



