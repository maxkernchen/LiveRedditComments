from django.db import models

class ActiveSubmissions(models.Model):
    submission_permalink = models.CharField(max_length=1000, primary_key=True)
    submission_title = models.CharField(max_length=1000)
    subreddit_name = models.CharField(max_length=1000)
    num_comments = models.IntegerField(default=0)
    one_comment_avg = models.FloatField(default=0)
    rank = models.IntegerField(default=0)
