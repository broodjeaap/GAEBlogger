from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.ext.webapp import util
from google.appengine.api import memcache
from google.appengine.ext.webapp import template
import os
from models import *
import misc
import datetime


class Main(webapp.RequestHandler):
    def get(self):
        page = self.request.get('page')
        if(page.isdigit()):
            page = int(page)
        else:
            page = 1
        ret = misc.getPublicArticles(page)
        articles = ret[0]
        nextPageBool = ret[1]
        template_values = {
            'articles': articles,
            'nextpage': (page+1),
            'nextpagebool': nextPageBool,
            'prevpage': (page-1),
        }
        path = os.path.join(os.path.dirname(__file__), 'templates/articles.html')
        self.response.out.write(template.render(path, template_values))
        
        
class Search(webapp.RequestHandler):
    def get(self):
        allArticles = misc.getAllPublicArticles()
        articles = []
        search = self.request.get('s')
        page = self.request.get('page')
        if page.isdigit():
           page = int(page)-1
        else:
            page = 1
        searchList = search.split(" ")
        for article in allArticles:
            for word in searchList:
                if(article.title.lower().find(word.lower()) != -1):
                    articles.append(article)   
                    break
        nextPageBool = False
        if len(articles) > misc.ARTICLES_PER_PAGE * page + misc.ARTICLES_PER_PAGE:
            nextPageBool = True
        articles = articles[misc.ARTICLES_PER_PAGE*page:misc.ARTICLES_PER_PAGE*page+misc.ARTICLES_PER_PAGE]
        template_values = {
            'articles': articles,
            'nextpage': (page+2),
            'nextpagebool':nextPageBool,
            'prevpage':(page),
            'search': search,
        }
        path = os.path.join(os.path.dirname(__file__), 'templates/search.html')
        self.response.out.write(template.render(path, template_values))
        

class Article(webapp.RequestHandler):
    def get(self):
        id = self.request.get('id')
        user = users.get_current_user()
        if(id.isdigit()):
            article = misc.getArticle(id)
            if(article == None):
                self.redirect('/')
            elif(article.public):
                
                loggedIn = False
                loginUrl = ""
                if user:
                    loggedIn = True
                else:
                    loginUrl = users.create_login_url(self.request.uri)
                
                template_values = {
                    'article': article,
                    'comments':printComments(article.comments),
                    'loggedin':loggedIn,
                    'loginurl': loginUrl,
                    'key': article.key(),
                }
                path = os.path.join(os.path.dirname(__file__), 'templates/article.html')
                self.response.out.write(template.render(path, template_values))
            else:
                self.redirect('/')
        else:
            self.redirect('/')
        
class CommentPost(webapp.RequestHandler):
    def post(self):
        article = db.get(self.request.get('key'))
        commentBody = self.request.get('commentBody')
        try:
            commentBody = misc.cleanHtml(commentBody)
            comment = Comment(author=users.get_current_user(),body=commentBody,date=datetime.datetime.now().date(),article=article.key())
        except:
            self.redirect('/article?id='+str(article.id))
            return
        comment.put()
        memcache.set(str(comment.key()),comment)
        article.comments.append(comment.key())
        article.put()
        memcache.set("article"+str(article.id),article)
        memcache.delete("publicArticles")
        memcache.delete("allArticles")
        self.redirect('/article?id='+str(article.id))
        
class EditCommentPost(webapp.RequestHandler):
    def post(self):
        comment = db.get(self.request.get('commentKey'))
        if(comment.author == users.get_current_user()):
            commentBody = self.request.get('commentBody')
            try:
                commentBody = misc.cleanHtml(commentBody)
                comment.body = commentBody
                comment.put()
                memcache.set(str(comment.key()), comment)
            except:
                self.redirect('/article?id='+str(comment.article.id))
                return
        self.redirect('/article?id='+str(comment.article.id))
        
class ReplyPost(webapp.RequestHandler):
    def post(self):
        parentComment = db.get(self.request.get('commentKey'))
        commentBody = self.request.get('commentBody')
        commentBody = misc.cleanHtml(commentBody)
        comment = Comment(author=users.get_current_user(),body=self.request.get('commentBody'),date=datetime.datetime.now().date(),_parent=parentComment,article=parentComment.article.key())
        comment.put()
        parentComment.children.append(comment.key())
        parentComment.put()
        memcache.set(str(parentComment.key()),parentComment)
        memcache.delete("publicArticles")
        memcache.delete("allArticles")
        self.redirect('/article?id='+str(comment.article.id))

class DeleteCommentPost(webapp.RequestHandler):
    def post(self):
        comment = db.get(self.request.get('key'))
        if(comment.author == users.get_current_user()):
            if not comment.children:
                article = comment.article
                article.comments.remove(comment.key())
                memcache.delete(str(comment.key()))
                comment.delete()
                article.put()
                memcache.delete("publicArticles")
                memcache.delete("allArticles")
                memcache.set("article"+str(article.id),article)
            else:
                comment.title = "deleted"
                comment.body = "deleted"
                comment.author = users.User("deleted")
                comment.date = datetime.datetime.now().date()
                comment.put()
                memcache.set(str(comment.key()), comment)
        self.redirect('/article?id='+str(comment.article.id))

def printComments(comments,switch=False):
    if(switch):
        ret = "<div class='articleCommentsSwitch'>"
    else:
        ret = "<div class='articleComments'>"
    for key in comments:
        comment = misc.getComment(key)
        ret += printComment(comment)
        if comment.children:
            ret += printComments(comment.children,(not switch))
    ret += "</div>"
    return ret

def printComment(comment):
    user = users.get_current_user()
    loggedin = False
    if user:
        loggedin = True
    commentauthor = False
    if(user == comment.author):
        commentauthor = True
    template_values = {
        'comment': comment,
        'loggedin':loggedin,
        'commentauthor': commentauthor,
        'key': comment.key(),
    }
    path = os.path.join(os.path.dirname(__file__), 'templates/comment.html')
    return template.render(path, template_values)

def main():
    application = webapp.WSGIApplication([('/', Main),
                                          ('/article', Article),
                                          ('/commentpost', CommentPost),
                                          ('/deletecommentpost', DeleteCommentPost),
                                          ('/editcommentpost', EditCommentPost),
                                          ('/replypost', ReplyPost),
                                          ('/search', Search),],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
