# ============================================================================================
# RAKONTU
# Description: Rakontu is open source story sharing software.
# Version: pre-0.1
# License: GPL 3.0
# Google Code Project: http://code.google.com/p/rakontu/
# ============================================================================================

import logging
from datetime import *
import pytz
from pytz import timezone
import re

from site_configuration import *

from google.appengine.ext import db

def DebugPrint(text, msg="print"):
	logging.info(">>>>>>>> %s >>>>>>>> %s" %(msg, text))

def stripTags(text):
    pattern = re.compile(r'<.*?>')
    return pattern.sub('', text)
		
DEVELOPMENT = True
FETCH_NUMBER = 1000

MEMBER_TYPES = ["member", "on-line member", "off-line member", "liaison", "curator", "guide", "manager", "owner"]
HELPING_ROLE_TYPES = ["curator", "guide", "liaison"]
GOVERNANCE_ROLE_TYPES = ["member", "manager", "owner"]

EVENT_TYPES = ["downdrift", \
			"reading", "adding story", "adding pattern", "adding collage", "adding invitation", "adding resource", \
			"adding retold link", "adding reminded link", "adding related link", "adding included link", "adding responded link", \
			"answering question", "adding tag set", "adding comment", "adding request", "adding nudge"]


ARTICLE_TYPES = ["story", "invitation", "collage", "pattern", "resource"]
LINK_TYPES = ["retold", "reminded", "responded", "related", "included"]

ANNOTATION_TYPES = ["tag set", "comment", "request", "nudge"]
ANNOTATION_TYPES_URLS = ["tagset", "comment", "request", "nudge"]
ENTRY_TYPES = ["story", "pattern", "collage", "invitation", "resource", "answer", "tag set", "comment", "request", "nudge"]
ENTRY_TYPES_URLS = ["story", "pattern", "collage", "invitation", "resource", "answer", "tagset", "comment", "request", "nudge"]
STORY_ENTRY_TYPE_INDEX = 0
ANSWERS_ENTRY_TYPE_INDEX = 5

MINUTE_SECONDS = 60
HOUR_SECONDS = 60 * MINUTE_SECONDS
DAY_SECONDS = 24 * HOUR_SECONDS
WEEK_SECONDS = 7 * DAY_SECONDS
MONTH_SECONDS = 30 * DAY_SECONDS
YEAR_SECONDS = 365 * DAY_SECONDS
TIME_UNIT_STRINGS = {"minute": MINUTE_SECONDS, 
					"hour": HOUR_SECONDS,
					"day": DAY_SECONDS,
					"week": WEEK_SECONDS,
					"month": MONTH_SECONDS,
					"year": YEAR_SECONDS,}

QUESTION_REFERS_TO = ["story", "pattern", "collage", "invitation", "resource", "member"]
QUESTION_REFERS_TO_PLURAL = ["stories", "patterns", "collages", "invitations", "resources", "members"]
QUESTION_TYPES = ["boolean", "text", "ordinal", "nominal", "value"]

# from http://www.letsyouandhimfight.com/2008/04/12/time-zones-in-google-app-engine/
# with a few changes
class TzDateTimeProperty(db.DateTimeProperty):
	def get_value_for_datastore(self, model_instance):
		value = super(TzDateTimeProperty, self).get_value_for_datastore(model_instance)
		if value:
			if value.tzinfo is None:
				value = value.replace(tzinfo=pytz.utc)
			else:
				value = value.astimezone(pytz.utc)
			return super(TzDateTimeProperty, self).get_value_for_datastore(model_instance)
		else:
			return None
	def make_value_from_datastore(self, value):
		value = super(TzDateTimeProperty, self).make_value_from_datastore(value)
		if value:
			if value.tzinfo is None:
				value = value.replace(tzinfo=pytz.utc)
			else:
				value = value.astimezone(pytz.utc)
		return value

