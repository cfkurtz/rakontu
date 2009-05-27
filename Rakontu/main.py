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
import string

# GAE imports
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.api import images

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

def GetCurrentCommunityAndMemberFromSession():
    session = Session()
    if session and session.has_key('community_key'):
        community_key = session['community_key']
    else:
        community_key = None
    if session and session.has_key('member_key'):
        member_key = session['member_key']
    else:
        member_key = None
    if community_key: 
        community = db.get(community_key) 
    else:
        community = None
    if member_key:
        member = db.get(member_key)
    else:
        member = None
    return community, member

# --------------------------------------------------------------------------------------------
# Startup page
# --------------------------------------------------------------------------------------------
        
class StartPage(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        communities = []
        if user:
            members = Member.all().filter("googleAccountID = ", user.user_id()).fetch(FETCH_NUMBER)
            for member in members:
                try:
                    communities.append(member.community)
                except:
                    pass # if can't link to community don't use it
        template_values = {
                           'user': user, 
                           'communities': communities,
                           'logout_url': users.create_logout_url(self.request.uri),
                           }
        path = os.path.join(os.path.dirname(__file__), 'templates/startPage.html')
        self.response.out.write(template.render(path, template_values))

    @RequireLogin 
    def post(self):
        if "visitCommunity" in self.request.arguments():
            community_key = self.request.get('community_key')
            if community_key:
                community = db.get(community_key) 
                if community:
                    session = Session()
                    session['community_key'] = community_key
                    members = Member.all().filter("community = ", community).filter("googleAccountID = ", users.get_current_user().user_id()).fetch(FETCH_NUMBER)
                    if members:
                        session['member_key'] = members[0].key()
                    else:
                        self.redirect('/')
                    self.redirect('/visit/look')
                else:
                    self.redirect('/')
            else:
                self.redirect('/')
        elif "createCommunity" in self.request.arguments():
            self.redirect("/createCommunity")

# --------------------------------------------------------------------------------------------
# Create new community
# --------------------------------------------------------------------------------------------
        
class CreateCommunityPage(webapp.RequestHandler):
    @RequireLogin 
    def get(self):
        template_values = {
                           'user': users.get_current_user(),
                           'logout_url': users.create_logout_url(self.request.uri),
                           }
        path = os.path.join(os.path.dirname(__file__), 'templates/createCommunity.html')
        self.response.out.write(template.render(path, template_values))
            
    @RequireLogin 
    def post(self):
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
            nicknameIsRealName = self.request.get('nickname_is_real_name') =="yes",
            profileText = self.request.get('profile_text)'))
        member.put()
        self.redirect('/')
        
# --------------------------------------------------------------------------------------------
# Browse and read
# --------------------------------------------------------------------------------------------
                        
class BrowseArticlesPage(webapp.RequestHandler):
    @RequireLogin 
    def get(self):
        community, member = GetCurrentCommunityAndMemberFromSession()
        if community and member:
            template_values = {
                               'community': community, 
                               'current_member': member,
                               'articles': community.getArticles(),
                               'article_types': ARTICLE_TYPES,
                               'user_is_admin': users.is_current_user_admin(),
                               'logout_url': users.create_logout_url(self.request.uri),
                               }
            path = os.path.join(os.path.dirname(__file__), 'templates/visit/look.html')
            self.response.out.write(template.render(path, template_values))
        else:
            self.redirect('/')
            
class ReadArticlePage(webapp.RequestHandler):
    @RequireLogin 
    def get(self):
        community, member = GetCurrentCommunityAndMemberFromSession()
        if community and member:
            articleKey = self.request.uri[self.request.uri.find("?")+1:]
            article = db.get(articleKey)
            if article:
                template_values = {
                                   'community': community, 
                                   'current_member': member,
                                   'article': article,
                                   'user_is_admin': users.is_current_user_admin(),
                                   'logout_url': users.create_logout_url(self.request.uri),
                                   'answers': article.getAnswers(),
                                   'questions': community.getQuestionsOfType(article.type),
                                   'attachments': article.getAttachments(),
                                   'actions': ACTIONS_AFTER_READING,
                                   }
                path = os.path.join(os.path.dirname(__file__), 'templates/visit/read.html')
                self.response.out.write(template.render(path, template_values))
        else:
            self.redirect('/')
   
# --------------------------------------------------------------------------------------------
# Add or change article
# --------------------------------------------------------------------------------------------
   
