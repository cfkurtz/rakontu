# --------------------------------------------------------------------------------------------
# RAKONTU
# Description: Rakontu is open source story sharing software.
# Version: pre-0.1
# License: GPL 3.0
# Google Code Project: http://code.google.com/p/rakontu/
# --------------------------------------------------------------------------------------------

import logging
from datetime import *
import pytz
from pytz import timezone

from google.appengine.ext import db


def DebugPrint(text, msg="print"):
	logging.info(">>>>>>>> %s >>>>>>>> %s" %(msg, text))
	
# --------------------------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------------------------

DEVELOPMENT = True
FETCH_NUMBER = 1000

# community
NUM_NUDGE_CATEGORIES = 5
DEFAULT_MAX_NUDGE_POINTS_PER_ARTICLE = 25
DEFAULT_NUDGE_POINT_ACCUMULATIONS = [
									0, # time (doesn't apply here)
					 				4, # reading
					 				20, # telling
					 				5, # retelling
					 				5, # reminding
					 				10, # relating
					 				15, # including
					 				30, # responding
					 				2, # answering
					 				4, # tagging
					 				5, # commenting
					 				8, # requesting
					 				20, # nudging 
					 				]

DATE_FORMATS = {
			"j F Y": "%e %B %Y", # 3 January 2000
			"F j, Y": "%B %e, %Y", # January 3, 2000
			"j F": "%e %B", # 3 January
			"F j": "%B %e", # January 3
			"j/n/Y": "%d/%m/%Y", # 03/01/2000
			"n/j/Y": "%m/%d/%Y", # 01/03/2000
			}
TIME_FORMATS = {
			"h:i a": "%I:%M %p", #"5:00 pm", 
			"H:i": "%H:%M", #"17:00",
			}

# member
NO_NICKNAME_SET = "No nickname set"
MEMBER_TYPES = ["member", "on-line member", "off-line member", "liaison", "curator", "guide", "manager", "owner"]
HELPING_ROLE_TYPES = ["curator", "guide", "liaison"]
DEFAULT_ROLE_READMES = [
						"A curator pays attention to Rakontu's accumulated data. Curators add information, check for problems, create links, and in general maintain the vitality of the story bank.",
						"A guide pays attention to the Rakontu's on-line human community. Guides answer questions, write tutorials, encourage people to tell and use stories, create patterns, write and respond to requests, set up and run exercises, and in general maintain the vitality of the on-line member community.",
						"A liaison guides stories and other information over the barrier between on-line and off-line worlds. Liaisons conduct external interviews and add the stories people tell in them, read stories to people and gather comments, nudges, and other annotations, and in general make the system work for both on-line and off-line community members."]
GOVERNANCE_ROLE_TYPES = ["member", "manager", "owner"]
EVENT_TYPES = ["time (downdrift)", \
			"reading", "adding story", "adding pattern", "adding collage", "adding invitation", "adding resource", \
			"adding retold link", "adding reminded link", "adding related link", "adding included link", "adding responded link", \
			"answering question", "adding tag set", "adding comment", "adding request", "adding nudge"]
DEFAULT_MEMBER_NUDGE_POINT_ACCUMULATIONS = [
					0,	# time (downdrift)
					4,	# reading
					40,	# adding story
					20,	# adding pattern
					20,	# adding collage
					30,	# adding invitation
					10,	# adding resource
					10,	# adding retelling link
					5,	# adding reminding link
					5,	# adding relating link
					5,	# adding including link
					10,	# adding responding link
					2,	# answering question
					10,	# adding tag set
					15,	# adding comment
					15,	# adding request
					5,	# adding nudge
					]
DEFAULT_ARCTICLE_ACTIVITY_POINT_ACCUMULATIONS = [
					-1,	# time (downdrift)
					4,	# reading
					40,	# adding story
					20,	# adding pattern
					20,	# adding collage
					30,	# adding invitation
					10,	# adding resource
					10,	# adding retelling link
					5,	# adding reminding link
					5,	# adding relating link
					5,	# adding including link
					10,	# adding responding link
					2,	# answering question
					10,	# adding tag set
					15,	# adding comment
					15,	# adding request
					5,	# adding nudge
					]

# articles
ARTICLE_TYPES = ["story", "pattern", "collage", "invitation", "resource"]
LINK_TYPES = ["retold", "reminded", "responded", "related", "included"]
ACCEPTED_ATTACHMENT_FILE_TYPES = ["jpg", "png", "pdf", "doc", "txt", "mpg", "mp3", "html", "zip"]
ACCEPTED_ATTACHMENT_MIME_TYPES = ["image/jpeg", "image/png", "application/pdf", "application/msword", "text/plain", "video/mpeg", "audio/mpeg", "text/html", "application/zip"]

