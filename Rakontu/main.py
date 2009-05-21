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
import logging

# GAE imports
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import memcache

# third party imports
import sys
sys.path.append("/Users/cfkurtz/Documents/personal/eclipse_workspace_kfsoft/Rakontu/lib/") 
from appengine_utilities.sessions import Session

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

def RequireLogin(func):
    def check_login(request):
        if not users.get_current_user():
            request.redirect('/login')
            return
        func(request)
    return check_login 

def GoogleUserIDForEmail(email):
    """Return a stable user_id string based on an email address, or None if
    the address is not a valid/existing google account."""
    newUser = users.User(email)
    key = TempUser(user=newUser).put()
    obj = TempUser.get(key)
    return obj.user.user_id() 

def MyDebug(text, msg="print"):
    logging.debug(">>>>>>>> %s >>>>>>>> %s" %(msg, text))

# --------------------------------------------------------------------------------------------
# Startup and creation
# --------------------------------------------------------------------------------------------
        
class StartPage(webapp.RequestHandler):
    """ What users see when they come to the main site, outside of any community (but logged in to Google).
    """
    @RequireLogin 
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
    @RequireLogin 
    def get(self):
        """Show fields to create community."""
        url, url_linktext = GenerateURLs(self.request)
        template_values = {'url': url, 'url_linktext': url_linktext}
        if users.get_current_user(): 
            template_values = {'user': users.get_current_user()}
            path = os.path.join(os.path.dirname(__file__), 'templates/createCommunity.html')
            self.response.out.write(template.render(path, template_values))
            
    @RequireLogin 
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
            governanceType="owner",
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
    @RequireLogin 
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
    @RequireLogin 
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
    @RequireLogin 
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
        
    @RequireLogin 
    def post(self):
        """Process choice of community to manage."""
        community_key = self.request.get('community_key')
        if community_key:
            session = Session()
            session['community_key'] = community_key
            self.redirect('/manageCommunity')
        else:
            self.redirect('/')
        
class ManageCommunityPage(webapp.RequestHandler):
    """ Page where user manages a community. 
    """
    @RequireLogin 
    def get(self):
        """Show info about community."""
        user = users.get_current_user()
        url, url_linktext = GenerateURLs(self.request)
        session = Session()
        community_key = session['community_key']
        if community_key:
            community = db.get(community_key) 
            if community:
                template_values = {
                                   'url': url, 
                                   'url_linktext': url_linktext, 
                                   'community': community, 
                                   'current_user': user, 
                                   'members': Member.all().fetch(1000)}
                path = os.path.join(os.path.dirname(__file__), 'templates/manageCommunity.html')
                self.response.out.write(template.render(path, template_values))
            else:
                self.redirect('/')
                
class ManageCommunityMembersPage(webapp.RequestHandler):
    """ Review, add, remove members.
    """
    @RequireLogin 
    def get(self):
        """Show info about community members."""
        user = users.get_current_user()
        url, url_linktext = GenerateURLs(self.request)
        session = Session()
        community_key = session['community_key']
        if community_key:
            community = db.get(community_key) 
            if community:
                currentMember = Member.all().filter("community = ", community).filter("googleAccountID = ", user.user_id()).fetch(1000)[0]
                template_values = {
                                   'url': url, 
                                   'url_linktext': url_linktext, 
                                   'community': community, 
                                   'current_user': user, 
                                   'current_member': currentMember,
                                   'community_members': Member.all().filter("community = ", community).fetch(1000)}
                path = os.path.join(os.path.dirname(__file__), 'templates/manageCommunity_Members.html')
                self.response.out.write(template.render(path, template_values))
            else:
                self.redirect('/')
                
    @RequireLogin 
    def post(self):
        MyDebug(self.request.arguments())
        """Process new and removed members."""
        user = users.get_current_user()
        url, url_linktext = GenerateURLs(self.request)
        session = Session()
        if session and session.has_key('community_key'):
            community_key = session['community_key']
        else:
            community_key = None
        if community_key:
            community = db.get(community_key) 
            if community:
                if "changeMemberships" in self.request.arguments():
                    communityMembers = Member.all().filter("community = ", community).fetch(1000)
                    for member in communityMembers:
                        for name, value in self.request.params.items():
                            if value.find(member.googleAccountID) >= 0:
                                (newType, id) = value.split("|") 
                                okayToSet = False
                                if newType != member.governanceType:
                                    if newType == "member":
                                        if not member.isOwner() or not community.memberIsOnlyOwner(member):
                                            okayToSet = True
                                    elif newType == "manager":
                                        if not member.isOwner() or not community.memberIsOnlyOwner(member):
                                            okayToSet = True
                                    elif newType == "owner":
                                        okayToSet = True
                                if okayToSet:
                                    member.governanceType = newType
                                    member.put()
                    membersToRemove = []
                    for member in communityMembers:
                        if self.request.get("remove|%s" % member.googleAccountID):
                            membersToRemove.append(member)
                    if membersToRemove:
                        for member in membersToRemove:
                            db.delete(member)
                elif self.request.arguments()[0] == "addMembers":
                    memberEmailsToAdd = self.request.get("newMemberEmails").split('\n')
                    for email in memberEmailsToAdd:
                        if email.strip():
                            userID = GoogleUserIDForEmail(email)
                            if userID:
                                if not community.hasMemberWithUserID(userID):
                                    member = Member(
                                        googleAccountID=userID,
                                        community=community,
                                        governanceType="member")
                                    member.put()
        self.redirect('/manageCommunity_Members')
            
                
