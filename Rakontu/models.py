# --------------------------------------------------------------------------------------------
# RAKONTU
# Description: Rakontu is open source story sharing software.
# Version: pre-0.1
# License: GPL 3.0
# Google Code Project: http://code.google.com/p/rakontu/
# --------------------------------------------------------------------------------------------

from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.api import users
from google.appengine.ext.db import polymodel

# --------------------------------------------------------------------------------------------
# Articles
# --------------------------------------------------------------------------------------------

ATTRIBUTION_CHOICES = ["creator", "anonymous", "personification"]
ARTICLE_TYPES = ["stories", "patterns", "constructs", "invitations", "resources"]

class Article(db.PolyModel):
	""" Main element of the system. 
	
	Properties
		title:				A name for the article. Appears in the interface.
		text:				Main body of content. What is read. Will be expanded later.

		creator: 			Member who contributed the story. May be online or offline.
		collectedOffline:	Whether it was contributed by an offline member.
		liaison:			Person who entered the article for off-line member. None if not offline.
		attribution: 		Whether to show the creator's nickname, "anonymous" or a personification.
		personification: 	Reference to fictional member name (from global list).

		tookPlace:			When the events the article is about took place.
		collected:			When article was collected, usually from an off-line member.
		entered:			When article was added to database.
		lastEdited:			When the text or title was last changed.
		lastRead:			When it was last accessed by anyone.
		lastAnnotated:		The last time any annotation was added.
	"""
	title = db.StringProperty(default="Untitled")
	text = db.TextProperty(multiline=True)
	audio = db.BlobProperty()
	video = db.BlobProperty()
	image = db.BlobProperty()

	creator = db.UserProperty()
	collectedOffline = db.BooleanProperty(default=false)
	liaison = db.UserProperty(default=None)
	attribution = db.StringProperty(choices=ATTRIBUTION_CHOICES)
	personification = db.ReferenceProperty(Personification, default=None)

	tookPlace = db.DateTimeProperty()
	collected = db.DateTimeProperty()
	entered = db.DateTimeProperty(auto_now_add=True)
	lastEdited = db.DateTimeProperty()
	lastRead = db.DateTimeProperty()
	lastAnnotated = db.DateTimeProperty()
	
	def getComments(self):
		return Comment.all().filter("article =", self.key()).order("-date")
	
	def getAnswers(self):
		return Answer.all().filter("article =", self.key())
	
	def getTags(self):
		return Tag.all().filter("article =", self.key()).order("-date")
	
	def getNudges(self):
		return Nudge.all().filter("article =", self.key()).order("-date")
	
	def getRequests(self):
		return Request.all().filter("article =", self.key()).order("-date")
		
	def getOutgoingLinks(self):
		return Link.all().filter("articleFrom =", self.key())
		
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
	linksList = db.ListProperty(db.Key)

class Pattern(ArticleWithListOfLinksToStories):
	""" This type of article includes a screenshot (uploaded by the member)
		and instructions on how to get the screen to look that way.
		To be made better in later versions.
		
	Properties
		instructions:		Text telling other users how to set viewer properties.
		screenshot:			JPG uploaded by user.
	"""
	instructions = db.TextProperty(multiline=True)
	screenshot = db.BlobProperty()
	
class Construct(ArticleWithListOfLinksToStories):
	pass

LINK_TYPES = ["retold", "reminded", "related", "included"]

class Link(db.Model):
	""" For holding on to links between articles.
	
	Properties
		articleFrom:		Where the link originated. Story read first, or pattern/construct.
		articleTo:			Article referred to. Usually story.
		type:				One of retold, reminded, related, included.
		comment:			Optional user comment about the linkage, written when link made.
	"""
	articleFrom = db.ReferenceProperty(Article, collection_name="Article_reference_set1")
	articleTo = db.ReferenceProperty(Article, collection_name="Article_reference_set2")
	type = db.StringProperty(choices=LINK_TYPES)
	comment = db.StringProperty()
	
# --------------------------------------------------------------------------------------------
# Annotations
# --------------------------------------------------------------------------------------------

