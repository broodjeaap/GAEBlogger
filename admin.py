from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext import db
import models
import datetime
import blog
import misc


class AdminMain(webapp.RequestHandler):
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
        <div class='articleEditDiv'>
            <form name='editArticle' action='/admin/editpost' method='post'>
                <div class='titleEditDiv'>
                    <input type='text' name='title' value='%s' />
                </div>
                <div class='editBody'>
                    <textarea name='body' cols='60' rows='10'>%s</textarea>
                </div>
                <div class='editPublic'>
                    <input type='checkbox' name='public' %s value='public' />Public
                </div>
                <input type='submit' value='Save' />
                <input type='hidden' name='key' value='%s' />
            </form>
        </div>""" %(article.title, article.body, checked, str(article.key()))
        self.response.out.write(articleDiv)
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
        article.put()
        self.redirect('/admin/article?id='+str(article.id))

class AdminNewArticle(webapp.RequestHandler):
    def get(self):
        self.response.out.write(misc.header())
        form = "<div id='newArticleDiv'><form name='newArticle' action='/admin/newpost' method='post'>"
        form += "<div class='adminTitle' id='newArticleTitle'><input type='text' value='Title' name='title' id='title'/></div>"
        form += "<div class='adminBody' id='newArticleBody'><textarea name='body' cols='60' rows='10'></textarea></div>"
        form += "<div class='adminPublic' id='newArticlePublic'><input type='checkbox' name='public' value='public' /> Publish on blog. </div>"
        form += "<div class='adminSubmit' id='newArticleSubmit'><input type='submit' name='submit' value='Save' /></div>"
        form += "</form></div>"
        self.response.out.write(form)
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
        self.redirect('/article?id='+str(article.id))

def main():
    application = webapp.WSGIApplication([('/admin', AdminMain),
                                          ('/admin/new',AdminNewArticle),
                                          ('/admin/article',AdminArticle),
                                          ('/admin/newpost',AdminNewArticlePost),
                                          ('/admin/editpost',AdminEditArticlePost)],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