# ============================================================================================
# ============================================================================================
class Community(db.Model):
# ============================================================================================
# ============================================================================================

	name = db.StringProperty() # appears on all pages at top
	tagline = db.StringProperty(default="") # appears under name, optional
	image = db.BlobProperty(default=None) # appears on all pages, should be small (100x60 is best)
	contactEmail = db.StringProperty(default=DEFAULT_CONTACT_EMAIL) # sender address for emails sent from site
	
	description = db.TextProperty(default=None) # appears on "about community" page
	description_formatted = db.TextProperty() # formatted texts kept separate for re-editing original
	description_format = db.StringProperty(default=DEFAULT_TEXT_FORMAT)
	
	etiquetteStatement = db.TextProperty(default=None) # appears on "about community" page
	etiquetteStatement_formatted = db.TextProperty()
	etiquetteStatement_format = db.StringProperty(default=DEFAULT_TEXT_FORMAT)
	
	welcomeMessage = db.TextProperty(default=DEFAULT_WELCOME_MESSAGE) # appears only on new member welcome page
	welcomeMessage_formatted = db.TextProperty()
	welcomeMessage_format = db.StringProperty(default=DEFAULT_TEXT_FORMAT)
	
	defaultTimeZoneName = db.StringProperty(default=DEFAULT_TIME_ZONE) # appears on member preferences page
	defaultTimeFormat = db.StringProperty(default=DEFAULT_TIME_FORMAT) # appears on member preferences page
	defaultDateFormat = db.StringProperty(default=DEFAULT_DATE_FORMAT) # appears on member preferences page
	
	created = TzDateTimeProperty(auto_now_add=True) 
	lastPublish = TzDateTimeProperty(default=None)
	firstPublish = TzDateTimeProperty(default=None)
	firstPublishSet = db.BooleanProperty(default=False) # whether the first publish date was set yet
	
	maxNumAttachments = db.IntegerProperty(choices=NUM_ATTACHMENT_CHOICES, default=DEFAULT_MAX_NUM_ATTACHMENTS)

	maxNudgePointsPerArticle = db.IntegerProperty(default=DEFAULT_MAX_NUDGE_POINTS_PER_ARTICLE)
	memberNudgePointsPerEvent = db.ListProperty(int, default=DEFAULT_MEMBER_NUDGE_POINT_ACCUMULATIONS)
	nudgeCategories = db.StringListProperty(default=DEFAULT_NUDGE_CATEGORIES)

	articleActivityPointsPerEvent = db.ListProperty(int, default=DEFAULT_ARCTICLE_ACTIVITY_POINT_ACCUMULATIONS)
	
	allowCharacter = db.ListProperty(bool, default=DEFAULT_ALLOW_CHARACTERS)
	allowEditingAfterPublishing = db.ListProperty(bool, default=DEFAULT_ALLOW_EDITING_AFTER_PUBLISHING)
	
	roleReadmes = db.ListProperty(db.Text, default=[db.Text(DEFAULT_ROLE_READMES[0]), db.Text(DEFAULT_ROLE_READMES[1]), db.Text(DEFAULT_ROLE_READMES[2])])
	roleReadmes_formatted = db.ListProperty(db.Text, default=[db.Text(""), db.Text(""), db.Text("")])
	roleReadmes_formats = db.StringListProperty(default=DEFAULT_ROLE_READMES_FORMATS)
	roleAgreements = db.ListProperty(bool, default=DEFAULT_ROLE_AGREEMENTS)
	
	# OPTIONS
	
	def allowsPostPublishEditOfArticleType(self, type):
		i = 0
		for articleType in ARTICLE_TYPES:
			if type == articleType:
				return self.allowEditingAfterPublishing[i]
			i += 1
		return False
	
	def allowsAtLeastTwoAttachments(self):
		return self.maxNumAttachments >= 2
	
	def allowsAtLeastThreeAttachments(self):
		return self.maxNumAttachments >= 3
	
	def allowsAtLeastFourAttachments(self):
		return self.maxNumAttachments >= 4
	
	def allowsFiveAttachments(self):
		return self.maxNumAttachments == 5
	
	def maxNumAttachmentsAsText(self):
		if self.maxNumAttachments == 1:
			return "one"
		elif self.maxNumAttachments == 2:
			return "two"
		elif self.maxNumAttachments == 3:
			return "three"
		elif self.maxNumAttachments == 4:
			return "four"
		elif self.maxNumAttachments == 5:
			return "five"
	
	# MEMBERS
	
	def getPendingMembers(self):
		return PendingMember.all().filter("community = ", self.key()).fetch(FETCH_NUMBER)

	def getOfflineMembers(self):
		return Member.all().filter("community = ", self.key()).filter("isOnlineMember = ", False).fetch(FETCH_NUMBER)
	
	def getMemberNudgePointsForEvent(self, event):
		i = 0
		for eventType in EVENT_TYPES:
			if event == eventType:
				return self.memberNudgePointsPerEvent[i]
			i += 1
		return 0
	
	def getMemberForGoogleAccountId(self, id):
		return Member.all().filter("community = ", self.key()).filter("googleAccountID = ", id).fetch(1)
		
	def getActiveMembers(self):
		return Member.all().filter("community = ", self.key()).filter("active = ", True).fetch(FETCH_NUMBER)
	
	def getInactiveMembers(self):
		return Member.all().filter("community = ", self.key()).filter("active = ", False).fetch(FETCH_NUMBER)
	
	def hasMemberWithGoogleEmail(self, email):
		members = self.getActiveMembers()
		for member in members:
			if member.googleAccountEmail == email:
				return True
		return False
	
	def getManagers(self):
		return Member.all().filter("community = ", self.key()).filter("governanceType = ", "manager").fetch(FETCH_NUMBER)
	
	def getOwners(self):
		return Member.all().filter("community = ", self.key()).filter("governanceType = ", "owner").fetch(FETCH_NUMBER)
	
	def getManagersAndOwners(self):
		return Member.all().filter("community = ", self.key()).filter("governanceType IN ", ["owner", "manager"]).fetch(FETCH_NUMBER)
	
	def memberIsOnlyOwner(self, member):
		owners = self.getOwners()
		if len(owners) == 1 and owners[0].key() == member.key():
			return True
		return False
	
	# CHARACTERS
	
	def getCharacters(self):
		return Character.all().filter("community = ", self.key()).fetch(FETCH_NUMBER)
	
	def hasAtLeastOneCharacterEntryAllowed(self, entryTypeIndex):
		return len(self.getCharacters()) > 0 or self.allowCharacter[entryTypeIndex]
	
	# ARTICLES
	
	def getNonDraftArticles(self):
		return Article.all().filter("community = ", self.key()).filter("draft = ", False).fetch(FETCH_NUMBER)
	
	def getNonDraftArticlesOfType(self, type):
		return Article.all().filter("community = ", self.key()).filter("draft = ", False).filter("type = ", type).fetch(FETCH_NUMBER)
	
	def getNonDraftArticlesWithMissingMetadata(self):
		articlesWithoutTags = []
		articlesWithoutLinks = []
		articlesWithoutAnswers = []
		articlesWithoutComments = []
		invitationsWithoutResponses = []
		collagesWithoutInclusions = []
		for article in self.getNonDraftArticles():
			if not Annotation.all().filter("article = ", article.key()).filter("type = ", "tag set").filter("draft = ", False).get():
				articlesWithoutTags.append(article)
			if not Link.all().filter("articleFrom = ", article.key()).get() and not Link.all().filter("articleTo = ", article.key()).get():
				articlesWithoutLinks.append(article)
			if not Answer.all().filter("referent = ", article.key()).filter("draft = ", False).get():
				articlesWithoutAnswers.append(article)
			if not Annotation.all().filter("article = ", article.key()).filter("type = ", "comment").filter("draft = ", False).get():
				articlesWithoutComments.append(article)
		for invitation in self.getNonDraftArticlesOfType("invitation"):
			if not Link.all().filter("articleFrom = ", invitation.key()).filter("type = ", "responded").get():
				invitationsWithoutResponses.append(invitation)
		for collage in self.getNonDraftArticlesOfType("collage"):
			if not Link.all().filter("articleFrom = ", collage.key()).filter("type = ", "included").get():
				collagesWithoutInclusions.append(collage)
		return (articlesWithoutTags, articlesWithoutLinks, articlesWithoutAnswers, articlesWithoutComments, invitationsWithoutResponses, collagesWithoutInclusions)
	
	def getArticleActivityPointsForEvent(self, event):
		i = 0
		for eventType in EVENT_TYPES:
			if event == eventType:
				return self.articleActivityPointsPerEvent[i]
			i += 1
		return 0
	
	# ARTICLES, ANNOTATIONS, ANSWERS, LINKS - EVERYTHING
	
	def getAllFlaggedItems(self):
		articles = Article.all().filter("community = ", self.key()).filter("draft = ", False).filter("flaggedForRemoval = ", True).fetch(FETCH_NUMBER)
		annotations = Annotation.all().filter("community = ", self.key()).filter("draft = ", False).filter("flaggedForRemoval = ", True).fetch(FETCH_NUMBER)
		answers = Answer.all().filter("community = ", self.key()).filter("draft = ", False).filter("flaggedForRemoval = ", True).fetch(FETCH_NUMBER)
		links = Link.all().filter("community = ", self.key()).filter("flaggedForRemoval = ", True).fetch(FETCH_NUMBER)
		return (articles, annotations, answers, links)
	
	def getAllFlaggedItemsAsOneList(self):
		result = []
		(articles, annotations, answers, links) = self.getAllFlaggedItems()
		result.extend(links)
		result.extend(answers)
		result.extend(annotations)
		result.extend(articles)
		return result

	def getAllItems(self):
		articles = Article.all().filter("community = ", self.key()).filter("draft = ", False).fetch(FETCH_NUMBER)
		annotations = Annotation.all().filter("community = ", self.key()).filter("draft = ", False).fetch(FETCH_NUMBER)
		answers = Answer.all().filter("community = ", self.key()).filter("draft = ", False).fetch(FETCH_NUMBER)
		links = Link.all().filter("community = ", self.key()).fetch(FETCH_NUMBER)
		return (articles, annotations, answers, links)
	
	# QUESTIONS
	
	def getQuestions(self):
		return Question.all().filter("community = ", self.key()).fetch(FETCH_NUMBER)
	
	def getQuestionsOfType(self, type):
		return Question.all().filter("community = ", self.key()).filter("refersTo = ", type).fetch(FETCH_NUMBER)
	
	def getMemberQuestions(self):
		return self.getQuestionsOfType("member")
	
	def getNonMemberQuestions(self):
		return Question.all().filter("community = ", self.key()).filter("refersTo !=", "member").fetch(FETCH_NUMBER)
		
	def hasQuestionWithSameTypeAndName(self, question):
		allQuestions = self.getQuestions()
		for aQuestion in allQuestions:
			if aQuestion.refersTo == question.refersTo and aQuestion.name == question.name:
				return True
		return False
	
	def AddCopyOfQuestion(self, question):
		newQuestion = Question(
							   refersTo=question.refersTo,
							   name=question.name,
							   text=question.text,
							   type=question.type,
							   choices=question.choices,
							   help=question.help,
							   useHelp=question.useHelp,
							   multiple=question.multiple,
							   community=self)
		newQuestion.put()
	
