# ============================================================================================
# RAKONTU
# Description: Rakontu is open source story sharing software.
# Version: pre-0.1
# License: GPL 3.0
# Google Code Project: http://code.google.com/p/rakontu/
# ============================================================================================

import logging, pytz, re, csv, uuid, random
from datetime import *
from pytz import timezone

VERSION_NUMBER = "0.9"

from translationLookup import *

from google.appengine.ext import db

def KeyName(type):
	IncrementCount(type)
	return "%s%s" % (type, GetShardCount(type))

def GetShardCount(type):
	result = 0
	for counter in CounterShard.all().filter("type = ", type).fetch(FETCH_NUMBER):
		result += counter.count
	return result

def IncrementCount(type):
	config = CounterShardConfiguration.get_or_insert(type, type=type)
	def transaction():
		i = random.randint(0, config.numShards - 1)
		shardKeyName = type + str(i)
		counter = CounterShard.get_by_key_name(shardKeyName)
		if not counter:
			counter = CounterShard(key_name=shardKeyName, type=type)
		counter.count += 1
		counter.put()
	db.run_in_transaction(transaction)
	
def IncreaseNumberOfShards(type, number):
	config = CounterShardConfiguration.get_or_insert(type, type=type)
	def transaction():
		if config.numShards < number:
			config.numShards = number
			config.put()
	db.run_in_transaction(transaction)
	
def DebugPrint(text, msg="print"):
	logging.info(">>>>>>>> %s >>>>>>>> %s" %(msg, text))
	
def stripTags(text):
	if text:
		tags = re.compile(r'\<(.+?)\>').findall(text)
		for tag in tags:
			text = text.replace('<%s>' % tag, " ")
		text = text.replace("  ", " ")
		return text
	else:
		return "none"
   
def CleanUpCSV(parts):
	partsWithCommasQuoted = []
	for part in parts:
		if part:
			cleanPart = part
			cleanPart = cleanPart.replace('"', '""')
			if cleanPart.find(",") >= 0:
				cleanPart = '"%s"' % cleanPart
			partsWithCommasQuoted.append(cleanPart)
		else:
			partsWithCommasQuoted.append("")
	return ','.join(partsWithCommasQuoted) 

def caseInsensitiveFind(text, searchFor):
	return text.lower().find(searchFor.lower()) >= 0

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
class CounterShard(db.Model):
# ============================================================================================
# ============================================================================================

	type = db.StringProperty(required=True)
	count = db.IntegerProperty(required=True, default=0)
	
# ============================================================================================
# ============================================================================================
class CounterShardConfiguration(db.Model):
# ============================================================================================
# ============================================================================================

	type = db.StringProperty(required=True)
	numShards = db.IntegerProperty(required=True, default=20)
	
