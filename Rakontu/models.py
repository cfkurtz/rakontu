# --------------------------------------------------------------------------------------------
# RAKONTU
# Description: Rakontu is open source story sharing software.
# Version: pre-0.1
# License: GPL 3.0
# Google Code Project: http://code.google.com/p/rakontu/
# --------------------------------------------------------------------------------------------

import datetime
import logging

from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.api import users
from google.appengine.ext.db import polymodel

# --------------------------------------------------------------------------------------------
# Utility functions
# --------------------------------------------------------------------------------------------
        
def DebugPrint(text, msg="print"):
    logging.debug(">>>>>>>> %s >>>>>>>> %s" %(msg, text))
    
def checkedBlank(value):
    if value:
        return "checked"
    return ""

# --------------------------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------------------------

FETCH_NUMBER = 1000

# community
DEFAULT_MAX_NUDGE_POINTS_PER_ARTICLE = 10
DEFAULT_NUDGE_POINT_ACCUMULATIONS = [
									0, # time (doesn't apply here)
					 				2, # browsing
					 				4, # reading
					 				20, # telling
					 				30, # retelling
					 				25, # reminding
					 				10, # relating
					 				15, # including
					 				0, # annotating (subclasses)
					 				20, # answering questios
					 				4, # tagging
					 				5, # commenting
					 				8, # requesting
					 				0, # nudging (subclasses)
					 				8, # nudging - appropriateness
					 				8, # nudging - importance
					 				8, # nudging - utility
					 				8, # nudging - utility custom 1
					 				8, # nudging - utility custom 2
					 				8, # nudging - utility custom 3
					 				]

# member
NO_NICKNAME_SET = "No nickname set"
MEMBER_TYPES = ["member", "on-line member", "off-line member", "liaison", "curator", "guide", "manager", "owner"]
HELPING_ROLE_TYPES = ["curator", "guide", "liaison"]
DEFAULT_ROLE_READMES = [
					    "A curator pays attention to Rakontu's accumulated data. Curators add information, check for problems, create links, and in general maintain the vitality of the story bank.",
					    "A guide pays attention to the Rakontu's on-line human community. Guides answer questions, write tutorials, encourage people to tell and use stories, create patterns, write and respond to requests, set up and run exercises, and in general maintain the vitality of the on-line member community.",
					    "A liaison guides stories and other information over the barrier between on-line and off-line worlds. Liaisons conduct external interviews and add the stories people tell in them, read stories to people and gather comments, nudges, and other annotations, and in general make the system work for both on-line and off-line community members."]
GOVERNANCE_ROLE_TYPES = ["member", "manager", "owner"]
ACTIVITIES_GERUND = ["time", \
					   	 "browsing", "reading", \
						 "telling", "retelling", "reminding", "relating", "including", \
						 "annotating", "answering questions", "tagging", "commenting", "requesting", "nudging", \
						 "nudging - appropriateness", "nudging - importance", "nudging - utility", \
						 "nudging - utility custom 1", "nudging - utility custom 2", "nudging - utility custom 3"]
ACTIVITIES_VERB = ["time", \
					   	 "browsed", "read", \
						 "told", "retold", "reminded", "related", "included", \
						 "annotated", "questions answered about", "tagged", "commented", "requested", "nudged", \
						 "nudged - appropriateness", "nudged - importance", "nudged - utility", \
						 "nudged - utility custom 1", "nudged - utility custom 2", "nudged - utility custom 3"]

# articles
ARTICLE_TYPES = ["story", "pattern", "construct", "invitation", "resource"]
ATTRIBUTION_CHOICES = ["member", "anonymous", "personification"]
LINK_TYPES = ["retold", "reminded", "related", "included"]
ACCEPTED_ATTACHMENT_FILE_TYPES = ["jpg", "png", "pdf", "doc", "txt", "mpg", "mp3", "html", "zip"]
ACCEPTED_ATTACHMENT_MIME_TYPES = ["image/jpeg", "image/png", "application/pdf", "application/msword", "text/plain", "video/mpeg", "audio/mpeg", "text/html", "application/zip"]

