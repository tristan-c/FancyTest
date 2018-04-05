from functools import wraps

from twitter import Twitter, OAuth
from twitter.oauth_dance import parse_oauth_tokens
from flask import redirect, session, request, Response, g
from flask.ext import restful
from flask.ext.login import current_user
from flask_restful import reqparse

from app import application, api
from app.models import *
from app import socket


@application.before_request
def before_request():
    g.user = current_user


@application.login_manager.header_loader
def load_user_from_header(header_val):
    print(header_val)
################ Twitter ######################
parser = reqparse.RequestParser()
parser.add_argument('pin', type=int, help='Pin must be given', required=True)

class twitterRegister(restful.Resource):

    def get(self):
        twitter = Twitter(
            auth=OAuth('', '',
                       application.config.get('TWITTER_CONSUMER_KEY'),
                       application.config.get('TWITTER_CONSUMER_SECRET')),
            format='',
            api_version=None
        )

        # get authorisation token
        oauth_token, oauth_token_secret = parse_oauth_tokens(
            twitter.oauth.request_token(oauth_callback="oob")
        )

        session['oauth_token'] = oauth_token
        session['oauth_token_secret'] = oauth_token_secret

        oauth_url = 'https://api.twitter.com/oauth/authorize?oauth_token=%s' % oauth_token

        return redirect(oauth_url)

    def post(self, pin=None):
        args = parser.parse_args()

        oauth_verifier = args['pin']
        twitter = Twitter(
            auth=OAuth(
                session['oauth_token'],
                session['oauth_token_secret'],
                application.config.get('TWITTER_CONSUMER_KEY'),
                application.config.get('TWITTER_CONSUMER_SECRET')),
            format='', api_version=None)

        oauth_token, oauth_token_secret = parse_oauth_tokens(
            twitter.oauth.access_token(oauth_verifier=oauth_verifier))


        conf = TwitterConfiguration.objects(
                    oauth_token=oauth_token
                )

        if len(conf) > 0:
            return "already in db"

        configuration = TwitterConfiguration(
                user=session["user_id"],
                oauth_token = oauth_token,
                oauth_secret = oauth_token_secret
            )

        configuration.save()
        socket.send_json({
            "action":"register_new_job",
            "id":str(configuration.id)
        })

        return "token successfully retrieve"

api.add_resource(
    twitterRegister,
    "/twitterRegister",
    "/twitterRegister/<string:pin>")
