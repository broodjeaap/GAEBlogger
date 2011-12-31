from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.api import users

MAX = 2147483647

def makeLink(url,content):
    return "<a href='%s'>%s</a>" %(url,content)

def header():
    admin = ""
    if users.is_current_user_admin():
        admin = "<small><a href='/admin'>Admin</a></small>"
    ret = """
    <html>
        <head>
            <link rel="stylesheet" href="/static/global.css"/>
            <script type='text/javascript' src='/static/jquery-1.6.4.js'></SCRIPT>
            <script type='text/javascript' src='/static/script.js'></SCRIPT>
        </head>
        <body>
            <div class='content'>
                <div class='header'>
                    <a href='/'>David van Zessen</a> %s
                </div>""" %(admin)
    return ret

def footer():
    ret = "</div></body></html>"
    return ret

def getComment(key):
    comment = memcache.get(str(key))
    if(comment != None):
        return comment
    else:
        comment = db.get(key)
        memcache.set(str(key), comment)
        return comment

def getArticle(id):
    article = memcache.get("article"+id)
    if(article != None):
        return article
    else:
        articles = db.GqlQuery("SELECT * FROM Article WHERE id = "+id)
        if(articles.count() >= 1):
            article = articles.get()
            memcache.set("article"+id,article)
            return article
        else:
            return None

def getAllArticles():
    articles = memcache.get("allArticles")
    if(articles != None):
        return articles
    else:
        articles = db.GqlQuery("SELECT * FROM Article")
        articles = articles.fetch(MAX)
        memcache.set("allArticles",articles)
        return articles

def getAllPublicArticles():
    articles = memcache.get("publicArticles")
    if(articles != None):
        return articles
    else:
        articles = db.GqlQuery("SELECT * FROM Article WHERE public = True")
        articles = articles.fetch(MAX)
        memcache.set("publicArticles",articles)
        return articles
        
def countComments(list):
    count = 0
    for comment in list:
        db.get(comment)
        count += (countComments(db.get(comment).children) + 1)
    return count