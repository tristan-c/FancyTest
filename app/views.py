import json
import datetime

from flask.ext.restful import Resource, reqparse
from flask.ext.security import login_required
from flask import session, g, redirect, make_response,render_template
from Crypto.Cipher import AES
from Crypto import Random

from app import application, api, daemon
from app.models import *
from app.utils import get_bearer_token, get_only_urls
from app import socket

# TODO clean this
try:
    with open("config.py") as config_file:
        exec(compile(config_file.read(), "config.py", 'exec'))
except:
    pass

from twitter import Twitter, OAuth2

bearer_token = get_bearer_token(
                TWITTER_CONSUMER_KEY,
                TWITTER_CONSUMER_SECRET
            )
twitter = Twitter(auth=OAuth2(bearer_token=bearer_token))


class Resource(Resource):
    method_decorators = [login_required]


@application.route('/')
def index():
    if g.user is not None and g.user.is_authenticated:

        return application.send_static_file('index.html')
        # notifs = Notification.objects(user=session['user_id'])[:60]

        # notifs_dicts = [notif.dump() for notif in notifs]

        # return render_template(
        #                         'index.html',
        #                         notifs=notifs_dicts)
    else:
        return redirect("/login")

@application.route('/config')
def config():
    if g.user is not None and g.user.is_authenticated:
        configs = Configuration.objects(user=session['user_id'])[:40]

        return render_template(
                                'config.html',
                                configs=configs)
    else:
        return redirect("/login")

timeline_args = reqparse.RequestParser()
timeline_args.add_argument('date', type=int, location='args')

class GetTimeline(Resource):

    def get(self, date=None):
        args = timeline_args.parse_args()
        if args['date']:
            date = datetime.datetime.utcfromtimestamp(args['date'])
            notifs = Notification.objects(date_gt=date, user=session['user_id'])
        else:
            notifs = Notification.objects(user=session['user_id'])[:60]

        return [notif.dump() for notif in notifs]

api.add_resource(GetTimeline, "/getTimeline", "/getTimeline/<string:date>")

configuration_parser = reqparse.RequestParser()
configuration_parser.add_argument('_id', type=str, required=True)

class Configurations(Resource):

    def get(self):
        configs = Configuration.objects(user=session['user_id'])
        return [config.dump() for config in configs]

    def delete(self):
        args = configuration_parser.parse_args()
        config = Configuration.objects.get(
                    user=session['user_id'],
                    id=args['_id']
                )
        if config:
            config.delete()

api.add_resource(Configurations, "/configurations")

#---------FollowTwitter----------
twitter_follow_parser = reqparse.RequestParser()
twitter_follow_parser.add_argument('screen_name', type=str, required=True)
twitter_follow_parser.add_argument('refresh_every', type=int)

class FollowTwitter(Resource):

    def post(self):
        args = twitter_follow_parser.parse_args()
        twitter_id = twitter.users.lookup(screen_name=args['screen_name'])[0]["id"]

        configuration = TwitterFollow(
                            user=session["user_id"],
                            refresh_every= args["refresh_every"],
                            screen_name = args["screen_name"],
                            user_id = twitter_id
                        )

        configuration.save()
        socket.send_json({
            "action":"register_new_job",
            "id":str(configuration.id)
            })

api.add_resource(FollowTwitter, "/twitterFollowRegister")