class EnterArticlePage(webapp.RequestHandler):
    @RequireLogin 
    def get(self):
        community, member = GetCurrentCommunityAndMemberFromSession()
        if community and member:
            i = 0
            for aType in ARTICLE_TYPES:
                if self.request.uri.find(aType) >= 0:
                    type = aType
                    entryTypeIndexForAnonymity = i
                    break
                i += 1
            if not self.request.uri.find("?") >= 0:
                article = None
            else:
                articleKey = self.request.uri[self.request.uri.find("?")+1:]
                article = db.get(articleKey)
            if article:
                answers = article.getAnswers()
                attachments = article.getAttachments()
            else:
                answers = None
                attachments = None
            template_values = {
                               'user': users.get_current_user(),
                               'current_member': member,
                               'community': community, 
                               'refer_type': type,
                               'article_type': type,
                               'article': article,
                               'questions': community.getQuestionsOfType(type),
                               'answers': answers,
                               'attachments': attachments,
                               'community_members': community.getMembers(),
                               'anon_entry_allowed': community.allowAnonymousEntry[entryTypeIndexForAnonymity],
                               'show_attribution_choice': community.hasAtLeastOnePersonificationOrAnonEntryAllowed(entryTypeIndexForAnonymity),
                               'user_is_admin': users.is_current_user_admin(),
                               'logout_url': users.create_logout_url(self.request.uri),
                               }
            path = os.path.join(os.path.dirname(__file__), 'templates/visit/article.html')
            self.response.out.write(template.render(path, template_values))
        else:
            self.redirect("/")
            
    @RequireLogin 
    def post(self):
        community, member = GetCurrentCommunityAndMemberFromSession()
        if community and member:
            for aType in ARTICLE_TYPES:
                for argument in self.request.arguments():
                    if argument.find(aType) >= 0:
                        type = aType
                        break
            if not self.request.uri.find("?") >= 0:
                article = None
            else:
                articleKey = self.request.query_string
                article = db.get(articleKey)
            if not article:
                article=Article(community=community, type=type, creator=member, title="Untitled")
            else:
                if "remove|%s|%s" % (type, articleKey) in self.request.arguments():
                    db.delete(article)
                    self.redirect("/visit/look")
                    return
            if self.request.get("title"):
                article.title = self.request.get("title")
            article.text = self.request.get("text")
            article.collectedOffline = self.request.get("collectedOffline") == "yes"
            if article.collectedOffline and member.isLiaison():
                for aMember in community.getMembers():
                    if self.request.get("offlineSource") == aMember.key():
                        article.creator = aMember
                        article.liaison = member
                        break
            article.attribution = self.request.get("attribution")
            if article.attribution != "member" and article.attribution != "anonymous":
                article.attribution = "personification"
                article.personification = self.request.get("personification")
            article.put()
            questions = Question.all().filter("community = ", community).filter("refersTo = ", type).fetch(FETCH_NUMBER)
            for question in questions:
                foundAnswers = Answer.all().filter("question = ", question.key()).filter("referent =", article.key()).fetch(FETCH_NUMBER)
                if foundAnswers:
                    answerToEdit = foundAnswers[0]
                else:
                    answerToEdit = Answer(question=question, referent=article)
                if question.type == "text":
                    answerToEdit.answerIfText = self.request.get("%s" % question.key())
                elif question.type == "value":
                    oldValue = answerToEdit.answerIfValue
                    try:
                        answerToEdit.answerIfValue = int(self.request.get("%s" % question.key()))
                    except:
                        answerToEdit.answerIfValue = oldValue
                elif question.type == "boolean":
                    answerToEdit.answerIfBoolean = self.request.get("%s" % question.key()) == "%s" % question.key()
                elif question.type == "nominal" or question.type == "ordinal":
                    if question.multiple:
                        answerToEdit.answerIfMultiple = []
                        for choice in question.choices:
                            if self.request.get("%s|%s" % (question.key(), choice)):
                                answerToEdit.answerIfMultiple.append(choice)
                    else:
                        answerToEdit.answerIfText = self.request.get("%s" % (question.key()))
                answerToEdit.creator = member
                answerToEdit.put()
            foundAttachments = Attachment.all().filter("article = ", article.key()).fetch(FETCH_NUMBER)
            attachmentsToRemove = []
            DebugPrint(self.request.params.items())
            for attachment in foundAttachments:
                for name, value in self.request.params.items():
                    if value == "removeAttachment|%s" % attachment.key():
                        attachmentsToRemove.append(attachment)
            if attachmentsToRemove:
                for attachment in attachmentsToRemove:
                    db.delete(attachment)
            foundAttachments = Attachment.all().filter("article = ", article.key()).fetch(FETCH_NUMBER)
            for i in range(3):
                for name, value in self.request.params.items():
                    if name == "attachment%s" % i:
                        if value != None and value != "":
                            filename = value.filename
                            if len(foundAttachments) > i:
                                attachmentToEdit = foundAttachments[i]
                            else:
                                attachmentToEdit = Attachment(article=article)
                            j = 0
                            mimeType = None
                            for type in ACCEPTED_ATTACHMENT_FILE_TYPES:
                                if filename.find(".%s" % type) >= 0:
                                    mimeType = ACCEPTED_ATTACHMENT_MIME_TYPES[j]
                                j += 1
                            if mimeType:
                                attachmentToEdit.mimeType = mimeType
                                attachmentToEdit.fileName = filename
                                attachmentToEdit.name = self.request.get("attachmentName%s" % i)
                                attachmentToEdit.data = db.Blob(str(self.request.get("attachment%s" % i)))
                                attachmentToEdit.put()
        self.redirect("/visit/look")
           