# annotations
ANNOTATION_TYPES = ["tag set", "comment", "request", "nudge"]
ANNOTATION_TYPES_URLS = ["tagset", "comment", "request", "nudge"]
REQUEST_TYPES = ["edit text", "clean up audio/video", "add comments", "nudge", "add tags", "translate", "transcribe", "read aloud", "contact me", "other"]
NUDGE_TYPES = ["appropriateness", "importance", "utility", "utility custom 1", "utility custom 2", "utility custom 3"]
ENTRY_TYPES = ["story", "pattern", "construct", "invitation", "resource", "answer", "tag", "comment", "request", "nudge"]
STORY_ENTRY_TYPE_INDEX = 0
ANSWERS_ENTRY_TYPE_INDEX = 5
PRUNE_STRENGTH_NAMES = ["weak", "medium", "strong"]
PRUNE_STRENGTHS = [1, 2, 3]

# browsing
TIME_STEPS = ["hour", "day", "week", "month", "year"]
DEFAULT_VERTICAL_MOVEMENT_POINTS_PER_EVENT = [
									-1, # time
					 				2, # browsing
					 				5, # reading
					 				0, # telling  (doesn't apply here)
					 				0, # retelling (doesn't really apply here)
					 				0, # reminding (doesn't really apply here)
					 				0, # relating (doesn't really apply here)
					 				0, # including (doesn't really apply here)
					 				0, # annotating (subclasses)
					 				20, # answering questions
					 				10, # tagging
					 				10, # commenting
					 				20, # requesting
					 				0, # nudging (subclasses)
					 				15, # nudging - appropriateness
					 				10, # nudging - importance
					 				8, # nudging - utility
					 				8, # nudging - utility custom 1
					 				8, # nudging - utility custom 2
					 				8, # nudging - utility custom 3
					 				]

# querying
QUERY_TYPES = ["free text", "tags", "answers", "members", "activities", "links"]
QUERY_TARGETS = ["stories", "patterns", "constructs", "invitations", "resources", "articles", "answers", "tags", "comments", "requests", "nudge comments"]
BOOLEAN_CHOICES = ["ALL", "ANY"]
RECENT_TIME_FRAMES = ["last hour", "last day", "last week", "last month", "last six months", "last year", "ever"]

# questions 
QUESTION_REFERS_TO = ["story", "pattern", "construct", "invitation", "resource", "member"]
QUESTION_REFERS_TO_PLURAL = ["stories", "patterns", "constructs", "invitations", "resources", "members"]
QUESTION_TYPES = ["boolean", "text", "ordinal", "nominal", "value"]

# --------------------------------------------------------------------------------------------
# Community
# --------------------------------------------------------------------------------------------

