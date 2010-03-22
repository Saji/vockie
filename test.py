import os, json
from random import randint, shuffle
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import db

dicfile = file("barron.json").read()
dic = json.loads(dicfile)
templatepath = os.path.join(os.path.dirname(__file__), 'templates/dialog.tmpl')

def cumulate(dic = dic):
    dic[0][1] = 0
    for i, x in enumerate(dic): 
        if i != 0:
            dic[i][1] = dic[i][0] + dic[i-1][1]
cumulate()

class UserRecord(db.Model):
    ID = db.StringProperty()
    name = db.StringProperty()
    dic = db.StringProperty()
    settings = db.StringProperty()
    def test(record, bar):
        return bar

class MyUser:
    def __init__(self, ID, name, dic, settings):
        self.id = ID
        self.name = name
        self.dic = dic
        self.settings = settings
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
        return ret
    def getrandom(self):
        return self.dic[randint(0, len(dic)-1)]
    def incscore(self, word):
        for d in self.dic:
            if d[2] == word:
                d[1] += 1
                cumulate(self.dic)
                break

class MainPage(webapp.RequestHandler):
    def get(self):
        cookie = self.request.headers['Cookie'] if self.request.headers.has_key('Cookie') else False
        user_logged = bool(users.get_current_user())
        known = True if cookie and user_logged else False
        currentuser = MyUser(randint(0,10000000), 'anon', dic, {})
        self.response.headers['Content-Type'] = 'text/html'
        if not known:
            self.response.headers['Set-Cookie'] = currentuser.id
            a = [currentuser.getranked() for x in range(5)]
            dialog = {}
            dialog['question'] = a[0][2]
            dialog['choices'] = [{'word': x[2], 'defn': x[3]} for x in a]
            shuffle(dialog['choices'])
            testuser = UserRecord()
#            self.response.out.write(testuser.test('foo'))
            self.response.out.write(template.render(templatepath, dialog))
        else:
            pass


        # elif user_logged:
        #     pass
        # elif cookie:
        #     self.response.out.write(cookie)
        # if self.request.is_xhr:
        #     self.response.out.write('LOL AJAX FUCK YEAH!')

def main():
    application = webapp.WSGIApplication( [('/', MainPage)],
                                          debug=True )
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
