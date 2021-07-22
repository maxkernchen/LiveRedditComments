from django.apps import AppConfig

class RedditCommentsConfig(AppConfig):
    name = 'RedditComments'

    def ready(self):
        from . import active_submissions_thread
        import logging
        from logging.handlers import RotatingFileHandler
        loggerCfg = logging.basicConfig(
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.INFO,
                            handlers=[RotatingFileHandler('RedditCommentsLog.txt', maxBytes=1000000, backupCount=10)])

        ActiveSubThread = active_submissions_thread.ActiveSubmissionsThread()
        ActiveSubThread.thread.start()