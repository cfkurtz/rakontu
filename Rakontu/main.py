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
            pendingMembers = PendingMember.all().filter("email = ", user.email()).fetch(FETCH_NUMBER)
            for pendingMember in pendingMembers:
                try:
                    communities.append(pendingMember.community)
                except:
                    pass
        template_values = {
                           'user': user, 
                           'communities': communities,
                           'logout_url': users.create_logout_url("/"),
                           }
        path = os.path.join(os.path.dirname(__file__), 'templates/startPage.html')
        self.response.out.write(template.render(path, template_values))

    @RequireLogin 
    def post(self):
        user = users.get_current_user()
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
                        pendingMembers = PendingMember.all().filter("community = ", community.key()).filter("email = ", user.email()).fetch(FETCH_NUMBER)
                        if pendingMembers:
                            newMember = Member(
                                nickname=user.email(),
                                googleAccountID=user.user_id(),
                                googleAccountEmail=user.email(),
                                community=community,
                                governanceType="member")
                            newMember.put()
                            db.delete(pendingMembers[0])
                            session['member_key'] = newMember.key()
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
                           'logout_url': users.create_logout_url("/"),
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
            googleAccountEmail=user.email(),
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
                               'logout_url': users.create_logout_url("/"),
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
            article = db.get(self.request.query_string)
            if article:
                template_values = {
                                   'community': community, 
                                   'current_member': member,
                                   'article': article,
                                   'member_can_answer_questions': len(article.getAnswersForMember(member)) == 0,
                                   'member_can_add_nudge': len(article.getNudgesForMember(member)) == 0,
                                   'community_has_questions_for_this_article_type': len(community.getQuestionsOfType(article.type)) > 0,
                                   'user_is_admin': users.is_current_user_admin(),
                                   'logout_url': users.create_logout_url("/"),
                                   'answers': article.getAnswers(),
                                   'questions': community.getQuestionsOfType(article.type),
                                   'attachments': article.getAttachments(),
                                   'requests': article.getAnnotationsOfType("request"),
                                   'comments': article.getAnnotationsOfType("comment"),
                                   'tag_sets': article.getAnnotationsOfType("tag set"),
                                   'nudges': article.getAnnotationsOfType("nudge"),
                                   'retold_links_incoming': article.getIncomingLinksOfType("retold"),
                                   'retold_links_outgoing': article.getOutgoingLinksOfType("retold"),
                                   'reminded_links_incoming': article.getIncomingLinksOfType("reminded"),
                                   'reminded_links_outgoing': article.getOutgoingLinksOfType("reminded"),
                                   'related_links': article.getLinksOfType("related"),
                                   'included_links_incoming_from_invitations': article.getIncomingLinksOfTypeFromType("included", "invitation"),
                                   'included_links_incoming_from_patterns': article.getIncomingLinksOfTypeFromType("included", "pattern"),
                                   'included_links_incoming_from_constructs': article.getIncomingLinksOfTypeFromType("included", "construct"),
                                   'included_links_outgoing': article.getOutgoingLinksOfType("included"),
                                   'history': article.getHistory(),
                                   }
                path = os.path.join(os.path.dirname(__file__), 'templates/visit/read.html')
                self.response.out.write(template.render(path, template_values))
        else:
            self.redirect('/')
            
class SeeCommunityMembersPage(webapp.RequestHandler):
    @RequireLogin 
    def get(self):
        community, member = GetCurrentCommunityAndMemberFromSession()
        if community and member:
                template_values = {
                                   'community': community, 
                                   'current_member': member,
                                   'community_members': community.getMembers(),
                                   'user_is_admin': users.is_current_user_admin(),
                                   'logout_url': users.create_logout_url("/"),                                   
                                   }
                path = os.path.join(os.path.dirname(__file__), 'templates/visit/members.html')
                self.response.out.write(template.render(path, template_values))
        else:
            self.redirect('/')
   
class SeeMemberPage(webapp.RequestHandler):
    @RequireLogin 
    def get(self):
        community, member = GetCurrentCommunityAndMemberFromSession()
        if community and member:
                memberKey = self.request.query_string
                memberToSee = db.get(memberKey)
                if memberToSee:
                    template_values = {
                                       'community': community, 
                                       'current_member': member,
                                       'member': memberToSee,
                                       'history': member.getHistory(),
                                       'user_is_admin': users.is_current_user_admin(),
                                       'logout_url': users.create_logout_url("/"),                                   
                                       }
                    path = os.path.join(os.path.dirname(__file__), 'templates/visit/member.html')
                    self.response.out.write(template.render(path, template_values))
                else:
                    self.redirect('/visit/look')
        else:
            self.redirect('/')

