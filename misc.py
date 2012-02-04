from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.api import users
from BeautifulSoup import BeautifulSoup

MAX = 2147483647
ARTICLES_PER_PAGE = 5

VALID_TAGS = ['a','br','abbr','acronym','address','b','strong','big','em','i','small','tt','sub','sup','blockquote','table','th','tr','td','caption','ol','ul','li','p','pre']
VALID_ATTR = ['href','border']

def cleanHtml(content):
    soup = BeautifulSoup(content)
    soupOld = BeautifulSoup("")
    while(soupOld.renderContents() != soup.renderContents()):
        for tag in soup.findAll(True):
            if(tag.name not in VALID_TAGS):
                tag.hidden = True
            else:
                for attr, value in tag.attrs:
                    if(attr not in VALID_ATTR):
                        del tag[attr]
        soupOld = soup
    return soup.renderContents()

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
        articles = db.GqlQuery("SELECT * FROM Article WHERE public = True ORDER BY id")
        articles = articles.fetch(MAX)
        memcache.set("publicArticles",articles)
        return articles
    
def getPublicArticles(page=1):
    page -= 1
    start = page*ARTICLES_PER_PAGE
    limit = start + ARTICLES_PER_PAGE
    allArticles = getAllPublicArticles()
    length = len(allArticles)
    if(start > length):
        start = 0
        limit = ARTICLES_PER_PAGE
    if(limit > length):
        limit = length
    ret = []
    articles = []
    for x in range(start,limit):
        articles.append(allArticles[x])
    ret.append(articles)
    if(limit+1 > length):
        ret.append(False)
    else:
        ret.append(True)
    return ret
    
        
def countComments(list):
    count = 0
    for comment in list:
        count += (countComments(getComment(comment).children) + 1)
    return count