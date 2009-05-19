# --------------------------------------------------------------------------------------------
# RAKONTU
# Description: Rakontu is open source story sharing software.
# Version: pre-0.1
# License: GPL 3.0
# Google Code Project: http://code.google.com/p/rakontu/
# --------------------------------------------------------------------------------------------

# python imports
import cgi
import os

# GAE imports
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import memcache

# local file imports
from models import *

# --------------------------------------------------------------------------------------------
# Utility functions
# --------------------------------------------------------------------------------------------
        
def GenerateURLs(request):
    """ Used to make login/logout link on every page.
        Probably some better way to do this.
    """
    if users.get_current_user():
        url = users.create_logout_url(request.uri)
        url_linktext = 'Logout'
    else:
        url = users.create_login_url(request.uri)
        url_linktext = 'Login'
    return url, url_linktext

# --------------------------------------------------------------------------------------------
# Startup and creation
# --------------------------------------------------------------------------------------------
        
class StartPage(webapp.RequestHandler):
    """ What users see when they come to the main site, outside of any community.
    """
    def get(self):
        """Just a bunch of links at this point. If the user is a sys admin (for the GAE app) they get more links."""
        url, url_linktext = GenerateURLs(self.request)
        template_values = {
                           'url': url, 
                           'url_linktext': url_linktext, 
                           'user': users.get_current_user(), 
                           'user_is_admin': users.is_current_user_admin()}
        path = os.path.join(os.path.dirname(__file__), 'templates/startPage.html')
        self.response.out.write(template.render(path, template_values))

class CreateCommunityPage(webapp.RequestHandler):
    """ Page to make a new community.
    """
    def get(self):
        """Show fields to create community."""
        url, url_linktext = GenerateURLs(self.request)
        template_values = {'url': url, 'url_linktext': url_linktext}
        if users.get_current_user(): 
            template_values = {'user': users.get_current_user()}
            path = os.path.join(os.path.dirname(__file__), 'templates/createCommunity.html')
            self.response.out.write(template.render(path, template_values))
            
    def post(self):
        """Process request and create new community, with user as owner."""
        user = users.get_current_user()
        community = Community(
          name=self.request.get('name'),
          description=self.request.get('description'))
        community.put()
        member = Member(
            googleAccountID=user.user_id(),
            community=community,
            roles=["owner"],
            nickname = self.request.get('nickname'),
            nicknameIsRealName = self.request.get('nickname_is_real_name')=="yes",
            profileText = self.request.get('profile_text)'))
        member.put()
        self.redirect('/')
        
# --------------------------------------------------------------------------------------------
# Pages for sys admin
# --------------------------------------------------------------------------------------------
        
class ShowAllCommunities(webapp.RequestHandler):
    """For sys admin, to review all communities."""
    def get(self):
        """Show info on all communities."""
        if users.is_current_user_admin():
            url, url_linktext = GenerateURLs(self.request)
            template_values = {'url': url, 'url_linktext': url_linktext, 'communities': Community.all().fetch(1000), 'members': Member.all().fetch(1000)}
            path = os.path.join(os.path.dirname(__file__), 'templates/showAllCommunities.html')
            self.response.out.write(template.render(path, template_values))
        else:
            self.redirect('/')

class ShowAllMembers(webapp.RequestHandler):
    """For sys admin, to review all members."""
    def get(self):
        """Show info on all members."""
        if users.is_current_user_admin():
            url, url_linktext = GenerateURLs(self.request)
            template_values = {'url': url, 'url_linktext': url_linktext,'members': Member.all().fetch(1000)}
            path = os.path.join(os.path.dirname(__file__), 'templates/showAllMembers.html')
            self.response.out.write(template.render(path, template_values))
        else:
            self.redirect('/')

# --------------------------------------------------------------------------------------------
# Pages for managers and owners
# --------------------------------------------------------------------------------------------
        
class ChooseCommunityToManagePage(webapp.RequestHandler):
    """ Page where user chooses a community to manage. 
        Checks to see what communities the user is an owner or manager of.
    """
    def get(self):
        """"Show user list of communities they can manage."""
        user = users.get_current_user()
        url, url_linktext = GenerateURLs(self.request)
        communities = []
        if user:
            members = Member.all().filter("googleAccountID = ", user.user_id()).fetch(1000)
            for member in members:
                if member.isManager() or member.isOwner():
                    communities.append(member.community)
        template_values = {'url': url, 'url_linktext': url_linktext, 'communities': communities}
        path = os.path.join(os.path.dirname(__file__), 'templates/chooseCommunityToManage.html')
        self.response.out.write(template.render(path, template_values))
        
    def post(self):
        """Process choice of community to manage."""
        user = users.get_current_user()
        if user:
            community_key = self.request.get('community_key')
            if community_key:
                memcache.add("community_key", community_key, 60)
                self.redirect('/manageCommunity')
            else:
                self.redirect('/')
        
class ManageCommunityPage(webapp.RequestHandler):
    """ Page where user manages a community. 
        (Doesn't do much yet.)
    """
    def get(self):
        """Show info about community."""
        user = users.get_current_user()
        url, url_linktext = GenerateURLs(self.request)
        community_key = memcache.get("community_key")
        if community_key:
            community = db.get(community_key) 
            if community:
                template_values = {'url': url, 'url_linktext': url_linktext, 'community': community, 'user': user, 'members': Member.all().fetch(1000)}
                path = os.path.join(os.path.dirname(__file__), 'templates/manageCommunity.html')
                self.response.out.write(template.render(path, template_values))
            else:
                self.redirect('/')
        
application = webapp.WSGIApplication(
                                     [('/', StartPage),
                                      ('/createCommunity', CreateCommunityPage),
                                      ('/chooseCommunityToManage', ChooseCommunityToManagePage),
                                      ('/manageCommunity', ManageCommunityPage),
                                      ('/showAllCommunities', ShowAllCommunities),
                                      ('/showAllMembers', ShowAllMembers)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