class Community(db.Model):
	""" Preferences and settings for the whole community.
	    There can be multiple communities within one Rakontu installation.
	
	Properties
		name:					The name that appears on all pages.
		description:			Some text that describes the community. Can contain links. (simple markup?)
		image:					Picture to show on community page.
		
		nudgePointsPerActivity:	A number for each type of activity (ACTIVITIES_GERUND) denoting how many
								points the member accumulates for doing it.
		maxNudgePointsPerArticle:	How many nudge points a member is allowed to place (maximally) on any article.
		allowAnonymousEntry:	Whether members are allowed to enter things with only
								"anonymous" marked. One entry per type of thing (ENTRY_TYPES)
		nudgeCategories:		Names of nudge categories. Up to five allowed.
		roleReadmes:			Texts all role members read before taking on a role.
								One text per helping role type.
		roleAgreements:			Whether the user is asked to click a checkbox before taking on a role
								to show that they agree with the terms of the role. (Social obligation only.)
		autoPrune:				Whether items (article, annotations, answers) marked with a prune flag
								by curators, managers and owners should be pruned automatically
								or shown to managers and owners for removal.
		autoPruneStrength:		What strength level of pruning (and above) will be removed automatically
								(levels below this only show up in a prune flag list seen only
								by managers and owners). Combination of numbers allocated by
								different prune flags. 
		maxNumAttachments:		How many attachments are allowed per article.
								May be useful to keep the database from getting out of hand.
	"""
	name = db.StringProperty()
	description = db.TextProperty()
	image = db.BlobProperty(default=None)
	created = db.DateTimeProperty(auto_now_add=True)
	
	nudgePointsPerActivity = db.ListProperty(int, default=DEFAULT_NUDGE_POINT_ACCUMULATIONS)
	maxNudgePointsPerArticle = db.IntegerProperty(default=DEFAULT_MAX_NUDGE_POINTS_PER_ARTICLE)
	allowAnonymousEntry = db.ListProperty(bool, default=[False,False,False,False,False,False,False,False,False,False])
	nudgeCategories = db.StringListProperty(default=["appropriateness", "importance", "usefulness for new members", "usefulness for resolving conflicts", "usefulness for learning our group's history"])
	roleReadmes = db.StringListProperty(default=DEFAULT_ROLE_READMES)
	roleAgreements = db.ListProperty(bool, default=[False, False, False])
	
	autoPrune = db.BooleanProperty(default=False)
	autoPruneStrength = db.IntegerProperty(default=6)
	maxNumAttachments = db.IntegerProperty(choices=[0,1,2,3,4,5], default=3)
	
	# articles
	
	def getArticles(self):
		return Article.all().filter("community = ", self.key()).fetch(FETCH_NUMBER)
	
	def getStories(self):
		return Story.all().filter("community = ", self.key()).fetch(FETCH_NUMBER)
	
	def getPatterns(self):
		return Pattern.all().filter("community = ", self.key()).fetch(FETCH_NUMBER)
	
	def getConstructs(self):
		return Construct.all().filter("community = ", self.key()).fetch(FETCH_NUMBER)
	
	def getInvitations(self):
		return Invitation.all().filter("community = ", self.key()).fetch(FETCH_NUMBER)
	
	def getResources(self):
		return Resource.all().filter("community = ", self.key()).fetch(FETCH_NUMBER)
	
	def getLinks(self):
		return Link.all().filter("community = ", self.key()).fetch(FETCH_NUMBER)
		
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
	
	def getMembers(self):
		return Member.all().filter("community = ", self.key()).fetch(FETCH_NUMBER)
	
	def hasMemberWithUserID(self, userID):
		members = self.getMembers()
		for member in members:
			if member.googleAccountID == userID:
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

	# options
	
	def getCommunityLevelViewingPreferences(self):
		return ViewingPreferences.all().filter("community = ", self.key()).filter("owner = ", self.key()).fetch(FETCH_NUMBER)

	def getPersonifications(self):
		return Personification.all().filter("community = ", self.key()).fetch(FETCH_NUMBER)
	
	def hasAtLeastOnePersonificationOrAnonEntryAllowed(self, entryTypeIndex):
		return len(self.getPersonifications()) > 0 or self.allowAnonymousEntry[entryTypeIndex]
	
# --------------------------------------------------------------------------------------------
# Question generating system
# --------------------------------------------------------------------------------------------