# annotations
ANNOTATION_TYPES = ["tag set", "comment", "request", "nudge"]
ANNOTATION_TYPES_URLS = ["tagset", "comment", "request", "nudge"]
NUDGE_TYPES = ["appropriateness", "importance", "utility", "utility custom 1", "utility custom 2", "utility custom 3"]
ENTRY_TYPES = ["story", "pattern", "collage", "invitation", "resource", "answer", "tag set", "comment", "request", "nudge"]
ENTRY_TYPES_URLS = ["story", "pattern", "collage", "invitation", "resource", "answer", "tagset", "comment", "request", "nudge"]
STORY_ENTRY_TYPE_INDEX = 0
ANSWERS_ENTRY_TYPE_INDEX = 5

# browsing
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
TIME_FRAMES = ["minute", "hour", "day", "week", "month", "year"]

# querying
QUERY_TYPES = ["free text", "tags", "answers", "members", "activities", "links"]
QUERY_TARGETS = ["stories", "patterns", "collages", "invitations", "resources", "articles", "answers", "tags", "comments", "requests", "nudge comments"]
BOOLEAN_CHOICES = ["ALL", "ANY"]
RECENT_TIME_FRAMES = ["last hour", "last day", "last week", "last month", "last six months", "last year", "ever"]

# questions 
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

# --------------------------------------------------------------------------------------------
# Community
# --------------------------------------------------------------------------------------------

class Community(db.Model):
	""" Preferences and settings for the whole community.
		There can be multiple communities within one Rakontu installation.
	
	Properties
		name:					The name that appears on all pages.
		tagline:				Very short description that comes after the community name on the top of the page.
		description:			Some text that describes the community. 
		etiquetteStatement:		This is just some extra text in case they want to say how people should behave.
		welcomeMessage:			Extra text a new member will see.
		image:					Picture to show on community page.
		
		nudgePointsPerActivity:	A number for each type of activity (ACTIVITIES_GERUND) denoting how many
								points the member accumulates for doing it.
		maxNudgePointsPerArticle:	How many nudge points a member is allowed to place (maximally) on any article.
		allowCharacter:	Whether members are allowed to enter things with
								a character marked. One entry per type of thing (ENTRY_TYPES)
		nudgeCategories:		Names of nudge categories. Up to five allowed.
		roleReadmes:			Texts all role members read before taking on a role.
								One text per helping role type.
		roleAgreements:			Whether the user is asked to click a checkbox before taking on a role
								to show that they agree with the terms of the role. (Social obligation only.)
		maxNumAttachments:		How many attachments are allowed per article.
								May be useful to keep the database from getting out of hand.
	"""
	name = db.StringProperty()
	tagline = db.StringProperty(default="")
	description = db.TextProperty()
	description_formatted = db.TextProperty()
	description_format = db.StringProperty(default="plain text")
	etiquetteStatement = db.TextProperty()
	etiquetteStatement_formatted = db.TextProperty()
	etiquetteStatement_format = db.StringProperty(default="plain text")
	welcomeMessage = db.TextProperty()
	welcomeMessage_formatted = db.TextProperty()
	welcomeMessage_format = db.StringProperty(default="plain text")
	image = db.BlobProperty(default=None)
	
	defaultTimeZoneName = db.StringProperty(default="US/Eastern")
	defaultTimeFormat = db.StringProperty(default="h:i a")
	defaultDateFormat = db.StringProperty(default="F j, Y")
	
	created = TzDateTimeProperty(auto_now_add=True)
	lastPublish = TzDateTimeProperty(default=None)
	firstPublish = TzDateTimeProperty(default=None)
	firstPublishSet = db.BooleanProperty(default=False)
	
	maxNudgePointsPerArticle = db.IntegerProperty(default=DEFAULT_MAX_NUDGE_POINTS_PER_ARTICLE)
	memberNudgePointsPerEvent = db.ListProperty(int, default=DEFAULT_MEMBER_NUDGE_POINT_ACCUMULATIONS)
	articleActivityPointsPerEvent = db.ListProperty(int, default=DEFAULT_ARCTICLE_ACTIVITY_POINT_ACCUMULATIONS)
	allowCharacter = db.ListProperty(bool, default=[True,True,True,True,True,True,True,True,True,True])
	nudgeCategories = db.StringListProperty(default=["appropriate", "important", "useful to new members", "useful for resolving conflicts", "useful for understanding"])
	roleReadmes = db.ListProperty(db.Text, default=[db.Text(DEFAULT_ROLE_READMES[0]), db.Text(DEFAULT_ROLE_READMES[1]), db.Text(DEFAULT_ROLE_READMES[2])])
	roleReadmes_formatted = db.ListProperty(db.Text, default=[db.Text(""), db.Text(""), db.Text("")])
	roleReadmes_formats = db.StringListProperty(default=["plain text", "plain text", "plain text"])
	roleAgreements = db.ListProperty(bool, default=[False, False, False])
	maxNumAttachments = db.IntegerProperty(choices=[0,1,2,3,4,5], default=3)
	
	def getArticleActivityPointsForEvent(self, event):
		i = 0
		for eventType in EVENT_TYPES:
			if event == eventType:
				return self.articleActivityPointsPerEvent[i]
			i += 1
		return 0
	
	def getMemberNudgePointsForEvent(self, event):
		i = 0
		for eventType in EVENT_TYPES:
			if event == eventType:
				return self.memberNudgePointsPerEvent[i]
			i += 1
		return 0
	
	def getOfflineMembers(self):
		return Member.all().filter("community = ", self.key()).filter("isOnlineMember = ", False).fetch(FETCH_NUMBER)
	
	# articles
	
	def getNonDraftArticles(self):
		return Article.all().filter("community = ", self.key()).filter("draft = ", False).fetch(FETCH_NUMBER)
	
	def getNonDraftArticlesOfType(self, type):
		return Article.all().filter("community = ", self.key()).filter("draft = ", False).filter("type = ", type).fetch(FETCH_NUMBER)
	
	def getMemberForGoogleAccountId(self, id):
		return Member.all().filter("community = ", self.key()).filter("googleAccountID = ", id).fetch(1)
		
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
	
	# community level questions and answers
	
	def getPendingMembers(self):
		return PendingMember.all().filter("community = ", self.key()).fetch(FETCH_NUMBER)

	def getMemberQuestions(self):
		return Question.all().filter("community = ", self.key()).filter("refersTo = ", "member").fetch(FETCH_NUMBER)
	
	def getQuestions(self):
		return Question.all().filter("community = ", self.key()).fetch(FETCH_NUMBER)
	
	def getQuestionsOfType(self, type):
		return Question.all().filter("community = ", self.key()).filter("refersTo = ", type).fetch(FETCH_NUMBER)
		
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
	
	def memberIsOnlyOwner(self, member):
		owners = self.getOwners()
		if len(owners) == 1 and owners[0].key() == member.key():
			return True
		return False

	def getCommunityLevelViewingPreferences(self):
		return ViewingPreferences.all().filter("community = ", self.key()).filter("owner = ", self.key()).fetch(FETCH_NUMBER)

	def getCharacters(self):
		return Character.all().filter("community = ", self.key()).fetch(FETCH_NUMBER)
	
	def hasAtLeastOneCharacterEntryAllowed(self, entryTypeIndex):
		return len(self.getCharacters()) > 0 or self.allowCharacter[entryTypeIndex]
	