# --------------------------------------------------------------------------------------------
# Manage memberhip
# --------------------------------------------------------------------------------------------
   
class ChangeMemberProfilePage(webapp.RequestHandler):
    @RequireLogin 
    def get(self):
        community, member = GetCurrentCommunityAndMemberFromSession()
        if community and member:
            liaison = None
            if not member.isOnlineMember:
                try:
                    liaison = db.get(member.liaisonAccountID)
                except:
                    liaison = None
            template_values = {
                               'community': community, 
                               'current_user': users.get_current_user(), 
                               'current_member': member,
                               'questions': community.getMemberQuestions(),
                               'answers': member.getAnswers(),
                               'liaison': liaison,
                               'helping_role_names': HELPING_ROLE_TYPES,
                               'refer_type': "member",
                               'user_is_admin': users.is_current_user_admin(),
                               'logout_url': users.create_logout_url(self.request.uri),
                               }
            path = os.path.join(os.path.dirname(__file__), 'templates/visit/profile.html')
            self.response.out.write(template.render(path, template_values))
        else:
            self.redirect('/')
                             
    @RequireLogin 
    def post(self):
        community, member = GetCurrentCommunityAndMemberFromSession()
        if community and member:
            member.nickname = self.request.get("nickname")
            member.nicknameIsRealName = self.request.get('nickname_is_real_name') =="yes"
            member.profileText = self.request.get("description")
            if self.request.get("img"):
                member.profileImage = db.Blob(images.resize(str(self.request.get("img")), 100, 60))
            i = 0
            for role in HELPING_ROLE_TYPES:
                if self.request.get("helpingRole%s" % i):
                    member.addHelpingRole(i)
                    i += 1
            member.put()
            questions = Question.all().filter("community = ", community).filter("refersTo = ", "member").fetch(FETCH_NUMBER)
            for question in questions:
                foundAnswers = Answer.all().filter("question = ", question.key()).filter("referent =", member.key()).fetch(FETCH_NUMBER)
                if foundAnswers:
                    answerToEdit = foundAnswers[0]
                else:
                    answerToEdit = Answer(question=question, referent=member)
                if question.type == "text":
                    answerToEdit.answerIfText = self.request.get("%s" % question.key())
                elif question.type == "value":
                    oldValue = answerToEdit.answerIfValue
                    try:
                        answerToEdit.answerIfValue = int(self.request.get("%s" % question.key()))
                    except:
                        answerToEdit.answerIfValue = oldValue
                elif question.type == "boolean":
                    answerToEdit.answerIfBoolean = self.request.get("%s" % question.key()) == "%s" % question.key()
                elif question.type == "nominal" or question.type == "ordinal":
                    if question.multiple:
                        answerToEdit.answerIfMultiple = []
                        for choice in question.choices:
                            if self.request.get("%s|%s" % (question.key(), choice)):
                                answerToEdit.answerIfMultiple.append(choice)
                    else:
                        answerToEdit.answerIfText = self.request.get("%s" % (question.key()))
                answerToEdit.creator = member
                answerToEdit.put()
        self.redirect('/visit/look')
        
