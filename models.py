from google.appengine.ext import db
import sys

MAX = (sys.maxint - 1)

class Article(db.Model):
    id = db.IntegerProperty()
    title = db.StringProperty(required=True)
    body = db.TextProperty(required=True)
    date = db.DateProperty(auto_now_add=True, required=True)
    comments = db.ListProperty(db.Key)
    public = db.BooleanProperty(required=True, default=False)
    
def getArticle(id):
    articles = db.GqlQuery("SELECT * FROM Article WHERE id = "+id)
    if(articles.count() >= 1):
        return articles.get()
    else:
        return None

def getAll():
    articles = db.GqlQuery("SELECT * FROM Article")
    return articles.fetch(MAX)

def getAllPublic():
    articles = db.GqlQuery("SELECT * FROM Article WHERE public = True")
    return articles.fetch(MAX)
        
        
class Comment(db.Model):
    author = db.StringProperty()
    body = db.TextProperty(required=True)
    date = db.DateProperty(required=True)
    children = db.ListProperty(db.Key)
    
def getComment(key):
    return db.get(key)