class Question(db.Model):
	""" Questions asked about the community, a member, or an article.
	
	Properties
		community:			The Rakontu community this question belongs to.
							If None, is in a global list communities can copy from. (??)
		refersTo:			What the question is in reference to: an article (story, pattern, construct, invitation, resource), 
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
	community = db.ReferenceProperty(Community)
	refersTo = db.StringProperty(choices=QUESTION_REFERS_TO, required=True)
	
	name = db.StringProperty(required=True, default="No name")
	text = db.TextProperty(required=True, default="No question text yet.")
	type = db.StringProperty(choices=QUESTION_TYPES, default="text")
	lengthIfText = db.IntegerProperty(default=40)
	minIfValue = db.IntegerProperty(default=0)
	maxIfValue = db.IntegerProperty(default=1000)
	responseIfBoolean = db.StringProperty(default="Yes")
	options = db.StringProperty(default="")
	multiple = db.BooleanProperty(default=False)
	choices = db.StringListProperty(default=["", "", "", "", "", "", "", "", "", ""])
	
	help = db.TextProperty()
	useHelp = db.TextProperty()
	
	created = db.DateTimeProperty(auto_now_add=True)
	
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
		liaisonAccountID:	Can be permanently linked to a liaison. This is to help
							liaisons manage the offline members they have responsibility for.
							
		governanceType:		Whether they are a member, manager or owner.
		governanceView:		What views (of GOVERNANCE_VIEWS) the member wants to see if they 
							are a manager or owner.
		helpingRoles:		Helping roles the member has chosen (curator, guide, liaison).
		helpingRolesAvailable:	A manager/owner can ban a member from taking on these roles in future
							(this is for if people abuse them).
		
		nicknameIsRealName:	Whether their nickname is their real name. For display only.
		profileText:		Small amount of member-submitted info about themselves.
							Can include URLs which are converted to links.
		profileImage:		Thumbnail picture. Optional.
		
		lastEnteredArticle:	These "last" dates are for quickly showing activity.
		lastEnteredAnnotation: 	These "last" dates are for quickly showing activity.
		lastReadAnything:	These "last" dates are for quickly showing activity.
		nudgePoints: 		Points accumulated by activity. Used for nudging articles.

	"""
	community = db.ReferenceProperty(Community, required=True)
	nickname = db.StringProperty(default=NO_NICKNAME_SET)
	googleAccountID = db.StringProperty(required=True)
	googleAccountEmail = db.StringProperty(required=True)
	isOnlineMember = db.BooleanProperty(default=True)
	liaisonAccountID = db.StringProperty(default=None)
	
	governanceType = db.StringProperty(choices=GOVERNANCE_ROLE_TYPES, default="member")
	governanceView = db.StringListProperty(default=None)
	helpingRoles = db.ListProperty(bool, default=[False, False, False])
	helpingRolesAvailable = db.ListProperty(bool, default=[True, True, True])
	
	nicknameIsRealName = db.BooleanProperty(default=False)
	profileText = db.TextProperty(default="No profile information.")
	profileImage = db.BlobProperty(default=None)
	
	joined = db.DateTimeProperty(auto_now_add=True)
	lastEnteredArticle = db.DateTimeProperty()
	lastEnteredAnnotation = db.DateTimeProperty()
	lastReadAnything = db.DateTimeProperty()
	nudgePoints = db.IntegerProperty(default=50)

	def getHistory(self):
		articles = Article.all().filter("creator =", self.key()).order("-date").fetch(FETCH_NUMBER)
		annotations = Annotation.all().filter("creator =", self.key()).order("-date").fetch(FETCH_NUMBER)
		links = Link.all().filter("creator =", self.key()).order("-date").fetch(FETCH_NUMBER)
		return articles, annotations, links
	
	def getViewingPreferences(self):
		return ViewingPreferences.all().filter("owner = ", self.key()).fetch(FETCH_NUMBER)
	
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
	
class PendingMember(db.Model):
	""" A person who has been invited to join a community but who has not yet logged in.
		
	Properties
		community:			Which community they have been invited to join.
		email:				An email address related to a Google account.
		invited:			When invited.
	"""
	community = db.ReferenceProperty(Community, required=True)
	email = db.StringProperty(required=True)
	invited = db.DateTimeProperty(auto_now_add=True)
	
class Personification(db.Model):
	""" Used to anonymize entries but provide some information about intent. Optional.
	
	Properties
		community:			The Rakontu community this personification belongs to.
		name:				The fictional name of the personification, like "Coyote".
		description:		Simple text description of the personification
		image:				Optional image.
	"""
	community = db.ReferenceProperty(Community, required=True)
	name = db.StringProperty(required=True)
	description = db.TextProperty()
	image = db.BlobProperty()
	
