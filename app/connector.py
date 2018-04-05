import imaplib
import requests
import datetime
import iso8601
import email
import urllib
import time
import dateutil
import logging
import feedparser

from email.header import decode_header
from twitter import *
from json import loads
from bs4 import BeautifulSoup

from app.models import *
from app.utils import get_bearer_token

try:
    with open("config.py") as config_file:
        exec(compile(config_file.read(), "config.py", 'exec'))
except:
    pass

logger = logging.getLogger(__name__)


class Connector():

    def __init__(self, config):
        logger.info("Spawning %s connector" % type(self))
        self.config = config

    def get_refresh_interval(self):
        return self.config.refresh_every


class TwitterConnector(Connector):

    def check(self):
        logger.info("Check twitter refresh")

        #if oauth -> twitter account, otherwise, oauth2
        if getattr(self.config,"oauth_token",None) and \
           getattr(self.config,"oauth_secret",None):
            twitter = Twitter(
                auth=OAuth(
                    self.config.oauth_token,
                    self.config.oauth_secret,
                    TWITTER_CONSUMER_KEY,
                    TWITTER_CONSUMER_SECRET))
        else:
            bearer_token = get_bearer_token(
                TWITTER_CONSUMER_KEY,
                TWITTER_CONSUMER_SECRET
            )
            twitter = Twitter(auth=OAuth2(bearer_token=bearer_token))

        #home or user timeline
        if hasattr(self.config,"user_id"):
            timeline = twitter.statuses.user_timeline(
                user_id=self.config.user_id,
                count=20
            )
        else:
            timeline = twitter.statuses.home_timeline(count=20)


        #for each tweet in timeline
        for tweet in timeline:

            existing_tweet = TwitterNotification.objects(
                                sender=tweet["user"]["screen_name"],
                                date=tweet['created_at']
                            )

            # tweet already in db ?
            if not existing_tweet:
                record = TwitterNotification(
                    body = tweet["text"],
                    sender = tweet["user"]["screen_name"],
                    sender_avatar = tweet["user"]["profile_image_url_https"],
                    user=self.config.user,
                    date=tweet['created_at']
                )

                #Get each media attached with tweet
                media_list = []

                if tweet.get("extended_entities", None):
                    for entity in tweet["extended_entities"].get("media",[]):
                        print(tweet["extended_entities"])
                        try:
                            entity = TwitterMedia.objects.get(url=entity["media_url_https"])
                        except Exception as e:
                            entity = TwitterMedia(
                                url=entity["media_url_https"],
                                media_type=entity["type"],
                            )
                            entity.save()
                        media_list.append(entity)

                record.medias = media_list
                record.save()

def create_connector_by_type(configObj):
    _type = configObj.type
    if _type == "T":
        return TwitterConnector(configObj)
    else:
        return None
