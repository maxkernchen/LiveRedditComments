from datetime import datetime
import configparser
import praw
import praw.config
import praw.exceptions
import praw.models.reddit.more
import requests
from django.db import transaction
from RedditComments.models import ActiveSubmissions
from praw.models import MoreComments
from better_profanity import profanity
import wordninja
import logging
import os
logger = logging.getLogger(__name__)


def get_active_submissions():
    config = configparser.ConfigParser()
    config.read(os.getcwd() + '\RedditComments\praw.ini')
    reddit_obj = praw.Reddit(client_id=config['bot1']['client_id'],
                             client_secret=config['bot1']['client_secret'],
                             user_agent=config['bot1']['user_agent'])

    logger.info('Starting new interation of active submissions')
    all_submissions = list(reddit_obj.subreddit('all').hot(limit=5000))
    add_excluded_subreddits(all_submissions, reddit_obj)

    filtered_posts = filter_posts(all_submissions)
    avg_time_dict = {}
    for i in range(len(filtered_posts)):
        filtered_posts[i].comment_sort = 'new'
        post = filtered_posts[i]
        comment_list_post = list(post.comments)
        avg_time_between_comments = 0
        # look at avg time between comment posted for a portion of newest comments
        num_comments = 0
        for j in range(25):
            if j >= len(comment_list_post) - 1:
                break
            temp_comment = comment_list_post[j]
            next_temp_comment = comment_list_post[j + 1]
            if isinstance(temp_comment, MoreComments) or temp_comment.stickied or \
                    temp_comment.author is None or isinstance(next_temp_comment, MoreComments) \
                    or next_temp_comment.stickied or next_temp_comment.author is None:
                continue
            avg_time_between_comments += (temp_comment.created_utc - next_temp_comment.created_utc)
            num_comments += 1
        avg_time_dict[i] = avg_time_between_comments / num_comments

    i = 1
    logger.info(avg_time_dict)
    for k in sorted(avg_time_dict, key=avg_time_dict.get):
        logger.info(str(avg_time_dict[k]) + '-' + str(k))
        store_post_data(filtered_posts[k], i, avg_time_dict[k])
        # only check top 5 values
        if(i == 5):
            break
        i+=1
    logger.info('Finished interation of active submissions')
def store_post_data(post, rank, avg_comment_time):
    ActiveSubmissions.objects.filter(rank=rank).delete()
    title = post.title
    # limit title length so it can fit nicely in a bootstrap card
    #if(len(title) > 60):
     #   str_index = title.rfind(' ',0 , 60)
      #  title = title[:str_index] + '...'
    act_sub = ActiveSubmissions(submission_title=title,
                                num_comments=post.num_comments,
                                subreddit_name=post.subreddit_name_prefixed,
                                submission_permalink='https://reddit.com' + post.permalink,
                                one_comment_avg= round(avg_comment_time,2),
                                rank=rank)
    act_sub.save()

def query_active_submissions():
    act_sub_str_lst = []
    all_act_subs = []
    if (ActiveSubmissions.objects.all().exists()):
        all_act_subs = ActiveSubmissions.objects.select_for_update().order_by('rank')
        with transaction.atomic():
            for active_sub in all_act_subs:
                act_sub_str_lst.append(active_sub.submission_title + ' - ' + str(active_sub.num_comments) + ' - ' +
                               active_sub.submission_permalink)

    return all_act_subs

def add_excluded_subreddits(all_list, reddit_obj):
    all_list += list(reddit_obj.subreddit('nfl').hot(limit=10))
    all_list += list(reddit_obj.subreddit('soccer').hot(limit=10))
    wsb = list(reddit_obj.subreddit('wallstreetbets').hot(limit=10))
    all_list += wsb



def filter_posts(all_list):
    profanity.load_censor_words()
    custom_badwords = []
    with open(os.getcwd() + '\RedditComments\custom_profanity_keywords.txt') as file:
        custom_badwords = file.read().splitlines()
    profanity.add_censor_words(custom_badwords)
    all_list = list(filter(lambda post: post.num_comments >= 1000 and not post.over_18, all_list))
    all_list = list(filter(lambda post: not profanity.contains_profanity(post.title) and
                            not is_profanity_split(post.subreddit_name_prefixed[2:])
                            # check both word splits and whole subreddit as a word
                            and not profanity.contains_profanity(post.subreddit_name_prefixed[2:]), all_list))
    return all_list

def is_profanity_split(input_str):
    word_list = wordninja.split(input_str)
    for word in word_list:
        if(profanity.contains_profanity(word)):
            return True

    return False