class SeeCommunityCharactersPage(webapp.RequestHandler):
    @RequireLogin 
    def get(self):
        community, member = GetCurrentCommunityAndMemberFromSession()
        if community and member:
                template_values = {
                                   'community': community, 
                                   'current_member': member,
                                   'characters': community.getCharacters(),
                                   'user_is_admin': users.is_current_user_admin(),
                                   'logout_url': users.create_logout_url("/"),                                   
                                   }
                path = os.path.join(os.path.dirname(__file__), 'templates/visit/characters.html')
                self.response.out.write(template.render(path, template_values))
        else:
            self.redirect('/')
   
class SeeCharacterPage(webapp.RequestHandler):
    @RequireLogin 
    def get(self):
        community, member = GetCurrentCommunityAndMemberFromSession()
        if community and member:
                characterKey = self.request.query_string
                characterToSee = db.get(characterKey)
                if characterToSee:
                    template_values = {
                                       'community': community, 
                                       'current_member': member,
                                       'character': characterToSee,
                                       'history': characterToSee.getHistory(),
                                       'user_is_admin': users.is_current_user_admin(),
                                       'logout_url': users.create_logout_url("/"),                                   
                                       }
                    path = os.path.join(os.path.dirname(__file__), 'templates/visit/character.html')
                    self.response.out.write(template.render(path, template_values))
                else:
                    self.redirect('/visit/look')
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
            if self.request.uri.find("retell") >= 0:
                type = "story"
                linkType = "retell"
                articleFromKey = self.request.query_string
                articleFrom = db.get(articleFromKey)
                article = None
                entryTypeIndexForCharacters = STORY_ENTRY_TYPE_INDEX
            elif self.request.uri.find("remind") >= 0:
                type = "story"
                linkType = "remind"
                articleFromKey = self.request.query_string
                articleFrom = db.get(articleFromKey)
                article = None
                entryTypeIndexForCharacters = STORY_ENTRY_TYPE_INDEX
            elif self.request.uri.find("respond") >= 0:
                type = "story"
                linkType = "respond"
                articleFromKey = self.request.query_string
                articleFrom = db.get(articleFromKey)
                article = None
                entryTypeIndexForCharacters = STORY_ENTRY_TYPE_INDEX
            else:
                linkType = ""
                articleFrom = None
                i = 0
                for aType in ARTICLE_TYPES:
                    if self.request.uri.find(aType) >= 0:
                        type = aType
                        entryTypeIndexForCharacters = i
                        break
                    i += 1
                if not self.request.uri.find("?") >= 0:
                    article = None
                else:
                    articleKey = self.request.query_string
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
                               'article_type': type,
                               'article': article,
                               'questions': community.getQuestionsOfType(type),
                               'answers': answers,
                               'attachments': attachments,
                               'community_members': community.getMembers(),
                               'character_allowed': community.allowCharacter[entryTypeIndexForCharacters],
                               'link_type': linkType,
                               'article_from': articleFrom,
                               'user_is_admin': users.is_current_user_admin(),
                               'logout_url': users.create_logout_url("/"),
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
            newArticle = False
            if not article:
                article=Article(community=community, type=type, creator=member, title="Untitled")
                newArticle = True
            else:
                if "remove|%s|%s" % (type, articleKey) in self.request.arguments():
                    annotations = Annotation.all().filter("article = ", article.key()).fetch(FETCH_NUMBER)
                    for annotation in annotations:
                        article.addHistoryItem(annotation.memberNickNameOrCharacterName(), "removed", annotation)
                        db.delete(annotation)
                    linksFrom = Link.all().filter("articleFrom = ", article.key()).fetch(FETCH_NUMBER)
                    for link in linksFrom:
                        article.addHistoryItem(link.creator.nickname, "removed", link)
                        db.delete(link)
                    linksTo = Link.all().filter("articleTo = ", article.key()).fetch(FETCH_NUMBER)
                    for link in linksTo:
                        article.addHistoryItem(link.creator.nickname, "removed", link)
                        db.delete(link)
                    article.addHistoryItem(article.memberNickNameOrCharacterName(), "removed", article)
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
            if self.request.get("attribution"):
                characterKey = self.request.get("attribution")
                article.character = Character.get(characterKey)
            else:
                article.character = None
            article.put()
            if self.request.get("article_from"):
                articleFrom = db.get(self.request.get("article_from"))
                if articleFrom:
                    if self.request.get("link_type") == "retell":
                        linkType = "retold"
                    elif self.request.get("link_type") == "remind":
                        linkType = "reminded"
                    elif self.request.get("link_type") == "respond":
                        linkType = "included"
                    elif self.request.get("link_type") == "relate":
                        linkType = "related"
                    elif self.request.get("link_type") == "include":
                        linkType = "included"
                    link = Link(articleFrom=articleFrom, articleTo=article, type=linkType, \
                                creator=member, comment=self.request.get("link_comment"))
                    link.put()
            questions = Question.all().filter("community = ", community).filter("refersTo = ", type).fetch(FETCH_NUMBER)
            for question in questions:
                foundAnswers = Answer.all().filter("question = ", question.key()).filter("referent =", article.key()).filter("creator = ", member.key()).fetch(FETCH_NUMBER)
                if foundAnswers:
                    answerToEdit = foundAnswers[0]
                    article.addHistoryItem(answerToEdit.memberNickNameOrCharacterName(), "changed", answerToEdit)
                else:
                    answerToEdit = Answer(question=question, referent=article)
                    article.addHistoryItem(answerToEdit.memberNickNameOrCharacterName(), "created", answerToEdit)
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
            if newArticle:
                article.addHistoryItem(article.memberNickNameOrCharacterName(), "created", article)
            else:
                article.addHistoryItem(article.memberNickNameOrCharacterName(), "changed", article)
            self.redirect("/visit/read?%s" % article.key())
        else:
            self.redirect("/visit/look")
            
