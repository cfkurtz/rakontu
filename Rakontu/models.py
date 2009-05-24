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
        
def MyDebug(text, msg="print"):
    logging.debug(">>>>>>>> %s >>>>>>>> %s" %(msg, text))
    
def checkedBlank(value):
    if value:
        return "checked"
    return ""

# --------------------------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------------------------

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
					 				20, # interpreting
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
MEMBER_TYPES = ["member", "on-line member", "off-line member", "liaison", "curator", "booster", "manager", "owner"]
HELPING_ROLE_TYPES = ["curator", "booster", "liaison"]
GOVERNANCE_ROLE_TYPES = ["member", "manager", "owner"]
GOVERNANCE_VIEWS = ["settings", "members", "watch", "technical"]
ACTIVITIES_GERUND = ["time", \
					   	 "browsing", "reading", \
						 "telling", "retelling", "reminding", "relating", "including", \
						 "annotating", "interpreting", "tagging", "commenting", "requesting", "nudging", \
						 "nudging - appropriateness", "nudging - importance", "nudging - utility", \
						 "nudging - utility custom 1", "nudging - utility custom 2", "nudging - utility custom 3"]
ACTIVITIES_VERB = ["time", \
					   	 "browsed", "read", \
						 "told", "retold", "reminded", "related", "included", \
						 "annotated", "interpreted", "tagged", "commented", "requested", "nudged", \
						 "nudged - appropriateness", "nudged - importance", "nudged - utility", \
						 "nudged - utility custom 1", "nudged - utility custom 2", "nudged - utility custom 3"]

# articles
ARTICLE_TYPES = ["story", "pattern", "construct", "invitation", "resource"]
ATTRIBUTION_CHOICES = ["member", "anonymous", "personification"]
LINK_TYPES = ["retold", "reminded", "related", "included"]

# annotations
ANNOTATION_TYPES = ["answer", "tag", "comment", "request", "nudge"]
REQUEST_TYPES = ["edit text", "clean up audio/video", "add comments", "nudge", "add tags", "translate", "transcribe", "read aloud", "contact me"]
NUDGE_TYPES = ["appropriateness", "importance", "utility", "utility custom 1", "utility custom 2", "utility custom 3"]
ENTRY_TYPES = ["story", "pattern", "construct", "invitation", "resource", "answer", "tag", "comment", "request", "nudge"]

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
					 				20, # interpreting
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
QUERY_TARGETS = ["stories", "patterns", "constructs", "invitations", "resources", "articles", "interpretations", "tags", "comments", "requests", "nudge comments"]
BOOLEAN_CHOICES = ["ALL", "ANY"]
RECENT_TIME_FRAMES = ["last hour", "last day", "last week", "last month", "last six months", "last year", "ever"]

