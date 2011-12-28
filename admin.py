from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
import models
import datetime


class AdminMain(webapp.RequestHandler):
    def get(self):
        self.response.out.write(header())
        self.response.out.write('Hello admin!')
        self.response.out.write(footer())
        
class AdminNewArticle(webapp.RequestHandler):
    def get(self):
        self.response.out.write(header())
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
    ret = ""
    ret += "<html><body>"
    return ret

def footer():
    ret = "</body></html>"
    return ret

def main():
    application = webapp.WSGIApplication([('/admin', AdminMain),
                                          ('/admin/new',AdminNewArticle),
                                          ('/admin/newpost',AdminNewArticlePost)],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
