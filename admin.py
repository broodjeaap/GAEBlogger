from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import memcache
import models
import datetime
import blog
import misc
import os


class AdminMain(webapp.RequestHandler):
    def get(self):
        self.response.out.write(misc.header())
        appName = "#"
        id = os.environ["APPLICATION_ID"]
        tilde = id.find("~")
        if(tilde != -1):
            appName = "<a href='https://appengine.google.com/dashboard?app_id="+id[tilde+1:]+"'>App Settings</a>"
        self.response.out.write(
        """
        <div class='adminMainDiv'>
            <div class='adminNewArticleDiv'>
                <a href='/admin/new'>New Article</a>
            </div>
            
            <div class='adminArticleArchiveDiv'>
                <a href='/admin/archive'>Article Archive</a>
            </div>
            <div style="clear: both;"></div>
            <div class='adminAppSettingsDiv'>
                %s
            </div>
            <div style="clear: both;"></div>
        </div>
        """ %(appName)) 

        self.response.out.write(misc.footer())
        
class AdminArchive(webapp.RequestHandler):
    def get(self):
        self.response.out.write(misc.header())
        articleTable = "<div class='articleTableDiv'><table class='articleTable'><tr class='head'><th class='id'>ID#</th><th class='title'>Title</th><th class='comment'>Comments</th><th class='public'>Public</th></tr>"
        articles = misc.getAllArticles()
        even = True
        for article in articles:
            link = "/admin/article?id="+str(article.id)
            if(even):
                articleTable += "<tr class='even'><td class='id'>%s</td><td class='title'>%s</td><td class='comment'>%s</td><td class='public'>%s</td></tr>" %(misc.makeLink(link, str(article.id)),misc.makeLink(link, article.title),misc.makeLink(link, str(misc.countComments(article.comments))),misc.makeLink(link, str(article.public)))
            else:
                articleTable += "<tr class='odd'><td class='id'>%s</td><td class='title'>%s</td><td class='comment'>%s</td><td class='public'>%s</td></tr>" %(misc.makeLink(link, str(article.id)),misc.makeLink(link, article.title),misc.makeLink(link, str(misc.countComments(article.comments))),misc.makeLink(link, str(article.public)))
            even = not even
        articleTable += "</table></div>"
        self.response.out.write(articleTable)
        self.response.out.write(misc.footer())

class AdminArticle(webapp.RequestHandler):
    def get(self):
        self.response.out.write(misc.header())
        article = misc.getArticle(self.request.get('id'))
        checked = ""
        if(article.public):
            checked = "checked='checked'"
        articleDiv = """
        <script type='text/javascript' src='/static/admin.js'></SCRIPT>
        <div class='articleEditDiv'>
            <form name='editArticle' action='/admin/editpost' method='post'>
                <div class='titleEditDiv'>
                    <input type='text' name='title' value='%s' />
                </div>
                <div class='editBody'>
                    <textarea name='body' cols='100' rows='20'>%s</textarea>
                </div>
                <div class='editPublic'>
                    <input type='checkbox' name='public' %s value='public' />Public
                </div>
                <input type='submit' value='Save' />
                <input type='hidden' name='key' value='%s' />
            </form>
        </div>""" %(article.title, article.body, checked, str(article.key()))
        self.response.out.write(articleDiv)
        self.response.out.write(printAdminComments(article.comments))
        self.response.out.write(misc.footer())

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
        self.response.out.write(misc.header())
        self.response.out.write(
        """
        <div id='newArticleDiv'><form name='newArticle' action='/admin/newpost' method='post'>
        <div class='adminTitle' id='newArticleTitle'><input type='text' value='Title' name='title' id='title'/></div>
        <div class='adminBody' id='newArticleBody'><textarea name='body' cols='100' rows='20'></textarea></div>
        <div class='adminPublic' id='newArticlePublic'><input type='checkbox' name='public' value='public' /> Publish on blog. </div>
        <div class='adminSubmit' id='newArticleSubmit'><input type='submit' name='submit' value='Save' /></div>
        </form></div>
        """)
        self.response.out.write(misc.footer())

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
    key = str(comment.key())
    ret = """
    <div class='articleComment'>
        <div class='commentHeader'>
            <div class='commentAuthor'>    
                %s
            </div>
            <div class='commentDate'>
                %s
            </div>
            <div class='commentDelete'>
                <form id='form_%s' name='deleteComment' action='/admin/deletecommentpost' method='post'>
                    <input type='hidden' name='key' value='%s' />
                    <input type='hidden' name='reason' value='' id='reason_%s'/>
                    <input type='button' value='Delete' onclick="deletecomment('%s')" />
                </form>
                
            </div>
        </div>
        <div class='commentBody'>
            %s
        </div>
    </div>
    """ %(comment.author,str(comment.date),key,key,key,key,comment.body)
    return ret

def main():
    application = webapp.WSGIApplication([('/admin', AdminMain),
                                          ('/admin/archive', AdminArchive),
                                          ('/admin/new',AdminNewArticle),
                                          ('/admin/article',AdminArticle),
                                          ('/admin/newpost',AdminNewArticlePost),
                                          ('/admin/editpost',AdminEditArticlePost),
                                          ('/admin/deletecommentpost',DeleteCommentPost)],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
