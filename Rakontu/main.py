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

# third party imports
import sys
sys.path.append("/Users/cfkurtz/Documents/personal/eclipse_workspace_kfsoft/Rakontu/lib/") 
from appengine_utilities.sessions import Session

# local file imports
from models import *
import systemquestions

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

# --------------------------------------------------------------------------------------------
# Startup page
# --------------------------------------------------------------------------------------------
        
class StartPage(webapp.RequestHandler):
    """ What users see when they come to the main site, outside of any community (but logged in to Google).
    """
    def get(self):
        url, url_linktext = GenerateURLs(self.request)
        user = users.get_current_user()
        communities = []
        if user:
            members = Member.all().filter("googleAccountID = ", user.user_id()).fetch(1000)
            for member in members:
                try:
                    communities.append(member.community)
                except:
                    pass # if can't link to community don't use it
        template_values = {
                           'url': url, 
                           'url_linktext': url_linktext, 
                           'user': users.get_current_user(), 
                           'communities': communities,
                           }
        path = os.path.join(os.path.dirname(__file__), 'templates/startPage.html')
        self.response.out.write(template.render(path, template_values))

    @RequireLogin 
    def post(self):
        MyDebug("in startpage post!")
        MyDebug(self.request.arguments())
        if "visitCommunity" in self.request.arguments():
            community_key = self.request.get('community_key')
            if community_key:
                session = Session()
                session['community_key'] = community_key
                self.redirect('/visitCommunity')
            else:
                self.redirect('/')
        elif "createCommunity" in self.request.arguments():
            self.redirect("/createCommunity")

# --------------------------------------------------------------------------------------------
# Create new community
# --------------------------------------------------------------------------------------------
        
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
        else:
            self.redirect("/")
            
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
# Visit community
# --------------------------------------------------------------------------------------------
        
class VisitCommunityPage(webapp.RequestHandler):
    """ Page where user visits a community. 
    """
    @RequireLogin 
    def get(self):
        """Show info about community."""
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
                currentMember = Member.all().filter("community = ", community).filter("googleAccountID = ", user.user_id()).fetch(1000)[0]
                template_values = {
                                   'url': url, 
                                   'url_linktext': url_linktext, 
                                   'community': community, 
                                   'current_user': user, 
                                   'current_member': currentMember,
                                   'members': Member.all().fetch(1000),
                                   'user_is_admin': users.is_current_user_admin(),
                                   }
                path = os.path.join(os.path.dirname(__file__), 'templates/visitCommunity.html')
                self.response.out.write(template.render(path, template_values))
            else:
                self.redirect('/')
                
# --------------------------------------------------------------------------------------------
# Manage memberhip
# --------------------------------------------------------------------------------------------
   
class MemberProfilePage(webapp.RequestHandler):
    """ Change elements of member profile for community.
    """
    @RequireLogin 
    def get(self):
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
                currentMember = Member.all().filter("community = ", community).filter("googleAccountID = ", user.user_id()).fetch(1000)[0]
                liaison = None
                if not currentMember.isOnlineMember:
                    try:
                        liaison = db.get(currentMember.liaisonAccountID)
                    except:
                        liaison = None
                template_values = {
                                   'url': url, 
                                   'url_linktext': url_linktext, 
                                   'community': community, 
                                   'current_user': user, 
                                   'member': currentMember,
                                   'liaison': liaison,
                                   'helping_role_names': HELPING_ROLE_TYPES,
                                   }
                path = os.path.join(os.path.dirname(__file__), 'templates/visit/profile.html')
                self.response.out.write(template.render(path, template_values))
            else:
                self.redirect('/')
                             

                                
# --------------------------------------------------------------------------------------------
# Manage community
# --------------------------------------------------------------------------------------------
                                