class AnswerQuestionsAboutArticlePage(webapp.RequestHandler):
    @RequireLogin 
    def get(self):
        community, member = GetCurrentCommunityAndMemberFromSession()
        if community and member:
            article = None
            if self.request.query_string:
                article = Article.get(self.request.query_string)
            if article:
                template_values = {
                                   'user': users.get_current_user(),
                                   'current_member': member,
                                   'community': community, 
                                   'article': article,
                                   'article_type': article.type,
                                   'questions': community.getQuestionsOfType(article.type),
                                   'answers': article.getAnswersForMember(member),
                                   'community_members': community.getMembers(),
                                   'character_allowed': community.allowCharacter[ANSWERS_ENTRY_TYPE_INDEX],
                                   'user_is_admin': users.is_current_user_admin(),
                                   'logout_url': users.create_logout_url("/"),
                                   }
                path = os.path.join(os.path.dirname(__file__), 'templates/visit/answers.html')
                self.response.out.write(template.render(path, template_values))
            else:
                self.redirect("/visit/look")
        else:
            self.redirect("/")
                
    @RequireLogin 
    def post(self):
        community, member = GetCurrentCommunityAndMemberFromSession()
        if community and member:
            articleKey = self.request.query_string
            article = db.get(articleKey)
            if "remove|answers|%s" % articleKey in self.request.arguments():
                answers = Answer.all().filter("referent = ", article.key()).fetch(FETCH_NUMBER)
                for answer in answers:
                    db.delete(answer)
                self.redirect("/visit/read?%s" % article.key())
                return
            if article:
                character = None
                if self.request.get("attribution"):
                    characterKey = self.request.get("attribution")
                    character = Character.get(characterKey)
                newAnswers = False
                questions = Question.all().filter("community = ", community).filter("refersTo = ", article.type).fetch(FETCH_NUMBER)
                for question in questions:
                    foundAnswers = Answer.all().filter("question = ", question.key()).filter("referent =", article.key()).filter("creator = ", member.key()).fetch(FETCH_NUMBER)
                    if foundAnswers:
                        answerToEdit = foundAnswers[0]
                    else:
                        answerToEdit = Answer(question=question, referent=article)
                        newAnswers = True
                    answerToEdit.character = character
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
                    if newAnswers:
                        article.addHistoryItem(answerToEdit.memberNickNameOrCharacterName(), "created", answerToEdit)
                    else:
                        article.addHistoryItem(answerToEdit.memberNickNameOrCharacterName(), "changed", answerToEdit)
            self.redirect("/visit/read?%s" % article.key())
        else:
            self.redirect("/visit/look")
            