# ============================================================================================
# ============================================================================================
class Rakontu(db.Model):
# ============================================================================================
# ============================================================================================

	appRocketTimeStamp = TzDateTimeProperty(auto_now=True)
	
	# identification
	name = db.StringProperty(required=True) # appears on all pages at top
	
	# state
	active = db.BooleanProperty(default=True)
	created = TzDateTimeProperty(auto_now_add=True) 
	firstVisit = TzDateTimeProperty(default=None)
	lastPublish = TzDateTimeProperty(default=None)
	firstPublish = TzDateTimeProperty(default=None)

	# governance options
	maxNumAttachments = db.IntegerProperty(choices=NUM_ATTACHMENT_CHOICES, default=DEFAULT_MAX_NUM_ATTACHMENTS, indexed=False)
	maxNudgePointsPerEntry = db.IntegerProperty(default=DEFAULT_MAX_NUDGE_POINTS_PER_ENTRY, indexed=False)
	memberNudgePointsPerEvent = db.ListProperty(int, default=DEFAULT_MEMBER_NUDGE_POINT_ACCUMULATIONS, indexed=False)
	nudgeCategories = db.StringListProperty(default=DEFAULT_NUDGE_CATEGORIES, indexed=False)
	nudgeCategoryQuestions = db.StringListProperty(default=DEFAULT_NUDGE_CATEGORY_QUESTIONS, indexed=False)
	entryActivityPointsPerEvent = db.ListProperty(int, default=DEFAULT_ARCTICLE_ACTIVITY_POINT_ACCUMULATIONS, indexed=False)
	allowCharacter = db.ListProperty(bool, default=DEFAULT_ALLOW_CHARACTERS, indexed=False)
	allowEditingAfterPublishing = db.ListProperty(bool, default=DEFAULT_ALLOW_EDITING_AFTER_PUBLISHING, indexed=False)
	allowNonManagerCuratorsToEditTags = db.BooleanProperty(default=False, indexed=False)
	
	# descriptive options
	type = db.StringProperty(choices=RAKONTU_TYPES, default=RAKONTU_TYPES[-1]) # only used to determine questions at front, but may be useful later so saving
	tagline = db.StringProperty(default="", indexed=False) # appears under name, optional
	image = db.BlobProperty(default=None) # appears on all pages, should be small (100x60 is best)
	contactEmail = db.StringProperty(default=DEFAULT_CONTACT_EMAIL) # sender address for emails sent from site
	
	description = db.TextProperty(default=DEFAULT_RAKONTU_DESCRIPTION) # appears on "about rakontu" page
	description_formatted = db.TextProperty() # formatted texts kept separate for re-editing original
	description_format = db.StringProperty(default=DEFAULT_TEXT_FORMAT, indexed=False)
	
	etiquetteStatement = db.TextProperty(default=DEFAULT_ETIQUETTE_STATEMENT) # appears on "about rakontu" page
	etiquetteStatement_formatted = db.TextProperty()
	etiquetteStatement_format = db.StringProperty(default=DEFAULT_TEXT_FORMAT, indexed=False)
	
	welcomeMessage = db.TextProperty(default=DEFAULT_WELCOME_MESSAGE) # appears only on new member welcome page
	welcomeMessage_formatted = db.TextProperty()
	welcomeMessage_format = db.StringProperty(default=DEFAULT_TEXT_FORMAT, indexed=False)
	
	roleReadmes = db.ListProperty(db.Text, default=[db.Text(DEFAULT_ROLE_READMES[0]), db.Text(DEFAULT_ROLE_READMES[1]), db.Text(DEFAULT_ROLE_READMES[2])])
	roleReadmes_formatted = db.ListProperty(db.Text, default=[db.Text(""), db.Text(""), db.Text("")])
	roleReadmes_formats = db.StringListProperty(default=DEFAULT_ROLE_READMES_FORMATS, indexed=False)
	
	# display options
	defaultTimeZoneName = db.StringProperty(default=DEFAULT_TIME_ZONE, indexed=False) # appears on member preferences page
	defaultTimeFormat = db.StringProperty(default=DEFAULT_TIME_FORMAT, indexed=False) # appears on member preferences page
	defaultDateFormat = db.StringProperty(default=DEFAULT_DATE_FORMAT, indexed=False) # appears on member preferences page
	
	skinName = db.StringProperty(default=DEFAULT_SKIN_NAME)
	
	def initializeFormattedTexts(self):
		self.description_formatted = db.Text("<p>%s</p>" % self.description)
		self.etiquetteStatement_formatted = db.Text("<p>%s</p>" % self.etiquetteStatement)
		self.welcomeMessage_formatted = db.Text("<p>%s</p>" % self.welcomeMessage)
		for i in range(3):
			self.roleReadmes_formatted[i] = db.Text(self.roleReadmes[i])
	
	# OPTIONS
	
	def allowsPostPublishEditOfEntryType(self, type):
		i = 0
		for entryType in ENTRY_TYPES:
			if type == entryType:
				return self.allowEditingAfterPublishing[i]
			i += 1
		return False
	
	def allowsAttachments(self):
		return self.maxNumAttachments > 0
	
	def allowsAtLeastTwoAttachments(self):
		return self.maxNumAttachments >= 2
	
	def allowsAtLeastThreeAttachments(self):
		return self.maxNumAttachments >= 3
	
	def allowsAtLeastFourAttachments(self):
		return self.maxNumAttachments >= 4
	
	def allowsFiveAttachments(self):
		return self.maxNumAttachments == 5
	
	def getSkinDictionary(self):
		skin = Skin.all().filter("name = ", self.skinName).get()
		if skin:
			return skin.getPropertiesAsDictionary()
		else:
			return {}
		
	# DISPLAY
	
	def imageEmbed(self):
		return '<img src="/%s/%s?%s=%s" class="bordered">' % (DIRS["dir_visit"], URLS["url_image"], URL_IDS["url_query_rakontu"], self.getKeyName())
	
	def getKeyName(self):
		return self.key().name()
	
	def linkString(self):
		return '<a href="%s">%s</a>' % (self.linkURL(), self.name)
		
	def linkURL(self):
		return '%s?%s' % (self.urlWithoutQuery(), self.urlQuery())
		
	def urlWithoutQuery(self):
		return "/%s/%s" % (DIRS["dir_visit"], URLS["url_home"])

	def urlQuery(self):
		return "%s=%s" % (URL_IDS["url_query_rakontu"], self.key().name())

	# MEMBERS
	
	def getPendingMembers(self):
		return PendingMember.all().filter("rakontu = ", self.key()).fetch(FETCH_NUMBER)

	def getOfflineMembers(self):
		return Member.all().filter("rakontu = ", self.key()).filter("isOnlineMember = ", False).fetch(FETCH_NUMBER)
	
	def getMemberNudgePointsForEvent(self, event):
		i = 0
		for eventType in EVENT_TYPES:
			if event == eventType:
				return self.memberNudgePointsPerEvent[i]
			i += 1
		return 0
	
	def getMemberForGoogleAccountId(self, id):
		return Member.all().filter("rakontu = ", self.key()).filter("googleAccountID = ", id).fetch(1)
		
	def getActiveAndInactiveMembers(self):
		return Member.all().filter("rakontu = ", self.key()).fetch(FETCH_NUMBER)
	
	def getActiveMembers(self):
		return Member.all().filter("rakontu = ", self.key()).filter("active = ", True).fetch(FETCH_NUMBER)
	
	def getInactiveMembers(self):
		return Member.all().filter("rakontu = ", self.key()).filter("active = ", False).fetch(FETCH_NUMBER)
	
	def getActiveOnlineMembers(self):
		return Member.all().filter("rakontu = ", self.key()).filter("active = ", True).filter("isOnlineMember = ", True).fetch(FETCH_NUMBER)
	
	def getActiveOfflineMembers(self):
		return Member.all().filter("rakontu = ", self.key()).filter("active = ", True).filter("isOnlineMember = ", False).fetch(FETCH_NUMBER)
	
	def getInactiveOfflineMembers(self):
		return Member.all().filter("rakontu = ", self.key()).filter("active = ", False).filter("isOnlineMember = ", False).fetch(FETCH_NUMBER)
	
	def getActiveAndInactiveOfflineMembers(self):
		return Member.all().filter("rakontu = ", self.key()).filter("active = ", False).filter("isOnlineMember = ", False).fetch(FETCH_NUMBER)
	
	def getGuides(self):
		result = []
		onlineMembers = Member.all().filter("rakontu = ", self.key()).filter("active = ", True).filter("isOnlineMember = ", True).fetch(FETCH_NUMBER)
		for member in onlineMembers:
			if member.isGuide():
				result.append(member)
		return result
	
	def hasMemberWithGoogleEmail(self, email):
		members = self.getActiveMembers()
		for member in members:
			if member.googleAccountEmail == email:
				return True
		return False
	
	def memberWithGoogleUserID(self, id):
		members = self.getActiveMembers()
		for member in members:
			if member.googleAccountID == id:
				return member
		return None
	
	def memberWithNickname(self, nickname):
		members = self.getActiveAndInactiveMembers()
		for member in members:
			if member.nickname == nickname:
				return member
		return None
	
	def hasMemberWithNickname(self, nickname):
		members = self.getActiveAndInactiveMembers()
		for member in members:
			if member.nickname == nickname:
				return True
		return False
	
	def getOfflineMemberForNickname(self, nickname):
		members = self.getActiveAndInactiveOfflineMembers()
		for member in members:
			if member.nickname == nickname:
				return member
		return None
	
	def getManagers(self):
		return Member.all().filter("rakontu = ", self.key()).filter("governanceType = ", "manager").fetch(FETCH_NUMBER)
	
	def getOwners(self):
		return Member.all().filter("rakontu = ", self.key()).filter("governanceType = ", "owner").fetch(FETCH_NUMBER)
	
	def getManagersAndOwners(self):
		return Member.all().filter("rakontu = ", self.key()).filter("governanceType IN ", ["owner", "manager"]).fetch(FETCH_NUMBER)
	
	def memberIsOnlyOwner(self, member):
		owners = self.getOwners()
		if len(owners) == 1 and owners[0].key() == member.key():
			return True
		return False
	
	# CHARACTERS
	
	def getActiveCharacters(self):
		return Character.all().filter("rakontu = ", self.key()).filter("active = ", True).fetch(FETCH_NUMBER)
	
	def getInactiveCharacters(self):
		return Character.all().filter("rakontu = ", self.key()).filter("active = ", False).fetch(FETCH_NUMBER)
	
	def hasAtLeastOneCharacterEntryAllowed(self, entryTypeIndex):
		return self.allowCharacter[entryTypeIndex] or len(self.getActiveCharacters()) > 0

	def hasActiveCharacters(self):
		return Character.all().filter("rakontu = ", self.key()).filter("active = ", True).count() > 0
	
	# ENTRIES
	
	def getNonDraftEntries(self):
		return Entry.all().filter("rakontu = ", self.key()).filter("draft = ", False).fetch(BIG_FETCH_NUMBER)
	
	def getNonDraftEntriesOfTypesInListBetweenDateTimesInReverseTimeOrder(self, typeList, minTime, maxTime):
		return Entry.all().filter("rakontu = ", self.key()).filter("draft = ", False).filter("type IN ", typeList).\
			filter("published >= ", minTime).filter("published < ", maxTime).order("-published").fetch(BIG_FETCH_NUMBER)
	
	def getNonDraftEntriesInAlphabeticalOrder(self):
		return Entry.all().filter("rakontu = ", self.key()).filter("draft = ", False).order("-title").fetch(BIG_FETCH_NUMBER)
	
	def getNonDraftStoriesInAlphabeticalOrder(self):
		return Entry.all().filter("rakontu = ", self.key()).filter("type = ", "story").filter("draft = ", False).order("-title").fetch(BIG_FETCH_NUMBER)
	
	def getNonDraftEntriesAnnotationsAndAnswersInReverseTimeOrder(self):
		result = []
		entries = Entry.all().filter("rakontu = ", self.key()).filter("draft = ", False).order("-published").fetch(BIG_FETCH_NUMBER)
		annotations = Annotation.all().filter("rakontu = ", self.key()).filter("draft = ", False).order("-published").fetch(BIG_FETCH_NUMBER)
		answers = Answer.all().filter("rakontu = ", self.key()).filter("draft = ", False).order("-published").fetch(BIG_FETCH_NUMBER)
		result.extend(entries)
		result.extend(annotations)
		result.extend(answers)
		result.sort(lambda a,b: cmp(b.published, a.published))
		return result
	
	def getNonDraftEntriesOfType(self, type):
		return Entry.all().filter("rakontu = ", self.key()).filter("draft = ", False).filter("type = ", type).fetch(BIG_FETCH_NUMBER)
	
	def getNonDraftEntriesWithMissingMetadata(self, sortBy):
		entriesWithoutTags = []
		entriesWithoutLinks = []
		entriesWithoutAnswers = []
		entriesWithoutComments = []
		invitationsWithoutResponses = []
		collagesWithoutInclusions = []
		for entry in self.getNonDraftEntries():
			if not Annotation.all().filter("entry = ", entry.key()).filter("type = ", "tag set").filter("draft = ", False).get():
				entriesWithoutTags.append(entry)
			if not Link.all().filter("itemFrom = ", entry.key()).get() and not Link.all().filter("itemTo = ", entry.key()).get():
				entriesWithoutLinks.append(entry)
			if not Answer.all().filter("referent = ", entry.key()).filter("draft = ", False).get():
				entriesWithoutAnswers.append(entry)
			if not Annotation.all().filter("entry = ", entry.key()).filter("type = ", "comment").filter("draft = ", False).get():
				entriesWithoutComments.append(entry)
		for invitation in self.getNonDraftEntriesOfType("invitation"):
			if not Link.all().filter("itemFrom = ", invitation.key()).filter("type = ", "responded").get():
				invitationsWithoutResponses.append(invitation)
		for collage in self.getNonDraftEntriesOfType("collage"):
			if not Link.all().filter("itemFrom = ", collage.key()).filter("type = ", "included").get():
				collagesWithoutInclusions.append(collage)
		if sortBy == "activity":
			entriesWithoutTags.sort(lambda a,b: cmp(b.activityPoints, a.activityPoints))
			entriesWithoutLinks.sort(lambda a,b: cmp(b.activityPoints, a.activityPoints))
			entriesWithoutAnswers.sort(lambda a,b: cmp(b.activityPoints, a.activityPoints))
			entriesWithoutComments.sort(lambda a,b: cmp(b.activityPoints, a.activityPoints))
			invitationsWithoutResponses.sort(lambda a,b: cmp(b.activityPoints, a.activityPoints))
			collagesWithoutInclusions.sort(lambda a,b: cmp(b.activityPoints, a.activityPoints))
		elif sortBy == "nudges":
			entriesWithoutTags.sort(lambda a,b: cmp(b.nudgePointsCombined(), a.nudgePointsCombined()))
			entriesWithoutLinks.sort(lambda a,b: cmp(b.nudgePointsCombined(), a.nudgePointsCombined()))
			entriesWithoutAnswers.sort(lambda a,b: cmp(b.nudgePointsCombined(), a.nudgePointsCombined()))
			entriesWithoutComments.sort(lambda a,b: cmp(b.nudgePointsCombined(), a.nudgePointsCombined()))
			invitationsWithoutResponses.sort(lambda a,b: cmp(b.nudgePointsCombined(), a.nudgePointsCombined()))
			collagesWithoutInclusions.sort(lambda a,b: cmp(b.nudgePointsCombined(), a.nudgePointsCombined()))
		elif sortBy == "date":
			entriesWithoutTags.sort(lambda a,b: cmp(b.published, a.published))
			entriesWithoutLinks.sort(lambda a,b: cmp(b.published, a.published))
			entriesWithoutAnswers.sort(lambda a,b: cmp(b.published, a.published))
			entriesWithoutComments.sort(lambda a,b: cmp(b.published, a.published))
			invitationsWithoutResponses.sort(lambda a,b: cmp(b.published, a.published))
			collagesWithoutInclusions.sort(lambda a,b: cmp(b.published, a.published))
		elif sortBy == "annotations":
			entriesWithoutTags.sort(lambda a,b: cmp(b.getNonDraftAnnotationCount(), a.getNonDraftAnnotationCount()))
			entriesWithoutLinks.sort(lambda a,b: cmp(b.getNonDraftAnnotationCount(), a.getNonDraftAnnotationCount()))
			entriesWithoutAnswers.sort(lambda a,b: cmp(b.getNonDraftAnnotationCount(), a.getNonDraftAnnotationCount()))
			entriesWithoutComments.sort(lambda a,b: cmp(b.getNonDraftAnnotationCount(), a.getNonDraftAnnotationCount()))
			invitationsWithoutResponses.sort(lambda a,b: cmp(b.getNonDraftAnnotationCount(), a.getNonDraftAnnotationCount()))
			collagesWithoutInclusions.sort(lambda a,b: cmp(b.getNonDraftAnnotationCount(), a.getNonDraftAnnotationCount()))
		return (entriesWithoutTags, entriesWithoutLinks, entriesWithoutAnswers, entriesWithoutComments, invitationsWithoutResponses, collagesWithoutInclusions)
	
	def getEntryActivityPointsForEvent(self, event):
		i = 0
		for eventType in EVENT_TYPES:
			if event == eventType:
				return self.entryActivityPointsPerEvent[i]
			i += 1
		return 0
	
	def getNonDraftNewMemberResources(self):
		return Entry.all().filter("rakontu = ", self.key()). \
			filter("draft = ", False). \
			filter("type = ", "resource"). \
			filter("resourceForNewMemberPage =", True). \
			filter("resourceForManagersAndOwnersOnly = ", False). \
			fetch(FETCH_NUMBER)
	
	def getNonDraftHelpResources(self):
		return Entry.all().filter("rakontu = ", self.key()). \
			filter("draft = ", False). \
			filter("type = ", "resource"). \
			filter("resourceForHelpPage = ", True). \
			filter("resourceForManagersAndOwnersOnly = ", False). \
			fetch(FETCH_NUMBER)
			
	def getNonDraftManagerOnlyHelpResources(self):
		return Entry.all().filter("rakontu = ", self.key()). \
			filter("draft = ", False). \
			filter("type = ", "resource"). \
			filter("resourceForManagersAndOwnersOnly = ", True). \
			fetch(FETCH_NUMBER)
	
	# ENTRIES, ANNOTATIONS, ANSWERS, LINKS - EVERYTHING
	
	def getAllFlaggedItems(self):
		entries = Entry.all().filter("rakontu = ", self.key()).filter("draft = ", False).filter("flaggedForRemoval = ", True).fetch(BIG_FETCH_NUMBER)
		annotations = Annotation.all().filter("rakontu = ", self.key()).filter("draft = ", False).filter("flaggedForRemoval = ", True).fetch(BIG_FETCH_NUMBER)
		answers = Answer.all().filter("rakontu = ", self.key()).filter("draft = ", False).filter("flaggedForRemoval = ", True).fetch(BIG_FETCH_NUMBER)
		links = Link.all().filter("rakontu = ", self.key()).filter("flaggedForRemoval = ", True).fetch(BIG_FETCH_NUMBER)
		searches = SavedSearch.all().filter("rakontu = ", self.key()).filter("flaggedForRemoval = ", True).fetch(BIG_FETCH_NUMBER)
		return (entries, annotations, answers, links, searches)
	
	def getAllFlaggedItemsAsOneList(self):
		result = []
		(entries, annotations, answers, links, searches) = self.getAllFlaggedItems()
		result.extend(links)
		result.extend(answers)
		result.extend(annotations)
		result.extend(entries)
		result.extend(searches)
		return result

	def getAllItems(self):
		entries = Entry.all().filter("rakontu = ", self.key()).filter("draft = ", False).fetch(FETCH_NUMBER)
		annotations = Annotation.all().filter("rakontu = ", self.key()).filter("draft = ", False).fetch(FETCH_NUMBER)
		answers = Answer.all().filter("rakontu = ", self.key()).filter("draft = ", False).fetch(FETCH_NUMBER)
		links = Link.all().filter("rakontu = ", self.key()).filter("inBatchEntryBuffer = ", False).fetch(FETCH_NUMBER)
		return (entries, annotations, answers, links)
	
	def getAllEntriesAnnotationsAndAnswersAsOneList(self):
		result = []
		(entries, annotations, answers, links) = self.getAllItems()
		result.extend(entries)
		result.extend(answers)
		result.extend(annotations)
		return result

	def getEntryInImportBufferWithTitle(self, title):	
		return Entry.all().filter("rakontu = ", self.key()).filter("inBatchEntryBuffer = ", True).filter("title = ", title).get()
										
	def getEntriesInImportBufferForLiaison(self, liaison):
		return Entry.all().filter("rakontu = ", self.key()).filter("inBatchEntryBuffer = ", True).filter("liaison = ", liaison.key()).fetch(FETCH_NUMBER)
	
	def getCommentsInImportBufferForLiaison(self, liaison):
		return Annotation.all().filter("rakontu = ", self.key()).filter("type = ", "comment").filter("inBatchEntryBuffer = ", True).filter("liaison = ", liaison.key()).fetch(FETCH_NUMBER)
		
	def getTagsetsInImportBufferForLiaison(self, liaison):
		return Annotation.all().filter("rakontu = ", self.key()).filter("type = ", "tag set").filter("inBatchEntryBuffer = ", True).filter("liaison = ", liaison.key()).fetch(FETCH_NUMBER)
		
	def getAllNonDraftRequests(self):
		return Annotation.all().filter("rakontu = ", self.key()).filter("type = ", "request").filter("draft = ", False).fetch(FETCH_NUMBER)
		
	def getAllNonDraftRequestsOfType(self, type):
		return Annotation.all().filter("rakontu = ", self.key()).filter("type = ", "request").filter("draft = ", False).\
			filter("typeIfRequest = ", type).fetch(FETCH_NUMBER)
		
	def getAllUncompletedNonDraftRequestsOfType(self, type):
		return Annotation.all().filter("rakontu = ", self.key()).filter("type = ", "request").filter("draft = ", False).\
				filter("typeIfRequest = ", type).filter("completedIfRequest = ", False).fetch(FETCH_NUMBER)
	
	def moveImportedEntriesOutOfBuffer(self, items):
		for item in items:
			item.draft = False
			item.inBatchEntryBuffer = False
			item.put()
			item.publish()
			
	def getAttachmentsForAllNonDraftEntries(self):
		result = []
		entries = self.getNonDraftEntries()
		for entry in entries:
			attachments =  Attachment.all().filter('entry = ', entry.key())
			result.extend(attachments)
		return result
	
	def getNonDraftTagSets(self):
		return Annotation.all().filter("rakontu = ", self.key()).filter("type = ", "tag set").filter("draft = ", False).fetch(FETCH_NUMBER)
	
	def getNonDraftTags(self):
		# cfk check - this may be too slow and may need to be updated instead when a tag set is added or removed
		tags = {}
		tagsets = self.getNonDraftTagSets()
		for tagset in tagsets:
			for tag in tagset.tagsIfTagSet:
				tags[tag] = 1
		tagsSorted = []
		tagsSorted.extend(tags.keys())
		tagsSorted.sort()
		return tagsSorted
	
	def firstPublishOrCreatedWhicheverExists(self):
		if self.firstPublish:
			# the reason this "padding" is needed is in the case of data being generated at rakontu creation,
			# when the time of item creation may actually be slightly before the "firstPublish" flag is set
			# it won't hurt to have an extra second in otherwise, anyway
			return self.firstPublish - timedelta(seconds=1)
		else:
			return self.created
	
	# QUESTIONS
	
	def getAllQuestions(self):
		return Question.all().filter("rakontu = ", self.key()).fetch(FETCH_NUMBER)
	
	def getAllQuestionsOfReferType(self, type):
		return Question.all().filter("rakontu = ", self.key()).filter("refersTo = ", type).fetch(FETCH_NUMBER)
	
	def getActiveQuestions(self):
		return Question.all().filter("rakontu = ", self.key()).filter("active = ", True).fetch(FETCH_NUMBER)
	
	def getActiveQuestionsOfType(self, type):
		return Question.all().filter("rakontu = ", self.key()).filter("refersTo = ", type).filter("active = ", True).fetch(FETCH_NUMBER)
	
	def getInactiveQuestionsOfType(self, type):
		return Question.all().filter("rakontu = ", self.key()).filter("refersTo = ", type).filter("active = ", False).fetch(FETCH_NUMBER)
	
	def getActiveMemberQuestions(self):
		return self.getActiveQuestionsOfType("member")
	
	def getActiveNonMemberQuestions(self):
		return Question.all().filter("rakontu = ", self.key()).filter("refersTo !=", "member").filter("active = ", True).fetch(FETCH_NUMBER)
		
	def getActiveMemberAndCharacterQuestions(self):
		return Question.all().filter("rakontu = ", self.key()).filter("refersTo IN ", ["character", "member"]).filter("active = ", True).fetch(FETCH_NUMBER)
	
	def hasActiveQuestionsOfType(self, type):
		return Question.all().filter("rakontu = ", self.key()).filter("refersTo = ", type).filter("active = ", True).count() > 0
	
	def hasActiveNonMemberQuestions(self):
		return Question.all().filter("rakontu = ", self.key()).filter("refersTo !=", "member").filter("active = ", True).count() > 0
		
	def hasQuestionWithSameTypeAndName(self, question):
		allQuestions = self.getAllQuestions()
		for aQuestion in allQuestions:
			if aQuestion.refersTo == question.refersTo and aQuestion.name == question.name:
				return True
		return False
	
	def AddCopyOfQuestion(self, question):
		newQuestion = Question(
							   key_name=KeyName("question"),
							   rakontu=self,
							   refersTo=question.refersTo,
							   name=question.name,
							   text=question.text,
							   type=question.type,
							   choices=question.choices,
							   multiple=question.multiple,
							   help=question.help,
							   useHelp=question.useHelp)
		newQuestion.put()
		
	def addQuestionsOfTypeFromCSV(self, type, input):
		rows = csv.reader(input.split("\n"))
		questionsToPut = []
		for row in rows:
			if len(row) >= 4 and row[0] and row[1] and row[0][0] != ";":
				refersTo = row[0].strip()
				if not refersTo in QUESTION_REFERS_TO:
					continue
				name = row[1]
				text = row[2]
				type = row[3]
				choices = []
				minValue = DEFAULT_QUESTION_VALUE_MIN
				maxValue = DEFAULT_QUESTION_VALUE_MAX
				responseIfBoolean = DEFAULT_QUESTION_BOOLEAN_RESPONSE
				if type == "ordinal" or type == "nominal":
					choices = [x.strip() for x in row[4].split(",")]
				elif type == "value":
					minAndMax = row[4].split("-")
					try:
						minValue = int(minAndMax[0])
					except:
						pass
					try:
						maxValue = int(minAndMax[1])
					except:
						pass
				elif type == "boolean":
					responseIfBoolean = row[4]
				multiple = row[5] == "yes"
				help = row[6]
				useHelp=row[7]
				question = Question(
								key_name=KeyName("question"),
								refersTo=refersTo, 
								name=name, 
								text=text, 
								type=type, 
								choices=choices, 
								multiple=multiple,
								responseIfBoolean=responseIfBoolean, 
								minIfValue=minValue, 
								maxIfValue=maxValue, 
								help=help, 
								useHelp=useHelp, 
								rakontu=self)
				questionsToPut.append(question)
		if questionsToPut:
			db.put(questionsToPut)
		
	# SEARCHES
	
	def getNonPrivateSavedSearches(self):
		return SavedSearch.all().filter("rakontu = ", self.key()).filter("private = ", False).fetch(FETCH_NUMBER)
		
	# REMOVAL
	
	def removeAllDependents(self):
		entries = Entry.all().filter("rakontu = ", self.key()).fetch(BIG_FETCH_NUMBER)
		for entry in entries:
			entry.removeAllDependents()
		db.delete(entries)
		db.delete(Member.all().filter("rakontu = ", self.key()).fetch(FETCH_NUMBER))
		db.delete(PendingMember.all().filter("rakontu = ", self.key()).fetch(FETCH_NUMBER))
		db.delete(Character.all().filter("rakontu = ", self.key()).fetch(FETCH_NUMBER))
		db.delete(Question.all().filter("rakontu = ", self.key()).fetch(FETCH_NUMBER))
		
	# IMPORT
	
	def addEntriesFromCSV(self, data, liaison):
		reader = csv.reader(data.split("\n"), delimiter=',', doublequote='"', quotechar='"')
		for row in reader:
			dateOkay = True
			if len(row) > 0 and len(row[0]) > 0 and row[0][0] != ";" and row[0][0] != "#":
				nickname = row[0].strip()
				member = self.memberWithNickname(nickname)
				if member:
					if len(row) >= 1:
						dateString = row[1].strip()
					else:
						dateString = None
						dateOkay = False
					if dateOkay:
						try:
							(year, month, day) = dateString.split("-")
						except:
							dateOkay = False
						if dateOkay:
							try:
								collected = datetime(int(year), int(month), int(day))
							except:
								collected = None
								dateOkay = False
							if dateOkay:
								if len(row) >= 3:
									type = row[2].strip()
								else:
									type = None
								typeOkay = type in ENTRY_TYPES # NOTE: does not allow translated name
								if type and typeOkay:
									if len(row) >= 4:
										title = row[3].strip()
									else:
										title = None
									if title:
										foundEntry = self.getEntryInImportBufferWithTitle(title)
										if not foundEntry:
											if len(row) >= 5:
												text = row[4].strip()
											else:
												text = "No text imported."
											entry = Entry(key_name=KeyName("entry"), rakontu=self, type=type, title=title) 
											entry.text = text
											entry.rakontu = self
											entry.creator = member
											entry.collectedOffline = True
											entry.collected = collected
											entry.liaison = liaison
											entry.inBatchEntryBuffer = True
											entry.draft = True
											entry.put()	
		
	# EXPORT
	
	def getExportOfType(self, type):
		return Export.all().filter("rakontu = ", self.key()).filter("type = ", type).get()

	def createOrRefreshExport(self, type, itemList=None, member=None, questionType=None, fileFormat="csv"):
		exportAlreadyThereForType = self.getExportOfType(type)
		if exportAlreadyThereForType:
			db.delete(exportAlreadyThereForType)
		export = Export(key_name=KeyName("export"), rakontu=self, type=type, fileFormat=fileFormat)
		exportText = ""
		if type == "csv_export_search":
			if member and member.viewEntriesList:
				if member.viewSearch:
					exportText += '"Export of search result ""%s"" for Rakontu %s"\n' % (member.viewSearch.name, self.name)
				else:
					exportText += '"Export of entries for Rakontu %s"\n' % self.name
				members = self.getActiveMembers()
				characters = self.getActiveCharacters()
				memberQuestions = self.getActiveQuestionsOfType("member")
				characterQuestions = self.getActiveQuestionsOfType("character")
				typeCount = 0
				for type in ENTRY_TYPES:
					entries = self.getNonDraftEntriesOfType(type)
					entriesToInclude = []
					for entry in entries:
						if entry.key() in member.viewEntriesList:
							entriesToInclude.append(entry)
					if entriesToInclude:
						questions = self.getActiveQuestionsOfType(type)
						exportText += '\n%s\nNumber,Title,Contributor,' % ENTRY_TYPES_PLURAL_DISPLAY[typeCount].upper()
						for question in questions:
							exportText += question.name + ","
						for question in memberQuestions:
							exportText += question.name + ","
						for question in characterQuestions:
							exportText += question.name + ","
						exportText += '\n'
						i = 0
						for entry in entriesToInclude:
							try:
								exportText += entry.csvLineWithAnswers(i+1, members, characters, questions, memberQuestions, characterQuestions) 
							except:
								pass # if it doesn't exist, move on
							i += 1
					typeCount += 1
		elif type == "csv_export_all":
			exportText += '"Export of all entries for Rakontu %s"\n' % (self.name)
			members = self.getActiveMembers()
			characters = self.getActiveCharacters()
			memberQuestions = self.getActiveQuestionsOfType("member")
			characterQuestions = self.getActiveQuestionsOfType("character")
			typeCount = 0
			for type in ENTRY_TYPES:
				entries = self.getNonDraftEntriesOfType(type)
				if entries:
					questions = self.getActiveQuestionsOfType(type)
					exportText += '\n%s\nNumber,Title,Contributor,' % ENTRY_TYPES_PLURAL_DISPLAY[typeCount].upper()
					for question in questions:
						exportText += question.name + ","
					for question in memberQuestions:
						exportText += question.name + ","
					for question in characterQuestions:
						exportText += question.name + ","
					exportText += '\n'
					for i in range(len(entries)):
						exportText += entries[i].csvLineWithAnswers(i+1, members, characters, questions, memberQuestions, characterQuestions) 
				typeCount += 1
		elif type == "xml_export":
			exportText += self.to_xml()
			for member in self.getActiveMembers():
				exportText += member.to_xml() + "\n\n"
			for pendingMember in self.getPendingMembers():
				exportText += pendingMember.to_xml() + "\n\n"
			for character in self.getActiveCharacters():
				exportText += character.to_xml() + "\n\n"
			for type in QUESTION_REFERS_TO:
				for question in self.getActiveQuestionsOfType(type):
					exportText += question.to_xml() + "\n\n"
			for search in self.getNonPrivateSavedSearches():
				exportText += search.to_xml() + "\n\n"
				for searchRef in search.getQuestionReferences():
					exportText += searchRef.to_xml() + "\n\n"
			for entry in self.getNonDraftEntries():
				exportText += entry.to_xml() + "\n\n"
				for attachment in entry.getAttachments():
					exportText += attachment.to_xml() + "\n\n"
				for annotation in entry.getNonDraftAnnotations():
					exportText += annotation.to_xml() + "\n\n"
				for answer in entry.getAnswers():
					exportText += answer.to_xml() + "\n\n"
				for link in entry.getAllLinks():
					exportText += link.to_xml() + "\n\n"
		elif type == "liaisonPrint_simple":
			exportText += '<html><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8">'
			exportText += '<title>Printed from Rakontu</title></head><body>'
			if itemList:
				for item in itemList:
					try:
						exportText += item.PrintText()
					except: 
						pass
			elif member:
				if member.viewEntriesList:
					for entry in self.getNonDraftEntries():
						if entry.key() in member.viewEntriesList:
							try:
								exportText += entry.PrintText()
							except:
								pass
			exportText += "</body></html>"
		elif type == "exportQuestions":
			exportText += '; refersTo,name,text,type,choices or min-max or boolean "yes" text,multiple,help,help for using\n'
			questions = self.getActiveQuestionsOfType(questionType)
			for question in questions:
				cells = []
				cells.append(question.refersTo)
				cells.append(question.name)
				cells.append(question.text)
				cells.append(question.type)
				if question.type == "nominal" or question.type == "ordinal":
					choicesToReport = []
					for choice in question.choices:
						if len(choice):
							choicesToReport.append(choice)
					cells.append(", ".join(choicesToReport))
				elif question.type == "value":
					cells.append("%s-%s" % (question.minIfValue, question.maxIfValue))
				elif question.type == "boolean":
					cells.append(question.responseIfBoolean)
				else:
					cells.append("")
				if question.multiple:
					cells.append("yes")
				else:
					cells.append("no")
				cells.append(question.help)
				cells.append(question.useHelp)
				exportText += CleanUpCSV(cells) + "\n"
		export.data = db.Text(exportText)
		export.put()
		return export
		