# --------------------------------------------------------------------------------------------
# Question 
# --------------------------------------------------------------------------------------------

class Question(db.Model):
	""" Questions asked about the community, a member, or an article.
	
	Properties
		community:			The Rakontu community this question belongs to.
							If None, is in a global list communities can copy from. (??)
		refersTo:			What the question is in reference to: an article (story, pattern, collage, invitation, resource), 
							community, or member.
		
		type:				One of boolean, text, ordinal, nominal, value.
		lengthIfText:		How long is allowed for a text answer.
		minIfValue:			Minimum value allowed, if value.
		maxIfValue:			Maximum value allowed, if value.
		responseIfBoolean:	What the checkbox should say if the response is positive.
		options:			Options for display. Not using this field, saving in case of need later.
							Replaced "required" field which I got rid of.
		multiple:			Whether multiple answers are allowed.
		name:				Name to display in viewer or wherever a short handle is needed.
		text:				The actual text question asked. May be much longer.
		choices:			A list of strings with possible answers.
		
		help:				Explanatory text about how to answer the question.
		useHelp:			Appears to manager choosing question. Helps them decide when to use it.
	"""
	community = db.ReferenceProperty(Community, collection_name="questions_to_community")
	refersTo = db.StringProperty(choices=QUESTION_REFERS_TO, required=True)
	
	name = db.StringProperty(required=True, default="No name")
	text = db.StringProperty(required=True, default="No question text yet.")
	type = db.StringProperty(choices=QUESTION_TYPES, default="text")
	lengthIfText = db.IntegerProperty(default=40)
	minIfValue = db.IntegerProperty(default=0)
	maxIfValue = db.IntegerProperty(default=1000)
	responseIfBoolean = db.StringProperty(default="Yes")
	options = db.StringProperty(default="")
	multiple = db.BooleanProperty(default=False)
	choices = db.StringListProperty(default=["", "", "", "", "", "", "", "", "", ""])
	
	help = db.TextProperty()
	help_formatted = db.TextProperty()
	help_format = db.StringProperty(default="plain text")
	useHelp = db.TextProperty()
	useHelp_formatted = db.TextProperty()
	useHelp_format = db.StringProperty(default="plain text")
	
	created = TzDateTimeProperty(auto_now_add=True)
	
	def isOrdinalOrNominal(self):
		return self.type == "ordinal" or self.type == "nominal"
		
