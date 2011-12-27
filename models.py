from google.appengine.ext import db

class Article(db.Model):
    id = IntegerProperty()
    title = db.StringProperty(required=True)
    body = db.TextProperty(required=True)
    date = db.DateProperty(required=True)
    comments = ListProperty(db.Key)
    public = BooleanProperty(required=True, default=True)
    
class Comment(db.Model):
    body = db.TextProperty(required=True)
    date = db.DateProperty(required=True)
    parent = ReferenceProperty(reference_class=models.Article)