class Annotation(CollectedItem):
	""" Additions to articles.
	
	Properties
		article:			The thing being annotated.

		creator: 			Member who contributed the story. May be online or offline.
		collectedOffline:	Whether it was contributed by an offline member.
		liaison:			Person who entered the article for off-line member. None if not offline.
		attribution: 		Whether to show the creator's nickname, "anonymous" or a personification.
		personification: 	Reference to fictional member name (from global list).

		collected:			When article was collected, usually from an off-line member.
		entered:			When article was added to database.
		
		inappropriateMarks:	A list of user comments marking the annotation as inappropriate.
	"""
	article = db.ReferenceProperty(Article)

	creator = db.UserProperty()
	collectedOffline = db.BooleanProperty(default=false)
	liaison = db.UserProperty(default=None)
	attribution = db.StringProperty(choices=ATTRIBUTION_CHOICES)
	personification = db.ReferenceProperty(Personification, default=None)

	collected = db.DateTimeProperty()
	entered = db.DateTimeProperty(auto_now_add=True)
	
	inappropriateMarks = db.StringListProperty()
	
class AnnotationAnswer(Annotation):
	""" Answer to annotation question with reference to article. 
		Can have more than one per question, if question allows it.
	
	Properties
		question:			Refers to annotation question, for display.
		answer:				Text string. If numerical choice, this is converted on use.
	"""
	question = db.ReferenceProperty(AnnotationQuestion)
	answer = db.StringProperty()
	
class Tag(Annotation):
	""" Member tag to describe article.
	
	Properties
		tag:				Short text.
	"""
	tag = db.StringProperty()

class Comment(Annotation):
	""" Member comment on article.
	
	Properties
		subject:			Subject line of post. 
		post:				Text. Can contain URLs which are converted to links.
	"""
	subject = db.StringProperty()
	post = db.TextProperty(multiline=True)

REQUEST_TYPES = ["edit text", "clean up audio/video", "add comments", "nudge", "add tags", "translate", "transcribe", "read aloud", "contact me"]

class Request(Annotation):
	""" Member communication to other members about article, asking them to do something.
	
	Properties
		title:				What displays in shortened version.
		text:				Message body.
		type:				What the other members are being asked to do. 
							For display and grouping/sorting/filtering.
	"""
	title = db.StringProperty()
	text = db.TextProperty(multiline=True)
	type = db.StringProperty(choices=REQUEST_TYPES)

NUDGE_TYPES = ["appropriateness", "importance", "utility", "utility custom 1", "utility custom 2", "utility custom 3"]

class Nudge(Annotation):
	""" Member rating of article up or down, in any of 3-5 dimensions.
	
	Properties
		value:				Some number of nudge points up (positive) or down (negative).
		type:				One of the nudge categories: appropriateness, importance,
							or utility (either plain or in up to three sub-categories).
	"""
	value = db.IntegerProperty(default=0)
	type = db.StringProperty(choices=NUDGE_TYPES)
	comment = db.TextProperty(multiline=True)
	
# --------------------------------------------------------------------------------------------
# Question generating system
# --------------------------------------------------------------------------------------------

QUESTION_TYPES = ["boolean", "text", "ordinal", "nominal", "value"]

class Question(db.PolyModel):
	""" Questions asked about either the community or an article.
	
	Properties
		type:				One of boolean, text, ordinal, nominal, value.
		name:				Name to display in viewer or wherever a short handle is needed.
		text:				The actual text question asked. May be much longer.
		help:				Explanatory text about how to answer the question.
	"""
	type = db.StringProperty(choices=QUESTION_TYPES)
	name = db.StringProperty()
	text = db.TextProperty(multiline=True)
	help = db.TextProperty(multiline=True)
	
class AnnotationQuestion(Question):
	""" Questions asked about an article.
	
	Properties
		articleType:		Which type of article this question refers to.
	"""
	articleType = db.StringProperty(choices=ARTICLE_TYPES)

class CommunityQuestion(Question):
	pass

class MemberQuestion(Question):
	pass

RULE_TESTS = ["same as", "<", "<=", ">", ">=", "=", "includes"]