class EnterAnnotationPage(webapp.RequestHandler):
    @RequireLogin 
    def get(self):
        community, member = GetCurrentCommunityAndMemberFromSession()
        if community and member:
            i = 0
            for aType in ANNOTATION_TYPES_URLS:
                if self.request.uri.find(aType) >= 0:
                    type = ANNOTATION_TYPES[i]
                    break
                i += 1
            i = 0
            for aType in ENTRY_TYPES_URLS:
                if self.request.uri.find(aType) >= 0:
                    entryTypeIndex = i
                    break
                i += 1
            article = None
            annotation = None
            if self.request.query_string:
                try:
                    article = Article.get(self.request.query_string)
                except:
                    annotation = Annotation.get(self.request.query_string)
                    article = annotation.article
            if article:
                template_values = {
                                   'user': users.get_current_user(),
                                   'current_member': member,
                                   'community': community, 
                                   'annotation_type': type,
                                   'annotation': annotation,
                                   'community_members': community.getMembers(),
                                   'article': article,
                                   'request_types': REQUEST_TYPES,
                                   'nudge_categories': community.nudgeCategories,
                                   'character_allowed': community.allowCharacter[entryTypeIndex],
                                   'user_is_admin': users.is_current_user_admin(),
                                   'logout_url': users.create_logout_url("/"),
                                   }
                path = os.path.join(os.path.dirname(__file__), 'templates/visit/annotation.html')
                self.response.out.write(template.render(path, template_values))
            else:
                self.redirect("/visit/look")
        else:
            self.redirect("/")
            
    @RequireLogin 
    def post(self):
        community, member = GetCurrentCommunityAndMemberFromSession()
        if community and member:
            for aType in ANNOTATION_TYPES:
                for argument in self.request.arguments():
                    if argument.find(aType) >= 0:
                        type = aType
                        break
            article = None
            annotation = None
            newAnnotation = False
            if self.request.query_string:
                try:
                    article = Article.get(self.request.query_string)
                except:
                    annotation = Annotation.get(self.request.query_string)
                    article = annotation.article
            if article:
                if not annotation:
                    annotation = Annotation(community=community, type=type, creator=member, article=article)
                    newAnnotation = True
                else:
                    if "remove|%s|%s" % (type, annotation.key()) in self.request.arguments():
                        if annotation.type == "nudge":
                            member.nudgePoints += annotation.totalNudgePointsAbsolute
                            member.put()
                        article.addHistoryItem(annotation.memberNickNameOrCharacterName(), "removed", annotation)
                        db.delete(annotation)
                        self.redirect("/visit/read?%s" % article.key())
                        return
                annotation.collectedOffline = self.request.get("collectedOffline") == "yes"
                if annotation.collectedOffline and member.isLiaison():
                    for aMember in community.getMembers():
                        if self.request.get("offlineSource") == aMember.key():
                            annotation.creator = aMember
                            annotation.liaison = member
                            break
                if self.request.get("attribution"):
                    characterKey = self.request.get("attribution")
                    character = Character.get(characterKey)
                    annotation.character = character
                else:
                    annotation.character = None
                if type == "tag set":
                    annotation.tagsIfTagSet = []
                    for i in range (5):
                        if self.request.get("tag%s" % i):
                            annotation.tagsIfTagSet.append(self.request.get("tag%s" % i))
                elif type == "comment":
                    annotation.shortString = self.request.get("shortString")
                    annotation.longString = self.request.get("longString")
                elif type == "request":
                    annotation.shortString = self.request.get("shortString")
                    annotation.longString = self.request.get("longString")
                    annotation.typeIfRequest = self.request.get("typeIfRequest")
                elif type == "nudge":
                    oldTotalNudgePointsInThisNudge = annotation.totalNudgePointsAbsolute()
                    nudgeValuesTheyWantToSet = []
                    totalNudgeValuesTheyWantToSet = 0
                    for i in range(5):
                        category = community.nudgeCategories[i]
                        if category:
                            oldValue = annotation.valuesIfNudge[i]
                            try:
                                nudgeValuesTheyWantToSet.append(int(self.request.get("nudge%s" % i)))
                            except:
                                nudgeValuesTheyWantToSet.append(oldValue)
                            totalNudgeValuesTheyWantToSet += abs(nudgeValuesTheyWantToSet[i])
                    adjustedValues = []
                    maximumAllowedInThisInstance = min(member.nudgePoints, community.maxNudgePointsPerArticle)
                    if totalNudgeValuesTheyWantToSet > maximumAllowedInThisInstance:
                        totalNudgePointsAllocated = 0
                        for i in range(5):
                            category = community.nudgeCategories[i]
                            if category:
                                overLimit = totalNudgePointsAllocated + nudgeValuesTheyWantToSet[i] > maximumAllowedInThisInstance
                                if not overLimit:
                                    adjustedValues.append(nudgeValuesTheyWantToSet[i])
                                    totalNudgePointsAllocated += abs(nudgeValuesTheyWantToSet[i])
                                else:
                                    break
                    else:
                        adjustedValues.extend(nudgeValuesTheyWantToSet)
                    annotation.valuesIfNudge = [0,0,0,0,0]
                    i = 0
                    for value in adjustedValues:
                        annotation.valuesIfNudge[i] = value
                        i += 1
                    annotation.shortString = self.request.get("shortString")
                    newTotalNudgePointsInThisNudge = annotation.totalNudgePointsAbsolute()
                    member.nudgePoints += oldTotalNudgePointsInThisNudge
                    member.nudgePoints -= newTotalNudgePointsInThisNudge
                    member.put()
                annotation.put()
                if newAnnotation:
                    article.addHistoryItem(annotation.memberNickNameOrCharacterName(), "created", annotation)
                else:
                    article.addHistoryItem(annotation.memberNickNameOrCharacterName(), "changed", annotation)
                self.redirect("/visit/read?%s" % article.key())
            else:
                self.redirect("/visit/look")
        else:
            self.redirect("/")
        
