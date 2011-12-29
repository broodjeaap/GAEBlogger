from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.ext.webapp import util
from models import *
import misc
import datetime


class Main(webapp.RequestHandler):
    def get(self):
        self.response.out.write(misc.header())
        articles = misc.getAllPublicArticles()
        articlesDiv = "<div class='articlesDiv'>"
        for article in articles:
            articlesDiv += printArticle(article)
        articlesDiv += "</div>"
        self.response.out.write(articlesDiv)
        self.response.out.write(misc.footer())

class Article(webapp.RequestHandler):
    def get(self):
        self.response.out.write(misc.header())
        id = self.request.get('id')
        user = users.get_current_user()
        if(id.isdigit()):
            article = misc.getArticle(id)
            if(article == None):
                self.redirect('/')
            else:
                self.response.out.write(
                                        """
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
                                    """ %(article.title, str(article.date), article.body))
                length = len(article.comments) 
                if(length > 0):
                    self.response.out.write("Comments ("+str(misc.countComments(article.comments))+"): ")
                else:
                    self.response.out.write("Be the first to comment!")
                self.response.out.write(printComments(article.comments))
                if(user):
                    self.response.out.write(
                                            """
                                            <div class='commentBox'><form name='comment' action='/commentpost' method='post'>
                                                <div class='commentTextArea'>
                                                    <textarea name='commentBody' cols='50' rows='6'></textarea>
                                                </div>
                                                <div class='commentHiddenSubmit'>
                                                    <input type='hidden' name='key' value='%s' />
                                                    <input type='submit' value='Comment' />
                                                </div>
                                            </div>
                                            """ %(str(article.key())))
                else:
                    self.response.out.write("<a href='"+users.create_login_url(self.request.uri)+"'>Login to comment.</a>")
        else:
            self.redirect('/')
        self.response.out.write(misc.footer())
        
class CommentPost(webapp.RequestHandler):
    def post(self):
        article = db.get(self.request.get('key'))
        comment = Comment(author=users.get_current_user(),body=self.request.get('commentBody'),date=datetime.datetime.now().date(),article=article.key())
        comment.put()
        article.comments.append(comment.key())
        article.put()
        self.redirect('/article?id='+str(article.id))
        
class ReplyPost(webapp.RequestHandler):
    def post(self):
        parentComment = db.get(self.request.get('commentKey'))
        comment = Comment(author=users.get_current_user(),body=self.request.get('commentBody'),date=datetime.datetime.now().date(),article=parentComment.article)
        comment.put()
        parentComment.children.append(comment.key())
        parentComment.put()
        self.redirect('/article?id='+str(comment.article.id))

def printArticlePage(article):
    
    return ret

def printArticle(article):
    title = misc.makeLink("/article?id="+str(article.id), article.title)
    comments = misc.makeLink("/article?id="+str(article.id), "Comments ("+str(misc.countComments(article.comments))+")")   
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

def printComments(comments,switch=False):
    if(switch):
        ret = "<div class='articleCommentsSwitch'>"
    else:
        ret = "<div class='articleComments'>"
    for key in comments:
        comment = misc.getComment(key)
        ret += printComment(comment)
        if(len(comment.children) > 0):
            ret += printComments(comment.children,(not switch))
        
    ret += "</div>"
    return ret

def printComment(comment):
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
            <div class='commentReply'>
                <a id='link_%s' href='javascript:void(0)' onclick="reply('%s')" >reply</a>
            </div>
        </div>
        <div class='commentBody'>
            %s
        </div>
        <div id='div_%s' class='commentReplyDiv'>
            
        </div>
    </div>
    """ %(comment.author,str(comment.date),key,key,comment.body,key)
    return ret

def main():
    application = webapp.WSGIApplication([('/', Main),
                                          ('/article', Article),
                                          ('/commentpost', CommentPost),
                                          ('/replypost', ReplyPost)],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