class ManageCommunityMembersPage(webapp.RequestHandler):
    """ Review, add, remove members.
    """
    @RequireLogin 
    def get(self):
        """Show info about community members."""
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
                currentMember = Member.all().filter("community = ", community).filter("googleAccountID = ", user.user_id()).fetch(1000)[0]
                communityMembers = Member.all().filter("community = ", community).fetch(1000)
                template_values = {
                                   'url': url, 
                                   'url_linktext': url_linktext, 
                                   'community': community, 
                                   'current_user': user, 
                                   'current_member': currentMember,
                                   'community_members': communityMembers}
                path = os.path.join(os.path.dirname(__file__), 'templates/manage/members.html')
                self.response.out.write(template.render(path, template_values))
            else:
                self.redirect('/')
                
    @RequireLogin 
    def post(self):
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
                for i in range(3):
                    community.roleReadmes[i] = self.request.get("readme%s" % i)
                    community.roleAgreements[i] = self.request.get("agreement%s" % i) == ("agreement%s" % i)
                community.put()
        self.redirect('/visitCommunity')
            
                
class ManageCommunitySettingsPage(webapp.RequestHandler):
    """ Page where user sets global options for the community.
    """
    @RequireLogin 
    def get(self):
        user = users.get_current_user()
        url, url_linktext = GenerateURLs(self.request)
        session = Session()
        community_key = None
        if session and session.has_key('community_key'):
            community_key = session['community_key']
        if community_key:
            community = db.get(community_key) 
            if community:
                currentMember = Member.all().filter("community = ", community).filter("googleAccountID = ", user.user_id()).fetch(1000)[0]
                nudgePointIncludes = []
                i = 0
                for pointType in ACTIVITIES_GERUND:
                    if DEFAULT_NUDGE_POINT_ACCUMULATIONS[i] != 0: # if zero, not appropriate for nudge point accumulation
                        nudgePointIncludes.append('<tr><td>%s</td><td align="right"><input type="text" name="%s" size="4" value="%s"/></td></tr>' \
                            % (pointType, pointType, community.nudgePointsPerActivity[i]))
                    i += 1
                anonIncludes = []
                i = 0
                for entryType in ENTRY_TYPES:
                    anonIncludes.append('<p><label><input type="checkbox" name="%s" value="%s" %s/>%s</label></p>' \
                            % (entryType, entryType, checkedBlank(community.allowAnonymousEntry[i]), entryType))
                    i += 1
                template_values = {
                                   'url': url, 
                                   'url_linktext': url_linktext, 
                                   'community': community, 
                                   'current_user': user, 
                                   'current_member': currentMember,
                                   'anonIncludes': anonIncludes,
                                   'nudge_point_includes': nudgePointIncludes,
                                   }
                path = os.path.join(os.path.dirname(__file__), 'templates/manage/settings.html')
                self.response.out.write(template.render(path, template_values))
        else:
            self.redirect("/")
    
    @RequireLogin 
    def post(self):
        """Process changes to community-wide settings."""
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
                community.name = self.request.get("name")
                community.description = self.request.get("description")
                i = 0
                for entryType in ENTRY_TYPES:
                    community.allowAnonymousEntry[i] = self.request.get(entryType) == entryType
                    i += 1
                oldValue = community.maxNudgePointsPerArticle
                try:
                    community.maxNudgePointsPerArticle = int(self.request.get("maxNudgePointsPerArticle"))
                except:
                    community.maxNudgePointsPerArticle = oldValue
                for i in range(5):
                    community.utilityNudgeCategories[i] = self.request.get("nudgeCategory%s" % i)
                i = 0
                for pointType in ACTIVITIES_GERUND:
                    if DEFAULT_NUDGE_POINT_ACCUMULATIONS[i] != 0: # if zero, not appropriate for nudge point accumulation
                        oldValue = community.nudgePointsPerActivity[i]
                        try:
                            community.nudgePointsPerActivity[i] = int(self.request.get(pointType))
                        except:
                            community.nudgePointsPerActivity[i] = oldValue
                    i += 1
                community.put()
        self.redirect('/visitCommunity')
        