# ============================================================================================
# ============================================================================================
class Question(db.Model):
# ============================================================================================
# ============================================================================================

	community = db.ReferenceProperty(Community, collection_name="questions_to_community")
	refersTo = db.StringProperty(choices=QUESTION_REFERS_TO, required=True) # member or article
	
	name = db.StringProperty(required=True, default=DEFAULT_QUESTION_NAME)
	text = db.StringProperty(required=True)
	type = db.StringProperty(choices=QUESTION_TYPES, default="text") # text, boolean, ordinal, nominal, value
	
	lengthIfText = db.IntegerProperty(default=DEFAULT_QUESTION_TEXT_LENGTH)
	minIfValue = db.IntegerProperty(default=DEFAULT_QUESTION_VALUE_MIN)
	maxIfValue = db.IntegerProperty(default=DEFAULT_QUESTION_VALUE_MAX)
	responseIfBoolean = db.StringProperty(default=DEFAULT_QUESTION_BOOLEAN_RESPONSE) # what the checkbox label should say
	multiple = db.BooleanProperty(default=False) # whether multiple answers are allowed (for ordinal/nominal only)
	choices = db.StringListProperty(default=[""] * MAX_NUM_CHOICES_PER_QUESTION) 
	
	help = db.TextProperty() # appears to person answering question
	help_formatted = db.TextProperty()
	help_format = db.StringProperty(default=DEFAULT_TEXT_FORMAT)
	
	useHelp = db.TextProperty() # appears to manager choosing question, about when to use it
	useHelp_formatted = db.TextProperty()
	useHelp_format = db.StringProperty(default=DEFAULT_TEXT_FORMAT)
	
	created = TzDateTimeProperty(auto_now_add=True)
	
	def isOrdinalOrNominal(self):
		return self.type == "ordinal" or self.type == "nominal"
	
	def numChoices(self):
		return len(self.choices)
		
