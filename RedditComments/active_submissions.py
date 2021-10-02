import configparser
import praw
import praw.config
import praw.exceptions
import praw.models.reddit.more
import prawcore.exceptions
import requests
from django.db import transaction
from RedditComments.models import ActiveSubmissions
from praw.models import MoreComments
from better_profanity import profanity
from pathlib import Path
import wordninja
import logging
import os
logger = logging.getLogger(__name__)
__author__  = 'Max Kernchen'
__version__ = '1.0.'
__email__   = 'max.f.kernchen@gmail.com'


""" Module whoses main purpose is to fetch the top 5 active submissions currently on reddit, these 5 submissions
are then stored in the index page. This module will be called by a seperte daemon thread. 
"""

def get_active_submissions():
    """ Fetches 5k of the most hot posts, then filters them down by eliminating posts with < 1000 comments
    and profantity in the title or subreddit name. Then each submission left is sorted by new comments and the time
    between comments is averaged. This will then give us a dictionary of indexes for our list of posts as the key
    and the average time per new comment as our value.
    We then take the top 5 of these sorted by least average time per comment and consider them the top 5 most active
    submissions. These are stored as our ActiveSubmission model and replaces existing rows in the database.

    WARNING - this method is long running, it takes an average of 5 mintues to complete due to the built in Reddit API
    calling limitations.

    @return - None if any exceptions are found, this is method is called every 5 minutes from a thread which does not
    expect any return values

    """
    # read the reddit config and login using our OAuth2 credentials
    config_dir = Path('/RedditComments/praw.ini')
    config = configparser.ConfigParser()
    config.read(os.getcwd() / config_dir)

    try:
        reddit_obj = praw.Reddit(client_id=config['bot1']['client_id'],
                                 client_secret=config['bot1']['client_secret'],
                                 user_agent=config['bot1']['user_agent'])

        logger.info('Starting new iteration of active submissions')

        all_submissions = list(reddit_obj.subreddit('all').hot(limit=5000))
    except (praw.exceptions.PRAWException, prawcore.PrawcoreException, praw.exceptions.RedditAPIException) as e:
        # None is okay as the thread will just wait for next 5 minute interval
        return None
    # add any subreddits which are not in r/all and then filter profanity/posts with < 1000 comments
    add_excluded_subreddits(all_submissions, reddit_obj)
    filtered_posts = filter_posts(all_submissions)

    # find the avg time between comments for all filtered posts and stored them in avg_time_dict
    avg_time_dict = {}
    for i in range(len(filtered_posts)):
        try:
            filtered_posts[i].comment_sort = 'new'
            post = filtered_posts[i]
            comment_list_post = list(post.comments)
        except(praw.exceptions.PRAWException, prawcore.PrawcoreException, praw.exceptions.RedditAPIException) as e:
            # None is okay as the thread will just wait for next 5 minute interval
            return None
        avg_time_between_comments = 0
        num_comments = 0
        for j in range(25):
            if j >= len(comment_list_post) - 1:
                break
            temp_comment = comment_list_post[j]
            next_temp_comment = comment_list_post[j + 1]
            # skip any comments which are stickied, deleted, or are a MoreComments object.
            # this is to prevent any issues with how the avg time between comments is calcuated, i.e. it should
            # never result in a negative value
            if isinstance(temp_comment, MoreComments) or temp_comment.stickied or \
                    temp_comment.author is None or isinstance(next_temp_comment, MoreComments) \
                    or next_temp_comment.stickied or next_temp_comment.author is None:
                continue
            difference = temp_comment.created_utc - next_temp_comment.created_utc
            if(difference > 0):
                avg_time_between_comments += (temp_comment.created_utc - next_temp_comment.created_utc)
                num_comments += 1
        # store the avg time where the key is the index of the list of posts and the value is the average time
        if(num_comments > 0):
            avg_time_dict[i] = avg_time_between_comments / num_comments

    i = 1
    # iterate through the dictionary ordered by the value, this results in top 5 most active posts with least time
    # between each new comment
    for k in sorted(avg_time_dict, key=avg_time_dict.get):
        logger.info(str(avg_time_dict[k]) + '-' + str(k))
        store_post_data(filtered_posts[k], i, avg_time_dict[k])
        # only check top 5 values
        if(i == 5):
            break
        i+=1
    logger.info('Finished iteration of active submissions')


def store_post_data(post, rank, avg_comment_time):
    """ Store the ActiveSubmissions model and delete any existing entries with same rank value
    -----params-----
    @post - the Reddit Submission object to be saved
    @rank - the rank int of this submission
    @avg_comment_time - the float value for each
    """
    ActiveSubmissions.objects.filter(rank=rank).delete()
    act_sub = ActiveSubmissions(submission_title=post.title,
                                num_comments=post.num_comments,
                                subreddit_name=post.subreddit_name_prefixed,
                                submission_permalink='https://reddit.com' + post.permalink,
                                one_comment_avg= round(avg_comment_time,2),
                                rank=rank)
    act_sub.save()

def query_active_submissions():
    """ Query to ActiveSubmissions model to return all rows from the database.

    @return - list of all ActiveSubmissions rows sorted by rank
    """
    all_act_subs = []
    if (ActiveSubmissions.objects.all().exists()):
        all_act_subs = ActiveSubmissions.objects.all().order_by('rank')
    return all_act_subs

def add_excluded_subreddits(all_list, reddit_obj):
    """ Certain subreddits which are popular have decicded to be excluded from r/all,
    This method will add the top 10 posts from these subreddits to our list all_list
    This method will open a text file in our root directory to add excluded subreddits to our
    -----params-----
    @all_list - list of all submissions from get_active_submissions method
    @reddit_obj - used to call Reddit API

    """
    excluded_subreddits = []
    excluded_subreddits_dir = Path('/RedditComments/excluded_subreddits_add.txt')
    with open(os.getcwd() / excluded_subreddits_dir) as file:
        excluded_subreddits = file.read().splitlines()
    for subreddit in excluded_subreddits:
        all_list += list(reddit_obj.subreddit(subreddit.strip()).hot(limit=10))

def filter_posts(all_list):
    """ This method will filter posts to reduce number of submissions that we will fetch comments for.
    The main critera is that the number of comments in the submission is >= 1000 and that the title or subreddit name
    does not contain profanity.
    -----params-----
    @all_list - the list of all submissions that we will filter down.
    ---------------
    @returns all_list with filtered critera
    """
    profanity.load_censor_words()
    # A file will be opened to read some custom profanity keywords which show up on more inappropriate subreddits
    custom_badwords = []
    custom_badwords_dir = Path('/RedditComments/custom_profanity_keywords.txt')
    with open(os.getcwd() / custom_badwords_dir) as file:
        custom_badwords = file.read().splitlines()
    profanity.add_censor_words(custom_badwords)
    all_list = list(filter(lambda post: post.num_comments >= 1000 and not post.over_18, all_list))
    all_list = list(filter(lambda post: not profanity.contains_profanity(post.title) and
                            not is_profanity_split(post.subreddit_name_prefixed[2:])
                            # check both word splits and whole subreddit as a word
                            and not profanity.contains_profanity(post.subreddit_name_prefixed[2:]), all_list))
    return all_list

def is_profanity_split(input_str):
    """ Because the subreddit name is combined without spaces e.g. r/ThisIsASubreddit
    I am using wordninja package to parse the words seperately and check if they contain profanity.
    @return - boolean value True for the subreddit name contains profanity else False
    """
    word_list = wordninja.split(input_str)
    for word in word_list:
        if(profanity.contains_profanity(word)):
            return True

    return False