# questions and question generating system
QUESTION_REFERS_TO = ["story", "pattern", "construct", "invitation", "resource", "community", "member"]
QUESTION_TYPES = ["boolean", "text", "ordinal", "nominal", "value"]
RULE_TESTS = ["same as", "<", "<=", ">", ">=", "=", "includes"]

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
		utilityNudgeCategories:	Names of custom nudge categories. Up to three allowed.
		roleReadmes:			Texts all role members read before taking on a role.
								One text per helping role type.
		roleAgreements:			Whether the user is asked to click a checkbox before taking on a role
								to show that they agree with the terms of the role. (Social obligation only.)
	"""
	name = db.StringProperty()
	description = db.TextProperty()
	image = db.BlobProperty(default=None)
	
	nudgePointsPerActivity = db.ListProperty(int, default=DEFAULT_NUDGE_POINT_ACCUMULATIONS)
	maxNudgePointsPerArticle = db.IntegerProperty(default=DEFAULT_MAX_NUDGE_POINTS_PER_ARTICLE)
	allowAnonymousEntry = db.ListProperty(bool, default=[False,False,False,False,False,False,False,False,False,False])
	utilityNudgeCategories = db.StringListProperty(default=["", "", "", "", ""])
	roleReadmes = db.StringListProperty(default=["", "", ""])
	roleAgreements = db.ListProperty(bool, default=[False, False, False])
	
	# articles
	
	def getArticles(self):
		return Article.all().filter("community = ", self.key())
	
	def getStories(self):
		return Story.all().filter("community = ", self.key())
	
	def getPatterns(self):
		return Pattern.all().filter("community = ", self.key())
	
	def getConstructs(self):
		return Construct.all().filter("community = ", self.key())
	
	def getInvitations(self):
		return Invitation.all().filter("community = ", self.key())
	
	def getResources(self):
		return Resource.all().filter("community = ", self.key())
	
	def getLinks(self):
		return Link.all().filter("community = ", self.key())
	
	# community level questions and answers

	def getCommunityQuestions(self):
		return Question.all().filter("community = ", self.key()).filter("refersTo = ", "community").fetch(1000)
	
	def getCommunityAnswers(self):
		return Answer.all().filter("referent = ", self.key()).fetch(1000)
	
	def getAnnotationQuestions(self, articleType):
		return Question.all().filter("community = ", self.key()).filter("refersTo = ", articleType).fetch(1000)
		
	def getMemberQuestions(self):
		return Question.all().filter("community = ", self.key()).filter("refersTo = ", "member").fetch(1000)
	
	def getQuestions(self):
		return Question.all().filter("community = ", self.key()).fetch(1000)
	
	def hasQuestionWithSameTypeAndName(self, question):
		allQuestions = self.getQuestions()
		for aQuestion in allQuestions:
			if aQuestion.refersTo == question.refersTo and aQuestion.name == question.name:
				return True
		return False
	
	def AddOrRemoveSystemQuestion(self, question, shouldHaveQuestion):
		haveQuestion = self.hasQuestionWithSameTypeAndName(question)
		if haveQuestion and not shouldHaveQuestion:
			self.RemoveMatchingQuestion(question)
		if not haveQuestion and shouldHaveQuestion:
			self.AddCopyOfQuestion(question)
			
	def RemoveMatchingQuestion(self, question):
		questions = self.getQuestions()
		for aQuestion in questions: 
			if aQuestion.refersTo == question.refersTo and aQuestion.name == question.name:
				db.delete(aQuestion)
				break
			
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
		return Member.all().filter("community = ", self.key()).fetch(1000)
	
	def hasMemberWithUserID(self, userID):
		members = self.getMembers()
		for member in members:
			if member.googleAccountID == userID:
				return True
		return False
	
	def getCurators(self):
		return Member.all().filter("community = ", self.key()).filter("helpingRoles IN ", "curator").fetch(1000)
	
	def getBoosters(self):
		return Member.all().filter("community = ", self.key()).filter("helpingRoles IN ", "booster").fetch(1000)
	
	def getLiaisons(self):
		return Member.all().filter("community = ", self.key()).filter("helpingRoles IN ", "liaison").fetch(1000)
	
	def getManagers(self):
		return Member.all().filter("community = ", self.key()).filter("governanceType = ", "manager").fetch(1000)
	
	def getOwners(self):
		return Member.all().filter("community = ", self.key()).filter("governanceType = ", "owner").fetch(1000)
	
	def memberIsOnlyOwner(self, member):
		owners = self.getOwners()
		if len(owners) == 1 and owners[0].key() == member.key():
			return True
		return False

	# options
	
	def getCommunityLevelViewingPreferences(self):
		return ViewingPreferences.all().filter("community = ", self.key()).filter("owner = ", self.key())

	def getPersonifications(self):
		return Personification.all().filter("community = ", self.key())
	
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
		systemic:			Belongs to the system rather than to any community.
		
		type:				One of boolean, text, ordinal, nominal, value.
		lengthIftext:		How long is allowed for a text answer.
		minIfValue:			Minimum value allowed, if value.
		maxIfValue:			Maximum value allowed, if value.
		required:			Whether an answer is required.
		multiple:			Whether multiple answers are allowed.
		name:				Name to display in viewer or wherever a short handle is needed.
		text:				The actual text question asked. May be much longer.
		choices:			A list of strings with possible answers.
							If the type is value, these are converted to ints.
		
		help:				Explanatory text about how to answer the question.
		useHelp:			Appears to manager choosing question. Helps them decide when to use it.
	"""
	community = db.ReferenceProperty(Community)
	refersTo = db.StringProperty(choices=QUESTION_REFERS_TO, required=True)
	systemic = db.BooleanProperty(default=False)
	
	type = db.StringProperty(choices=QUESTION_TYPES)
	lengthIftext = db.IntegerProperty(default=40)
	minIfValue = db.IntegerProperty(default=0)
	maxIfValue = db.IntegerProperty(default=1000)
	required = db.BooleanProperty(default=False)
	multiple = db.BooleanProperty(default=False)
	name = db.StringProperty(required=True)
	text = db.TextProperty(required=True)
	choices = db.StringListProperty()
	
	help = db.TextProperty()
	useHelp = db.TextProperty()
	
	def isOrdinalOrNominal(self):
		return self.type == "ordinal" or self.type == "nominal"
		
