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
                    try:
                        communities.append(member.community)
                    except:
                        pass # if the community doesn't exist, don't use it
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
        if session and session.has_key('community_key'):
            community_key = session['community_key']
        else:
            community_key = None
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
                path = os.path.join(os.path.dirname(__file__), 'templates/manageCommunity_Members.html')
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
        self.redirect('/manageCommunity')
            
                
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
                path = os.path.join(os.path.dirname(__file__), 'templates/manageCommunity_Settings.html')
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
        self.redirect('/manageCommunity')
        
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
                path = os.path.join(os.path.dirname(__file__), 'templates/manageCommunity_Questions.html')
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
        self.redirect('/manageCommunity_Questions')

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
                path = os.path.join(os.path.dirname(__file__), 'templates/manageCommunity_Personifications.html')
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
        self.redirect('/manageCommunity_Personifications')
            
                
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
        if session and session.has_key('community_key'):
            community_key = session['community_key']
        else:
            community_key = None
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
                                      ('/manageCommunity_Questions', ManageCommunityQuestionsPage),
                                      ('/manageCommunity_Personifications', ManageCommunityPersonificationsPage),
                                      ('/manageCommunity_Technical', ManageCommunityTechnicalPage),
                                      
                                      # sys admin
                                      ('/admin/showAllCommunities', ShowAllCommunities),
                                      ('/admin/showAllMembers', ShowAllMembers)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    systemquestions.AddSystemQuestionsToDataStore()
    main()