# ============================================================================================
# ============================================================================================
class Question(db.Model):
# ============================================================================================
# ============================================================================================

	appRocketTimeStamp = TzDateTimeProperty(auto_now=True)
	rakontu = db.ReferenceProperty(Rakontu, collection_name="questions_to_rakontu")
	refersTo = db.StringProperty(choices=QUESTION_REFERS_TO, required=True) 
	
	name = db.StringProperty(required=True, default=DEFAULT_QUESTION_NAME)
	text = db.StringProperty(required=True)
	type = db.StringProperty(choices=QUESTION_TYPES, default="text") # text, boolean, ordinal, nominal, value
	
	active = db.BooleanProperty(default=True) # used to hide questions no longer being used, same as members
	
	minIfValue = db.IntegerProperty(default=DEFAULT_QUESTION_VALUE_MIN, indexed=False)
	maxIfValue = db.IntegerProperty(default=DEFAULT_QUESTION_VALUE_MAX, indexed=False)
	responseIfBoolean = db.StringProperty(default=DEFAULT_QUESTION_BOOLEAN_RESPONSE, indexed=False) # what the checkbox label should say
	multiple = db.BooleanProperty(default=False) # whether multiple answers are allowed (for ordinal/nominal only)
	choices = db.StringListProperty(default=[""] * MAX_NUM_CHOICES_PER_QUESTION, indexed=False) 
	
	help = db.TextProperty() # appears to person answering question
	help_formatted = db.TextProperty()
	help_format = db.StringProperty(default=DEFAULT_TEXT_FORMAT, indexed=False)
	
	useHelp = db.TextProperty() # appears to manager choosing question, about when to use it
	useHelp_formatted = db.TextProperty()
	useHelp_format = db.StringProperty(default=DEFAULT_TEXT_FORMAT, indexed=False)
	
	created = TzDateTimeProperty(auto_now_add=True)
	
	inBatchEntryBuffer = db.BooleanProperty(default=False) # in the process of being imported, not "live" yet
	
	def isOrdinalOrNominal(self):
		return self.type == "ordinal" or self.type == "nominal"
	
	def isTextOrValue(self):
		return self.type == "text" or self.type == "value"
	
	def numChoices(self):
		return len(self.choices)

	def refersToEntryType(self):
		return self.refersTo == "story" \
			or self.refersTo == "pattern" \
			or self.refersTo == "collage" \
			or self.refersTo == "invitation" \
			or self.refersTo == "resource" 
			
	def refersToMemberOrCharacter(self):
		return self.refersTo == "member" or self.refersTo == "character"
	
	def keyAsString(self):
		return "%s" % self.key()
	
	def getAnswerCount(self):
		return Answer.all().filter("question = ", self.key()).count()
	