class EnterAnswersPage(webapp.RequestHandler):
    pass
           
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
                               'logout_url': users.create_logout_url("/"),
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
            for i in range(3):
                member.helpingRoles[i] = self.request.get("helpingRole%s" % i) == "helpingRole%s" % i
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
                               'pending_members': community.getPendingMembers(),
                               'user_is_admin': users.is_current_user_admin(),
                               'logout_url': users.create_logout_url("/"),
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
                if aMember.isRegularMember():
                    for i in range(3):
                        aMember.helpingRolesAvailable[i] = self.request.get("%sAvailable|%s" % (HELPING_ROLE_TYPES[i], aMember.key())) == "yes"
                else:
                    for i in range(3):
                        aMember.helpingRolesAvailable[i] = True
                aMember.put()
            membersToRemove = []
            for aMember in communityMembers:
                if self.request.get("remove|%s" % aMember.googleAccountID):
                    membersToRemove.append(aMember)
            if membersToRemove:
                for aMember in membersToRemove:
                    db.delete(aMember)
            for pendingMember in community.getPendingMembers():
                pendingMember.email = self.request.get("email|%s" % pendingMember.key())
                pendingMember.put()
                if self.request.get("removePendingMember|%s" % pendingMember.key()):
                    db.delete(pendingMember)
            memberEmailsToAdd = self.request.get("newMemberEmails").split('\n')
            for email in memberEmailsToAdd:
                if email.strip():
                    pendingMember = PendingMember(community=community, email=email)
                    pendingMember.put()
        self.redirect('/manage/members')
                
