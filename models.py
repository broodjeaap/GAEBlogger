from google.appengine.ext import db


class Article(db.Model):
    id = db.IntegerProperty()
    title = db.StringProperty(required=True)
    body = db.TextProperty(required=True)
    date = db.DateProperty(auto_now_add=True, required=True)
    comments = db.ListProperty(db.Key)
    public = db.BooleanProperty(required=True, default=False)

               
class Comment(db.Model):
    author = db.UserProperty()
    body = db.TextProperty(required=True)
    date = db.DateProperty(required=True)
    children = db.ListProperty(db.Key)
    article = db.ReferenceProperty(required=True)