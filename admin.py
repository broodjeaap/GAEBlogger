from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import memcache
from google.appengine.ext.webapp import template
import os
import models
import datetime
import blog
import misc


class AdminMain(webapp.RequestHandler):
    def get(self):
        appName = "#"
        id = os.environ["APPLICATION_ID"]
        tilde = id.find("~")
        if(tilde != -1):
            appName = id[tilde+1:]
        template_values = {
            'appname': appName,
        }
        path = os.path.join(os.path.dirname(__file__), 'templates/admin.html')
        self.response.out.write(template.render(path, template_values))
             
class AdminArchive(webapp.RequestHandler):
    def get(self):
        articles = misc.getAllArticles()
        template_values = {
            'articles': articles,
        }
        path = os.path.join(os.path.dirname(__file__), 'templates/adminarchive.html')
        self.response.out.write(template.render(path, template_values))

class AdminArticle(webapp.RequestHandler):
    def get(self):
        article = misc.getArticle(self.request.get('id'))
        comments = printAdminComments(article.comments)
        template_values = {
            'article': article,
            'key': article.key(),
            'comments': comments,
        }
        path = os.path.join(os.path.dirname(__file__), 'templates/adminarticle.html')
        self.response.out.write(template.render(path, template_values))

class AdminEditArticlePost(webapp.RequestHandler):
    def post(self):
        article = db.get(self.request.get('key'))
        article.title = self.request.get('title')
        article.body = self.request.get('body')
        if(self.request.get('public') == 'public'):
            article.public = True
        else:
            article.public = False
        article.date = datetime.datetime.now().date()
        memcache.set("article"+str(article.id),article)
        memcache.delete("publicArticles")
        memcache.delete("allArticles")
        article.put()
        self.redirect('/admin/article?id='+str(article.id))

class DeleteArticlePost(webapp.RequestHandler):
    def post(self):
        if(self.request.get('delete') == 'delete'):
            article = db.get(self.request.get('key'))
            for commentKey in article.comments:
                deleteComment(commentKey)
            memcache.delete("article"+str(article.id))
            memcache.delete("publicArticles")
            memcache.delete("allArticles")
            article.delete()
        self.redirect('/admin/archive')

def deleteComment(key):
    comment = misc.getComment(key)
    if comment.children:
        for commentKey in comment.children:
            deleteComment(misc.getComment(commentKey).key())
    memcache.delete(str(comment.key()))
    comment.delete()
            
class DeleteCommentPost(webapp.RequestHandler):
    def post(self):
        key = self.request.get('key')
        comment = db.get(key)
        comment.title = "removed"
        comment.body = "This comment was removed because: <br />"+self.request.get('reason')
        comment.author = users.User("removed")
        comment.date = datetime.datetime.now().date()
        comment.put()
        memcache.set(str(comment.key()),comment)
        self.redirect('/admin/article?id='+str(comment.article.id))       
    
class AdminNewArticle(webapp.RequestHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'templates/adminnewarticle.html')
        self.response.out.write(template.render(path, {}))

class AdminNewArticlePost(webapp.RequestHandler):
    def post(self):
        id = 0
        articles = models.Article.all()
        for article in articles:
            if(article.id > id):
                id = article.id
        id += 1;
        title = self.request.get('title')
        body = self.request.get('body')
        public = (self.request.get('public') == 'public')
        article = models.Article(id= id,title = title,body = body,date=datetime.datetime.now().date(),public=public)
        article.put()
        memcache.add("article"+str(article.id),article)
        memcache.delete("publicArticles")
        memcache.delete("allArticles")
        if(article.public):
            self.redirect('/article?id='+str(article.id))
        else:
            self.redirect('/admin/article?id='+str(article.id))

def printAdminComments(comments,switch=False):
    if(switch):
        ret = "<div class='articleCommentsSwitch'>"
    else:
        ret = "<div class='articleComments'>"
    for key in comments:
        comment = misc.getComment(key)
        ret += printAdminComment(comment)
        if(len(comment.children) > 0):
            ret += printAdminComments(comment.children,(not switch))
    ret += "</div>"
    return ret

def printAdminComment(comment):
    template_values = {
        'comment': comment,
        'key': comment.key(),
    }
    path = os.path.join(os.path.dirname(__file__), 'templates/admincomment.html')
    return template.render(path, template_values)

def main():
    application = webapp.WSGIApplication([('/admin', AdminMain),
                                          ('/admin/archive', AdminArchive),
                                          ('/admin/new',AdminNewArticle),
                                          ('/admin/article',AdminArticle),
                                          ('/admin/newpost',AdminNewArticlePost),
                                          ('/admin/editpost',AdminEditArticlePost),
                                          ('/admin/deletecommentpost',DeleteCommentPost),
                                          ('/admin/deletearticlepost',DeleteArticlePost)],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
