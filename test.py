import os, string
from django.utils import simplejson
from random import randint, shuffle, Random
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import db

dicfile = file("barron.json").read()
dic = simplejson.loads(dicfile)
templatepath = os.path.join(os.path.dirname(__file__), 'templates/dialog.tmpl')
maintemplate = 'main.tmpl'
ajxtemplate = 'dialogwrapper.tmpl'
scoreincorrect = 10
scorecorrect = -5
maxscore = 100
choices = 6

def cumulate(dic = dic):
    dic[0][1] = 0
    for i, x in enumerate(dic):
        if i != 0:
            dic[i][1] = dic[i][0] + dic[i-1][1]

def getuser(ident):
    query = MyUser.all()
    return query.filter('ident =', ident).get()
def createuser(user):
    if isinstance(user, str):
        user = MyUser(ident=randstr(), name=user, dic=dic);
    else:
        user = MyUser(ident=user.user_id(), name=user.nickname(), dic=dic)
    user.put()
    return user
def isgooglecookie(handler):
    return True if len(getcookie(handler)) > 12 else False
def deletecookie(handler):
    del(handler.request.headers['Cookie'])
def getcookie(handler):
    if handler.request.headers.has_key('Cookie'):
        return handler.request.headers['Cookie']
    else:
        return ''
def getpostvar(handler, var):
    if handler.request.postvars.has_key(var):
        return handler.request.postvars.get(var)
    else: return ''
def cookieuser(handler):
    cookie = getcookie(handler)
    return None if not cookie else getuser(cookie)
def googleuser():
    return users.get_current_user()
def randstr():
    return ''.join(Random().sample(string.letters+string.digits, 12))
def serve(handler, currentuser):
    handler.response.headers['Set-Cookie'] = currentuser.ident
    a = [currentuser.getrandom() for x in range(choices - 1)]
    a.insert(0, currentuser.getranked())
    templatedata = {'question': a[0][2],
              'choices': [{'word': x[2], 'defn': x[3]} for x in a]}
    if handler.request.is_xhr:
        templatedata['mode'] = ajxtemplate
    else:
        templatedata['mode'] = maintemplate
        if googleuser():
            templatedata['loginurl'] = users.create_logout_url(handler.request.path)
            templatedata['logoption'] = 'Logout'
        else:
            templatedata['loginurl'] = users.create_login_url(handler.request.path)
            templatedata['logoption'] = 'Login'
    templatedata['name'] = currentuser.name
    shuffle(templatedata['choices'])
    handler.response.out.write(template.render(templatepath, templatedata))
def deletestraycookie(handler):
    if not googleuser() and isgooglecookie(handler):
        deletecookie(handler)
cumulate()

################# REWRITE THIS ##########################
class JSONProperty(db.Property):
    # data_type = db.Text
    # def __init__(self, *args, **kwds):
    #     self._require_parameter(kwds, 'indexed', False)
    #     kwds['indexed'] = True
    #     super(JSONProperty, self).__init__(*args, **kwds)
    def get_value_for_datastore(self, model_instance):
        value = super(JSONProperty, self).get_value_for_datastore(
            model_instance)
        if value is not None:
            value = simplejson.dumps(value)
            return db.Text(value)
    def make_value_from_datastore(self, value):
        if value is not None:
            return simplejson.loads(value)

class MyUser(db.Model):
    ident = db.StringProperty()
    name = db.StringProperty()
    dic = JSONProperty()
    lastattempt = JSONProperty()
    def getranked(self):
        n = randint(0, self.dic[-1][1])
        def closer(a, b, n):
            return True if abs(n - a) <= abs(n - b) else False
        ret = []
        for i in range(len(self.dic)):
            this = self.dic[i][1]
            if i + 1 == len(self.dic): #no next
                ret = dic[i]
            else:
                next = self.dic[i+1][1]
                if closer(this, next, n):
                    ret = dic[i]
                    break
        self.lastattempt = ret
        self.put()
        return ret
    def getrandom(self):
        return self.dic[randint(0, len(dic)-1)]
    def updatescore(self, word, score):
        for d in self.dic:
            if d[2] == word:
                if (score < 0 and d[1] < score) or (score + d[1] > maxscore):
                    return
                d[1] += score
                cumulate(self.dic)
                self.put()
                break

class MainPage(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        deletestraycookie(self)
        user = None
        if googleuser():
            if not getuser(googleuser().user_id()):
                user = createuser(user=googleuser())
            else:
                user = getuser(googleuser().user_id())
        elif cookieuser(self):
            user = cookieuser(self)
        else:
            user = createuser(user='anon')
        serve(self, user)

class AJX(webapp.RequestHandler):
    def post(self):
        deletestraycookie(self)
        user = None
        question = getpostvar(self, 'ques')
        iscorrect = getpostvar(self, 'iscorrect')
        if googleuser():
            user = getuser(googleuser().user_id())
        elif cookieuser(self):
            user = cookieuser(self)
        else:
            self.response.out.write('unknown user')
            return
        if not question == user.lastattempt[2]:
            self.response.out.write('off sync')
            return
        else:
            if iscorrect == 'true':
                user.updatescore(question, scorecorrect)
            else:
                user.updatescore(question, scoreincorrect)
        serve(self, user)                                  
#        self.response.out.write(user.lastattempt)

def main():
    application = webapp.WSGIApplication( [('/', MainPage), ('/ajx', AJX)],
                                          debug=True )
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