# --------------------------------------------------------------------------------------------
# Member
# --------------------------------------------------------------------------------------------

class Member(db.Model):
	""" A member is essentially the combination of a Google user and a Rakontu community,
		since a Google user can belong to more than one Rakontu community.
		Though members can also exist without Google accounts (those are off-line members).
	
	Properties
		community:			The community this member belongs to. 
		nickname:			The member's "handle" in the system. 
		googleAccountID:	UserID field from Google account. None if offline.
		googleAccountEmail:	The email with which the account was created. For display only.
		isOnlineMember:		Whether the member is online (has a Google account).
							Note that offline members cannot have helping roles or be managers or owners.
		active:				Flag set to false when members quit; so they can be reinstated easier.
		acceptsMessages:	Other members can send them messages, and they come through their email address.
		liaisonAccountID:	Can be permanently linked to a liaison. This is to help
							liaisons manage the offline members they have responsibility for.
							
		governanceType:		Whether they are a member, manager or owner.
		governanceView:		What views (of GOVERNANCE_VIEWS) the member wants to see if they 
							are a manager or owner.
		helpingRoles:		Helping roles the member has chosen (curator, guide, liaison).
		helpingRolesAvailable:	A manager/owner can ban a member from taking on these roles in future
							(this is for if people abuse them).
		guideIntro:			An introduction to be shown if the person is a guide
							about what sorts of questions they can best answer.
		
		nicknameIsRealName:	Whether their nickname is their real name. For display only.
		profileText:		Small amount of member-submitted info about themselves.
							Can include URLs which are converted to links.
		profileImage:		Thumbnail picture. Optional.
		
		lastEnteredArticle:	These "last" dates are for quickly showing activity.
		lastEnteredAnnotation: 	These "last" dates are for quickly showing activity.
		lastAnsweredQuestion:	These "last" dates are for quickly showing activity.
		lastReadAnything:	These "last" dates are for quickly showing activity.
		nudgePoints: 		Points accumulated by activity. Used for nudging articles.

	"""
	community = db.ReferenceProperty(Community, required=True, collection_name="members_to_community")
	nickname = db.StringProperty(default=NO_NICKNAME_SET)
	googleAccountID = db.StringProperty(required=True)
	googleAccountEmail = db.StringProperty(required=True)
	isOnlineMember = db.BooleanProperty(default=True)
	active = db.BooleanProperty(default=True)
	acceptsMessages = db.BooleanProperty(default=True)
	liaisonAccountID = db.StringProperty(default=None)
	
	timeZoneName = db.StringProperty()
	timeFormat = db.StringProperty()
	dateFormat = db.StringProperty()
	
	governanceType = db.StringProperty(choices=GOVERNANCE_ROLE_TYPES, default="member")
	governanceView = db.StringListProperty(default=None)
	helpingRoles = db.ListProperty(bool, default=[False, False, False])
	helpingRolesAvailable = db.ListProperty(bool, default=[True, True, True])
	guideIntro = db.TextProperty(default="")
	guideIntro_formatted = db.TextProperty()
	guideIntro_format = db.StringProperty(default="plain text")
	
	nicknameIsRealName = db.BooleanProperty(default=False)
	profileText = db.TextProperty(default="No profile information.")
	profileText_formatted = db.TextProperty()
	profileText_format = db.StringProperty(default="plain text")
	profileImage = db.BlobProperty(default=None)
	
	joined = TzDateTimeProperty(auto_now_add=True)
	lastEnteredArticle = db.DateTimeProperty()
	lastEnteredAnnotation = db.DateTimeProperty()
	lastEnteredLink = db.DateTimeProperty()
	lastAnsweredQuestion = db.DateTimeProperty()
	lastReadAnything = db.DateTimeProperty()
	nudgePoints = db.IntegerProperty(default=50)
	
	viewTimeEnd = TzDateTimeProperty(auto_now_add=True)
	viewTimeFrameInSeconds = db.IntegerProperty(default=3600)
	viewNumTimeFrames = db.IntegerProperty(default=1)
	viewNumTimeColumns = db.IntegerProperty(default=10)
	
	def initialize(self):
		self.timeZoneName = self.community.defaultTimeZoneName
		self.timeFormat = self.community.defaultTimeFormat
		self.dateFormat = self.community.defaultDateFormat
	
	def getViewingPreferences(self):
		return ViewingPreferences.all().filter("owner = ", self.key()).fetch(FETCH_NUMBER)
	
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
	
	def googleUserEmailOrNotOnline(self):
		if self.isOnlineMember:
			return self.googleAccountEmail
		return "Offline member"
	
	def isCurator(self):
		return self.helpingRoles[0]
	
	def isGuide(self):
		return self.helpingRoles[1]
	
	def isLiaison(self):
		return self.helpingRoles[2]
	
	def hasAnyHelpingRole(self):
		return self.helpingRoles[0] or self.helpingRoles[1] or self.helpingRoles[2]

	def canTakeOnAnyHelpingRole(self):
		return self.helpingRolesAvailable[0] or self.helpingRolesAvailable[1] or self.helpingRolesAvailable[2]
	
	def setGovernanceType(self, type):
		self.governanceType = type
		
	def isRegularMember(self):
		return self.governanceType == "member"
	
	def checkedIfRegularMember(self):
		if self.isRegularMember():
			return "checked"
		return ""
	
	def isManager(self):
		return self.governanceType == "manager"
	
	def isManagerOrOwner(self):
		return self.governanceType == "manager" or self.governanceType == "owner"
	
	def checkedIfManager(self):
		if self.isManager():
			return "checked"
		return ""
	
	def isOwner(self):
		return self.governanceType == "owner"
	
	def checkedIfOwner(self):
		if self.isOwner():
			return "checked"
		return ""
	
	def getAnswers(self):
		return Answer.all().filter("referent = ", self.key()).fetch(FETCH_NUMBER)
	
	def getNonDraftArticlesAttributedToMember(self):
		return Article.all().filter("creator = ", self.key()).filter("draft = ", False).filter("character = ", None).fetch(FETCH_NUMBER)
	
	def getDraftArticles(self):
		return Article.all().filter("creator = ", self.key()).filter("draft = ", True).fetch(FETCH_NUMBER)
	
	def getNonDraftAnnotationsAttributedToMember(self):
		return Annotation.all().filter("creator = ", self.key()).filter("draft = ", False).filter("character = ", None).fetch(FETCH_NUMBER)
	
	def getDraftAnswersForArticle(self, article):
		return Answer.all().filter("creator = ", self.key()).filter("draft = ", True).filter("referent = ", article.key()).fetch(FETCH_NUMBER)
	
	def getNonDraftAnswersAboutArticlesAttributedToMember(self):
		return Answer.all().filter("creator = ", self.key()).filter("draft = ", False).filter("character = ", None).filter("referentType = ", "article").fetch(FETCH_NUMBER)
	
	def getDraftAnnotations(self):
		return Annotation.all().filter("creator = ", self.key()).filter("draft = ", True).fetch(FETCH_NUMBER)
	
	def getArticlesWithDraftAnswers(self):
		answers = Answer.all().filter("creator = ", self.key()).filter("draft = ", True).filter("referentType = ", "article").fetch(FETCH_NUMBER)
		articles = {}
		for answer in answers:
			if not articles.has_key(answer.referent):
				articles[answer.referent] = 1
		return articles.keys()
	