# --------------------------------------------------------------------------------------------
# Manage community
# --------------------------------------------------------------------------------------------
                                
class ManageCommunityMembersPage(webapp.RequestHandler):
    @RequireLogin 
    def get(self):
        community, member = GetCurrentCommunityAndMemberFromSession()
        if community and member:
            communityMembers = Member.all().filter("community = ", community).fetch(FETCH_NUMBER)
            template_values = {
                               'community': community, 
                               'current_user': users.get_current_user(), 
                               'current_member': member,
                               'community_members': community.getMembers(),
                               'user_is_admin': users.is_current_user_admin(),
                               'logout_url': users.create_logout_url(self.request.uri),
                               }
            path = os.path.join(os.path.dirname(__file__), 'templates/manage/members.html')
            self.response.out.write(template.render(path, template_values))
        else:
            self.redirect('/')
                
    @RequireLogin 
    def post(self):
        community, member = GetCurrentCommunityAndMemberFromSession()
        if community and member:
            communityMembers = Member.all().filter("community = ", community).fetch(FETCH_NUMBER)
            for aMember in communityMembers:
                for name, value in self.request.params.items():
                    if value.find(aMember.googleAccountID) >= 0:
                        (newType, id) = value.split("|") 
                        okayToSet = False
                        if newType != aMember.governanceType:
                            if newType == "member":
                                if not aMember.isOwner() or not community.memberIsOnlyOwner(aMember):
                                    okayToSet = True
                            elif newType == "manager":
                                if not aMember.isOwner() or not community.memberIsOnlyOwner(aMember):
                                    okayToSet = True
                            elif newType == "owner":
                                okayToSet = True
                        if okayToSet:
                            aMember.governanceType = newType
                            aMember.put()
            membersToRemove = []
            for aMember in communityMembers:
                if self.request.get("remove|%s" % aMember.googleAccountID):
                    membersToRemove.append(aMember)
            if membersToRemove:
                for aMember in membersToRemove:
                    db.delete(aMember)
            memberEmailsToAdd = self.request.get("newMemberEmails").split('\n')
            for email in memberEmailsToAdd:
                if email.strip():
                    userID = GoogleUserIDForEmail(email)
                    if userID:
                        if not community.hasMemberWithUserID(userID):
                            newMember = Member(
                                googleAccountID=userID,
                                community=community,
                                governanceType="member")
                            newMember.put()
        self.redirect('/visit/look')
            
                
class ManageCommunitySettingsPage(webapp.RequestHandler):
    @RequireLogin 
    def get(self):
        community, member = GetCurrentCommunityAndMemberFromSession()
        if community and member:
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
                               'community': community, 
                               'current_user': users.get_current_user(), 
                               'current_member': member,
                               'anonIncludes': anonIncludes,
                               'nudge_point_includes': nudgePointIncludes,
                               'user_is_admin': users.is_current_user_admin(),
                               'logout_url': users.create_logout_url(self.request.uri),
                               }
            path = os.path.join(os.path.dirname(__file__), 'templates/manage/settings.html')
            self.response.out.write(template.render(path, template_values))
        else:
            self.redirect("/")
    
    @RequireLogin 
    def post(self):
        community, member = GetCurrentCommunityAndMemberFromSession()
        if community and member:
            community.name = self.request.get("name")
            community.description = self.request.get("description")
            if self.request.get("img"):
                community.image = db.Blob(images.resize(str(self.request.get("img")), 100, 60))
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
            for i in range(3):
                community.roleReadmes[i] = self.request.get("readme%s" % i)
                community.roleAgreements[i] = self.request.get("agreement%s" % i) == ("agreement%s" % i)
            community.put()
        self.redirect('/visit/look')
                