class ManageCommunityQuestionsPage(webapp.RequestHandler):
    """ Page where user sets questions.
    """
    @RequireLogin 
    def get(self):
        user = users.get_current_user()
        url, url_linktext = GenerateURLs(self.request)
        session = Session()
        community_key = None
        if session and session.has_key('community_key'):
            community_key = session['community_key']
        if community_key:
            community = db.get(community_key) 
            if community:
                currentMember = Member.all().filter("community = ", community).filter("googleAccountID = ", user.user_id()).fetch(1000)[0]
                communityMemberQuestions = community.getMemberQuestions()
                systemQuestions = Question.all().filter("community = ", None).fetch(1000)
                template_values = {
                                   'url': url, 
                                   'url_linktext': url_linktext, 
                                   'community': community, 
                                   'current_user': user, 
                                   'current_member': currentMember,
                                   'system_questions': systemQuestions,
                                   'question_refer_types': QUESTION_REFERS_TO,
                                   }
                path = os.path.join(os.path.dirname(__file__), 'templates/manage/questions.html')
                self.response.out.write(template.render(path, template_values))
        else:
            self.redirect("/")
    
    @RequireLogin 
    def post(self):
        """Process changes to community-wide settings."""
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
                systemQuestions = Question.all().filter("community = ", None).fetch(1000)
                for question in systemQuestions:
                    reference = "%s|%s" % (question.refersTo, question.name)
                    shouldHaveQuestion = self.request.get(reference) == reference
                    community.AddOrRemoveSystemQuestion(question, shouldHaveQuestion)
                community.put()
        self.redirect('/visitCommunity')

class ManageCommunityPersonificationsPage(webapp.RequestHandler):
    """ Review, add, remove personifications.
    """
    @RequireLogin 
    def get(self):
        """Show info about community members."""
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
                personifications = Personification.all().filter("community = ", community).fetch(1000)
                template_values = {
                                   'url': url, 
                                   'url_linktext': url_linktext, 
                                   'community': community, 
                                   'community_personifications': personifications,
                                   }
                path = os.path.join(os.path.dirname(__file__), 'templates/manage/personifications.html')
                self.response.out.write(template.render(path, template_values))
            else:
                self.redirect('/')
                
    @RequireLogin 
    def post(self):
        """Process new and removed personifications."""
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
                personifications = Personification.all().filter("community = ", community).fetch(1000)
                psToRemove = []
                for personification in personifications:
                    personification.name = self.request.get("name|%s" % personification.key())
                    personification.description = self.request.get("description|%s" % personification.key())
                    personification.put()
                    if self.request.get("remove|%s" % personification.key()):
                        psToRemove.append(personification)
                if psToRemove:
                    for personification in psToRemove:
                        db.delete(personification)
                namesToAdd = self.request.get("newPersonificationNames").split('\n')
                for name in namesToAdd:
                    if name.strip():
                        newPersonification = Personification(
                            name=name,
                            community=community,
                            )
                        newPersonification.put()
                community.put()
        self.redirect('/visitCommunity')
            
                
class ManageCommunityTechnicalPage(webapp.RequestHandler):
    pass
    
# --------------------------------------------------------------------------------------------
# Site admin
# --------------------------------------------------------------------------------------------
        
class ShowAllCommunities(webapp.RequestHandler):
    """For sys admin, to review all communities."""
    @RequireLogin 
    def get(self):
        """Show info on all communities."""
        if users.is_current_user_admin():
            url, url_linktext = GenerateURLs(self.request)
            template_values = {'url': url, 'url_linktext': url_linktext, 'communities': Community.all().fetch(1000), 'members': Member.all().fetch(1000)}
            path = os.path.join(os.path.dirname(__file__), 'templates/admin/showAllCommunities.html')
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
            path = os.path.join(os.path.dirname(__file__), 'templates/admin/showAllMembers.html')
            self.response.out.write(template.render(path, template_values))
        else:
            self.redirect('/')

# --------------------------------------------------------------------------------------------
# Application and main
# --------------------------------------------------------------------------------------------
        
application = webapp.WSGIApplication(
                                     [('/', StartPage),
                                      
                                      # visiting
                                      ('/visitCommunity', VisitCommunityPage),
                                      ('/visit/profile', MemberProfilePage),
                                      
                                      # managing
                                      ('/createCommunity', CreateCommunityPage),
                                      ('/manage/members', ManageCommunityMembersPage),
                                      ('/manage/settings', ManageCommunitySettingsPage),
                                      ('/manage/questions', ManageCommunityQuestionsPage),
                                      ('/manage/personifications', ManageCommunityPersonificationsPage),
                                      ('/manage/technical', ManageCommunityTechnicalPage),
                                      
                                      # site admin
                                      ('/admin/showAllCommunities', ShowAllCommunities),
                                      ('/admin/showAllMembers', ShowAllMembers)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    systemquestions.AddSystemQuestionsToDataStore()
    main()
