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

QUESTION_TYPES = ["boolean", "text", "ordinal", "nominal", "value"]
NUDGE_TYPES = ["appropriateness", "importance", "useful", "useful custom 1", "useful custom 2", "useful custom 3"]
REQUEST_TYPES = ["edit text", "clean up audio/video", "add comments", "nudge", "add tags", "translate", "transcribe", "read aloud", "contact me"]
RULE_TESTS = ["same as", "<", "<=", ">", ">=", "=", "includes"]
ATTRIBUTION_CHOICES = ["creator", "anonymous", "personification"]
LINK_TYPES = ["retold", "reminded", "related", "included"]

# --------------------------------------------------------------------------------------------
# Articles
# --------------------------------------------------------------------------------------------

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
	title = db.StringProperty(verbose_name="Title", default="Untitled")
	text = db.TextProperty(verbose_name="Text", multiline=True, verbose_name="Text")

	creator = db.UserProperty()
	collectedOffline = db.BooleanProperty(verbose_name="Collected off-line", default=false)
	liaison = db.UserProperty(default=None)
	attribution = db.StringProperty(choices=ATTRIBUTION_CHOICES)
	personification = db.ReferenceProperty(Personification, verbose_name="Personification", default=None)

	tookPlace = db.DateTimeProperty(verbose_name="When the events referred to took place")
	collected = db.DateTimeProperty(auto_now_add=True, verbose_name="When gathered")
	entered = db.DateTimeProperty(auto_now_add=True, verbose_name="When entered")
	lastEdited = db.DateTimeProperty(auto_now_add=True, verbose_name="When last edited")
	lastRead = db.DateTimeProperty(auto_now_add=True, verbose_name="When last read")
	lastAnnotated = db.DateTimeProperty(auto_now_add=True, verbose_name="When last annotated")
	
	def getComments():
		return Comment.all().filter("article =", self.key()).order("-date")
	
	def getAnswers():
		return Answer.all().filter("article =", self.key())
	
	def getTags():
		return Tag.all().filter("article =", self.key()).order("-date")
	
	def getNudges():
		return Nudge.all().filter("article =", self.key()).order("-date")
	
	def getRequests():
		return Request.all().filter("article =", self.key()).order("-date")
		
	def getOutgoingLinks():
		return Link.all().filter("articleFrom =", self.,key())
		
class Story(Article):
	
class Invitation(Article):

class Resource(Article):