# ============================================================================================
# ============================================================================================
class Member(db.Model):
# ============================================================================================
# ============================================================================================

	appRocketTimeStamp = TzDateTimeProperty(auto_now=True)
	rakontu = db.ReferenceProperty(Rakontu, required=True, collection_name="members_to_rakontu")
	nickname = db.StringProperty(default=NO_NICKNAME_SET)
	isOnlineMember = db.BooleanProperty(default=True)
	liaisonIfOfflineMember = db.SelfReferenceProperty(default=None, collection_name="offline_members_to_liaisons")
	googleAccountID = db.StringProperty() # none if off-line member
	googleAccountEmail = db.StringProperty() # blank if off-line member
	
	# active: members are never removed, just inactivated, so entries can still link to something.
	# inactive members do not show up in any display, but they can be "reactivated" by issuing an invitation
	# to the same google email as before.
	active = db.BooleanProperty(default=True) 
	
	governanceType = db.StringProperty(choices=GOVERNANCE_ROLE_TYPES, default="member") # can only be set by managers
	helpingRoles = db.ListProperty(bool, default=[False, False, False]) # members can choose
	helpingRolesAvailable = db.ListProperty(bool, default=[True, True, True], indexed=False) # managers can ban members from roles
	
	guideIntro = db.TextProperty(default=DEFAULT_GUIDE_INTRO) # appears on the welcome and get help pages if the member is a guide
	guideIntro_formatted = db.TextProperty()
	guideIntro_format = db.StringProperty(default=DEFAULT_TEXT_FORMAT, indexed=False)
	
	profileText = db.TextProperty(default=NO_PROFILE_TEXT)
	profileText_formatted = db.TextProperty()
	profileText_format = db.StringProperty(default=DEFAULT_TEXT_FORMAT, indexed=False)
	profileImage = db.BlobProperty(default=None) # optional, resized to 100x60
	acceptsMessages = db.BooleanProperty(default=True, indexed=False) # other members can send emails to their google email (without seeing it)
	preferredTextFormat = db.StringProperty(default=DEFAULT_TEXT_FORMAT, indexed=False)
	
	timeZoneName = db.StringProperty(default=DEFAULT_TIME_ZONE) # members choose these in their prefs page
	timeFormat = db.StringProperty(default=DEFAULT_TIME_FORMAT, indexed=False) # how they want to see dates
	dateFormat = db.StringProperty(default=DEFAULT_DATE_FORMAT, indexed=False) # how they want to see times
	showAttachedImagesInline = db.BooleanProperty(default=False)
	
	joined = TzDateTimeProperty(auto_now_add=True)
	firstVisited = db.DateTimeProperty()
	lastEnteredEntry = db.DateTimeProperty()
	lastEnteredAnnotation = db.DateTimeProperty()
	lastEnteredLink = db.DateTimeProperty()
	lastAnsweredQuestion = db.DateTimeProperty()
	lastReadAnything = db.DateTimeProperty()
	
	nudgePoints = db.IntegerProperty(default=DEFAULT_START_NUDGE_POINTS) # accumulated through participation
	
	viewTimeEnd = TzDateTimeProperty(auto_now_add=True)
	viewTimeFrameInSeconds = db.IntegerProperty(default=WEEK_SECONDS, indexed=False)
	viewNudgeCategories = db.ListProperty(bool, default=[True] * NUM_NUDGE_CATEGORIES, indexed=False)
	viewSearch = db.ReferenceProperty(None, collection_name="member_to_search", indexed=False)
	viewDetails = db.BooleanProperty(default=False, indexed=False)
	viewEntryTypes = db.ListProperty(bool, default=[True, True, False, False, False]) # stories and invitations on by default
	viewHomeOptionsOnTop = db.BooleanProperty(default=False)
	viewEntriesList = db.ListProperty(db.Key, indexed=False)
	
	# CREATION
	
	def initialize(self):
		self.timeZoneName = self.rakontu.defaultTimeZoneName
		self.timeFormat = self.rakontu.defaultTimeFormat
		self.dateFormat = self.rakontu.defaultDateFormat
		if self.viewTimeEnd.tzinfo is None:
			self.viewTimeEnd = self.viewTimeEnd.replace(tzinfo=pytz.utc)
		self.profileText_formatted = db.Text("<p>%s</p>" % self.profileText)
		self.guideIntro_formatted = db.Text("<p>%s</p>" % self.guideIntro)
		# caller does put
		
	# INFO
	
	def isMember(self):
		return True
		
	def googleUserEmailOrNotOnline(self):
		if self.isOnlineMember:
			return self.googleAccountEmail
		return "%s (%s)" % (TERMS["term_none"], TEMPLATE_TERMS["template_offline"])
	
	# GOVERNANCE
	
	def isRegularMember(self):
		return self.governanceType == "member"
	
	def isManager(self):
		return self.governanceType == "manager"
	
	def isOwner(self):
		return self.governanceType == "owner"
	
	def isManagerOrOwner(self):
		return self.governanceType == "manager" or self.governanceType == "owner"
	
	def governanceTypeForDisplay(self):
		# GOVERNANCE_ROLE_TYPES_DISPLAY = ["member", "manager", "owner"]
		if self.governanceType == "member":
			return GOVERNANCE_ROLE_TYPES_DISPLAY[0]
		elif self.governanceType == "manager":
			return GOVERNANCE_ROLE_TYPES_DISPLAY[1]
		elif self.governanceType == "owner":
			return GOVERNANCE_ROLE_TYPES_DISPLAY[2]
	
	def governanceTypeForDisplayNotShowingOwner(self):
		# GOVERNANCE_ROLE_TYPES_DISPLAY = ["member", "manager", "owner"]
		if self.governanceType == "member":
			return GOVERNANCE_ROLE_TYPES_DISPLAY[0]
		elif self.governanceType == "manager":
			return GOVERNANCE_ROLE_TYPES_DISPLAY[1]
		elif self.governanceType == "owner":
			return GOVERNANCE_ROLE_TYPES_DISPLAY[1]
	
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
	
	def isLiaisonOrManagerOrOwner(self):
		return self.isLiaison() or self.isManagerOrOwner()
	
	def hasAnyHelpingRole(self):
		return self.helpingRoles[0] or self.helpingRoles[1] or self.helpingRoles[2]

	def helpingRolesForDisplay(self):
		result = []
		if self.helpingRoles[0]:
			result.append(HELPING_ROLE_TYPES_DISPLAY[0])
		if self.helpingRoles[1]:
			result.append(HELPING_ROLE_TYPES_DISPLAY[1])
		if self.helpingRoles[2]:
			result.append(HELPING_ROLE_TYPES_DISPLAY[2])
		return result

	def canTakeOnAnyHelpingRole(self):
		return self.helpingRolesAvailable[0] or self.helpingRolesAvailable[1] or self.helpingRolesAvailable[2]
	
	def canEditTags(self):
		return (NUM_TAGS_IN_TAG_SET) and (self.isCurator() and self.isManagerOrOwner()) or (self.isCurator() and self.rakontu.allowNonManagerCuratorsToEditTags)
	
	# BROWSING
	
	def getViewStartTime(self):
		return self.viewTimeEnd - timedelta(seconds=self.viewTimeFrameInSeconds)
			
	def setViewTimeFrameFromTimeFrameString(self, frame):
		for aFrame, seconds in TIME_FRAMES:
			if frame == aFrame:
				if aFrame == TIMEFRAME_EVERYTHING:
					self.viewTimeEnd = datetime.now(tz=pytz.utc)
					self.viewTimeFrameInSeconds = (self.viewTimeEnd - self.rakontu.firstPublishOrCreatedWhicheverExists()).seconds \
						+ (self.viewTimeEnd - self.rakontu.firstPublishOrCreatedWhicheverExists()).days * DAY_SECONDS
				else:
					self.viewTimeFrameInSeconds = seconds
				# caller should do the put
				break
			
	def getFrameStringForViewTimeFrame(self):
		for aFrame, seconds in TIME_FRAMES:
			if self.viewTimeFrameInSeconds == seconds:
				return aFrame
		return TIMEFRAME_EVERYTHING
			
	def setTimeFrameToStartAtFirstPublish(self):
		self.viewTimeEnd = self.rakontu.firstPublish + timedelta(seconds=self.viewTimeFrameInSeconds)
		# caller should do the put
		
	def firstVisitURL(self):
		if self.isManagerOrOwner():
			return BuildURL("dir_manage", "url_first", rakontu=self.rakontu)
		else:
			return BuildURL("dir_visit", "url_new", rakontu=self.rakontu)
		
	# CONTRIBUTIONS
	
	def getAllItemsAttributedToMember(self):
		allItems = []
		allItems.extend(self.getNonDraftEntriesAttributedToMember())
		allItems.extend(self.getNonDraftAnnotationsAttributedToMember())
		allItems.extend(self.getNonDraftAnswersAboutEntriesAttributedToMember())
		allItems.extend(self.getLinksCreatedByMember())
		return allItems
	
	def getAnswers(self):
		return Answer.all().filter("referent = ", self.key()).fetch(FETCH_NUMBER)
	
	def getAnswerForQuestion(self, question):
		return Answer.all().filter("referent = ", self.key()).filter("question = ", question.key()).get()
	
	def getAnswerForMemberQuestion(self, question):
		return Answer.all().filter("question = ", question.key()).filter("referent =", self.key()).get()
	
	def getAnswersForQuestionAndMember(self, question, member):
		return Answer.all().filter("question = ", question.key()).filter("referent =", self.key()).filter("creator = ", member.key()).fetch(FETCH_NUMBER)
	
	def getNonDraftEntriesAttributedToMember(self):
		return Entry.all().filter("creator = ", self.key()).filter("draft = ", False).filter("character = ", None).fetch(BIG_FETCH_NUMBER)
	
	def getNonDraftAnnotationsAttributedToMember(self):
		return Annotation.all().filter("creator = ", self.key()).filter("draft = ", False).filter("character = ", None).fetch(BIG_FETCH_NUMBER)
	
	def getNonDraftAnswersAboutEntriesAttributedToMember(self):
		return Answer.all().filter("creator = ", self.key()).filter("draft = ", False).filter("character = ", None).filter("referentType = ", "entry").fetch(BIG_FETCH_NUMBER)
	
	def getNonDraftLiaisonedEntries(self):
		return Entry.all().filter("liaison = ", self.key()).filter("draft = ", False).fetch(BIG_FETCH_NUMBER)
	
	def getNonDraftLiaisonedAnnotations(self):
		return Annotation.all().filter("liaison = ", self.key()).filter("draft = ", False).fetch(BIG_FETCH_NUMBER)
	
	def getNonDraftLiaisonedAnswers(self):
		return Answer.all().filter("liaison = ", self.key()).filter("draft = ", False).filter("referentType = ", "entry").fetch(BIG_FETCH_NUMBER)
	
	def getLinksCreatedByMember(self):
		return Link.all().filter("creator = ", self.key()).fetch(BIG_FETCH_NUMBER)
	
	# DRAFTS
	
	def getDraftEntries(self):
		return Entry.all().filter("creator = ", self.key()).filter("draft = ", True).fetch(FETCH_NUMBER)
	
	def getDraftAnswersForEntry(self, entry):
		return Answer.all().filter("creator = ", self.key()).filter("draft = ", True).filter("referent = ", entry.key()).fetch(FETCH_NUMBER)
	
	def getDraftAnnotations(self):
		return Annotation.all().filter("creator = ", self.key()).filter("draft = ", True).fetch(FETCH_NUMBER)
	
	def getEntriesWithDraftAnswers(self):
		answers = Answer.all().filter("creator = ", self.key()).filter("draft = ", True).filter("referentType = ", "entry").fetch(FETCH_NUMBER)
		entries = {}
		for answer in answers:
			if not answer.referent.draft: # don't include entries that are themselves in draft format
				if not entries.has_key(answer.referent.getKeyName()):
					entries[answer.referent.getKeyName()] = answer.referent
		return entries.values()
	
	# DISPLAY
	
	def getKeyName(self):
		return self.key().name()
	
	def linkString(self):
		if self.isOnlineMember:
			offlineImageString = ""
		else:
			offlineImageString = '<img src="/images/offline.png" alt="offline member"> '
		return '%s<a href="%s?%s">%s</a>' % (offlineImageString, self.urlWithoutQuery(), self.urlQuery(), self.nickname)
	
	def askLinkString(self):
		return '<a href="%s?%s">%s</a>' % (self.askUrlWithoutQuery(), self.urlQuery(), self.nickname)
	
	def linkURL(self):
		return '%s?%s' % (self.urlWithoutQuery(), self.urlQuery())
		
	def urlWithoutQuery(self):
		return "/%s/%s" % (DIRS["dir_visit"], URLS["url_member"])

	def askUrlWithoutQuery(self):
		return "/%s/%s" % (DIRS["dir_visit"], URLS["url_ask"])

	def urlQuery(self):
		return "%s=%s" % (URL_IDS["url_query_member"], self.getKeyName())

	def imageEmbed(self):
		return '<img src="/%s/%s?%s=%s" class="bordered">' % (DIRS["dir_visit"], URLS["url_image"], URL_IDS["url_query_member"], self.getKeyName())
	
	def getSavedSearches(self):
		return SavedSearch.all().filter("creator = ", self.key()).fetch(FETCH_NUMBER)
	
	def getPrivateSavedSearches(self):
		return SavedSearch.all().filter("creator = ", self.key()).filter("private = ", True).fetch(FETCH_NUMBER)
	