# --------------------------------------------------------------------------------------------
# Answer
# --------------------------------------------------------------------------------------------

class Answer(db.Model):
	""" Answer to question. 
	
	Properties
		question: 			Refers to annotation question, for display.
		referent:			Whatever the answer refers to.
		creator:			Who answered the question.
		
		answerIfBoolean:	True or false. Only used if question type is boolean.
		answerIfText:		String. Only used if question type is text.
		answerIfMultiple:	List of strings. Only used if question type is ordinal or nominal and multiple flag is set.
		answerIfValue:		Integer. Only used if question type is value.
							(Note we are leaving float values out.)
		
		entered: 			When entered.
		lastChanged: 		When last changed.
	"""
	question = db.ReferenceProperty(Question, collection_name="answers to questions")
	referent = db.ReferenceProperty(None, collection_name="answers to objects")
	creator = db.ReferenceProperty(Member, collection_name="answers to creators")
	
	collectedOffline = db.BooleanProperty(default=False)
	liaison = db.ReferenceProperty(Member, default=None, collection_name="answers_liaisoned")
	attribution = db.StringProperty(choices=ATTRIBUTION_CHOICES, default="member")
	personification = db.ReferenceProperty(Personification, default=None)
	
	answerIfBoolean = db.BooleanProperty(default=False)
	answerIfText = db.StringProperty(default="")
	answerIfMultiple = db.StringListProperty(default=["", "", "", "", "", "", "", "", "", ""])
	answerIfValue = db.IntegerProperty(default=0)
	
	entered = db.DateTimeProperty(auto_now_add=True)
	lastChanged = db.DateTimeProperty(auto_now_add=True)
	
	def questionKey(self):
		return self.question.key()
	
# --------------------------------------------------------------------------------------------
# Article
# --------------------------------------------------------------------------------------------

class Article(db.Model):
	""" Main element of the system. 
	
	Properties
		title:				A name for the article. Appears in the interface.
		text:				Main body of content. What is read. 
		type:				Whether it is a story, pattern, construct, invitation or resource.

		creator: 			Member who contributed the story. May be online or offline.
		community:			The Rakontu community this article belongs to.
		collectedOffline:	Whether it was contributed by an offline member.
		liaison:			Person who entered the article for off-line member. None if not offline.
		attribution: 		Whether to show the creator's nickname, "anonymous" or a personification.
		personification: 	Reference to fictional member name (from global list).
		
		instructionsIfPattern:	If this is a pattern, instructions on how to reproduce it.
		screenshotIfPattern:	If this is a pattern, an uploaded picture of it.

		tookPlace:			When the events the article is about took place.
		collected:			When article was collected, usually from an off-line member.
		entered:			When article was added to database.
		lastChanged:			When the text or title was last changed.
		lastRead:			When it was last accessed by anyone.
		lastAnnotated:		The last time any annotation was added.
		numBrowses:			The number of times this article appeared in the main browse window.
							(This may be too CPU intensive to store here so it may go away.)
		numReads:			The number of times this article was read.
	"""
	title = db.StringProperty(required=True)
	text = db.TextProperty(default="No text")
	type = db.StringProperty(choices=ARTICLE_TYPES, required=True)

	creator = db.ReferenceProperty(Member, required=True, collection_name="articles")
	community = db.ReferenceProperty(Community, required=True)
	collectedOffline = db.BooleanProperty(default=False)
	liaison = db.ReferenceProperty(Member, default=None, collection_name="articles_liaisoned")
	attribution = db.StringProperty(choices=ATTRIBUTION_CHOICES, default="member")
	personification = db.ReferenceProperty(Personification, default=None)
	
	tookPlace = db.DateTimeProperty(default=None)
	collected = db.DateTimeProperty(default=None)
	entered = db.DateTimeProperty(auto_now_add=True)
	lastChanged = db.DateTimeProperty(default=None)
	lastRead = db.DateTimeProperty(default=None)
	lastAnnotated = db.DateTimeProperty(default=None)
	numBrowses = db.IntegerProperty(default=0)
	numReads = db.IntegerProperty(default=0)
	
	def isInvitation(self):
		return self.type == "invitation"
	
	def isPatternOrConstruct(self):
		return self.type == "pattern" or self.type == "construct"
	
	def getAttachments(self):
		return Attachment.all().filter("article =", self.key()).fetch(FETCH_NUMBER)
	
	def getAnswers(self):
		return Answer.all().filter("referent = ", self.key()).fetch(FETCH_NUMBER)

	def getAnnotationsOfType(self, type):
		return Annotation.all().filter("article =", self.key()).filter("type = ", type).fetch(FETCH_NUMBER)
	
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
	
	def getAnswersForMember(self, member):
		return Answer.all().filter("referent = ", self.key()).filter("creator = ", member.key()).fetch(FETCH_NUMBER)
	
	def getNudgesForMember(self, member):
		return Annotation.all().filter("article = ", self.key()).filter("type = ", "nudge").filter("creator = ", member.key()).fetch(FETCH_NUMBER)
	
