import datetime
import copy
import json

from mongoengine import *
from flask.ext.security import UserMixin, RoleMixin
from flask.ext.mongoengine import *

TYPE = (
    ('T', 'Twitter'),
)


class Role(Document, RoleMixin):
    name = StringField(max_length=80, unique=True)
    description = StringField(max_length=255)


class User(Document):
    password = StringField()

    # flask-security
    email = StringField(unique=True, max_length=255)
    password = StringField(max_length=255)
    active = BooleanField(default=True)
    confirmed_at = DateTimeField()
    roles = ListField(ReferenceField(Role), default=[])

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 3


class Sender(Document):
    name = StringField()
    ref = StringField()
    type = StringField(max_length=2, choices=TYPE)


################## Notification ###################


class Notification(Document):
    date = DateTimeField(default=datetime.datetime.now)
    configuration = ReferenceField('Configuration')
    user = ReferenceField('User')
    seen = BooleanField(default=False)
    sender = StringField()

    meta = {
        'allow_inheritance': True,
        'ordering': ['-date']
    }

    def get_medias(self):
        if getattr(self,"medias",None):
            medias_list = []
            for media in self.medias:
                medias_list.append({
                    "url": media.url,
                    "origin_id": str(self.id)
                })

            return medias_list
        return []


    def dump(self):
        data = self.to_mongo().to_dict()
        print(data)

        if data.get("_id", None):
            data["_id"] = str(data["_id"])

        if data.get("user", None):
            del data["user"]

        if data.get("date", None):
            data["date"] = data["date"].isoformat()

        if "configuration" in data:
            del data["configuration"]

        data["medias"] = self.get_medias()

        return data


class TwitterNotification(Notification):
    body = StringField()
    sender_avatar = StringField()
    configuration = ReferenceField('TwitterConfiguration')
    medias = ListField(ReferenceField('TwitterMedia'))
    url = StringField()

class TwitterMedia(Document):
    url = StringField()
    media_type = StringField()


################## Configuration ##################

class Configuration(Document):
    notifications = ListField(ReferenceField('Notification',reverse_delete_rule=mongoengine.NULLIFY))
    user = ReferenceField('User')
    lastCheck = DateTimeField(default=datetime.datetime.now)
    refresh_every = IntField(default="3")
    valid = BooleanField(default=True)

    meta = {'allow_inheritance': True}

    def dump(self):
        data = copy.deepcopy(self.__dict__['_data'])

        if data.get("id", None):
            data["id"] = str(data["id"])

        del data['lastCheck']
        del data['notifications']
        del data['user']

        return data


class TwitterConfiguration(Configuration):
    type = StringField(max_length=2, choices=TYPE, default="T")
    oauth_token = StringField(required=True)
    oauth_secret = StringField(required=True)

#configuration for only following account
class TwitterFollow(Configuration):
    type = StringField(max_length=2, choices=TYPE, default="T")
    screen_name = StringField()
    user_id = IntField()
