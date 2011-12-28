from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from models import *
import datetime


class Main(webapp.RequestHandler):
    def get(self):
        self.response.out.write(header())
        articles = getAllPublic()
        self.response.out.write(printArticles(articles))
        self.response.out.write(footer())

class Article(webapp.RequestHandler):
    def get(self):
        self.response.out.write(header())
        id = self.request.get('id')
        if(id.isdigit()):
            article = getArticle(id)
            if(article == None):
                self.redirect('/')
            else:
                self.response.out.write(printArticlePage(article))
                self.response.out.write(printComments(article))
                self.response.out.write(commentBox(article))
        else:
            self.redirect('/')
        self.response.out.write(footer())
        
class CommentPost(webapp.RequestHandler):
    def post(self):
        article = db.get(self.request.get('key'))
        comment = Comment(author="anon",body=self.request.get('commentBody'),date=datetime.datetime.now().date())
        comment.put()
        article.comments.append(comment.key())
        article.put()
        self.redirect('/article?id='+str(article.id))

def commentBox(article):
    ret = """
    <div class='commentBox'><form name='comment' action='/commentpost' method='post'>
        <div class='commentTextArea'>
            <textarea name='commentBody' cols='50' rows='6'></textarea>
        </div>
        <div class='commentHiddenSubmit'>
            <input type='hidden' name='key' value='%s' />
            <input type='submit' value='Comment' />
        </div>
    </div>
    """ %(str(article.key()))
    return ret

def printArticles(articles):
    ret = "<div class='articlesDiv'>"
    for article in articles:
        ret += printArticle(article)
    ret += "</div>"
    return ret

def printArticlePage(article):
    ret = """
        <div class='article'>
            <div class='articleHeader'>
                <div class='articleTitle'>
                    %s
                </div>
                <div class='articleDate'>
                    %s
                </div>
            </div>
            <div class='articleBody'>
                %s
            </div>
        </div>
    """ %(article.title, str(article.date), article.body)
    return ret

def printArticle(article):
    title = makeLink("/article?id="+str(article.id), article.title)
    comments = makeLink("/article?id="+str(article.id), "Comments ("+str(len(article.comments))+")")   
    ret = """
        <div class='article'>
            <div class='articleHeader'>
                <div class='articleTitle'>
                    %s
                </div>
                <div class='articleDate'>
                    %s
                </div>
            </div>
            <div class='articleBody'>
                %s
            </div>
            <div class='articleCommentLink'>
                %s
            </div>
        </div>
    """ %(title, str(article.date), article.body,comments)
    return ret

def printComments(article):
    ret = "<div class='articleComments'>"
    length = len(article.comments)
    if(length > 0):
        ret += str(length)+" comments:"
    else:
        ret += "Be the first to comment!"
    for key in article.comments:
        ret += printComment(getComment(key))
    ret += "</div>"
    return ret

def printComment(comment):
    ret = """
    <div class='articleComment'>
        <div class='commentHeader'>
            <div class='commentAuthor'>    
                %s
            </div>
            <div class='commentDate'>
                %s
            </div>
        </div>
        <div class='commentBody'>
            %s
        </div>
    </div>
    """ %(comment.author,str(comment.date),comment.body)
    return ret

def makeLink(url,content):
    return "<a href='%s'>%s</a>" %(url,content)

def header():
    ret = """
    <html>
        <head>
            <link rel="stylesheet" href="/static/global.css"/>
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
    application = webapp.WSGIApplication([('/', Main),
                                          ('/article', Article),
                                          ('/commentpost', CommentPost)],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