# ============================================================================================
# ============================================================================================
class PendingMember(db.Model): # person invited to join rakontu but not yet logged in
# ============================================================================================
# ============================================================================================

	appRocketTimeStamp = TzDateTimeProperty(auto_now=True)
	rakontu = db.ReferenceProperty(Rakontu, required=True, collection_name="pending_members_to_rakontu")
	email = db.StringProperty(required=True) # must match google account
	invited = TzDateTimeProperty(auto_now_add=True)
	governanceType = db.StringProperty(default="member")
	
# ============================================================================================
# ============================================================================================
class Character(db.Model): # optional fictions to anonymize entries but provide some information about intent
# ============================================================================================
# ============================================================================================

	appRocketTimeStamp = TzDateTimeProperty(auto_now=True)
	rakontu = db.ReferenceProperty(Rakontu, required=True, collection_name="characters_to_rakontu")
	name = db.StringProperty(required=True)
	created = TzDateTimeProperty(auto_now_add=True)
	active = db.BooleanProperty(default=True)
	
	description = db.TextProperty(default=None) # appears on rakontu page
	description_formatted = db.TextProperty()
	description_format = db.StringProperty(default=DEFAULT_TEXT_FORMAT, indexed=False)
	
	etiquetteStatement = db.TextProperty(default=None) # appears under "how to be [name]"
	etiquetteStatement_formatted = db.TextProperty()
	etiquetteStatement_format = db.StringProperty(default=DEFAULT_TEXT_FORMAT, indexed=False)
	
	image = db.BlobProperty(default=None) # optional
	
	def isMember(self):
		return False
	
	def getAllItemsAttributedToCharacter(self):
		allItems = []
		allItems.extend(self.getNonDraftEntriesAttributedToCharacter())
		allItems.extend(self.getNonDraftAnnotationsAttributedToCharacter())
		allItems.extend(self.getNonDraftAnswersAboutEntriesAttributedToCharacter())
		return allItems
	
	def getNonDraftEntriesAttributedToCharacter(self):
		return Entry.all().filter("character = ", self.key()).filter("draft = ", False).fetch(BIG_FETCH_NUMBER)
	
	def getNonDraftAnnotationsAttributedToCharacter(self):
		return Annotation.all().filter("character = ", self.key()).filter("draft = ", False).fetch(BIG_FETCH_NUMBER)
	
	def getNonDraftAnswersAboutEntriesAttributedToCharacter(self):
		return Answer.all().filter("character = ", self.key()).filter("draft = ", False).filter("referentType = ", "entry").fetch(BIG_FETCH_NUMBER)

	def getKeyName(self):
		return self.key().name()
	
	def linkString(self):
		return '<a href="%s?%s">%s</a>' % (self.urlWithoutQuery(), self.urlQuery(), self.name)
		
	def linkURL(self):
		return '%s?%s' % (self.urlWithoutQuery(), self.urlQuery())
		
	def urlWithoutQuery(self):
		return "/%s/%s" % (DIRS["dir_visit"], URLS["url_character"])

	def urlQuery(self):
		return "%s=%s" % (URL_IDS["url_query_character"], self.key().name())
	
	def imageEmbed(self):
		return '<img src="/%s/%s?%s=%s">' % (DIRS["dir_visit"], URLS["url_image"], URL_IDS["url_query_character"], self.getKeyName())
		
	def getAnswers(self):
		return Answer.all().filter("referent = ", self.key()).fetch(FETCH_NUMBER)
	
	def getAnswerForQuestion(self, question):
		return Answer.all().filter("referent = ", self.key()).filter("question = ", question.key()).get()
		
# ============================================================================================
# ============================================================================================
class SavedSearch(db.Model):
# ============================================================================================
# ============================================================================================

	appRocketTimeStamp = TzDateTimeProperty(auto_now=True)
	rakontu = db.ReferenceProperty(Rakontu, required=True, collection_name="searches_to_rakontu")
	creator = db.ReferenceProperty(Member, required=True, collection_name="searches_to_member")
	private = db.BooleanProperty(default=True)
	created = TzDateTimeProperty(auto_now_add=True)
	name = db.StringProperty(default=DEFAULT_SEARCH_NAME)
	# the type is mainly to make it display in a list of entries, but it may be useful later anyway
	type = db.StringProperty(default="search filter") 
	
	flaggedForRemoval = db.BooleanProperty(default=False)
	flagComment = db.StringProperty(indexed=False)

	words_anyOrAll = db.StringProperty(choices=ANY_ALL, default="any")
	words_locations = db.ListProperty(bool, default=[True] * (len(ANNOTATION_TYPES) + 1))
	words = db.StringListProperty()
	
	tags_anyOrAll = db.StringProperty(choices=ANY_ALL)
	tags = db.StringListProperty()
	
	overall_anyOrAll = db.StringProperty(choices=ANY_ALL, default="any")
	answers_anyOrAll = db.StringProperty(choices=ANY_ALL, default="any")
	creatorAnswers_anyOrAll = db.StringProperty(choices=ANY_ALL, default="any")
	
	comment = db.TextProperty(default="")
	comment_formatted = db.TextProperty()
	comment_format = db.StringProperty(default=DEFAULT_TEXT_FORMAT, indexed=False)

	def copyDataFromOtherSearchAndPut(self, search):
		self.private = True
		self.name = "%s %s" % (TERMS["term_copy_of"], search.name)
		self.words_anyOrAll = search.words_anyOrAll
		self.words_locations = []
		self.words_locations.extend(search.words_locations)
		self.words = []
		self.words.extend(search.words)
		self.tags_anyOrAll = search.tags_anyOrAll
		self.tags = []
		self.tags.extend(search.tags)
		self.answers_anyOrAll = search.answers_anyOrAll
		self.creatorAnswers_anyOrAll = search.creatorAnswers_anyOrAll
		self.comment = db.Text(search.comment)
		self.comment_formatted = db.Text(search.comment_formatted)
		self.comment_format = search.comment_format
		for ref in search.getQuestionReferences():
			myRef = SavedSearchQuestionReference(
												key_name=KeyName("searchref"),
												rakontu=self.rakontu, 
												creator=self.creator,
												search=self, 
												question=ref.question,
												type=ref.type,
												order=ref.order,
												answer=ref.answer,
												comparison=ref.comparison
												)
			myRef.put()
		self.put()
	
	def getQuestionReferences(self):
		return SavedSearchQuestionReference.all().filter("search = ", self.key()).fetch(FETCH_NUMBER)
	
	def getQuestionReferencesOfType(self, type):
		return SavedSearchQuestionReference.all().filter("search = ", self.key()).filter("type = ", type).fetch(FETCH_NUMBER)
	
	def getEntryQuestionRefs(self):
		return self.getQuestionReferencesOfType("entry")
	
	def getCreatorQuestionRefs(self):
		return self.getQuestionReferencesOfType("creator")
	
	def getIncomingLinks(self):
		return Link.all().filter("itemTo = ", self.key()).fetch(FETCH_NUMBER)
	
	def deleteAllDependents(self):
		for ref in self.getQuestionReferences():
			db.delete(ref)
			
	def notPrivate(self):
		return self.private == False
	
	def displayString(self):
		if self.private:
			return self.name
		else:
			return "%s (%s)" % (self.name, self.creator.nickname)
	
	# LINKING TO PATTERNS
		
	def getKeyName(self):
		return self.key().name()
	
	def linkString(self):
		return '<a href="%s?%s">%s</a>' % (self.urlWithoutQuery(), self.urlQuery(), self.name)
		
	def linkURL(self):
		return '%s?%s' % (self.urlWithoutQuery(), self.urlQuery())
		
	def urlWithoutQuery(self):
		return "/%s/%s" % (DIRS["dir_visit"], URLS["url_home"])

	def urlQuery(self):
		return "%s=%s" % (URL_IDS["url_query_search_filter"], self.key().name())

	def shortFormattedText(self):
		result = ""
		if self.words:
			result += '<p>%s %s "%s"</p>' % (self.words_anyOrAll, TERMS["term_of_the_words"], ",".join(self.words))
		if self.tags:
			result += '<p>%s %s "%s"</p>' % (self.tags_anyOrAll, TERMS["term_of_the_tags"], ",".join(self.tags))
		entryRefs = self.getEntryQuestionRefs()
		if entryRefs:
			result += "<p>%s %s " % (self.answers_anyOrAll, TERMS["term_of_the_entry_questions"])
			for ref in entryRefs:
				result += '%s %s ' % (ref.question.text, ref.answer)
			result += "</p>"
		creatorRefs = self.getCreatorQuestionRefs()
		if creatorRefs:
			result += "<p>%s %s " % (self.creatorAnswers_anyOrAll, TERMS["term_of_the_creator_questions"])
			for ref in creatorRefs:
				result += ' %s %s ' % (ref.question.text, ref.answer)
			result += "</p>"
		return result
	
	def isEntry(self):
		# has to do with linking to patterns
		return False 
	
# ============================================================================================
# ============================================================================================
class SavedSearchQuestionReference(db.Model):
# ============================================================================================
# ============================================================================================

	appRocketTimeStamp = TzDateTimeProperty(auto_now=True)
	created = TzDateTimeProperty(auto_now_add=True)
	rakontu = db.ReferenceProperty(Rakontu, required=True, collection_name="searchrefs_to_rakontu")
	search = db.ReferenceProperty(SavedSearch, required=True, collection_name="question_refs_to_saved_search")
	question = db.ReferenceProperty(Question, required=True, collection_name="question_refs_to_question")
	
	type = db.StringProperty() # entry or creator
	order = db.IntegerProperty()
	answer = db.StringProperty()
	comparison = db.StringProperty()
	
