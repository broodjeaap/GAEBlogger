import sys
from google.appengine.ext import db

MAX = 2147483647

def makeLink(url,content):
    return "<a href='%s'>%s</a>" %(url,content)

def header():
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
                    <a href='/'>David van Zessen</a>
                </div>"""
    return ret

def footer():
    ret = "</div></body></html>"
    return ret

def getComment(key):
    return db.get(key)

def getArticle(id):
    articles = db.GqlQuery("SELECT * FROM Article WHERE id = "+id)
    if(articles.count() >= 1):
        return articles.get()
    else:
        return None

def getAllArticles():
    articles = db.GqlQuery("SELECT * FROM Article")
    return articles.fetch(MAX)

def getAllPublicArticles():
    articles = db.GqlQuery("SELECT * FROM Article WHERE public = True")
    return articles.fetch(MAX)
        
def countComments(list):
    count = 0
    for comment in list:
        db.get(comment)
        count += (countComments(db.get(comment).children) + 1)
    return count