# ============================================================================================
# ============================================================================================
class Member(db.Model):
# ============================================================================================
# ============================================================================================

	community = db.ReferenceProperty(Community, required=True, collection_name="members_to_community")
	nickname = db.StringProperty(default=NO_NICKNAME_SET)
	isOnlineMember = db.BooleanProperty(default=True)
	googleAccountID = db.StringProperty() # none if off-line member
	googleAccountEmail = db.StringProperty() # blank if off-line member
	
	# active: members are never removed, just inactivated, so articles can still link to something.
	# inactive members do not show up in any display, but they can be "reactivated" by issuing an invitation
	# to the same google email as before.
	active = db.BooleanProperty(default=True) 
	
	governanceType = db.StringProperty(choices=GOVERNANCE_ROLE_TYPES, default="member") # can only be set by managers
	helpingRoles = db.ListProperty(bool, default=[False, False, False]) # members can choose
	helpingRolesAvailable = db.ListProperty(bool, default=[True, True, True]) # managers can ban members from roles
	
	guideIntro = db.TextProperty(default=None) # appears on the welcome and get help pages if the member is a guide
	guideIntro_formatted = db.TextProperty()
	guideIntro_format = db.StringProperty(default=DEFAULT_TEXT_FORMAT)
	
	nicknameIsRealName = db.BooleanProperty(default=False) # shows on member page only
	profileText = db.TextProperty(default=NO_PROFILE_TEXT)
	profileText_formatted = db.TextProperty()
	profileText_format = db.StringProperty(default=DEFAULT_TEXT_FORMAT)
	profileImage = db.BlobProperty(default=None) # optional, resized to 100x60
	acceptsMessages = db.BooleanProperty(default=True) # other members can send emails to their google email (without seeing it)
	
	timeZoneName = db.StringProperty() # members choose these in their prefs page
	timeFormat = db.StringProperty() # how they want to see dates
	dateFormat = db.StringProperty() # how they want to see times
	
	joined = TzDateTimeProperty(auto_now_add=True)
	lastEnteredArticle = db.DateTimeProperty()
	lastEnteredAnnotation = db.DateTimeProperty()
	lastEnteredLink = db.DateTimeProperty()
	lastAnsweredQuestion = db.DateTimeProperty()
	lastReadAnything = db.DateTimeProperty()
	
	nudgePoints = db.IntegerProperty(default=DEFAULT_START_NUDGE_POINTS) # accumulated through participation
	
	viewTimeEnd = TzDateTimeProperty(auto_now_add=True)
	viewTimeFrameInSeconds = db.IntegerProperty(default=3600)
	viewNumTimeFrames = db.IntegerProperty(default=1)
	viewNumTimeColumns = db.IntegerProperty(default=10)
	
	# CREATION
	
	def initialize(self):
		self.timeZoneName = self.community.defaultTimeZoneName
		self.timeFormat = self.community.defaultTimeFormat
		self.dateFormat = self.community.defaultDateFormat
		
	# INFO
		
	def googleUserEmailOrNotOnline(self):
		if self.isOnlineMember:
			return self.googleAccountEmail
		return "Offline member"
	
	# GOVERNANCE
	
	def isRegularMember(self):
		return self.governanceType == "member"
	
	def isManager(self):
		return self.governanceType == "manager"
	
	def isOwner(self):
		return self.governanceType == "owner"
	
	def isManagerOrOwner(self):
		return self.governanceType == "manager" or self.governanceType == "owner"
	
	# HELPING ROLES
	
	def isCurator(self):
		return self.helpingRoles[0]
	
	def isGuide(self):
		return self.helpingRoles[1]
	
	def isLiaison(self):
		return self.helpingRoles[2]
	
	def isCuratorOrManagerOrOwner(self):
		return self.isCurator() or self.isManagerOrOwner()
	
	def isGuideOrManagerOrOwner(self):
		return self.isGuide() or self.isManagerOrOwner()
	
	def hasAnyHelpingRole(self):
		return self.helpingRoles[0] or self.helpingRoles[1] or self.helpingRoles[2]

	def canTakeOnAnyHelpingRole(self):
		return self.helpingRolesAvailable[0] or self.helpingRolesAvailable[1] or self.helpingRolesAvailable[2]
	
	# BROWSING
	
	def getViewStartTime(self):
		deltaSeconds = self.viewTimeFrameInSeconds * self.viewNumTimeFrames
		return self.viewTimeEnd - timedelta(seconds=deltaSeconds)
			
	def setViewTimeFrameFromTimeUnitString(self, unit):
		for aUnit in TIME_UNIT_STRINGS.keys():
			if unit == aUnit:
				self.viewTimeFrameInSeconds = TIME_UNIT_STRINGS[aUnit]
				break
				# caller should do the put
			
	def getUnitStringForViewTimeFrame(self):
		for key, value in TIME_UNIT_STRINGS.items():
			if self.viewTimeFrameInSeconds == value:
				return key
			
	def setTimeFrameToStartAtFirstPublish(self):
		deltaSeconds = self.viewTimeFrameInSeconds * self.viewNumTimeFrames
		self.viewTimeEnd = self.community.firstPublish + timedelta(seconds=deltaSeconds)
		
	# CONTRIBUTIONS
	
	def getAnswers(self):
		return Answer.all().filter("referent = ", self.key()).fetch(FETCH_NUMBER)
	
	def getNonDraftArticlesAttributedToMember(self):
		return Article.all().filter("creator = ", self.key()).filter("draft = ", False).filter("character = ", None).fetch(FETCH_NUMBER)
	
	def getNonDraftAnnotationsAttributedToMember(self):
		return Annotation.all().filter("creator = ", self.key()).filter("draft = ", False).filter("character = ", None).fetch(FETCH_NUMBER)
	
	def getNonDraftAnswersAboutArticlesAttributedToMember(self):
		return Answer.all().filter("creator = ", self.key()).filter("draft = ", False).filter("character = ", None).filter("referentType = ", "article").fetch(FETCH_NUMBER)
	
	# DRAFTS
	
	def getDraftArticles(self):
		return Article.all().filter("creator = ", self.key()).filter("draft = ", True).fetch(FETCH_NUMBER)
	
	def getDraftAnswersForArticle(self, article):
		return Answer.all().filter("creator = ", self.key()).filter("draft = ", True).filter("referent = ", article.key()).fetch(FETCH_NUMBER)
	
	def getDraftAnnotations(self):
		return Annotation.all().filter("creator = ", self.key()).filter("draft = ", True).fetch(FETCH_NUMBER)
	
	def getArticlesWithDraftAnswers(self):
		answers = Answer.all().filter("creator = ", self.key()).filter("draft = ", True).filter("referentType = ", "article").fetch(FETCH_NUMBER)
		articles = {}
		for answer in answers:
			if not articles.has_key(answer.referent):
				articles[answer.referent] = 1
		return articles.keys()
	