class Link(db.Model):
	""" For holding on to links between articles.
	
	Properties
		articleFrom:		Where the link originated. Story read first, or pattern/construct.
		articleTo:			Article referred to. Usually story.
		creator: 			Member who created the link. May be online or offline.
		type:				One of retold, reminded, related, included.
		comment:			Optional user comment about the linkage, written when link made.
	"""
	articleFrom = db.ReferenceProperty(Article, collection_name="linksFrom", required=True)
	articleTo = db.ReferenceProperty(Article, collection_name="linksTo", required=True)
	creator = db.ReferenceProperty(Member, required=True, collection_name="links")
	type = db.StringProperty(choices=LINK_TYPES, required=True)
	comment = db.StringProperty(default="")
	
class Attachment(db.Model):
	""" For binary attachments to articles.
	
	Properties:
		name:		Name of the attachment.
		mimeType:	Determines how it is shown/downloaded.
		fileName:	The name of the file that was uploaded.
		
		data:		Binary data.
		article:	Which artice it is associated with. (Only one allowed.)
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
		typeIfRequest:		Which type of request it is.
		valuesIfNudge:		The number of nudge points (+ or -) this adds to the article.
							One value per category (up to 5).

		collectedOffline:	Whether it was contributed by an offline member.
		liaison:			Person who entered the article for off-line member. None if not offline.
		attribution: 		Whether to show the creator's nickname, "anonymous" or a personification.
		personification: 	Reference to fictional member name (from global list).

		collected:			When article was collected, usually from an off-line member.
		entered:			When article was added to database.
		
		inappropriateMarks:	A list of user comments marking the annotation as inappropriate.
	"""
	article = db.ReferenceProperty(Article, required=True, collection_name="annotations")
	creator = db.ReferenceProperty(Member, required=True, collection_name="annotations")
	community = db.ReferenceProperty(Community, required=True)
	type = db.StringProperty(choices=ANNOTATION_TYPES, required=True)
	
	shortString = db.StringProperty()
	longString = db.TextProperty()
	tagsIfTagSet = db.StringListProperty(default=["", "", "", "", ""])
	typeIfRequest = db.StringProperty(choices=REQUEST_TYPES)
	valuesIfNudge = db.ListProperty(int, default=[0,0,0,0,0])

	collectedOffline = db.BooleanProperty(default=False)
	liaison = db.ReferenceProperty(Member, default=None, collection_name="annotations_liaisoned")
	attribution = db.StringProperty(choices=ATTRIBUTION_CHOICES, default="member")
	personification = db.ReferenceProperty(Personification, default=None)

	collected = db.DateTimeProperty(default=None)
	entered = db.DateTimeProperty(auto_now_add=True)
	
	def totalNudgePointsAbsolute(self):
		result = 0
		for value in self.valuesIfNudge:
			result += abs(value)
		return result

