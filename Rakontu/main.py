# --------------------------------------------------------------------------------------------
# RAKONTU
# Description: Rakontu is open source story sharing software.
# Version: pre-0.1
# License: GPL 3.0
# Google Code Project: http://code.google.com/p/rakontu/
# --------------------------------------------------------------------------------------------

import cgi
import os

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

# NOTE most of this code is just from the guestbook example right now, it's just here for reference
# while I get something real written. My plan is to (a) write a method to generate some fake data, then
# (b) put up one page with the main viewer showing the generated data. Then I can move on from there.

class Greeting(db.Model):
  creator = db.UserProperty()
  teller = db.UserProperty()
  editor = db.UserProperty()
  text = db.StringProperty(multiline=True)
  dateCreated = db.DateTimeProperty(auto_now_add=True)

class MainPage(webapp.RequestHandler):
  def get(self):
    greetings_query = Greeting.all().order('-date')
    greetings = greetings_query.fetch(10)

    if users.get_current_user():
      url = users.create_logout_url(self.request.uri)
      url_linktext = 'Logout'
    else:
      url = users.create_login_url(self.request.uri)
      url_linktext = 'Login'

    template_values = {
      'greetings': greetings,
      'url': url,
      'url_linktext': url_linktext,
      }

    path = os.path.join(os.path.dirname(__file__), 'template.html')
    self.response.out.write(template.render(path, template_values))
    
class MainHandler(webapp.RequestHandler):
  def post(self):
    greeting = Greeting()

    if users.get_current_user():
      greeting.author = users.get_current_user()

    greeting.content = self.request.get('content')
    greeting.put()
    self.redirect('/')
    
# THIS is where I'm actually adding code right now
    
def CreateABunchOfFakeData():
    aMember = Member()
    aStory = Story(
                  title="My day at the zoo",
                  text="I lost my freeze pop, and the lion ate my cousin. Pretty fun day.",
                  creator=aMember,
                  attribution="member",
                  tookPlace=datetime.datetime(2009, 4, 2),
                  collected=datetime.datetime.now)
    aStory.put()
    aComment = Comment(
                       subject="Your cousin??", 
                       post="Is that really true about your cousin?",
                       article=aStory,
                       creator=anotherMember,
                       attribution="personification",
                       personification=aPersonification,
                       collected=datetime.datetime.now)
    # CFK WORKING HERE

application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/sign', MainHandler)],
                                     debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