class PendingMember(db.Model):
	""" A person who has been invited to join a community but who has not yet logged in.
		
	Properties
		community:			Which community they have been invited to join.
		email:				An email address related to a Google account.
		invited:			When invited.
	"""
	community = db.ReferenceProperty(Community, required=True, collection_name="pending_members_to_community")
	email = db.StringProperty(required=True)
	invited = TzDateTimeProperty(auto_now_add=True)
	
class Character(db.Model):
	""" Used to anonymize entries but provide some information about intent. Optional.
	
	Properties
		community:			The Rakontu community this character belongs to.
		name:				The fictional name of the character, like "Coyote".
		description:		Simple text description of the character.
		etiquetteStatement:	Just some guidelines for when the person is taking on the character.
							How not to behave.
		image:				Optional image.
	"""
	community = db.ReferenceProperty(Community, required=True, collection_name="characters_to_community")
	name = db.StringProperty(required=True)
	description = db.TextProperty(default="")
	description_formatted = db.TextProperty()
	description_format = db.StringProperty(default="plain text")
	etiquetteStatement = db.TextProperty(default="")
	etiquetteStatement_formatted = db.TextProperty()
	etiquetteStatement_format = db.StringProperty(default="plain text")
	image = db.BlobProperty(default=None)
	
# --------------------------------------------------------------------------------------------
# Answer
# --------------------------------------------------------------------------------------------