class ManageCommunitySettingsPage(webapp.RequestHandler):
    @RequireLogin 
    def get(self):
        community, member = GetCurrentCommunityAndMemberFromSession()
        if community and member:
            nudgePointIncludes = []
            i = 0
            for pointType in ACTIVITIES_GERUND:
                if DEFAULT_NUDGE_POINT_ACCUMULATIONS[i] != 0: # if zero, not appropriate for nudge point accumulation
                    nudgePointIncludes.append('<tr><td align="right">%s</td><td align="left"><input type="text" name="%s" size="4" value="%s"/></td></tr>' \
                        % (pointType, pointType, community.nudgePointsPerActivity[i]))
                i += 1
            characterIncludes = []
            i = 0
            for entryType in ENTRY_TYPES:
                characterIncludes.append('<input type="checkbox" name="%s" value="%s" %s id="%s"/><label for="%s">%s</label>' \
                        % (entryType, entryType, checkedBlank(community.allowCharacter[i]), entryType, entryType, entryType))
                i += 1
            template_values = {
                               'community': community, 
                               'current_user': users.get_current_user(), 
                               'current_member': member,
                               'character_includes': characterIncludes,
                               'nudge_point_includes': nudgePointIncludes,
                               'user_is_admin': users.is_current_user_admin(),
                               'logout_url': users.create_logout_url("/"),
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
                community.allowCharacter[i] = self.request.get(entryType) == entryType
                i += 1
            oldValue = community.maxNudgePointsPerArticle
            try:
                community.maxNudgePointsPerArticle = int(self.request.get("maxNudgePointsPerArticle"))
            except:
                community.maxNudgePointsPerArticle = oldValue
            for i in range(5):
                community.nudgeCategories[i] = self.request.get("nudgeCategory%s" % i)
            community.autoPrune = self.request.get("autoPrune") == "yes"
            oldValue = community.autoPruneStrength
            try:
                community.autoPruneStrength = int(self.request.get("autoPruneStrength"))
            except:
                community.autoPruneStrength = oldValue
            oldValue = community.maxNumAttachments
            try:
                community.maxNumAttachments = int(self.request.get("maxNumAttachments"))
            except:
                community.maxNumAttachments = oldValue
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
                               'logout_url': users.create_logout_url("/"),
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

class ManageCommunityCharactersPage(webapp.RequestHandler):
    @RequireLogin 
    def get(self):
        community, member = GetCurrentCommunityAndMemberFromSession()
        if community and member:
            characters = Character.all().filter("community = ", community).fetch(FETCH_NUMBER)
            template_values = {
                               'community': community, 
                               'current_user': users.get_current_user(), 
                               'current_member': member,
                               'characters': characters,
                               'user_is_admin': users.is_current_user_admin(),
                               'logout_url': users.create_logout_url("/"),
                               }
            path = os.path.join(os.path.dirname(__file__), 'templates/manage/characters.html')
            self.response.out.write(template.render(path, template_values))
        else:
            self.redirect('/')
                
    @RequireLogin 
    def post(self):
        community, member = GetCurrentCommunityAndMemberFromSession()
        if community and member:
            characters = Character.all().filter("community = ", community).fetch(FETCH_NUMBER)
            charactersToRemove = []
            for name, value in self.request.params.items():
                DebugPrint(name)
                DebugPrint(value)
            for character in characters:
                character.name = self.request.get("name|%s" % character.key())
                character.description = self.request.get("description|%s" % character.key())
                imageQueryKey = "image|%s" % character.key()
                if self.request.get(imageQueryKey):
                    character.image = db.Blob(images.resize(str(self.request.get(imageQueryKey)), 100, 60))
                character.put()
                if self.request.get("remove|%s" % character.key()):
                    charactersToRemove.append(character)
            if charactersToRemove:
                for character in charactersToRemove:
                    db.delete(character)
            namesToAdd = self.request.get("newCharacterNames").split('\n')
            for name in namesToAdd:
                if name.strip():
                    newCharacter = Character(
                        name=name,
                        community=community,
                        )
                    newCharacter.put()
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
                               'logout_url': users.create_logout_url("/"),
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
                               'logout_url': users.create_logout_url("/"),
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
        elif self.request.get("character_id"):
            character = db.get(self.request.get("character_id"))
            if character:
                self.response.headers['Content-Type'] = "image/jpg"
                self.response.out.write(character.image)
               
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
                                      ('/visit', BrowseArticlesPage),
                                      ('/visit/', BrowseArticlesPage),
                                      ('/visit/look', BrowseArticlesPage),
                                      ('/visit/read', ReadArticlePage),
                                      ('/visit/story', EnterArticlePage),
                                      ('/visit/retell', EnterArticlePage),
                                      ('/visit/remind', EnterArticlePage),
                                      ('/visit/respond', EnterArticlePage),
                                      
                                      ('/visit/pattern', EnterArticlePage),
                                      ('/visit/construct', EnterArticlePage),
                                      ('/visit/invitation', EnterArticlePage),
                                      ('/visit/resource', EnterArticlePage),
                                      ('/visit/article', EnterArticlePage),
                                      ('/visit/answers', AnswerQuestionsAboutArticlePage),
                                      
                                      ('/visit/request', EnterAnnotationPage),
                                      ('/visit/tagset', EnterAnnotationPage),
                                      ('/visit/comment', EnterAnnotationPage),
                                      ('/visit/nudge', EnterAnnotationPage),
                                      ('/visit/annotation', EnterAnnotationPage),
                                      
                                      ('/visit/answers', EnterAnswersPage),
                                      
                                      ('/visit/members', SeeCommunityMembersPage),
                                      ('/visit/member', SeeMemberPage),
                                      ('/visit/characters', SeeCommunityCharactersPage),
                                      ('/visit/character', SeeCharacterPage),
                                      
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
                                      ('/manage/characters', ManageCommunityCharactersPage),
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