class Answer(db.Model):
	""" Answer to community question with reference to community. 
	
	Properties
		question: 			Refers to annotation question, for display.
		referent:			The community, member, or annotation (answer set) the answer refers to.
		answerTexts:		Text string. If numerical choice, this is converted on use. Can be multiple.
		
		entered: 			When entered.
		lastChanged: 		When last changed.
	"""
	question = db.ReferenceProperty(Question, collection_name="answers referring to questions")
	referent = db.Key
	answerTexts = db.StringListProperty()
	
	entered = db.DateTimeProperty(auto_now_add=True)
	lastChanged = db.DateTimeProperty()
	
class Rule(db.Model):
	""" Simple if-then statement to choose annotation questions based on community questions.
	
	Properties
		community:			The Rakontu community this rule belongs to.
							If None, is in a global list communities can copy from.
		communityQuestion:	What question about the community the rule is based on.
		annotationQuestion: What question about articles is affected by the rule.
		memberQuestion: 	What question about members is affected by the rule.
							The same rule can affect both annotation and member questions.

		test:				The operation used to compare the community answer to the test value.
		testValues:			The thing(s) compared to the community answer.
		includeIf:			Whether the test should be true or false to include the annotation question. 

	Usage
		In the abstract:
			For the community question <communityQuestion>, 
			IF the evaluation of (<Answer> <test> <testValues>) = includeIf, 
			THEN include <annotationOrMemberQuestion>.
		Examples:
			For the community question "Is this community united by a geographic place?",
		  	IF the evaluation of (<Answer> "=" ["yes"]) = true, 
		  	THEN include "Where do you live?" in member questions.
		  	
		  	For the community question "Do people want to talk about social issues?",
		  	IF the evaluation of (<Answer> "includes" ["no!", "maybe not", "not sure"] = false,
		  	THEN include "Who needs to hear this story?" in annotation questions.
	"""
	community = db.ReferenceProperty(Community)
	communityQuestion = db.ReferenceProperty(Question, collection_name="rules pointing to community questions")
	annotationQuestion = db.ReferenceProperty(Question, collection_name="rules pointing to annotation questions")
	memberQuestion = db.ReferenceProperty(Question, collection_name="rules pointing to member questions")

	test = db.StringProperty(choices=RULE_TESTS)
	testValues = db.StringListProperty()
	includeIf = db.BooleanProperty(default=True)
	
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
		googleUser:			User object from Google account. None if offline.
		googleAccountID:	UserID field from Google account. None if offline.
		isOnlineMember:		Whether the member is online (has a Google account).
							Note that offline members cannot have helping roles or be managers or owners.
		liaisonAccountID:	Can be permanently linked to a liaison. This is to help
							liaisons manage the offline members they have responsibility for.
							
		governanceType:		Whether they are a member, manager or owner.
		governanceView:		What views (of GOVERNANCE_VIEWS) the member wants to see if they 
							are a manager or owner.
		roles:				Helping roles the member has chosen (curator, booster, liaison).
		
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
	googleUser = db.UserProperty(auto_current_user=True)
	googleAccountID = db.StringProperty(required=True)
	isOnlineMember = db.BooleanProperty(default=True)
	liaisonAccountID = db.StringProperty(default=None)
	
	governanceType = db.StringProperty(choices=GOVERNANCE_ROLE_TYPES, default="member")
	governanceView = db.StringListProperty(default=None)
	helpingRoles = db.StringListProperty(default=["", "", ""])
	
	nicknameIsRealName = db.BooleanProperty(default=False)
	profileText = db.TextProperty(default="No profile information.")
	profileImage = db.BlobProperty(default=None)
	
	joined = db.DateTimeProperty(auto_now_add=True)
	lastEnteredArticle = db.DateTimeProperty()
	lastEnteredAnnotation = db.DateTimeProperty()
	lastReadAnything = db.DateTimeProperty()
	nudgePoints = db.IntegerProperty(default=0)

	def getHistory(self):
		articles = Article.all().filter("creator =", self.key()).order("-date").fetch(1000)
		annotations = Annotation.all().filter("creator =", self.key()).order("-date").fetch(1000)
		links = Link.all().filter("creator =", self.key()).order("-date").fetch(1000)
		return articles, annotations, links
	
	def getViewingPreferences(self):
		return ViewingPreferences.all().filter("owner = ", self.key()).fetch(1000)
	
	def googleUserNicknameOrNotOnline(self):
		if self.isOnlineMember:
			return self.googleUser.nickname()
		return "Offline member"
	
	def googleUserEmailOrNotOnline(self):
		if self.isOnlineMember:
			return self.googleUser.nickname()
		return "Offline member"
	
	def isCurator(self):
		return "curator" in self.roles
	
	def isBooster(self):
		return "booster" in self.roles
	
	def isLiaison(self):
		return "liaison" in self.roles
	
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
		return Answer.all().filter("referent = ", self.key())
	