class Rule(db.Model):
	""" Simple if-then statement to choose annotation questions based on community questions.
	
	Properties
		communityQuestion:	What question about the community the rule is based on.
		test:				The operation used to compare the community answer to the test value.
		testValues:			The thing(s) compared to the community answer.
		includeIf:			Whether the test should be true or false to include the annotation question. 
		annotationQuestion: What question about articles is affected by the rule.

	Usage
		In the abstract:
			For the community question <communityQuestion>, 
			IF the evaluation of (<CommunityAnswer> <test> <testValues>) = includeIf, 
			THEN include <annotationQuestion>.
		Examples:
			For the community question "Is this community united by a geographic place?",
		  	IF the evaluation of (<CommunityAnswer> "=" ["yes"]) = true, 
		  	THEN include "Where did this story take place?".
		  	
		  	For the community question "Do people want to talk about social issues?",
		  	IF the evaluation of (<CommunityAnswer> "includes" ["no!", "maybe not", "not sure"] = false,
		  	THEN include "Who needs to hear this story?".
	"""
	communityQuestion = db.ReferenceProperty(CommunityQuestion)
	test = db.StringProperty(choices=RULE_TESTS)
	testValues = db.StringListProperty()
	includeIf = db.BooleanProperty(default=true)
	annotationQuestion = db.ReferenceProperty(AnnotationQuestion)
	
class CommunityAnswer(Annotation):
	""" Answer to annotation question with reference to article. 
		Can have more than one per question, if question allows it.
	
	Properties
		question:			Refers to annotation question, for display.
		answer:				Text string. If numerical choice, this is converted on use.
	"""
	question = db.ReferenceProperty(CommunityQuestion)
	answer = db.StringProperty()
	
# --------------------------------------------------------------------------------------------
# Queries
# --------------------------------------------------------------------------------------------

QUERY_TYPES = ["words", "tags", "answers", "members", "activities", "links"]
QUERY_TARGETS = ["stories", "patterns", "constructs", "invitations", "resources", "articles", "interpretations", "tags", "comments", "requests", "nudge comments"]
BOOLEAN_CHOICES = ["ALL", "ANY"]
ACTIVITIES = ["told", "retold", "reminded", "related", "included", "annotated", "interpreted", "commented on", "nudged", "tagged", "requested", "read"]
RECENT_TIME_FRAMES = ["last hour", "last day", "last week", "last month", "last six months", "last year", "ever"]

class Query(db.Model):
	""" Choice to show subsets of items in main viewer.

	Properties (common to all types):
		type:				One of free text, tags, answers, members, activities, links. 
		targets:			All searches return articles, annotations, or members (no combinations). 
		creator:			Who this query belongs to.
		created:			When it was created.
	"""
	type = db.StringProperty(choices=QUERY_TYPES)
	targets = db.StringListProperty(choices=QUERY_TARGETS)
	creator = db.UserProperty()
	created = db.DateTimeProperty(auto_now_add=True)
	
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
	combination = db.StringProperty(choices=BOOLEAN_CHOICES)
	
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
		Show [MEMBER_TYPES] who have [ACTIVITIES] in [RECENT_TIME_FRAMES]
	Examples: 
		Show [off-line members] who [commented] in [the last week]
		(with selection) Show [members] who [nudged] the selected story in [the last hour]
	"""
	memberType = db.StringProperty(choices=MEMBER_TYPES)
	activity = db.StringProperty(choices=ACTIVITIES)
	timeFrame = db.StringProperty(choices=RECENT_TIME_FRAMES)
	
	""" Activity search
	Properties:
		targets:			Articles or annotations, or specific types of either. 
		activity:			What the member should have done. 
		memberIDS:			Who should have done it. 1-n.
		combination:		Whether to search for all or any of the members listed.
		timeFrame:			When the member(s) should have done it. 
	Usage:
		Show [QUERY_TARGETS] in which [ACTIVITIES] were done by {members} in [RECENT_TIME_FRAMES]
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
# Users
# --------------------------------------------------------------------------------------------

class Personification(db.Model):
	""" Used to anonymize entries but provide some information about intent. Optional.
	
	Properties
		name:				The fictional name of the personification, like "Coyote".
	"""
	name = db.StringProperty(required=true)
	description = db.TextProperty(multiline=True)

MEMBER_TYPES = ["members", "on-line members", "off-line members", "liaisons", "curators", "sustainers", "facilitators", "administrators"]
HELPING_ROLE_TYPES = ["curators", "sustainers", "liaisons"]
MANAGING_ROLE_TYPES = ["facilitator", "administrator"]