# --------------------------------------------------------------------------------------------
# Pruning
# --------------------------------------------------------------------------------------------

class PruneFlag(db.Model):
	""" Flags that say anything is inappropriate and should be removed.
		Can only be added by curators, managers or owners. 
		Items can only be removed by managers, owners, or their creators.
	
	Properties
		referent:			What object is recommended for pruning: article, annotation or answer.
		creator:			Who recommended pruning the object.
		
		comment:			An optional comment on why pruning is recommended.
		strength:			How strong the pruning recommendation is.
		
		entered:			When the flag was created.
	"""
	referent = db.ReferenceProperty(None, required=True)
	creator = db.ReferenceProperty(Member, required=True, collection_name="prune flags")
	
	comment = db.StringProperty(default="")
	strength = db.StringProperty(choices=PRUNE_STRENGTH_NAMES, default=PRUNE_STRENGTH_NAMES[0])

	entered = db.DateTimeProperty(auto_now_add=True)
	
# --------------------------------------------------------------------------------------------
# Queries
# --------------------------------------------------------------------------------------------

class Query(db.Model):
	""" Choice to show subsets of items in main viewer.

	Properties (common to all types):
		owner:			Who this query belongs to.
		created:			When it was created.

		type:				One of free text, tags, answers, members, activities, links. 
		targets:			All searches return articles, annotations, or members (no combinations). 
	"""
	owner = db.ReferenceProperty(Member, required=True, collection_name="queries")
	created = db.DateTimeProperty(auto_now_add=True)

	type = db.StringProperty(choices=QUERY_TYPES, required=True)
	targets = db.StringListProperty(choices=QUERY_TARGETS, required=True)
	
	""" Free text search
	
	Properties:
		targets:			Articles or annotations, or specific types of either.
		text:				The text to search on. Can include boolean AND, OR, NOT.
	Usage: 
		Show [QUERY_TARGETS] with <text> 
	Examples: 
		Show [comments] with <hate OR love> 
		(with selection) Show [nudges] in the selection with <NOT ""> (meaning, with non-blank nudge comments)
	"""
	text = db.StringProperty()
	
	""" Tag search
	
	Properties:
		targets:			Articles or annotations, or specific types of either. 
		tags:				List of tags to search on. 1-n.
		combination:		Whether to search for all or any of the tags listed.
	Usage:
		Show [QUERY_TARGETS] in which [All, ANY] of <tags> appear 
	Examples: 
		Show [invitations] with [ANY OF] the tags <"need for project", "important">
		(with selection) Show [resources] in the selection with the tag <"planning"> 
	"""
	tags = db.StringListProperty()
	combination = db.StringProperty(choices=BOOLEAN_CHOICES, default="ANY")
	
	""" Answer search
	
	Properties:
		targets:			Articles or annotations, or specific types of either. 
		questionAnswers:	List of strings denoting question and one or more answers.
							Saved together and parsed. 1-n.
		combination:		Whether to search for all or any of the question-answer sets listed.
	Usage:
		Show [QUERY_TARGETS] in which {questions+answers} appear 
	Examples: 
		Show [stories] with [ALL OF] <How do you feel ~ includes ~ happy> and <What was the outcome ~ is ~ bad>
		(with selection) Show [articles] in the selection with <How damaging is this story ~ >= ~ 75>
	"""
	questionAnswers = db.StringListProperty()
	
	""" Member search
	
	Properties:
		memberType:			What sort of member to find. 
		activity:			What the member should have done. 
		timeFrame:			When the member should have done it. 
	Usage:
		Show [MEMBER_TYPES] who have [ACTIVITIES_VERB] in [RECENT_TIME_FRAMES]
	Examples: 
		Show [off-line members] who [commented] in [the last week]
		(with selection) Show [members] who [nudged] the selected story in [the last hour]
	"""
	memberType = db.StringProperty(choices=MEMBER_TYPES)
	activity = db.StringProperty(choices=ACTIVITIES_VERB)
	timeFrame = db.StringProperty(choices=RECENT_TIME_FRAMES)
	
	""" Activity search
	Properties:
		targets:			Articles or annotations, or specific types of either. 
		activity:			What the member should have done. 
		memberIDS:			Who should have done it. 1-n.
		combination:		Whether to search for all or any of the members listed.
		timeFrame:			When the member(s) should have done it. 
	Usage:
		Show [QUERY_TARGETS] in which [ACTIVITIES_VERB] were done by {members} in [RECENT_TIME_FRAMES]
	Examples:
		Show [stories] [retold] by {Joe OR Jim} in [the past 6 months]
		(with selection) Show which of the selected [articles] {I} have [nudged] [ever]
	"""
	memberIDs = db.StringListProperty()
	
	""" Link search
	Properties:
		articleType:		Articles (without annotations). 
		linkType:			Type of link. 
		typeLinkedTo:		What sort of article should have been linked to. 
		memberIDS:			Who should have done it. 1-n.
		timeFrame:			When the member(s) should have done it. 
	Usage:
		Show [ARTICLE_TYPES] {members} connected with [LINK_TYPES] to [ARTICLE_TYPES] in [RECENT_TIME_FRAMES]
	Examples:
		Show [resources] {I} have [related] to [stories] in [the past month]
		(with selection) Show [stories] [included] in the selected pattern by {anyone} [ever]
	"""
	articleType = db.StringProperty(choices=ARTICLE_TYPES)
	linkType = db.StringProperty(choices=LINK_TYPES)
	typeLinkedTo = db.StringProperty(choices=ARTICLE_TYPES)
	