class Answer(db.Model):
	""" Answer to question. 
	
	Properties
		question: 			Refers to annotation question, for display.
		referent:			Whatever the answer refers to.
		referentType:		Whether the answer refers to an article or member.
		creator:			Who answered the question.
		
		answerIfBoolean:	True or false. Only used if question type is boolean.
		answerIfText:		String. Only used if question type is text.
		answerIfMultiple:	List of strings. Only used if question type is ordinal or nominal and multiple flag is set.
		answerIfValue:		Integer. Only used if question type is value.
							(Note we are leaving float values out.)
		
		created: 			When object was created.
		edited: 			When last changed.
		published:			When published (if).
		draft:				Whether this is a draft or published entry.
	"""
	question = db.ReferenceProperty(Question, collection_name="answers_to_questions")
	referent = db.ReferenceProperty(None, collection_name="answers_to_objects")
	referentType = db.StringProperty(default="article")
	creator = db.ReferenceProperty(Member, collection_name="answers_to_creators")
	community = db.ReferenceProperty(Community, collection_name="answers_to_community")
	
	collectedOffline = db.BooleanProperty(default=False)
	liaison = db.ReferenceProperty(Member, default=None, collection_name="answers_to_liaisons")
	character = db.ReferenceProperty(Character, default=None)
	
	answerIfBoolean = db.BooleanProperty(default=False)
	answerIfText = db.StringProperty(default="")
	answerIfMultiple = db.StringListProperty(default=["", "", "", "", "", "", "", "", "", ""])
	answerIfValue = db.IntegerProperty(default=0)
	
	created = TzDateTimeProperty(auto_now_add=True)
	edited = TzDateTimeProperty(auto_now_add=True)
	published = TzDateTimeProperty(auto_now_add=True)
	draft = db.BooleanProperty(default=True)
	articleNudgePointsWhenPublished = db.ListProperty(int, default=[0,0,0,0,0])
	articleActivityPointsWhenPublished = db.IntegerProperty(default=0)
	
	def questionKey(self):
		return self.question.key()
	
	def attributedToMember(self):
		return self.character == None
	
	def memberNickNameOrCharacterName(self):
		if self.character:
			return self.character.name
		else:
			return self.creator.nickname
		
	def publish(self):
		if self.referentType == "article":
			self.draft = False
			self.published = datetime.now(pytz.utc)
			self.put()
			self.referent.recordAction("added", self)
			if self.referentType == "article":
				for i in range(5):
					self.articleNudgePointsWhenPublished[i] = self.referent.nudgePoints[i]
				self.articleActivityPointsWhenPublished = self.referent.activityPoints
				self.put()
			self.creator.nudgePoints += self.community.getMemberNudgePointsForEvent("answering question")
			self.creator.lastAnsweredQuestion = datetime.now(pytz.utc)
			self.creator.put()
			self.community.lastPublish = self.published
			self.community.put()
				
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
		
# --------------------------------------------------------------------------------------------
# Article
# --------------------------------------------------------------------------------------------