# ============================================================================================
# ============================================================================================
class PendingMember(db.Model): # person invited to join community but not yet logged in
# ============================================================================================
# ============================================================================================

	community = db.ReferenceProperty(Community, required=True, collection_name="pending_members_to_community")
	email = db.StringProperty(required=True) # must match google account
	invited = TzDateTimeProperty(auto_now_add=True)
	
# ============================================================================================
# ============================================================================================
class Character(db.Model): # optional fictions to anonymize entries but provide some information about intent
# ============================================================================================
# ============================================================================================

	community = db.ReferenceProperty(Community, required=True, collection_name="characters_to_community")
	name = db.StringProperty(required=True)
	
	description = db.TextProperty(default=None) # appears on community page
	description_formatted = db.TextProperty()
	description_format = db.StringProperty(default=DEFAULT_TEXT_FORMAT)
	
	etiquetteStatement = db.TextProperty(default=None) # appears under "how to be [name]"
	etiquetteStatement_formatted = db.TextProperty()
	etiquetteStatement_format = db.StringProperty(default=DEFAULT_TEXT_FORMAT)
	
	image = db.BlobProperty(default=None) # optional
	
	def getNonDraftArticlesAttributedToCharacter(self):
		return Article.all().filter("character = ", self.key()).filter("draft = ", False).fetch(FETCH_NUMBER)
	
	def getNonDraftAnnotationsAttributedToCharacter(self):
		return Annotation.all().filter("character = ", self.key()).filter("draft = ", False).fetch(FETCH_NUMBER)
	
	def getNonDraftAnswersAboutArticlesAttributedToCharacter(self):
		return Answer.all().filter("character = ", self.key()).filter("draft = ", False).filter("referentType = ", "article").fetch(FETCH_NUMBER)

# ============================================================================================
# ============================================================================================
class Answer(db.Model):
# ============================================================================================
# ============================================================================================

	community = db.ReferenceProperty(Community, collection_name="answers_to_community")
	question = db.ReferenceProperty(Question, collection_name="answers_to_questions")
	referent = db.ReferenceProperty(None, collection_name="answers_to_objects") # article or member
	referentType = db.StringProperty(default="article") # article or member
	creator = db.ReferenceProperty(Member, collection_name="answers_to_creators") 
	
	collectedOffline = db.BooleanProperty(default=False)
	liaison = db.ReferenceProperty(Member, default=None, collection_name="answers_to_liaisons")
	character = db.ReferenceProperty(Character, default=None)
	
	draft = db.BooleanProperty(default=True)
	flaggedForRemoval = db.BooleanProperty(default=False)
	
	answerIfBoolean = db.BooleanProperty(default=False)
	answerIfText = db.StringProperty(default="")
	answerIfMultiple = db.StringListProperty(default=[""] * MAX_NUM_CHOICES_PER_QUESTION)
	answerIfValue = db.IntegerProperty(default=0)
	
	created = TzDateTimeProperty(auto_now_add=True)
	edited = TzDateTimeProperty(auto_now_add=True)
	published = TzDateTimeProperty(auto_now_add=True)
	
	articleNudgePointsWhenPublished = db.ListProperty(int, default=[0] * NUM_NUDGE_CATEGORIES)
	articleActivityPointsWhenPublished = db.IntegerProperty(default=0)
	
	def publish(self):
		if self.referentType == "article":
			self.draft = False
			self.published = datetime.now(pytz.utc)
			self.put()
			self.referent.recordAction("added", self)
			if self.referentType == "article":
				for i in range(NUM_NUDGE_CATEGORIES):
					self.articleNudgePointsWhenPublished[i] = self.referent.nudgePoints[i]
				self.articleActivityPointsWhenPublished = self.referent.activityPoints
				self.put()
			self.creator.nudgePoints += self.community.getMemberNudgePointsForEvent("answering question")
			self.creator.lastAnsweredQuestion = datetime.now(pytz.utc)
			self.creator.put()
			self.community.lastPublish = self.published
			self.community.put()
				
	# DISPLAY
		
	def getImageLinkForType(self):
		return'<img src="/images/answers.png" alt="answer" border="0">'
	
	def displayStringShort(self):
		return self.displayString(includeQuestionName=False)
	
	def displayString(self, includeQuestionName=True):
		if includeQuestionName:
			result = self.question.name + ": "
		else: 
			result = ""
		if self.question.type == "boolean":
			if self.answerIfBoolean: 
				result += "yes"
			else:
				result += "no"
		elif self.question.type == "text":
			result += self.answerIfText
		elif self.question.type == "ordinal" or self.question.type == "nominal":
			answersToReport = []
			for answer in self.answerIfMultiple:
				if len(answer):
					answersToReport.append(answer)
			result +=  ", ".join(answersToReport)
		elif self.question.type == "value":
			result +=  "%s" % self.answerIfValue
		return result
	
	def linkString(self):
		return self.displayString()
		
	# ATTRIBUTION
	
	def attributedToMember(self):
		return self.character == None
	
	def memberNickNameOrCharacterName(self):
		if self.character:
			return self.character.name
		else:
			return self.creator.nickname
		
	def questionKey(self):
		return self.question.key()
	

