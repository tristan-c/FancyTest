from carotte import Carotte
from app.connector import *

my_app = Carotte()


@my_app.task
def refreshYoutube(author=None):
    youtube = youtubeConnector(username="")
    log = youtube.check()
    return log