class Article(db.Model):
	""" Main element of the system. 
	
	Properties
		title:				A name for the article. Appears in the interface.
		text:				Main body of content. What is read. 
		type:				Whether it is a story, pattern, collage, invitation or resource.

		creator: 			Member who contributed the story. May be online or offline.
		community:			The Rakontu community this article belongs to.
		collectedOffline:	Whether it was contributed by an offline member.
		liaison:			Person who entered the article for off-line member. None if not offline.
		character: 	Reference to fictional member name (from global list).
		
		instructionsIfPattern:	If this is a pattern, instructions on how to reproduce it.
		screenshotIfPattern:	If this is a pattern, an uploaded picture of it.

		tookPlace:			When the events the article is about took place.
		collected:			When article was collected, usually from an off-line member.
		created:			When article was added to database.
		edited:				When the text or title was last changed.
		published:			When the article was published.
		draft:				Whether this is a draft or published entry.
		
		lastRead:			When it was last accessed by anyone.
	"""
	title = db.StringProperty(required=True)
	text = db.TextProperty(default="No text")
	text_formatted = db.TextProperty()
	text_format = db.StringProperty(default="plain text")
	type = db.StringProperty(choices=ARTICLE_TYPES, required=True)

	creator = db.ReferenceProperty(Member, collection_name="articles")
	community = db.ReferenceProperty(Community, required=True, collection_name="articles_to_community")
	collectedOffline = db.BooleanProperty(default=False)
	liaison = db.ReferenceProperty(Member, default=None, collection_name="articles_to_liaisons")
	character = db.ReferenceProperty(Character, default=None)
	
	tookPlace = TzDateTimeProperty(auto_now_add=True)
	collected = TzDateTimeProperty(default=None)
	created = TzDateTimeProperty(auto_now_add=True)
	edited = TzDateTimeProperty(auto_now_add=True)
	published = TzDateTimeProperty(auto_now_add=True)
	draft = db.BooleanProperty(default=True)
	
	lastRead = TzDateTimeProperty(default=None)
	lastDowndrifted = TzDateTimeProperty(default=None)
	lastAnnotatedOrAnsweredOrLinked = TzDateTimeProperty(default=None)
	activityPoints = db.IntegerProperty(default=0)
	nudgePoints = db.ListProperty(int, default=[0,0,0,0,0])
	
	def getPublishDateForMember(self, member):
		if member:
			localTime = self.published.astimezone(timezone(member.timeZoneName))
			return localTime.strftime(str(member.timeFormat))
		else:
			return self.published
	
	def nudgePointsCombined(self):
		return self.nudgePoints[0] + self.nudgePoints[1] + self.nudgePoints[2] + self.nudgePoints[3] + self.nudgePoints[4]
	
	def attributedToMember(self):
		return self.character == None
	
	def isStory(self):
		return self.type == "story"
	
	def isResource(self):
		return self.type == "resource"
	
	def isInvitation(self):
		return self.type == "invitation"
	
	def isPatternOrCollage(self):
		return self.type == "pattern" or self.type == "collage"
	
	def isCollage(self):
		return self.type == "collage"
	
	def getAttachments(self):
		return Attachment.all().filter("article =", self.key()).fetch(FETCH_NUMBER)
	
	def getAnswers(self):
		return Answer.all().filter("referent = ", self.key()).fetch(FETCH_NUMBER)
	
	def getNonDraftAnswers(self):
		return Answer.all().filter("referent = ", self.key()).filter("draft = ", False).fetch(FETCH_NUMBER)

	def getNonDraftAnnotationsOfType(self, type):
		return Annotation.all().filter("article =", self.key()).filter("type = ", type).filter("draft = ", False).fetch(FETCH_NUMBER)
	
	def getNonDraftAnnotations(self):
		return Annotation.all().filter("article =", self.key()).filter("draft = ", False).fetch(FETCH_NUMBER)
	
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
	
	def getImageLinkForType(self):
		if self.type == "story":
			imageText = '<img src="/images/story.png" alt="story" border="0">'
		elif self.type == "pattern":
			imageText = '<img src="/images/pattern.png" alt="pattern" border="0">'
		elif self.type == "collage":
			imageText = '<img src="/images/collage.png" alt="collage" border="0">'
		elif self.type == "invitation":
			imageText = '<img src="/images/invitation.png" alt="invitation" border="0">'
		elif self.type == "resource":
			imageText = '<img src="/images/resource.png" alt="resource" border="0">'
		return imageText
	
	def getAnswersForMember(self, member):
		return Answer.all().filter("referent = ", self.key()).filter("creator = ", member.key()).fetch(FETCH_NUMBER)
	
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

	def recordAction(self, action, referent):
		if referent.__class__.__name__ == "Article":
			if action == "read":
				eventType = "reading"
				self.lastRead = datetime.now(tz=pytz.utc)
			elif action == "downdrift":
				eventType = "time (downdrift)"
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
		
	def getCurrentTotalNudgePointsInAllCategories(self):
		result = [0,0,0,0,0]
		for nudge in self.getNonDraftAnnotationsOfType("nudge"):
			i = 0
			for value in nudge.valuesIfNudge:
				result[i] += value
				i += 1
		return result
	
	def attributedToMember(self):
		return self.character == None
	
	def memberNickNameOrCharacterName(self):
		if self.character:
			return self.character.name
		else: 
			return self.creator.nickname

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
		
	def shortFormattedText(self):
		if len(self.text_formatted) > 100:
			return "%s ..." % self.text_formatted[:98]
		else:
			return self.text_formatted

class Link(db.Model):
	""" For holding on to links between articles.
	
	Properties
		articleFrom:		Where the link originated. Story read first, or pattern/collage.
		articleTo:			Article referred to. Usually story.
		creator: 			Member who created the link. May be online or offline.
		type:				One of retold, reminded, related, included.
		comment:			Optional user comment about the linkage, written when link made.
		published:			When created/published (no draft links).
	"""
	articleFrom = db.ReferenceProperty(Article, collection_name="linksFrom", required=True)
	articleTo = db.ReferenceProperty(Article, collection_name="linksTo", required=True)
	creator = db.ReferenceProperty(Member, collection_name="links")
	published = TzDateTimeProperty(auto_now_add=True)
	type = db.StringProperty(choices=LINK_TYPES, required=True)
	comment = db.StringProperty(default="")
	articleNudgePointsWhenPublished = db.ListProperty(int, default=[0,0,0,0,0])
	articleActivityPointsWhenPublished = db.IntegerProperty(default=0)
	
	def publish(self):
		self.published = datetime.now(pytz.utc)
		self.put()
		self.articleFrom.recordAction("added", self)
		self.articleTo.recordAction("added", self)
		for i in range(5):
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
		
	def attributedToMember(self):
		return True
		
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
		
class Attachment(db.Model):
	""" For binary attachments to articles.
	
	Properties:
		name:				Name of the attachment.
		mimeType:			Determines how it is shown/downloaded.
		fileName:			The name of the file that was uploaded.
		data:				Binary data.
		article:			Which article it is associated with. (Only one allowed.)
	"""
	name = db.StringProperty()
	mimeType = db.StringProperty()
	fileName = db.StringProperty()
	data = db.BlobProperty()
	article = db.ReferenceProperty(Article, collection_name="attachments")
	