# ============================================================================================
# ============================================================================================
class Article(db.Model):                       # story, invitation, collage, pattern, resource
# ============================================================================================
# ============================================================================================

	type = db.StringProperty(choices=ARTICLE_TYPES, required=True) 
	title = db.StringProperty(required=True, default=DEFAULT_UNTITLED_ARTICLE_TITLE)
	text = db.TextProperty(default=NO_TEXT_IN_ARTICLE)
	text_formatted = db.TextProperty()
	text_format = db.StringProperty(default=DEFAULT_TEXT_FORMAT)

	community = db.ReferenceProperty(Community, required=True, collection_name="articles_to_community")
	creator = db.ReferenceProperty(Member, collection_name="articles")
	collectedOffline = db.BooleanProperty(default=False)
	liaison = db.ReferenceProperty(Member, default=None, collection_name="articles_to_liaisons")
	character = db.ReferenceProperty(Character, default=None)
	
	draft = db.BooleanProperty(default=True)
	flaggedForRemoval = db.BooleanProperty(default=False)
	
	collected = TzDateTimeProperty(default=None)
	created = TzDateTimeProperty(auto_now_add=True)
	edited = TzDateTimeProperty(auto_now_add=True)
	published = TzDateTimeProperty(auto_now_add=True)
	
	lastRead = TzDateTimeProperty(default=None)
	lastDowndrifted = TzDateTimeProperty(default=None)
	lastAnnotatedOrAnsweredOrLinked = TzDateTimeProperty(default=None)
	
	activityPoints = db.IntegerProperty(default=0)
	nudgePoints = db.ListProperty(int, default=[0] * NUM_NUDGE_CATEGORIES)
	
	# IMPORTANT METHODS
	
	def publish(self):
		self.draft = False
		self.published = datetime.now(pytz.utc)
		self.recordAction("added", self)
		self.put()
		self.creator.nudgePoints += self.community.getMemberNudgePointsForEvent("adding %s" % self.type)
		self.creator.lastEnteredArticle = datetime.now(pytz.utc)
		self.creator.put()
		for answer in self.getAnswersForMember(self.creator):
			answer.publish()
		self.community.lastPublish = self.published
		if not self.community.firstPublishSet:
			self.community.firstPublish = self.published
			self.community.firstPublishSet = True
		self.community.put()
		
	def recordAction(self, action, referent):
		if referent.__class__.__name__ == "Article":
			if action == "read":
				eventType = "reading"
				self.lastRead = datetime.now(tz=pytz.utc)
			elif action == "downdrift":
				eventType = "downdrift"
				self.lastDowndrifted = datetime.now(tz=pytz.utc)
			elif action =="added":
				eventType = "adding %s" % self.type
		elif referent.__class__.__name__ == "Annotation":
			eventType = "adding %s" % referent.type
			self.lastAnnotatedOrAnsweredOrLinked = datetime.now(pytz.utc)
			if referent.type == "nudge":
				self.nudgePoints = self.getCurrentTotalNudgePointsInAllCategories()
		elif referent.__class__.__name__ == "Answer":
			eventType = "answering question"
			self.lastAnnotatedOrAnsweredOrLinked = datetime.now(pytz.utc)
		elif referent.__class__.__name__ == "Link":
			eventType = "adding %s link" % referent.type 
			self.lastAnnotatedOrAnsweredOrLinked = datetime.now(pytz.utc)
		self.activityPoints += self.community.getArticleActivityPointsForEvent(eventType)
		self.put()
		
	def updateForTimeDownDrift(self):
		if self.lastDowndrifted:
			timeOfPreviousAction = self.lastDowndrifted
		else:
			timeOfPreviousAction = self.published
		daysSinceLastDowndrift = datetime.now(tz=pytz.utc) - lastDowndrifted
		if daysSinceLastDowndrift > 0:
			self.recordAction("downdrift", self)
		
	def removeAllDependents(self):
		for attachment in self.getAttachments():
			db.delete(attachment)
		for link in self.getAllLinks():
			db.delete(link)
		for answer in self.getAnswers():
			db.delete(answer)
		for annotation in self.getAnnotations():
			db.delete(annotation)

	# TYPE
	
	def isStory(self):
		return self.type == "story"
	
	def isInvitation(self):
		return self.type == "invitation"
	
	def isCollage(self):
		return self.type == "collage"
	
	def isPattern(self):
		return self.type == "pattern"
	
	def isResource(self):
		return self.type == "resource"
	
	def isPatternOrCollage(self):
		return self.type == "pattern" or self.type == "collage"
	
	def isCollageOrResource(self):
		return self.type == "collage" or self.type == "resource"
	
	# MEMBERS
		
	def getPublishDateForMember(self, member):
		if member:
			localTime = self.published.astimezone(timezone(member.timeZoneName))
			return localTime.strftime(str(member.timeFormat))
		else:
			return self.published
	
	def attributedToMember(self):
		return self.character == None
	
	def memberNickNameOrCharacterName(self):
		if self.character:
			return self.character.name
		else: 
			return self.creator.nickname
		
	# NUDGE SYSTEM

	def getNudgesForMember(self, member):
		return Annotation.all().filter("article = ", self.key()).filter("type = ", "nudge").filter("creator = ", member.key()).fetch(FETCH_NUMBER)
	
	def getTotalNudgePointsForMember(self, member):
		nudges = self.getNudgesForMember(member)
		result = 0
		for nudge in nudges:
			result += nudge.totalNudgePointsAbsolute()
		return result
	
	def memberCanNudge(self, member):
		return member.key() != self.creator.key()

	def getCurrentTotalNudgePointsInAllCategories(self):
		result = [0] * NUM_NUDGE_CATEGORIES
		for nudge in self.getNonDraftAnnotationsOfType("nudge"):
			i = 0
			for value in nudge.valuesIfNudge:
				result[i] += value
				i += 1
		return result
	
	def nudgePointsCombined(self):
		return self.nudgePoints[0] + self.nudgePoints[1] + self.nudgePoints[2] + self.nudgePoints[3] + self.nudgePoints[4]
	
	# ANNOTATIONS, ANSWERS, LINKS
	
	def getAnnotations(self):
		return Annotation.all().filter("article =", self.key()).fetch(FETCH_NUMBER)
	
	def getNonDraftAnnotations(self):
		return Annotation.all().filter("article =", self.key()).filter("draft = ", False).fetch(FETCH_NUMBER)
	
	def getNonDraftAnnotationsOfType(self, type):
		return Annotation.all().filter("article =", self.key()).filter("type = ", type).filter("draft = ", False).fetch(FETCH_NUMBER)
	
	def getAttachments(self):
		return Attachment.all().filter("article =", self.key()).fetch(FETCH_NUMBER)
	
	def getAnswers(self):
		return Answer.all().filter("referent = ", self.key()).fetch(FETCH_NUMBER)
	
	def getNonDraftAnswers(self):
		return Answer.all().filter("referent = ", self.key()).filter("draft = ", False).fetch(FETCH_NUMBER)

	def getAnswersForMember(self, member):
		return Answer.all().filter("referent = ", self.key()).filter("creator = ", member.key()).fetch(FETCH_NUMBER)
	
	def getAllLinks(self):
		result = []
		outgoingLinks = Link.all().filter("articleFrom =", self.key()).fetch(FETCH_NUMBER)
		incomingLinks = Link.all().filter("articleTo =", self.key()).fetch(FETCH_NUMBER)
		result.extend(outgoingLinks)
		result.extend(incomingLinks)
		return result
	
	def getLinksOfType(self, type):
		result = []
		outgoingLinks = self.getOutgoingLinksOfType(type)
		incomingLinks = self.getIncomingLinksOfType(type)
		result.extend(outgoingLinks)
		result.extend(incomingLinks)
		return result
	
	def getOutgoingLinksOfType(self, type):
		return Link.all().filter("articleFrom =", self.key()).filter("type = ", type).fetch(FETCH_NUMBER)
	
	def getIncomingLinksOfType(self, type):
		return Link.all().filter("articleTo =", self.key()).filter("type = ", type).fetch(FETCH_NUMBER)
	
	def getIncomingLinksOfTypeFromType(self, type, fromType):
		result = []
		incomingLinks = self.getIncomingLinksOfType(type)
		for link in incomingLinks:
			if link.articleFrom.type == fromType:
				result.append(link)
		return result
	
	# DISPLAY
	
	def displayString(self):
		return self.title
	
	def linkString(self):
		return '<a href="/visit/read?%s">%s</a>' % (self.key(), self.title)
	
	def getTooltipText(self):
		if self.text_formatted:
			return'title="%s"' % stripTags(self.text_formatted[:100])
		else:
			return ""
	
	def shortFormattedText(self):
		if len(self.text_formatted) > 100:
			return "%s ..." % self.text_formatted[:98]
		else:
			return self.text_formatted

	def getImageLinkForType(self):
		text = self.getTooltipText()
		if self.type == "story":
			imageText = '<img src="/images/story.png" alt="story" border="0" %s\>' % text
		elif self.type == "pattern":
			imageText = '<img src="/images/pattern.png" alt="pattern" border="0" %s\>' % text
		elif self.type == "collage":
			imageText = '<img src="/images/collage.png" alt="collage" border="0" %s\>' % text
		elif self.type == "invitation":
			imageText = '<img src="/images/invitation.png" alt="invitation" border="0" %s\>' % text
		elif self.type == "resource":
			imageText = '<img src="/images/resource.png" alt="resource" border="0" %s\>' % text
		return imageText
	