class ManageCommunityQuestionsPage(webapp.RequestHandler):
    @RequireLogin 
    def get(self):
        community, member = GetCurrentCommunityAndMemberFromSession()
        if community and member:
            i = 0
            for aType in QUESTION_REFERS_TO:
                if self.request.uri.find(aType) >= 0:
                    type = aType
                    typePlural = QUESTION_REFERS_TO_PLURAL[i]
                    break
                i += 1
            communityQuestionsOfType = community.getQuestionsOfType(type)
            systemQuestionsOfType = Question.all().filter("community = ", None).filter("refersTo = ", type).fetch(FETCH_NUMBER)
            template_values = {
                               'community': community, 
                               'current_user': users.get_current_user(), 
                               'current_member': member,
                               'questions': communityQuestionsOfType,
                               'question_types': QUESTION_TYPES,
                               'system_questions': systemQuestionsOfType,
                               'refer_type': type,
                               'refer_type_plural': typePlural,
                               'question_refer_types': QUESTION_REFERS_TO,
                               'user_is_admin': users.is_current_user_admin(),
                               'logout_url': users.create_logout_url(self.request.uri),
                               }
            path = os.path.join(os.path.dirname(__file__), 'templates/manage/questions/questions.html')
            self.response.out.write(template.render(path, template_values))
        else:
            self.redirect("/")
    
    @RequireLogin 
    def post(self):
        community, member = GetCurrentCommunityAndMemberFromSession()
        if community and member:
            for aType in QUESTION_REFERS_TO:
                for argument in self.request.arguments():
                    if argument == "changesTo|%s" % aType:
                        type = aType
                        break
            communityQuestionsOfType = community.getQuestionsOfType(type)
            systemQuestionsOfType = Question.all().filter("community = ", None).filter("refersTo = ", type).fetch(FETCH_NUMBER)
            for question in communityQuestionsOfType:
                question.name = self.request.get("name|%s" % question.key())
                question.text = self.request.get("text|%s" % question.key())
                question.help = self.request.get("help|%s" % question.key())
                question.type = self.request.get("type|%s" % question.key())
                question.choices = []
                for i in range(10):
                    question.choices.append(self.request.get("choice%s|%s" % (i, question.key())))
                oldValue = question.lengthIfText
                try:
                    question.lengthIfText = self.request.get("lengthIfText|%s" % question.key())
                except:
                    question.lengthIfText = oldValue
                oldValue = question.minIfValue
                try:
                    question.minIfValue = self.request.get("minIfValue|%s" % question.key())
                except:
                    question.minIfValue = oldValue
                oldValue = question.maxIfValue
                try:
                    question.maxIfValue = self.request.get("maxIfValue|%s" % question.key())
                except:
                    question.maxIfValue = oldValue
                question.responseIfBoolean = self.request.get("responseIfBoolean|%s" % question.key())
                question.multiple = self.request.get("multiple|%s" % question.key()) == "multiple|%s" % question.key()
                question.put()
            questionsToRemove = []
            for question in communityQuestionsOfType:
                if self.request.get("remove|%s" % question.key()):
                    questionsToRemove.append(question)
            if questionsToRemove:
                for question in questionsToRemove:
                    answersWithThisQuestion = Answer().all().filter("question = ", question.key()).fetch(FETCH_NUMBER)
                    for answer in answersWithThisQuestion:
                        db.delete(answer)
                    db.delete(question)
            questionNamesToAdd = self.request.get("newQuestionNames").split('\n')
            for name in questionNamesToAdd:
                if name.strip():
                    question = Question(name=name, refersTo=type, community=community)
                    question.put()
            for sysQuestion in systemQuestionsOfType:
                if self.request.get("copy|%s" % sysQuestion.key()) == "copy|%s" % sysQuestion.key():
                    community.AddCopyOfQuestion(sysQuestion)
        self.redirect('/visit/look')

class ManageCommunityPersonificationsPage(webapp.RequestHandler):
    @RequireLogin 
    def get(self):
        community, member = GetCurrentCommunityAndMemberFromSession()
        if community and member:
            personifications = Personification.all().filter("community = ", community).fetch(FETCH_NUMBER)
            template_values = {
                               'community': community, 
                               'community_personifications': personifications,
                               'user_is_admin': users.is_current_user_admin(),
                               'logout_url': users.create_logout_url(self.request.uri),
                               }
            path = os.path.join(os.path.dirname(__file__), 'templates/manage/personifications.html')
            self.response.out.write(template.render(path, template_values))
        else:
            self.redirect('/')
                
    @RequireLogin 
    def post(self):
        community, member = GetCurrentCommunityAndMemberFromSession()
        if community and member:
            personifications = Personification.all().filter("community = ", community).fetch(FETCH_NUMBER)
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
        self.redirect('/visit/look')
            
                
class ManageCommunityTechnicalPage(webapp.RequestHandler):
    pass
    
# --------------------------------------------------------------------------------------------
# Site admin
# --------------------------------------------------------------------------------------------
        