# ============================================================================================
# ============================================================================================
class Answer(db.Model):
# ============================================================================================
# ============================================================================================

	appRocketTimeStamp = TzDateTimeProperty(auto_now=True)
	rakontu = db.ReferenceProperty(Rakontu, collection_name="answers_to_rakontu")
	question = db.ReferenceProperty(Question, collection_name="answers_to_questions")
	referent = db.ReferenceProperty(None, collection_name="answers_to_objects") # entry or member
	referentType = db.StringProperty(default="entry") # entry or member
	creator = db.ReferenceProperty(Member, collection_name="answers_to_creators") 
	
	collectedOffline = db.BooleanProperty(default=False)
	liaison = db.ReferenceProperty(Member, default=None, collection_name="answers_to_liaisons")
	character = db.ReferenceProperty(Character, default=None, collection_name="answers_to_characters")
	
	draft = db.BooleanProperty(default=True)
	inBatchEntryBuffer = db.BooleanProperty(default=False) # in the process of being imported, not "live" yet
	flaggedForRemoval = db.BooleanProperty(default=False)
	flagComment = db.StringProperty(indexed=False)
	
	answerIfBoolean = db.BooleanProperty(default=False)
	answerIfText = db.StringProperty(default="")
	answerIfMultiple = db.StringListProperty(default=[""] * MAX_NUM_CHOICES_PER_QUESTION)
	answerIfValue = db.IntegerProperty(default=0)
	
	created = TzDateTimeProperty(auto_now_add=True)
	edited = TzDateTimeProperty(auto_now_add=True)
	published = TzDateTimeProperty(auto_now_add=True)
	
	entryNudgePointsWhenPublished = db.ListProperty(int, default=[0] * NUM_NUDGE_CATEGORIES)
	entryActivityPointsWhenPublished = db.IntegerProperty(default=0)
	
	def isAnswer(self):
		return True
	
	def getClassName(self):
		return self.__class__.__name__
	
	# IMPORTANT METHODS
	
	def publish(self):
		if self.referentType == "entry":
			self.draft = False
			self.published = datetime.now(pytz.utc)
			self.put()
			self.referent.recordAction("added", self)
			if self.referentType == "entry":
				for i in range(NUM_NUDGE_CATEGORIES):
					self.entryNudgePointsWhenPublished[i] = self.referent.nudgePoints[i]
				self.entryActivityPointsWhenPublished = self.referent.activityPoints
				self.put()
			self.creator.nudgePoints += self.rakontu.getMemberNudgePointsForEvent("answering question")
			self.creator.lastAnsweredQuestion = datetime.now(pytz.utc)
			self.creator.put()
			self.rakontu.lastPublish = self.published
			self.rakontu.put()
				
	# DISPLAY
		
	def getImageLinkForType(self):
		return'<img src="/images/answers.png" alt="answer" border="0">'
	
	def displayStringShort(self):
		return self.displayString(includeQuestionText=False, includeQuestionName=False)
	
	def displayString(self, includeQuestionText=True, includeQuestionName=False):
		result = ""
		if includeQuestionText:
			result += self.question.text + " "
		if includeQuestionName:
			result += self.question.name + ": "
		if self.question.type == "boolean":
			if self.answerIfBoolean: 
				result += TERMS["term_yes"]
			else:
				result += TERMS["term_no"]
		elif self.question.type == "text":
			result += self.answerIfText
		elif self.question.type == "ordinal" or self.question.type == "nominal":
			if self.question.multiple:
				answersToReport = []
				for answer in self.answerIfMultiple:
					if len(answer):
						answersToReport.append(answer)
				result +=  ", ".join(answersToReport)
			else:
				result +=  self.answerIfText
		elif self.question.type == "value":
			result +=  "%s" % self.answerIfValue
		return result
	
	def getKeyName(self):
		return self.key().name()
	
	def linkString(self):
		return self.displayString()
	
	def urlQuery(self):
		return "%s=%s" % (URL_IDS["url_query_answer"], self.getKeyName())
	
	def linkStringWithQuestionName(self):
		return self.displayString(includeQuestionName=True, includeQuestionText=False)
	
	def linkStringWithQuestionText(self):
		return self.displayString(includeQuestionName=False, includeQuestionText=True, )
	
	def linkStringWithQuestionNameAndReferentLink(self):
		return "%s for %s" % (self.linkStringWithQuestionName(), self.referent.linkString())
		
	def linkStringWithQuestionTextAndReferentLink(self):
		return "%s for %s" % (self.linkStringWithQuestionText(), self.referent.linkString())
	
	def PrintText(self):
		return '<p>%s %s (%s)</p><hr>' \
			% (self.question.text, self.displayStringShort(), self.memberNickNameOrCharacterName())
		
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
class Entry(db.Model):					   # story, invitation, collage, pattern, resource
# ============================================================================================
# ============================================================================================

	appRocketTimeStamp = TzDateTimeProperty(auto_now=True)
	type = db.StringProperty(choices=ENTRY_TYPES, required=True) 
	title = db.StringProperty(required=True, default=DEFAULT_UNTITLED_ENTRY_TITLE)
	text = db.TextProperty(default=NO_TEXT_IN_ENTRY)
	text_formatted = db.TextProperty()
	text_format = db.StringProperty(default=DEFAULT_TEXT_FORMAT, indexed=False)
	
	resourceForHelpPage = db.BooleanProperty(default=False)
	resourceForNewMemberPage = db.BooleanProperty(default=False)
	resourceForManagersAndOwnersOnly = db.BooleanProperty(default=False)

	rakontu = db.ReferenceProperty(Rakontu, collection_name="entries_to_rakontu")
	creator = db.ReferenceProperty(Member, collection_name="entries")
	collectedOffline = db.BooleanProperty(default=False)
	liaison = db.ReferenceProperty(Member, default=None, collection_name="entries_to_liaisons")
	character = db.ReferenceProperty(Character, default=None, collection_name="entries_to_characters")
	
	draft = db.BooleanProperty(default=True)
	inBatchEntryBuffer = db.BooleanProperty(default=False) # in the process of being imported, not "live" yet
	flaggedForRemoval = db.BooleanProperty(default=False)
	flagComment = db.StringProperty(indexed=False)
	
	collected = TzDateTimeProperty(default=None)
	created = TzDateTimeProperty(auto_now_add=True)
	edited = TzDateTimeProperty(auto_now_add=True)
	published = TzDateTimeProperty(auto_now_add=True)
	
	lastRead = TzDateTimeProperty(default=None)
	lastAnnotatedOrAnsweredOrLinked = TzDateTimeProperty(default=None)
	
	activityPoints = db.IntegerProperty(default=0)
	nudgePoints = db.ListProperty(int, default=[0] * NUM_NUDGE_CATEGORIES)
	
	def isEntry(self):
		return True
	
	def getClassName(self):
		return self.__class__.__name__
	
	# IMPORTANT METHODS
	
	def publish(self):
		self.draft = False
		self.published = datetime.now(pytz.utc)
		self.recordAction("added", self) # does a put
		self.creator.nudgePoints += self.rakontu.getMemberNudgePointsForEvent("adding %s" % self.type)
		self.creator.lastEnteredEntry = datetime.now(pytz.utc)
		self.creator.put()
		for answer in self.getAnswersForMember(self.creator):
			answer.publish()
		self.rakontu.lastPublish = self.published
		if not self.rakontu.firstPublish:
			self.rakontu.firstPublish = self.published
		self.rakontu.put()
		
	def recordAction(self, action, referent):
		if referent.__class__.__name__ == "Entry":
			if action == "read":
				eventType = "reading"
				self.lastRead = datetime.now(tz=pytz.utc)
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
		self.activityPoints += self.rakontu.getEntryActivityPointsForEvent(eventType)
		self.put()
		
	def lastTouched(self):
		if self.lastRead and self.lastAnnotatedOrAnsweredOrLinked and self.published:
			return max(self.lastRead, max(self.lastAnnotatedOrAnsweredOrLinked, self.published))
		elif self.lastRead and self.published:
			return max(self.lastRead, self.published)
		elif self.lastAnnotatedOrAnsweredOrLinked and self.published:
			return max(self.lastAnnotatedOrAnsweredOrLinked, self.published)
		elif self.published:
			return self.published
		else:
			return None
		
	def lastPublishedOrAnnotated(self):
		if self.lastAnnotatedOrAnsweredOrLinked:
			return self.lastAnnotatedOrAnsweredOrLinked
		else:
			return self.published
		
	def removeAllDependents(self):
		db.delete(self.getAttachments())
		db.delete(self.getAllLinks())
		db.delete(self.getAnswers())
		db.delete(self.getAnnotations())
		
	def satisfiesSearchCriteria(self, search, entryRefs, creatorRefs):
		if not search.words and not search.tags and not entryRefs and not creatorRefs: # empty search
			return True
		if search.overall_anyOrAll == "any":
			satisfiesWords = False
			satisfiesTags = False
			satisfiesEntryQuestions = False
			satisfiesCreatorQuestions = False
		else:
			satisfiesWords = True
			satisfiesTags = True
			satisfiesEntryQuestions = True
			satisfiesCreatorQuestions = True
		if search.words:
			satisfiesWords = self.satisfiesWordSearch(search.words_anyOrAll, search.words_locations, search.words)
		if search.tags:
			satisfiesTags = self.satisfiesTagSearch(search.tags_anyOrAll, search.tags)
		if entryRefs:
			satisfiesEntryQuestions = self.satisfiesQuestionSearch(search.answers_anyOrAll, entryRefs, False)
		if creatorRefs:
			satisfiesCreatorQuestions = self.satisfiesQuestionSearch(search.creatorAnswers_anyOrAll, creatorRefs, True)
		if search.overall_anyOrAll == "any":
			return satisfiesWords or satisfiesTags or satisfiesEntryQuestions or satisfiesCreatorQuestions
		else:
			return satisfiesWords and satisfiesTags and satisfiesEntryQuestions and satisfiesCreatorQuestions
		
	def satisfiesQuestionSearch(self, anyOrAll, refs, aboutCreator):
		numAnswerSearchesSatisfied = 0
		for ref in refs:
			match = False
			if aboutCreator:
				try: # in case creator doesn't exist
					if self.character:
						answer = self.character.getAnswerForQuestion(ref.question)
					else:
						if self.creator.active:
							answer = self.creator.getAnswerForQuestion(ref.question)
						else:
							return False
					answers = [answer]
				except:
					return False
			else:
				answers = self.getAnswersForQuestion(ref.question)
			if answers:
				for answer in answers:
					if answer:
						if ref.question.type == "text":
							if ref.comparison == "contains":
								match = caseInsensitiveFind(answer.answerIfText, ref.answer)
							elif ref.comparison == "is":
								match = answer.answerIfText.lower() == ref.answer.lower()
						elif ref.question.type == "value":
							if ref.comparison == "is less than":
								try:
									answerValue = int(ref.answer)
									match = answer.answerIfValue < answerValue
								except:
									match = False
							elif ref.comparison == "is greater than":
								try:
									answerValue = int(ref.answer)
									match = answer.answerIfValue > answerValue
								except:
									match = False
							elif ref.comparison == "is":
								try:
									answerValue = int(ref.answer)
									match = answer.answerIfValue == answerValue
								except:
									match = False
						elif ref.question.type == "ordinal" or ref.question.type == "nominal":
							if ref.question.multiple:
								match = ref.answer in answer.answerIfMultiple
							else:
								match = ref.answer == answer.answerIfText
						elif ref.question.type == "boolean":
							if ref.answer == "yes":
								match = answer.answerIfBoolean == True
							else:
								match = answer.answerIfBoolean == False
						if match:
							break # don't need to check if more than one answer matches
			if match:
				numAnswerSearchesSatisfied += 1
		if anyOrAll == "any":
			return numAnswerSearchesSatisfied > 0
		else:
			return numAnswerSearchesSatisfied >= len(refs)
	
	def satisfiesWordSearch(self, anyOrAll, locations, words):
		numWordSearchesSatisfied = 0
		for word in words:
			match = False
			if locations[0]: #"in the title"
				match = match or caseInsensitiveFind(self.title, word) 
			if locations[1]: #"in the text"
				match = match or caseInsensitiveFind(self.text, word) 
			if locations[2]: #"in a comment"
				match = match or self.wordIsFoundInAComment(word)
			if locations[3]: #"in a request"
				match = match or self.wordIsFoundInARequest(word)
			if locations[4]: #"in a nudge comment"
				match = match or self.wordIsFoundInANudgeComment(word)
			if locations[5]: #"in a link comment"
				match = match or self.wordIsFoundInALinkComment(word)
			if match:
				numWordSearchesSatisfied += 1
		if anyOrAll == "any":
			return numWordSearchesSatisfied > 0
		else:
			return numWordSearchesSatisfied >= len(words)

	def wordIsFoundInAComment(self, word):
		comments = self.getNonDraftAnnotationsOfType("comment")
		for comment in comments:
			if caseInsensitiveFind(comment.longString, word):
				return True
		return False
	
	def wordIsFoundInARequest(self, word):
		requests = self.getNonDraftAnnotationsOfType("request")
		for request in requests:
			if caseInsensitiveFind(request.longString, word):
				return True
		return False
	
	def wordIsFoundInANudgeComment(self, word):
		nudges = self.getNonDraftAnnotationsOfType("nudge")
		for nudge in nudges:
			if caseInsensitiveFind(nudge.shortString, word):
				return True
		return False
	
	def wordIsFoundInALinkComment(self, word):
		links = self.getAllLinks()
		for link in links:
			if caseInsensitiveFind(link.comment, word):
				return True
		return False
	
	def satisfiesTagSearch(self, anyOrAll, words):
		numWordSearchesSatisfied = 0
		for word in words:
			match = False
			tagsets = self.getNonDraftAnnotationsOfType("tag set")
			for tagset in tagsets:
				for tag in tagset.tagsIfTagSet:
					match = match or caseInsensitiveFind(tag, word)
			if match:
				numWordSearchesSatisfied += 1
		if anyOrAll == "any":
			return numWordSearchesSatisfied > 0
		else:
			return numWordSearchesSatisfied >= len(words)

	def satisfiesEntryTypesCriteria(self, entryTypesToInclude):
		i = 0
		for type in ENTRY_TYPES:
			if type == self.type:
				if not entryTypesToInclude[i]:
					return False
			i += 1
		return True
	
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
		return Annotation.all().filter("entry = ", self.key()).filter("type = ", "nudge").filter("creator = ", member.key()).fetch(FETCH_NUMBER)
	
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
	
	def nudgePointsForMemberViewOptions(self, options):
		result = 0
		for i in range(NUM_NUDGE_CATEGORIES):
			if options[i]:
				result += self.nudgePoints[i]
		return result
	
	# ANNOTATIONS, ANSWERS, LINKS
	
	def getAnnotations(self):
		return Annotation.all().filter("entry =", self.key()).fetch(FETCH_NUMBER)
	
	def getNonDraftAnnotations(self):
		return Annotation.all().filter("entry =", self.key()).filter("draft = ", False).fetch(FETCH_NUMBER)
	
	def getNonDraftAnnotationCount(self):
		return Annotation.all().filter("entry =", self.key()).filter("draft = ", False).count()
	
	def getNonDraftAnnotationsOfType(self, type):
		return Annotation.all().filter("entry =", self.key()).filter("type = ", type).filter("draft = ", False).fetch(FETCH_NUMBER)
	
	def hasComments(self):
		return Annotation.all().filter("entry =", self.key()).filter("type = ", "comment").filter("draft = ", False).count() > 0
		
	def getComments(self):
		return Annotation.all().filter("entry =", self.key()).filter("type = ", "comment").filter("draft = ", False).fetch(FETCH_NUMBER)
		
	def getAttachments(self):
		return Attachment.all().filter("entry =", self.key()).fetch(FETCH_NUMBER)
	
	def getAnswers(self):
		return Answer.all().filter("referent = ", self.key()).fetch(FETCH_NUMBER)
	
	def getAnswersForQuestion(self, question):
		return Answer.all().filter("referent = ", self.key()).filter("question = ", question.key()).fetch(FETCH_NUMBER)
	
	def getNonDraftAnswers(self):
		return Answer.all().filter("referent = ", self.key()).filter("draft = ", False).fetch(FETCH_NUMBER)

	def getAnswersForMember(self, member):
		return Answer.all().filter("referent = ", self.key()).filter("creator = ", member.key()).fetch(FETCH_NUMBER)
	
	def getMembersAndCharactersWhoHaveAnsweredQuestionsAboutMe(self):
		members = []
		characters = []
		answers = Answer.all().filter("referent = ", self.key()).fetch(FETCH_NUMBER)
		for answer in answers:
			if answer.creator and answer.creator.active:
				if answer.creator.isMember():
					# have to do this silly thing because it won't do an equality test on objects, only on keys
				 	foundIt = False
				 	for member in members:
				 		if answer.creator.key() == member.key():
				 			foundIt = True
				 			break
				 	if not foundIt:
				 		members.append(answer.creator)
				else:
				 	foundIt = False
				 	for character in characters:
				 		if answer.creator.key() == character.key():
				 			foundIt = True
				 			break
				 	if not foundIt:
				 		characters.append(answer.creator)
		return (members, characters)
	
	def getAnswersForCharacter(self, character):
		return Answer.all().filter("referent = ", self.key()).filter("creator = ", character.key()).fetch(FETCH_NUMBER)
	
	def hasAnswersForCharacter(self, character):
		return Answer.all().filter("referent = ", self.key()).filter("creator = ", character.key()).count()
	
	def getAnswerForMemberAndQuestion(self, member, question):
		return Answer.all().filter("referent = ", self.key()).filter("creator = ", member.key()).filter("question = ", question.key()).get()
	
	def getAnswerForCharacterAndQuestion(self, character, question):
		return Answer.all().filter("referent = ", self.key()).filter("character = ", character.key()).filter("question = ", question.key()).get()
	
	def getAllLinks(self):
		result = []
		outgoingLinks = Link.all().filter("itemFrom = ", self.key()).fetch(FETCH_NUMBER)
		incomingLinks = Link.all().filter("itemTo = ", self.key()).fetch(FETCH_NUMBER)
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
		return Link.all().filter("itemFrom = ", self.key()).filter("type = ", type).filter("inBatchEntryBuffer = ", False).fetch(FETCH_NUMBER)
	
	def hasOutgoingLinksOfType(self, type):
		return Link.all().filter("itemFrom = ", self.key()).filter("type = ", type).filter("inBatchEntryBuffer = ", False).count() > 0
	
	def getResponses(self):
		result = []
		links = Link.all().filter("itemFrom = ", self.key()).filter("type = ", "responded").filter("inBatchEntryBuffer = ", False).fetch(FETCH_NUMBER)
		for link in links:
			result.append(link.itemTo)
		return result
	
	def getIncomingLinksOfType(self, type):
		return Link.all().filter("itemTo = ", self.key()).filter("type = ", type).filter("inBatchEntryBuffer = ", False).fetch(FETCH_NUMBER)
	
	def getOutgoingLinks(self):
		return Link.all().filter("itemFrom = ", self.key()).filter("inBatchEntryBuffer = ", False).fetch(FETCH_NUMBER)
	
	def getIncomingLinks(self):
		return Link.all().filter("itemTo = ", self.key()).filter("inBatchEntryBuffer = ", False).fetch(FETCH_NUMBER)
	
	def getIncomingLinksOfTypeFromType(self, type, fromType):
		result = []
		incomingLinks = self.getIncomingLinksOfType(type)
		for link in incomingLinks:
			if link.itemFrom.type == fromType:
				result.append(link)
		return result
	
	def copyCollectedDateToAllAnswersAndAnnotations(self):
		annotations = self.getAnnotations()
		for annotation in annotations:
			annotation.collected = self.collected
			annotation.put()
		answers = self.getAnswers()
		for answer in answers:
			answer.collected = self.collected
			answer.put()
			
	def getAllNonDraftDependents(self):
		result = []
		result.extend(self.getNonDraftAnnotations())
		result.extend(self.getNonDraftAnswers())
		result.extend(self.getAllLinks())
		return result
	
	# DISPLAY
	
	def displayString(self):
		return self.title
	
	def getKeyName(self):
		return self.key().name()
	
	def linkString(self):
		return '<a href="%s?%s" %s>%s</a>' % (self.urlWithoutQuery(), self.urlQuery(), self.getTooltipText(), self.title)
		
	def linkURL(self):
		return '%s?%s' % (self.urlWithoutQuery(), self.urlQuery())
		
	def urlWithoutQuery(self):
		return "/%s/%s" % (DIRS["dir_visit"], URLS["url_read"])

	def urlQuery(self):
		return "%s=%s" % (URL_IDS["url_query_entry"], self.key().name())

	def typeAsURL(self):
		return URLForEntryType(self.type)
	
	def typeForDisplay(self):
		return DisplayTypeForEntryType(self.type)
	
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
	
	def displayTextWithInlineAttachmentLinks(self):
		result = self.text_formatted
		attachments = self.getAttachments()
		for i in range(len(attachments)):
			findString = "#%s#" % (i+1)
			if result.find(findString) >= 0:
				if attachments[i].isImage():
					result = result.replace(findString, '<img src="/img?attachment_id=%s">' % attachments[i].key())
				else:
					result = result.replace(findString, '<a href="/visit/attachment?attachment_id=%s">%s</a>' % (attachments[i].key(), attachments[i].fileName))
		return result
	
	def csvLineWithAnswers(self, index, members, characters, questions, memberQuestions, characterQuestions):
		parts = []
		(members, characters) = self.getMembersAndCharactersWhoHaveAnsweredQuestionsAboutMe()
		for member in members:
			parts.append("\n%s" % index)
			parts.append(self.title)
			parts.append(member.nickname)
			# questions about entry
			for question in questions:
				answer = self.getAnswerForMemberAndQuestion(member, question)
				if answer: 
					parts.append(answer.displayStringShort())
				else:
					parts.append("")
			# about teller
			for question in memberQuestions:
				answer = member.getAnswerForQuestion(question)
				if answer:
					parts.append(answer.displayStringShort())
				else:
					parts.append("")
			# pad spaces for character questions
			for question in characterQuestions:
				parts.append("")
		for character in characters:
			parts.append("\n%s" % index)
			parts.append(self.title)
			parts.append(character.name)
			# questions about entry
			for question in questions:
				answer = self.getAnswerForCharacterAndQuestion(character, question)
				if answer: 
					parts.append(answer.displayStringShort())
				else:
					parts.append("")
			# pad spaces for member questions
			for question in memberQuestions:
				parts.append("")
			# about character attributed to
			for question in characterQuestions:
				answer = character.getAnswerForQuestion(question)
				if answer:
					parts.append(answer.displayStringShort())
				else:
					parts.append("")
		if not parts:
			parts = [str(index), self.title, '\n']
		return CleanUpCSV(parts)
	
	def PrintText(self):
		return "<p><b>%s</b> (%s)</p><p>%s</p><hr>" % (self.title, self.type, self.text_formatted)
		
	# SEARCH
	
	def satisfiesSearch(self, search, refs):
		pass

