from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.ext.webapp import util
from google.appengine.api import memcache
from models import *
import misc
import datetime


class Main(webapp.RequestHandler):
    def get(self):
        self.response.out.write(misc.header())
        page = self.request.get('page')
        if(page.isdigit()):
            page = int(page)
        else:
            page = 0
        ret = misc.getPublicArticles(page)
        articles = ret[0]
        nextPageBool = ret[1]
        articlesDiv = "<div class='articlesDiv'>"
        for article in articles:
            articlesDiv += printArticle(article)
        articlesDiv += "</div>"
        self.response.out.write(articlesDiv)
        prevPage = """<a href='/?page=%s'>Previous page""" %(page-1)
        nextPage = ""
        if(page == 0):
            prevPage = ""
        if(nextPageBool):
            nextPage = """<a href='/?page=%s'>Next page""" %(page+1)
        self.response.out.write("""
        <div class='pageControlDiv'>
            <div class='prevPageDiv'>
                %s
            </div>
            <div class='nextPageDiv'>
                %s
            </div>
        </div>
        """ %(prevPage,nextPage))
        self.response.out.write(misc.footer())
        
class Search(webapp.RequestHandler):
    def get(self):
        self.response.out.write(misc.header())
        allArticles = misc.getAllPublicArticles()
        articles = []
        search = self.request.get('s')
        for article in allArticles:
            if(article.title.lower().find(search.lower()) != -1):
                articles.append(article)
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
            elif(article.public):
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
                if article.comments:
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
        else:
            self.redirect('/')
        self.response.out.write(misc.footer())
        
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
        if comment.children:
            ret += printComments(comment.children,(not switch))
    ret += "</div>"
    return ret

def printComment(comment):
    user = users.get_current_user()
    key = str(comment.key())
    reply = ""
    if(user):
        reply ="""<a id='reply_%s' href='javascript:void(0)' onclick="reply('%s')" >reply</a>""" %(key,key)
    deleteEdit = ""
    if(user == comment.author):
        deleteEdit = """
        <a href='javascript:void(0)' onclick="deleteComment('%s')" >delete</a>
        <a id='edit_%s' href='javascript:void(0)' onclick="editComment('%s')" >edit</a>
        <form id='deleteComment_%s' name='deleteComment_%s' action='/deletecommentpost' method='post'>
            <input type='hidden' name='key' value='%s' />
        </form>
        """ %(key,key,key,key,key,key)
    
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
                %s
                %s
            </div>
        </div>
        <div id='commentBody_%s' class='commentBody'>
%s
        </div>
        <div id='div_%s' class='commentReplyDiv'>
            
        </div>
    </div>
    """ %(comment.author,str(comment.date),reply,deleteEdit,key,comment.body,key)
    return ret

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