# ============================================================================================
# ============================================================================================
class Link(db.Model):                         # related, retold, reminded, responded, included
# ============================================================================================
# ============================================================================================
	type = db.StringProperty(choices=LINK_TYPES, required=True) 
	# how links go: 
	#	related: either way
	#	retold: story to story
	# 	reminded: story or resource to story
	#   responded: invitation to story
	#	included: collage to story
	articleFrom = db.ReferenceProperty(Article, collection_name="linksFrom", required=True)
	articleTo = db.ReferenceProperty(Article, collection_name="linksTo", required=True)
	community = db.ReferenceProperty(Community, required=True, collection_name="links_to_community")
	creator = db.ReferenceProperty(Member, collection_name="links")
	
	# links cannot be in draft mode
	flaggedForRemoval = db.BooleanProperty(default=False)
	
	published = TzDateTimeProperty(auto_now_add=True)
	
	comment = db.StringProperty(default="")
	
	articleNudgePointsWhenPublished = db.ListProperty(int, default=[0] * NUM_NUDGE_CATEGORIES)
	articleActivityPointsWhenPublished = db.IntegerProperty(default=0)
	
	# IMPORTANT METHODS
	
	def publish(self):
		self.published = datetime.now(pytz.utc)
		self.put()
		self.articleFrom.recordAction("added", self)
		self.articleTo.recordAction("added", self)
		for i in range(NUM_NUDGE_CATEGORIES):
			self.articleNudgePointsWhenPublished[i] = self.articleFrom.nudgePoints[i]
		self.articleActivityPointsWhenPublished = self.articleFrom.activityPoints
		self.put()
		self.creator.nudgePoints = self.articleFrom.community.getMemberNudgePointsForEvent("adding %s link" % self.type)
		self.creator.lastEnteredLink = datetime.now(pytz.utc)
		self.creator.put()
		self.articleFrom.community.lastPublish = self.published
		if not self.articleFrom.community.firstPublishSet:
			self.articleFrom.community.firstPublish = self.published
			self.articleFrom.community.firstPublishSet = True
		self.articleFrom.community.put()
		
	# MEMBERS
		
	def attributedToMember(self):
		return True
	
	# DISPLAY
		
	def getImageLinkForType(self):
		return'<img src="/images/link.png" alt="link" border="0">'
	
	def displayString(self):
		result = '<a href="read?%s">%s</a> (%s' % (self.articleTo.key(), self.articleTo.title, self.type)
		if self.comment:
			result += ", %s)" % self.comment
		else:
			result += ")"
		return result
	
	def linkString(self):
		return self.displayString()
		