# ============================================================================================
# ============================================================================================
class Link(db.Model):						 # related, retold, reminded, responded, included
# ============================================================================================
# ============================================================================================
	appRocketTimeStamp = TzDateTimeProperty(auto_now=True)
	type = db.StringProperty(choices=LINK_TYPES, required=True) 
	# how links go: 
	#	related: any entry to any entry
	#	retold: story to story
	# 	reminded: story or resource to story
	#   responded: invitation to story
	#	included: collage to story
	#   referenced: pattern to saved search - note, this is the only non-entry link item, and it is ALWAYS itemTo
	itemFrom = db.ReferenceProperty(None, collection_name="fromLinks", required=True)
	itemTo = db.ReferenceProperty(None, collection_name="toLinks", required=True)
	rakontu = db.ReferenceProperty(Rakontu, required=True, collection_name="links_to_rakontu")
	creator = db.ReferenceProperty(Member, collection_name="links")
	
	# links cannot be in draft mode and cannot be entered in batch mode
	flaggedForRemoval = db.BooleanProperty(default=False)
	flagComment = db.StringProperty(indexed=False)
	
	created = TzDateTimeProperty(auto_now_add=True)
	published = TzDateTimeProperty()
	inBatchEntryBuffer = db.BooleanProperty(default=False)
	
	comment = db.StringProperty(default="", indexed=False)
	
	entryNudgePointsWhenPublished = db.ListProperty(int, default=[0] * NUM_NUDGE_CATEGORIES)
	entryActivityPointsWhenPublished = db.IntegerProperty(default=0)
	
	# IMPORTANT METHODS
	
	def publish(self):
		self.published = datetime.now(pytz.utc)
		self.put()
		if self.itemTo.isEntry():
			self.itemTo.recordAction("added", self)
		self.itemFrom.recordAction("added", self)
		for i in range(NUM_NUDGE_CATEGORIES):
			self.entryNudgePointsWhenPublished[i] = self.itemFrom.nudgePoints[i]
		self.entryActivityPointsWhenPublished = self.itemFrom.activityPoints
		self.put()
		self.creator.nudgePoints = self.itemFrom.rakontu.getMemberNudgePointsForEvent("adding %s link" % self.type)
		self.creator.lastEnteredLink = datetime.now(pytz.utc)
		self.creator.put()
		self.itemFrom.rakontu.lastPublish = self.published
		if not self.itemFrom.rakontu.firstPublish:
			self.itemFrom.rakontu.firstPublish = self.published
		self.itemFrom.rakontu.put()
		
	# MEMBERS
		
	def attributedToMember(self):
		return True
	
	# DISPLAY
		
	def getImageLinkForType(self):
		return'<img src="/images/link.png" alt="link" border="0">'
	
	def displayString(self):
		result = '%s, %s' % (self.itemTo.linkString(), DisplayTypeForLinkType(self.type))
		if self.comment:
			result += ", (%s)" % self.comment
		return result
	
	def getKeyName(self):
		return self.key().name()
	
	def linkString(self):
		return self.displayString()
	
	def urlQuery(self):
		return "%s=%s" % (URL_IDS["url_query_link"], self.getKeyName())
	
	def linkStringWithFromItem(self):
		result = self.itemFrom.linkString()
		if self.comment:
			result += ", (%s)" % self.comment
		return result
	