# --------------------------------------------------------------------------------------------
# Annotations
# --------------------------------------------------------------------------------------------

class Annotation(db.Model):
	""" Additions to articles.
	
	Properties
		article:			The thing being annotated.
		creator: 			Member who contributed the story. May be online or offline.
		community:			The Rakontu community this annotation belongs to.
							Maybe not necessary, but if you wanted to get a list of these without going through
							articles, this would be useful.
		type:				One of tag, comment, request or nudge.
		
		shortString:		A short string, usually used as a title
		longString:			A text property, used for the comment or request body.
		tagsIfTagSet:		A set of five tags, any or all of which might be blank.
		valuesIfNudge:		The number of nudge points (+ or -) this adds to the article.
							One value per category (up to 5).

		collectedOffline:	Whether it was contributed by an offline member.
		liaison:			Person who entered the article for off-line member. None if not offline.
		character: 	Reference to fictional member name (from global list).

		collected:			When article was collected, usually from an off-line member.
		created:			When article was added to database.
		edited:				When the text or title was last changed.
		published:			When the annotation was published.
		draft:				Whether this is a draft or published entry.
		
		inappropriateMarks:	A list of user comments marking the annotation as inappropriate.
	"""
	article = db.ReferenceProperty(Article, required=True, collection_name="annotations")
	creator = db.ReferenceProperty(Member, collection_name="annotations")
	community = db.ReferenceProperty(Community, required=True, collection_name="annotations_to_community")
	type = db.StringProperty(choices=ANNOTATION_TYPES, required=True)
	
	shortString = db.StringProperty()
	longString = db.TextProperty()
	longString_formatted = db.TextProperty()
	longString_format = db.StringProperty(default="plain text")
	tagsIfTagSet = db.StringListProperty(default=["", "", "", "", ""])
	valuesIfNudge = db.ListProperty(int, default=[0,0,0,0,0])

	collectedOffline = db.BooleanProperty(default=False)
	liaison = db.ReferenceProperty(Member, default=None, collection_name="annotations_liaisoned")
	character = db.ReferenceProperty(Character, default=None)

	collected = TzDateTimeProperty(default=None)
	created = TzDateTimeProperty(auto_now_add=True)
	edited = TzDateTimeProperty(auto_now_add=True)
	published = TzDateTimeProperty(auto_now_add=True)
	draft = db.BooleanProperty(default=True)
	articleNudgePointsWhenPublished = db.ListProperty(int, default=[0,0,0,0,0])
	articleActivityPointsWhenPublished = db.IntegerProperty(default=0)
	
	def isComment(self):
		return self.type == "comment"
	
	def isRequest(self):
		return self.type == "request"
	
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
	
	def attributedToMember(self):
		return self.character == None
	
	def memberNickNameOrCharacterName(self):
		if self.character:
			return self.character.name
		else:
			return self.creator.nickname
		
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
			for i in range(5):
				if self.valuesIfNudge[i] != 0:
					result.append("%s: %s" % (self.community.nudgeCategories[i], self.valuesIfNudge[i]))
			if self.shortString:
				result.append("(%s)" % self.shortString)
			return ", ".join(result)
	
	def linkString(self):
		if self.type == "comment" or self.type == "request":
			if self.longString_formatted and len(self.longString_formatted) > 30:
				return '<a href="readAnnotation?%s">%s</a>' % (self.key(), self.displayString())
			elif self.longString_formatted:
				return "%s: %s" % (self.shortString, self.longString_formatted)
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
	
	def publish(self):
		self.draft = False
		self.published = datetime.now(pytz.utc)
		self.put()
		self.article.recordAction("added", self)
		for i in range(5):
			self.articleNudgePointsWhenPublished[i] = self.article.nudgePoints[i]
		self.articleActivityPointsWhenPublished = self.article.activityPoints
		self.put()
		self.creator.nudgePoints += self.community.getMemberNudgePointsForEvent("adding %s" % self.type)
		self.creator.put()
		self.community.lastPublish = self.published
		self.community.put()
				
class InappropriateFlag(db.Model):
	""" Flags that say anything is inappropriate and should be removed.
		Can only be added by curators, managers or owners. 
		Items can only be removed by managers, owners, or their creators.
	
	Properties
		referent:			What object is recommended for removal: article, annotation or answer.
		creator:			Who recommended removing the object.
		comment:			An optional comment on why removal is recommended.
		entered:			When the flag was created.
	"""
	referent = db.ReferenceProperty(None, required=True)
	creator = db.ReferenceProperty(Member, collection_name="flags")
	comment = db.StringProperty(default="")
	entered = TzDateTimeProperty(auto_now_add=True)
	
class Help(db.Model):
	name = db.StringProperty()
	type = db.StringProperty()
	text = db.StringProperty()
	
	