# ============================================================================================
# ============================================================================================
class Attachment(db.Model):                                   # binary attachments to articles
# ============================================================================================
# ============================================================================================
	name = db.StringProperty()
	mimeType = db.StringProperty() # from ACCEPTED_ATTACHMENT_MIME_TYPES
	fileName = db.StringProperty() # as uploaded
	data = db.BlobProperty() # there is a practical limit on this size - cfk look at
	article = db.ReferenceProperty(Article, collection_name="attachments")
	
	def linkString(self):
		return '<a href="/visit/attachment?attachment_id=%s">%s</a>' % (self.key(), self.fileName)
	
	def isImage(self):
		return self.mimeType == "image/jpeg" or self.mimeType == "image/png"
	
# ============================================================================================
# ============================================================================================
class Annotation(db.Model):                                # tag set, comment, request, nudge
# ============================================================================================
# ============================================================================================

	type = db.StringProperty(choices=ANNOTATION_TYPES, required=True)
	community = db.ReferenceProperty(Community, required=True, collection_name="annotations_to_community")
	article = db.ReferenceProperty(Article, required=True, collection_name="annotations")
	creator = db.ReferenceProperty(Member, collection_name="annotations")
	
	draft = db.BooleanProperty(default=True)
	flaggedForRemoval = db.BooleanProperty(default=False)
	
	shortString = db.StringProperty() # comment/request subject, nudge comment
	
	longString = db.TextProperty() # comment/request body
	longString_formatted = db.TextProperty()
	longString_format = db.StringProperty(default=DEFAULT_TEXT_FORMAT)
	
	tagsIfTagSet = db.StringListProperty(default=[""] * NUM_TAGS_IN_TAG_SET)
	valuesIfNudge = db.ListProperty(int, default=[0] * NUM_NUDGE_CATEGORIES)

	collectedOffline = db.BooleanProperty(default=False)
	liaison = db.ReferenceProperty(Member, default=None, collection_name="annotations_liaisoned")
	character = db.ReferenceProperty(Character, default=None)

	collected = TzDateTimeProperty(default=None)
	created = TzDateTimeProperty(auto_now_add=True)
	edited = TzDateTimeProperty(auto_now_add=True)
	published = TzDateTimeProperty(auto_now_add=True)
	
	articleNudgePointsWhenPublished = db.ListProperty(int, default=[0] * NUM_NUDGE_CATEGORIES)
	articleActivityPointsWhenPublished = db.IntegerProperty(default=0)
	
	# IMPORTANT METHODS
	
	def publish(self):
		self.draft = False
		self.published = datetime.now(pytz.utc)
		self.put()
		self.article.recordAction("added", self)
		for i in range(NUM_NUDGE_CATEGORIES):
			self.articleNudgePointsWhenPublished[i] = self.article.nudgePoints[i]
		self.articleActivityPointsWhenPublished = self.article.activityPoints
		self.put()
		self.creator.nudgePoints += self.community.getMemberNudgePointsForEvent("adding %s" % self.type)
		self.creator.put()
		self.community.lastPublish = self.published
		self.community.put()

	# TYPE
	
	def isComment(self):
		return self.type == "comment"
	
	def isRequest(self):
		return self.type == "request"
	
	def isNudge(self):
		return self.type == "nudge"
	
	# NUDGE SYSTEM
	
	def totalNudgePoints(self):
		result = 0
		for value in self.valuesIfNudge:
			result += value
		return result
	
	def totalNudgePointsAbsolute(self):
		result = 0
		for value in self.valuesIfNudge:
			result += abs(value)
		return result
	
	# MEMBERS
	
	def attributedToMember(self):
		return self.character == None
	
	def memberNickNameOrCharacterName(self):
		if self.character:
			return self.character.name
		else:
			return self.creator.nickname
		
	# DISPLAY
		
	def typeAsURL(self):
		if self.type != "tag set":
			return self.type
		return "tagset"
	
	def displayString(self):
		if self.type == "comment" or self.type == "request":
			return self.shortString
		elif self.type == "tag set":
			return ", ".join(self.tagsIfTagSet)
		elif self.type == "nudge":
			result = []
			for i in range(NUM_NUDGE_CATEGORIES):
				if self.valuesIfNudge[i] != 0:
					result.append("%s %s" % (self.valuesIfNudge[i], self.community.nudgeCategories[i]))
			if self.shortString:
				result.append("(%s)" % self.shortString)
			return ", ".join(result)
	
	def linkString(self):
		if self.type == "comment" or self.type == "request":
			if self.longString_formatted and len(self.longString_formatted) > 30:
				return '<a href="/visit/readAnnotation?%s">%s</a>' % (self.key(), self.displayString())
			elif self.longString_formatted:
				return "%s - %s" % (self.shortString, stripTags(self.longString_formatted)[:50])
			else:
				return self.shortString
		else:
			return self.displayString()
		
	def getImageLinkForType(self):
		if self.type == "comment":
			imageText = '<img src="/images/comments.png" alt="comment" border="0">'
		elif self.type == "request":
			imageText = '<img src="/images/requests.png" alt="request" border="0">'
		elif self.type == "tag set":
			imageText = '<img src="/images/tags.png" alt="tag set" border="0">'
		elif self.type == "nudge":
			imageText = '<img src="/images/nudges.png" alt="nudge" border="0">'
		return imageText
	
# ============================================================================================
# ============================================================================================
class Help(db.Model):	     # context-sensitive help string - appears as title hover on icon 
# ============================================================================================
# ============================================================================================

	type = db.StringProperty() # info, tip, caution
	name = db.StringProperty() # links to name in template
	text = db.StringProperty() # text to show user (plain text)
	
	