# ============================================================================================
# ============================================================================================
class Attachment(db.Model):								   # binary attachments to entries
# ============================================================================================
# ============================================================================================

	appRocketTimeStamp = TzDateTimeProperty(auto_now=True)
	created = TzDateTimeProperty(auto_now_add=True)
	name = db.StringProperty()
	mimeType = db.StringProperty() # from ACCEPTED_ATTACHMENT_MIME_TYPES
	fileName = db.StringProperty() # as uploaded
	data = db.BlobProperty() # there is a practical limit on this size - cfk look at
	entry = db.ReferenceProperty(Entry, collection_name="attachments")
	rakontu = db.ReferenceProperty(Rakontu, required=True, collection_name="attachments_to_rakontu")
	
	def getKeyName(self):
		return self.key().name()
	
	def linkString(self):
		return '<a href="%s?%s">%s</a>' % (self.urlWithoutQuery(), self.urlQuery(), self.fileName)
		
	def linkURL(self):
		return '%s?%s' % (self.urlWithoutQuery(), self.urlQuery())
		
	def urlWithoutQuery(self):
		return "/%s/%s" % (DIRS["dir_visit"], URLS["url_attachment"])

	def urlQuery(self):
		return "%s=%s" % (URL_IDS["url_query_attachment"], self.getKeyName())
	
	def isImage(self):
		return self.mimeType == "image/jpeg" or self.mimeType == "image/png"
	
	def imageEmbed(self):
		return '<img src="/%s/%s?%s=%s">' % (DIRS["dir_visit"], URLS["url_image"], URL_IDS["url_query_attachment"], self.getKeyName())
	
	def attachmentEmbed(self):
		return '<a href="/%s?%s=%s">%s</a>' %(URLS["url_attachment"], URL_IDS["url_query_attachment"], self.getKeyName(), self.fileName)
	
# ============================================================================================
# ============================================================================================
class Annotation(db.Model):								# tag set, comment, request, nudge
# ============================================================================================
# ============================================================================================

	appRocketTimeStamp = TzDateTimeProperty(auto_now=True)
	type = db.StringProperty(choices=ANNOTATION_TYPES, required=True)
	rakontu = db.ReferenceProperty(Rakontu, required=True, collection_name="annotations_to_rakontu")
	entry = db.ReferenceProperty(Entry, required=True, collection_name="annotations")
	creator = db.ReferenceProperty(Member, collection_name="annotations")
	
	draft = db.BooleanProperty(default=True)
	inBatchEntryBuffer = db.BooleanProperty(default=False) # in the process of being imported, not "live" yet
	flaggedForRemoval = db.BooleanProperty(default=False)
	flagComment = db.StringProperty(indexed=False)
	
	shortString = db.StringProperty() # comment/request subject, nudge comment
	
	longString = db.TextProperty() # comment/request body
	longString_formatted = db.TextProperty()
	longString_format = db.StringProperty(default=DEFAULT_TEXT_FORMAT, indexed=False)
	
	tagsIfTagSet = db.StringListProperty(default=[""] * NUM_TAGS_IN_TAG_SET)
	valuesIfNudge = db.ListProperty(int, default=[0] * NUM_NUDGE_CATEGORIES)
	typeIfRequest = db.StringProperty(choices=REQUEST_TYPES)
	completedIfRequest = db.BooleanProperty(default=False)

	collectedOffline = db.BooleanProperty(default=False)
	liaison = db.ReferenceProperty(Member, default=None, collection_name="annotations_liaisoned")
	character = db.ReferenceProperty(Character, default=None, collection_name="annotations_to_characters")

	collected = TzDateTimeProperty(default=None)
	created = TzDateTimeProperty(auto_now_add=True)
	edited = TzDateTimeProperty()
	published = TzDateTimeProperty()
	
	entryNudgePointsWhenPublished = db.ListProperty(int, default=[0] * NUM_NUDGE_CATEGORIES)
	entryActivityPointsWhenPublished = db.IntegerProperty(default=0)
	
	def isAnnotation(self):
		return True
	
	def getClassName(self):
		return self.__class__.__name__
	
	def isCommentOrRequest(self):
		return self.type == "comment" or self.type == "request"
	
	# IMPORTANT METHODS
	
	def publish(self):
		self.draft = False
		self.published = datetime.now(pytz.utc)
		self.put()
		self.entry.recordAction("added", self)
		for i in range(NUM_NUDGE_CATEGORIES):
			self.entryNudgePointsWhenPublished[i] = self.entry.nudgePoints[i]
		self.entryActivityPointsWhenPublished = self.entry.activityPoints
		self.put()
		self.creator.nudgePoints += self.rakontu.getMemberNudgePointsForEvent("adding %s" % self.type)
		self.creator.put()
		self.rakontu.lastPublish = self.published
		self.rakontu.put()

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
		return URLForAnnotationType(self.type)
	
	def typeForDisplay(self):
		return DisplayTypeForAnnotationType(self.type)
	
	def displayString(self, includeType=True):
		if self.type == "comment":
			if self.shortString:
				return self.shortString
			elif self.longString_formatted:
				return self.longString_formatted
			else:
				return "no content"
		if self.type == "request":
			if self.shortString:
				if includeType:
					return "%s (%s)" % (self.shortString, self.typeIfRequest)
				else:
					return self.shortString
			elif self.longString_formatted:
				if includeType:
					return "%s (%s)" % (self.longString_formatted, self.typeIfRequest)
				else:
					return self.longString_formatted
			else:
				return "no content"
		elif self.type == "tag set":
			tagsToReport = []
			for tag in self.tagsIfTagSet:
				if len(tag):
					tagsToReport.append(tag)
			return  ", ".join(tagsToReport)
		elif self.type == "nudge":
			result = []
			for i in range(NUM_NUDGE_CATEGORIES):
				if self.valuesIfNudge[i] != 0:
					result.append("%s %s" % (self.valuesIfNudge[i], self.rakontu.nudgeCategories[i]))
			if self.shortString:
				result.append("(%s)" % self.shortString)
			return ", ".join(result)
		
	def displayStringShortAndWithoutTags(self):
		return self.displayString(includeType=False)
	
	def PrintText(self):
		if self.isCommentOrRequest():
			return '<p>%s "%s" (%s)<div style="padding: 0px 16px 0px 16px;">%s</div></p><hr>\n\n' % \
				(DisplayTypeForAnnotationType(self.type), self.shortString, self.memberNickNameOrCharacterName(), self.longString_formatted)
		else:
			return '<p>%s "%s" (%s)</p><hr>\n\n' % \
				(self.type, self.displayString(), self.memberNickNameOrCharacterName())
		
	def getKeyName(self):
		return self.key().name()
	
	def linkString(self):
		if self.type == "comment" or self.type == "request":
			return '<a href="%s?%s">%s</a>' % (self.urlWithoutQuery(), self.urlQuery(), self.shortString)
		else:
			return self.displayString()
		
	def linkURL(self):
		return '%s?%s' % (self.urlWithoutQuery(), self.urlQuery())
		
	def urlWithoutQuery(self):
		return "/%s/%s" % (DIRS["dir_visit"], URLS["url_read_annotation"])

	def urlQuery(self):
		return "%s=%s" % (URL_IDS["url_query_annotation"], self.key().name())
		
	def linkStringWithEntryLink(self):
		return "%s for %s" % (self.linkString(), self.entry.linkString())
		
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
class Help(db.Model):		 # context-sensitive help string - appears as title hover on icon 
# ============================================================================================
# ============================================================================================

	appRocketTimeStamp = TzDateTimeProperty(auto_now=True)
	created = TzDateTimeProperty(auto_now_add=True)
	type = db.StringProperty() # info, tip, caution
	name = db.StringProperty() # links to name in template
	text = db.StringProperty(indexed=False) # text to show user (plain text)
	
# ============================================================================================
# ============================================================================================
class Skin(db.Model):		 # style sets to change look of each Rakontu
# ============================================================================================
# ============================================================================================

	appRocketTimeStamp = TzDateTimeProperty(auto_now=True)
	created = TzDateTimeProperty(auto_now_add=True)
	name = db.StringProperty(required=True) 
	
	font_general = db.StringProperty(indexed=False) # on everything except buttons and headers
	font_top = db.StringProperty(indexed=False)
	font_menus = db.StringProperty(indexed=False)
	font_buttons = db.StringProperty(indexed=False)
	font_headers = db.StringProperty(indexed=False)
	
	color_background_general = db.StringProperty(indexed=False) # on all pages
	color_background_excerpt = db.StringProperty(indexed=False) # behind story texts and other "highlighted" boxes
	color_background_entry = db.StringProperty(indexed=False) # to indicate the user is entering data
	color_background_menus = db.StringProperty(indexed=False) # menu backgrounds
	color_background_menus_hover =  db.StringProperty(indexed=False) # menu backgrounds when hovering over
		
	color_background_grid_top = db.StringProperty(indexed=False) # entry grid on home page, annotation grid on entry page
	color_background_grid_bottom = db.StringProperty(indexed=False) # same but on bottom of grid (should be "faded" from top)
		
	color_background_button = db.StringProperty(indexed=False) # button at bottom of pages
	color_background_button_hover = db.StringProperty(indexed=False) # when button is hovered over
		
	color_border_normal = db.StringProperty(indexed=False) # around everything
	color_border_input_hover = db.StringProperty(indexed=False) # lights up when mouse is over entries (text, drop-down box)
	color_border_image = db.StringProperty(indexed=False) # border around images
		
	color_text_link = db.StringProperty(indexed=False) # links in text
	color_text_link_hover = db.StringProperty(indexed=False) # link light-up on hover (usually white, constrasts with background_link_hover)
	color_background_link_hover = db.StringProperty(indexed=False) # light-up effect for links

	color_text_plain = db.StringProperty(indexed=False) # plain text - usually black
	color_text_excerpt = db.StringProperty(indexed=False) # text color in excerpts
	color_text_menus = db.StringProperty(indexed=False) # text color in menus
	color_text_menus_hover = db.StringProperty(indexed=False) # text color in menus when hovering over
	color_text_buttons = db.StringProperty(indexed=False) # text color on buttons
	color_text_h1 = db.StringProperty(indexed=False) # h1 text
	color_text_h2 = db.StringProperty(indexed=False) # h2 text
	color_text_h3 = db.StringProperty(indexed=False) # h3 text
	color_text_label_hover = db.StringProperty(indexed=False) # color of labels, like checkbox names
	

	def getPropertiesAsDictionary(self):
		result = {}
		properties = Skin.properties()
		for key in properties.keys():
			result[key] = getattr(self, key)
		return result

# ============================================================================================
# ============================================================================================
class Export(db.Model):		 # data prepared for export, in XML or CSV or TXT format
# ============================================================================================
# ============================================================================================
	
	appRocketTimeStamp = TzDateTimeProperty(auto_now=True)
	rakontu = db.ReferenceProperty(Rakontu, required=True, collection_name="export_to_rakontu")
	type = db.StringProperty()
	fileFormat = db.StringProperty()
	created = TzDateTimeProperty(auto_now_add=True)
	data = db.TextProperty()
	
	def getKeyName(self):
		return self.key().name()
	
	def linkString(self):
		return '<a href="%s?%s">%s</a>' % (self.urlWithoutQuery(), self.urlQuery(), self.type)
		
	def linkURL(self):
		return '%s?%s' % (self.urlWithoutQuery(), self.urlQuery())
		
	def urlWithoutQuery(self):
		return "/%s/%s" % (DIRS["dir_visit"], URLS["url_export"])

	def urlQuery(self):
		if self.fileFormat == "csv":
			return "%s=%s" % (URL_IDS["url_query_export_csv"], self.getKeyName())
		elif self.fileFormat == "txt":
			return "%s=%s" % (URL_IDS["url_query_export_txt"], self.getKeyName())
		elif self.fileFormat == "xml":
			return "%s=%s" % (URL_IDS["url_query_export_xml"], self.getKeyName())

# ============================================================================================
# ============================================================================================
# SOME DB FETCHING METHODS - all get and fetch calls are in this file
# ============================================================================================
# ============================================================================================


def AllRakontus():
	return Rakontu.all().fetch(FETCH_NUMBER)

def AllHelps():
	return Help.all().fetch(FETCH_NUMBER)

def AllSkins():
	return Skin.all().fetch(FETCH_NUMBER)

def AllSystemQuestions():
	return Question.all().filter("rakontu = ", None).fetch(FETCH_NUMBER)

def SystemQuestionsOfType(type):
	return Question.all().filter("rakontu = ", None).filter("refersTo = ", type).fetch(FETCH_NUMBER)

def SystemEntriesOfType(type):
	Entry.all().filter("rakontu = ", None).filter("type = ", type).fetch(FETCH_NUMBER)