class Member(db.PolyModel):
	""" A user account. 
	
	Properties
		nickname:			The member's "handle" in the system. Cannot be changed.
		nicknameIsRealName:	Whether their nickname is their real name. For display only.
		googleAccountID:	UserID field from Google account. None if offline.
		profileText:		Small amount of member-submitted info about themselves.
							Can include URLs which are converted to links.
		profileImage:		Thumbnail picture. Optional.

		isOnline:			Whether the member is online or offline.
		liaisonAccountID:	Can be permanently linked to a liaison. This just sets the 
							default when entries are recorded, to save liaisons time.
	"""
	nickname = db.StringProperty()
	nicknameIsRealName = db.BooleanProperty()
	googleAccountID = db.StringProperty()
	profileText = db.TextProperty(multiline=True)
	profileImage = db.BlobProperty()
	
	numArticlesCreated = db.IntegerProperty()
	numArticlesRead = db.IntegerProperty()
	numAnnotationsCreated = db.IntegerProperty()
	numAnnotationsRead = db.IntegerProperty()
	numLinksCreated = db.IntegerProperty()
	nudgePoints = db.IntegerProperty()
	
	joined = db.DateTimeProperty()
	lastEnteredArticle = db.DateTimeProperty()
	lastEnteredAnnotation = db.DateTimeProperty()
	lastReadAnything = db.DateTimeProperty()

	isOnlineMember = db.BooleanProperty(default=true)
	liaisonAccountID = db.StringProperty()
	
	def getHistory(self):
		articles = Article.all().filter("creator =", self.key()).order("-date")
		annotations = Annotation.all().filter("creator =", self.key()).order("-date")
		return articles, annotations
	
	def getViewingPreferences(self):
		return ViewingPreferences.all().filter("owner = ", self.key())
	
class Curator(Member):
	pass

class Sustainer(Member):
	pass

class Liaison(Member):
	pass

class Facilitator(Member):
	pass

class Administrator(Member):
	pass

# --------------------------------------------------------------------------------------------
# Preferences
# --------------------------------------------------------------------------------------------

TIME_STEPS = ["hour", "day", "week", "month", "year"]
VERTICAL_PLACEMENTS = ["time", \
					   	 "browsing", "reading", \
						 "retelling", "reminding", "relating", "including", \
						 "interpreting", "tagging", "commenting", "requesting", "nudging", \
						 "nudging - appropriateness", "nudging - importance", "nudging - utility", \
						 "nudging - utility custom 1", "nudging - utility custom 2", "nudging - utility custom 3"]

class ViewingPreferences(db.Model):
	""" Preferences for the main viewer. Each user has these, and there is a global set as well for defaulting.
	
	Properties
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
	owner = db.UserProperty()
	xTimeStep = db.StringProperty(choices=TIME_STEPS)
	xTimeStepMultiplier = db.IntegerProperty()
	xStart = db.DateTimeProperty()
	xStop = db.DateTimeProperty()
	
	yPointStep = db.IntegerProperty()
	yTop = db.IntegerProperty()
	yBottom = db.IntegerProperty()
	yArrangement = db.StringListProperty(choices=VERTICAL_PLACEMENTS)
	verticalPoints = db.ListProperty(int)
	
	basement = db.IntegerProperty()
	numInappropriateMarksToHideAnnotations = db.IntegerProperty()
	
ROLE_ASSIGNMENT_TYPES = ["available", "moderated", "invited"]

class GlobalOptions(db.Model):
	""" Preferences for the whole system (community).
	
	Properties
		nudgePointsPerActivity:	A number for each type of activity (VERTICAL_PLACEMENTS) denoting how many
								points the member accumulates for doing it.
		nudgePointsPerArticle:	How many nudge points a member is allowed to place (maximally) on any article.
		helperRoleAssignmentTypes:	For each of HELPING_ROLE_TYPES, available, moderated or invited
		allowAnonymousEntry:	Whether members are allowed to enter articles and annotations with only
								"anonymous" marked. Different from personification system.
		utilityNudgeCategories:	Names of custom nudge categories. Up to three allowed.
	"""
	nudgePointsPerActivity = db.ListProperty(int)
	nudgePointsPerArticle = db.IntegerProperty()
	helperRoleAssignmentTypes = db.StringListProperty(choices=ROLE_ASSIGNMENT_TYPES)
	allowAnonymousEntry = db.BooleanProperty()
	utilityNudgeCategories = db.StringListProperty()

	def getViewingPreferences(self):
		return ViewingPreferences.all().filter("owner = ", self.key())
	
	def getMemberQuestions(self):
		return MemberQuestion.all()
	
	def getAnnotationQuestions(self, articleType):
		return AnnotationQuestion.all().filter("articleType = ", articleType)
		
	def getCommunitQuestions(self):
		return CommunityQuestion.all()
	
	def getPersonifications(self):
		return Personification.all()
	