class ArticleWithListOfLinksToStories(Article)
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
	comment = db.StringProperty(verbose_name="Comment")
	
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
	"""
	article = db.ReferenceProperty(Article)

	creator = db.UserProperty()
	collectedOffline = db.BooleanProperty(verbose_name="Collected off-line", default=false)
	liaison = db.UserProperty(default=None)
	attribution = db.StringProperty(choices=ATTRIBUTION_CHOICES)
	personification = db.ReferenceProperty(Personification, verbose_name="Personification", default=None)

	collected = db.DateTimeProperty(auto_now_add=True, verbose_name="When gathered")
	entered = db.DateTimeProperty(auto_now_add=True, verbose_name="When entered")
	
class AnnotationAnswer(Annotation):
	""" Answer to annotation question with reference to article. 
		Can have more than one per question, if question allows it.
	
	Properties
		question:			Refers to annotation question, for display.
		answer:				Text string. If numerical choice, this is converted on use.
	"""
	question = db.ReferenceProperty(AnnotationQuestion)
	answer = db.StringProperty(verbose_name="Answer")
	
class Tag(Annotation):
	""" Member tag to describe article.
	
	Properties
		tag:				Short text.
	"""
	tag = db.StringProperty(verbose_name="Tag")

class Comment(Annotation):
	""" Member comment on article.
	
	Properties
		subject:			Subject line of post. 
		post:				Text. Can contain URLs which are converted to links.
	"""
	subject = db.StringProperty(verbose_name="Title")
	post = db.TextProperty(verbose_name="Text", multiline=True)

class Request(Annotation):
	""" Member communication to other members about article, asking them to do something.
	
	Properties
		title:				What displays in shortened version.
		text:				Message body.
		type:				What the other members are being asked to do. 
							For display and grouping/sorting/filtering.
	"""
	title = db.StringProperty(verbose_name="Title")
	text = db.TextProperty(verbose_name="Text", multiline=True)
	type = db.StringProperty(verbose_name="Type", choices=REQUEST_TYPES)

class Nudge(Annotation):
	""" Member rating of article up or down, in any of 3-5 dimensions.
	
	Properties
		value:				Some number of nudge points up (positive) or down (negative).
		type:				One of the nudge categories: appropriateness, importance,
							or utility (either plain or in up to three sub-categories).
	"""
	value = db.IntegerProperty(default=0)
	type = db.StringProperty(verbose_name="Type", choices=NUDGE_TYPES)
	
# --------------------------------------------------------------------------------------------
# Question generating system
# --------------------------------------------------------------------------------------------

class Question(db.PolyModel):
	""" Questions asked about either the community or an article.
	
	Properties
		type:				One of boolean, text, ordinal, nominal, value.
		name:				Name to display in viewer or wherever a short handle is needed.
		text:				The actual text question asked. May be much longer.
		help:				Explanatory text about how to answer the question.
	"""
	type = db.StringProperty(verbose_name="Type", choices=QUESTION_TYPES)
	name = db.StringProperty(verbose_name="Short name")
	text = db.TextProperty(multiline=True, verbose_name="Text to show")
	help = db.TextProperty(multiline=True, verbose_name="Help")
	
class CommunityQuestion(Question):

class AnnotationQuestion(Question):

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
	test = db.StringProperty(verbose_name="Test type", choices=RULE_TESTS)
	testValues = db.StringListProperty(verbose_name="Test values") 
	includeIf = db.BooleanProperty(verbose_name="Include annotation question if test result is", default=true)
	annotationQuestion = db.ReferenceProperty(AnnotationQuestion)
	
class CommunityAnswer(Annotation):
	""" Answer to annotation question with reference to article. 
		Can have more than one per question, if question allows it.
	
	Properties
		question:			Refers to annotation question, for display.
		answer:				Text string. If numerical choice, this is converted on use.
	"""
	question = db.ReferenceProperty(CommunityQuestion)
	answer = db.StringProperty(verbose_name="Answer")
	
# --------------------------------------------------------------------------------------------
# Users
# --------------------------------------------------------------------------------------------

class Personification(db.Model):
	""" Used to anonymize entries but provide some information about intent. Optional.
	
	Properties
		name:				The fictional name of the personification, like "Coyote".
	"""
	name = db.StringProperty(verbose_name="Name", required=true)

class Member(db.PolyModel):
	""" A user account. 
	
	Properties
		nickname:			The member's "handle" in the sy stem. Cannot be changed.
		nicknameIsRealName:	Whether their nickname is their real name. For display only.
		googleAccountID:	UserID field from Google account. None if offline.
		profileText:		Small amount of member-submitted info about themselves.
							Can include URLs which are converted to links.

		isOnline:			Whether the member is online or offline.
		liaisonAccountID:	Can be permanently linked to a liaison. This just sets the 
							default when entries are recorded, to save liaisons time.
							
		viewingPreferences:	How they want the viewer to show things. None if offline.
	"""
	nickname = db.StringProperty(verbose_name="Nickname")
	nicknameIsRealName = db.BooleanProperty(verbose_name="Nickname is real name")
	googleAccountID = db.StringProperty(verbose_name="Google Account ID")
	profileText = db.TextProperty(multiline=True, verbose_name="Profile")

	isOnline = db.BooleanProperty(verbose_name="Online", default=true)
	liaisonAccountID = db.StringProperty(verbose_name="Liaison Account ID")
	
	viewingPreferences = db.ReferenceProperty(UserViewingPreferences)
	
	def getHistory():
		articles = Article.all().filter("creator =", self.key()).order("-date")
		annotations = Annotation.all().filter("creator =", self.key()).order("-date")
		return articles, annotations
	
class Curator(Member):

class Sustainer(Member):

class Liaison(Member):

class Facilitator(Member):

class Administrator(Member):

# --------------------------------------------------------------------------------------------
# Community
# --------------------------------------------------------------------------------------------

class Community(db.Model):
	communityQuestions = db.ListProperty(db.Key)
	rules = db.ListProperty(db.Key)
	communityAnswers = db.ListProperty(db.Key)
	annotationQuestions = db.ListProperty(db.Key)
	# lots more

# --------------------------------------------------------------------------------------------
# Preferences
# --------------------------------------------------------------------------------------------

class UserViewingPreferences(db.Model):