class ShowAllCommunities(webapp.RequestHandler):
    @RequireLogin 
    def get(self):
        if users.is_current_user_admin():
            template_values = {
                               'communities': Community.all().fetch(FETCH_NUMBER), 
                               'members': Member.all().fetch(FETCH_NUMBER),
                               'user_is_admin': users.is_current_user_admin(),
                               'logout_url': users.create_logout_url(self.request.uri),
                               }
            path = os.path.join(os.path.dirname(__file__), 'templates/admin/showAllCommunities.html')
            self.response.out.write(template.render(path, template_values))
        else:
            self.redirect('/')

class ShowAllMembers(webapp.RequestHandler):
    @RequireLogin 
    def get(self):
        if users.is_current_user_admin():
            template_values = {
                               'members': Member.all().fetch(FETCH_NUMBER),
                               'user_is_admin': users.is_current_user_admin(),
                               'logout_url': users.create_logout_url(self.request.uri),
                               }
            path = os.path.join(os.path.dirname(__file__), 'templates/admin/showAllMembers.html')
            self.response.out.write(template.render(path, template_values))
        else:
            self.redirect('/')
            
# --------------------------------------------------------------------------------------------
# Non-text handling
# --------------------------------------------------------------------------------------------
        
class ImageHandler(webapp.RequestHandler):
    def get(self):
        if self.request.get("member_id"):
            member = db.get(self.request.get("member_id"))
            if member and member.profileImage:
                self.response.headers['Content-Type'] = "image/jpg"
                self.response.out.write(member.profileImage)
            else:
                self.error(404)
        elif self.request.get("community_id"):
            community = db.get(self.request.get("community_id"))
            if community and community.image:
                self.response.headers['Content-Type'] = "image/jpg"
                self.response.out.write(community.image)
            else:
                self.error(404)
        elif self.request.get("article_id"):
            article = db.get(self.request.get("article_id"))
            if article and article.type == "pattern" and article.screenshotIfPattern:
                self.response.headers['Content-Type'] = "image/jpg"
                self.response.out.write(article.screenshotIfPattern)
                
class AttachmentHandler(webapp.RequestHandler):
    def get(self):
        if self.request.get("attachment_id"):
            attachment = db.get(self.request.get("attachment_id"))
            if attachment and attachment.data:
                if attachment.mimeType in ["image/jpeg", "image/png", "text/html", "text/plain"]:
                    self.response.headers.add_header('Content-Disposition', 'filename="%s"' % attachment.fileName)
                else:
                    self.response.headers.add_header('Content-Disposition', 'attachment; filename="%s"' % attachment.fileName)
                self.response.headers.add_header('Content-Type', attachment.mimeType)
                self.response.out.write(attachment.data)
            else:
                self.error(404)

# --------------------------------------------------------------------------------------------
# Application and main
# --------------------------------------------------------------------------------------------
        
application = webapp.WSGIApplication(
                                     [('/', StartPage),
                                      
                                      # visiting
                                      ('/visit/look', BrowseArticlesPage),
                                      ('/visit/read', ReadArticlePage),
                                      ('/visit/story', EnterArticlePage),
                                      ('/visit/pattern', EnterArticlePage),
                                      ('/visit/construct', EnterArticlePage),
                                      ('/visit/invitation', EnterArticlePage),
                                      ('/visit/resource', EnterArticlePage),
                                      ('/visit/article', EnterArticlePage),
                                      ('/visit/profile', ChangeMemberProfilePage),
                                      ('/img', ImageHandler),
                                      ('/visit/img', ImageHandler),
                                      ('/manage/img', ImageHandler),
                                      ('/visit/attachment', AttachmentHandler),
                                      
                                      # managing
                                      ('/createCommunity', CreateCommunityPage),
                                      ('/manage/members', ManageCommunityMembersPage),
                                      ('/manage/settings', ManageCommunitySettingsPage),
                                      ('/manage/questions/story', ManageCommunityQuestionsPage),
                                      ('/manage/questions/pattern', ManageCommunityQuestionsPage),
                                      ('/manage/questions/construct', ManageCommunityQuestionsPage),
                                      ('/manage/questions/invitation', ManageCommunityQuestionsPage),
                                      ('/manage/questions/resource', ManageCommunityQuestionsPage),
                                      ('/manage/questions/member', ManageCommunityQuestionsPage),
                                      ('/manage/questions/questions', ManageCommunityQuestionsPage),
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