class TempUser(db.Model):
	user = db.UserProperty(required=True)
	
# --------------------------------------------------------------------------------------------
# Personification
# --------------------------------------------------------------------------------------------

class Personification(db.Model):
	""" Used to anonymize entries but provide some information about intent. Optional.
	
	Properties
		community:			The Rakontu community this personification belongs to.
		name:				The fictional name of the personification, like "Coyote".
		description:		Simple text description of the personification
		image:				Optional image.
	"""
	community = db.ReferenceProperty(Community)
	name = db.StringProperty(required=True)
	description = db.TextProperty()
	image = db.BlobProperty()
	
# --------------------------------------------------------------------------------------------
# Article
# --------------------------------------------------------------------------------------------

class Article(polymodel.PolyModel):
	""" Main element of the system. 
	
	Properties
		title:				A name for the article. Appears in the interface.
		text:				Main body of content. What is read. 

		creator: 			Member who contributed the story. May be online or offline.
		community:			The Rakontu community this article belongs to.
		collectedOffline:	Whether it was contributed by an offline member.
		liaison:			Person who entered the article for off-line member. None if not offline.
		attribution: 		Whether to show the creator's nickname, "anonymous" or a personification.
		personification: 	Reference to fictional member name (from global list).

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
	
	def getAttachments(self):
		return Attachment.all().filter("article =", self.key()).fetch(1000)

	def getAnnotations(self):
		return Annotation.all().filter("article =", self.key()).fetch(1000)
	
	def getComments(self):
		return Comment.all().filter("article =", self.key()).fetch(1000)
	
	def getAnswerSets(self):
		return AnswerSet.all().filter("article =", self.key()).fetch(1000)
	
	def getTags(self):
		return Tag.all().filter("article =", self.key()).fetch(1000)
	
	def getNudges(self):
		return Nudge.all().filter("article =", self.key()).fetch(1000)
	
	def getRequests(self):
		return Request.all().filter("article =", self.key()).fetch(1000)
		
	def getOutgoingLinks(self):
		return Link.all().filter("articleFrom =", self.key()).fetch(1000)
		
class Story(Article):
	pass
	
class Invitation(Article):
	pass

class Resource(Article):
	pass

class ArticleWithListOfLinksToStories(Article):
	""" This type of article includes a list of links to other articles.
	
	Properties
		linksList:			A list of links to other articles. 
							Note these are link objects, not direct links,
							so that comments can be included.
	"""
	linksList = db.ListProperty(db.Key, default=None)

class Pattern(ArticleWithListOfLinksToStories):
	""" This type of article includes a screenshot (uploaded by the member)
		and instructions on how to get the screen to look that way.
		To be made better in later versions.
		
	Properties
		instructions:		Text telling other users how to set viewer properties.
		screenshot:			JPG uploaded by user.
	"""
	instructions = db.TextProperty(default="No instructions")
	screenshot = db.BlobProperty(default=None)
	
class Construct(ArticleWithListOfLinksToStories):
	pass

# --------------------------------------------------------------------------------------------
# Annotations
# --------------------------------------------------------------------------------------------

class Annotation(polymodel.PolyModel):
	""" Additions to articles.
	
	Properties
		article:			The thing being annotated.
		creator: 			Member who contributed the story. May be online or offline.
		community:			The Rakontu community this annotation belongs to.
							Maybe not necessary, but if you wanted to get a list of these without going through
							articles, this would be useful.

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

	collectedOffline = db.BooleanProperty(default=False)
	liaison = db.ReferenceProperty(Member, default=None, collection_name="annotations_liaisoned")
	attribution = db.StringProperty(choices=ATTRIBUTION_CHOICES, default="member")
	personification = db.ReferenceProperty(Personification, default=None)

	collected = db.DateTimeProperty(default=None)
	entered = db.DateTimeProperty(auto_now_add=True)
	
	inappropriateMarks = db.StringListProperty(default=None)
	
