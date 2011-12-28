from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
import models
import datetime
import blog
import misc


class AdminMain(webapp.RequestHandler):
    def get(self):
        self.response.out.write(misc.header())
        articleTable = "<div class='articleTableDiv'><table class='articleTable'><tr><th>ID#</th><th>Title</th><th>Comments</th><th>Public</th></tr>"
        articles = models.getAll()
        even = True
        for article in articles:
            link = "/admin/article?id="+str(article.id)
            if(even):
                articleTable += "<tr class='even'><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" %(misc.makeLink(link, str(article.id)),misc.makeLink(link, article.title),misc.makeLink(link, str(models.countComments(article.comments))),misc.makeLink(link, str(article.public)))
            else:
                articleTable += "<tr class='odd'><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" %(misc.makeLink(link, str(article.id)),misc.makeLink(link, article.title),misc.makeLink(link, str(models.countComments(article.comments))),misc.makeLink(link, str(article.public)))
            even = not even
        articleTable += "</table></div>"
        self.response.out.write(articleTable)
        self.response.out.write(footer())

class AdminArticle(webapp.RequestHandler):
    def get(self):
        self.response.out.write(misc.header())
        
        self.response.out.write(footer())
        
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
        self.response.out.write(footer())

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

def main():
    application = webapp.WSGIApplication([('/admin', AdminMain),
                                          ('/admin/new',AdminNewArticle),
                                          ('/admin/article',AdminArticle),
                                          ('/admin/newpost',AdminNewArticlePost)],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