# --------------------------------------------------------------------------------------------
# Preferences
# --------------------------------------------------------------------------------------------

class ViewingPreferences(db.Model):
	""" Preferences for the main viewer. Each user has these, and there is a community-wide set as well for defaulting.
	
	Properties
		owner:				The member these preferences belong to.
		communityIfCommon:	If these are common default options for the community, which community they are for.
		
		xTimeStep:			What time unit to show in grid columns (day, week, month, etc).
		xTimeStepMultiplier:How many days, weeks, etc to show in one column.
		xStart:				What time to show in the first column.
		xStop:				What time to show in the last column.
		
		yPointStep:			How many points in vertical space are covered by one grid row.
		yTop:				What point number to show in the top row.
		yBottom:			What point number to show in the bottom row.
		yArrangement:		How to arrange items on the Y axis. 1-n.
		verticalPoints:		A number for each type of placement denoting how many points (+ or -) an article moves
							each time something happens. For time the unit is one day; all other placements are events.
							
		basement:			A number of points below which articles are not displayed, no matter what yBottom users pick.
							Used mainly at the community level, though users could set a different basement for themselves.
							
		combinedPruneStrengthToHideItems: If items have this many prune flags, they are hidden.
							Used mainly at the community level, though users could set a different level for themselves.
	"""
	owner = db.ReferenceProperty(Member, required=True, collection_name="viewing_preferences")
	communityIfCommon = db.ReferenceProperty(Community, required=True)
	
	xTimeStep = db.StringProperty(choices=TIME_STEPS, default="day")
	xTimeStepMultiplier = db.IntegerProperty(default=1)
	xStart = db.DateTimeProperty(default=datetime.datetime(2009, 5, 1))
	xStop = db.DateTimeProperty(default=datetime.datetime(2009, 6, 1))
	
	yPointStep = db.IntegerProperty(default=10)
	yTop = db.IntegerProperty(default=100)
	yBottom = db.IntegerProperty(default=0)
	yArrangement = db.StringListProperty(choices=ACTIVITIES_GERUND, default=["time", "browsing", "reading", "nudging"])
	verticalPoints = db.ListProperty(int, default=DEFAULT_VERTICAL_MOVEMENT_POINTS_PER_EVENT)
	
	basement = db.IntegerProperty(default=0)
	combinedPruneStrengthToHideItems = db.IntegerProperty(default=5)
	