class AnswerSet(Annotation):
	""" A set of answers to annotation questions with reference to an article. 
	"""
	def getAnswers(self):
		return Answer.all().filter("referent =", self.key())
	
class Tag(Annotation):
	""" Member tag to describe article.
	
	Properties
		tag:				Short text.
	"""
	tag = db.StringProperty(required=True)

class Comment(Annotation):
	""" Member comment on article.
	
	Properties
		subject:			Subject line of post. 
		post:				Text. Can contain URLs which are converted to links.
	"""
	subject = db.StringProperty(required=True)
	post = db.TextProperty(required=True)

class Request(Annotation):
	""" Member communication to other members about article, asking them to do something.
	
	Properties
		title:				What displays in shortened version.
		text:				Message body.
		type:				What the other members are being asked to do. 
							For display and grouping/sorting/filtering.
	"""
	title = db.StringProperty(required=True)
	text = db.TextProperty(required=True)
	type = db.StringProperty(choices=REQUEST_TYPES, required=True)

class Nudge(Annotation):
	""" Member rating of article up or down, in any of 3-5 dimensions.
	
	Properties
		value:				Some number of nudge points up (positive) or down (negative).
		type:				One of the nudge categories: appropriateness, importance,
							or utility (either plain or in up to three sub-categories).
	"""
	value = db.IntegerProperty(default=0)
	type = db.StringProperty(choices=NUDGE_TYPES)
	comment = db.TextProperty()
	
class Link(db.Model):
	""" For holding on to links between articles.
	
	Properties
		community:			The Rakontu community this link belongs to.
		articleFrom:		Where the link originated. Story read first, or pattern/construct.
		articleTo:			Article referred to. Usually story.
		creator: 			Member who created the link. May be online or offline.
		type:				One of retold, reminded, related, included.
		comment:			Optional user comment about the linkage, written when link made.
	"""
	community = db.ReferenceProperty(Community, required=True)
	articleFrom = db.ReferenceProperty(Article, collection_name="linksFrom", required=True)
	articleTo = db.ReferenceProperty(Article, collection_name="linksTo", required=True)
	creator = db.ReferenceProperty(Member, required=True, collection_name="links")
	type = db.StringProperty(choices=LINK_TYPES, required=True)
	comment = db.StringProperty(default="")
	
class Attachment(db.Model):
	""" For binary attachments to articles.
	
	Properties:
		name:		Name of the attachment
		data:		Binary data.
		article:	Which artice it is associated with. (Only one allowed.)
	"""
	name = db.StringProperty()
	data = db.BlobProperty()
	article = db.ReferenceProperty(Article, collection_name="attachments")
	
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
							
		numInappropriateMarksToHideAnnotations: If annotations have this many inappropriate markings, they are hidden.
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
	numInappropriateMarksToHideAnnotations = db.IntegerProperty(default=5)
	