class ManageCommunitySettingsPage(webapp.RequestHandler):
    pass
    
class ManageCommunityTechnicalPage(webapp.RequestHandler):
    pass
    
# --------------------------------------------------------------------------------------------
# Pages for members
# --------------------------------------------------------------------------------------------
        
class ChooseCommunityToVisitPage(webapp.RequestHandler):
    """ Page where user chooses a community to visit. 
        Checks to see what communities the user is a member of.
    """
    @RequireLogin 
    def get(self):
        """"Show user list of communities they belong to."""
        user = users.get_current_user()
        url, url_linktext = GenerateURLs(self.request)
        communities = []
        if user:
            members = Member.all().filter("googleAccountID = ", user.user_id()).fetch(1000)
            for member in members:
                communities.append(member.community)
        template_values = {'url': url, 'url_linktext': url_linktext, 'communities': communities}
        path = os.path.join(os.path.dirname(__file__), 'templates/chooseCommunityToVisit.html')
        self.response.out.write(template.render(path, template_values))
        
    @RequireLogin 
    def post(self):
        """Process choice of community to visit."""
        community_key = self.request.get('community_key')
        if community_key:
            session = Session()
            session['community_key'] = community_key
            self.redirect('/visitCommunity')
        else:
            self.redirect('/')
        
class VisitCommunityPage(webapp.RequestHandler):
    """ Page where user visits a community. 
    """
    @RequireLogin 
    def get(self):
        """Show info about community."""
        user = users.get_current_user()
        url, url_linktext = GenerateURLs(self.request)
        session = Session()
        community_key = session['community_key']
        if community_key:
            community = db.get(community_key) 
            if community:
                template_values = {
                                   'url': url, 
                                   'url_linktext': url_linktext, 
                                   'community': community, 
                                   'current_user': user, 
                                   'members': Member.all().fetch(1000)}
                path = os.path.join(os.path.dirname(__file__), 'templates/visitCommunity.html')
                self.response.out.write(template.render(path, template_values))
            else:
                self.redirect('/')
                
# --------------------------------------------------------------------------------------------
# Application and main
# --------------------------------------------------------------------------------------------
        
application = webapp.WSGIApplication(
                                     [('/', StartPage),
                                      
                                      # members
                                      ('/chooseCommunityToVisit', ChooseCommunityToVisitPage),
                                      ('/visitCommunity', VisitCommunityPage),
                                      
                                      # managers, owners
                                      ('/createCommunity', CreateCommunityPage),
                                      ('/chooseCommunityToManage', ChooseCommunityToManagePage),
                                      ('/manageCommunity', ManageCommunityPage),
                                      ('/manageCommunity_Members', ManageCommunityMembersPage),
                                      ('/manageCommunity_Settings', ManageCommunitySettingsPage),
                                      ('/manageCommunity_Technical', ManageCommunityTechnicalPage),
                                      
                                      # sys admin
                                      ('/admin/showAllCommunities', ShowAllCommunities),
                                      ('/admin/showAllMembers', ShowAllMembers)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
