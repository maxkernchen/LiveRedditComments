from datetime import datetime
import configparser
import praw
import praw.config
import praw.exceptions
import praw.models.reddit.more
import requests
from praw.models import MoreComments
import os

def get_active_threads(self):
    config = configparser.ConfigParser()
    config.read(os.getcwd() + '\RedditComments\praw.ini')
    reddit_obj = praw.Reddit(client_id=config['bot1']['client_id'],
                             client_secret=config['bot1']['client_secret'],
                             user_agent=config['bot1']['user_agent'])
    """
    sort = 'desc'
    sort_type = 'num_comments'
    after = '24h'
    url = f'https://api.pushshift.io/reddit/search/comment/?sort={sort}&sort_type={sort_type}&after={after}'
    request = requests.get(url)
    json_response = request.json()
    print(json_response)
    """
    all_submissions = list(reddit_obj.subreddit('all').hot(limit=5000))
    # get the submission from the link passed in
    # TODO recent reddit changes allow for subs to opt out of all, calls those subs directly using
    # static list soccer and NFL are two to check
    filtered_posts = list(filter(lambda post: post.num_comments >= 1000 and not post.over_18, all_submissions))
    print(len(filtered_posts))
    avg_time_dict = {}
    for i in range(len(filtered_posts)):
        filtered_posts[i].comment_sort = 'new'
        post = filtered_posts[i]
        comment_list_post = list(post.comments)
        avg_time_between_comments = 0
        # look at avg time between comment posted for a portion of newest comments
        num_comments = 0
        for j in range(25):
            temp_comment = comment_list_post[j]
            if isinstance(temp_comment, MoreComments) or temp_comment.stickied or \
                    temp_comment.author is None:
                continue
            if comment_list_post[j].created_utc - comment_list_post[j + 1].created_utc < 0:
                print('comment found that is not a positive difference ')
            avg_time_between_comments += (comment_list_post[j].created_utc - comment_list_post[j + 1].created_utc)
            num_comments += 1
        avg_time_dict[i] = avg_time_between_comments / num_comments

    # TODO profanity filter
    print(avg_time_dict)
    for k in sorted(avg_time_dict, key=avg_time_dict.get):
        print('reddit.com' + filtered_posts[k].permalink)
        print(filtered_posts[k].score)
