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
import csv

from site_configuration import *

from google.appengine.ext import db

def DebugPrint(text, msg="print"):
	logging.info(">>>>>>>> %s >>>>>>>> %s" %(msg, text))

def stripTags(text):
	if text:
		pattern = re.compile(r'<.*?>')
		return pattern.sub('', text)
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

DEVELOPMENT = True
FETCH_NUMBER = 1000

MEMBER_TYPES = ["member", "on-line member", "off-line member", "liaison", "curator", "guide", "manager", "owner"]
HELPING_ROLE_TYPES = ["curator", "guide", "liaison"]
GOVERNANCE_ROLE_TYPES = ["member", "manager", "owner"]

EVENT_TYPES = ["downdrift", \
			"reading", "adding story", "adding pattern", "adding collage", "adding invitation", "adding resource", \
			"adding retold link", "adding reminded link", "adding related link", "adding included link", "adding responded link", \
			"answering question", "adding tag set", "adding comment", "adding request", "adding nudge"]


ENTRY_TYPES = ["story", "invitation", "collage", "pattern", "resource"]
ENTRY_TYPES_PLURAL = ["stories", "invitations", "collages", "patterns", "resources"]
LINK_TYPES = ["retold", "reminded", "responded", "related", "included"]

ANNOTATION_TYPES = ["tag set", "comment", "request", "nudge"]
ANNOTATION_TYPES_URLS = ["tagset", "comment", "request", "nudge"]
ENTRY_AND_ANNOTATION_TYPES = ["story", "pattern", "collage", "invitation", "resource", "answer", "tag set", "comment", "request", "nudge"]
ENTRY_AND_ANNOTATION_TYPES_URLS = ["story", "pattern", "collage", "invitation", "resource", "answer", "tagset", "comment", "request", "nudge"]
STORY_ENTRY_TYPE_INDEX = 0
ANSWERS_ENTRY_TYPE_INDEX = 5

TIME_UNIT_STRINGS = {"minute": MINUTE_SECONDS, 
					"hour": HOUR_SECONDS,
					"day": DAY_SECONDS,
					"week": WEEK_SECONDS,
					"month": MONTH_SECONDS,
					"year": YEAR_SECONDS,}

NUM_QUESTION_REFERS_TO = 7
QUESTION_REFERS_TO = ["story", "pattern", "collage", "invitation", "resource", "member", "character"]
QUESTION_REFERS_TO_PLURAL = ["stories", "patterns", "collages", "invitations", "resources", "members", "characters"]
QUESTION_TYPES = ["boolean", "text", "ordinal", "nominal", "value"]

ANY_ALL = ["any", "all"]
SEARCH_LOCATIONS = ["in the entry text", "in a comment", "in a request", "in a nudge comment", "in a link comment"]
ANSWER_COMPARISON_TYPES = ["contains", "is", "is greater than", "is less than"]

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
	tagline = db.StringProperty(default="", indexed=False) # appears under name, optional
	image = db.BlobProperty(default=None) # appears on all pages, should be small (100x60 is best)
	contactEmail = db.StringProperty(default=DEFAULT_CONTACT_EMAIL) # sender address for emails sent from site
	
	description = db.TextProperty(default=None) # appears on "about community" page
	description_formatted = db.TextProperty() # formatted texts kept separate for re-editing original
	description_format = db.StringProperty(default=DEFAULT_TEXT_FORMAT, indexed=False)
	
	etiquetteStatement = db.TextProperty(default=None) # appears on "about community" page
	etiquetteStatement_formatted = db.TextProperty()
	etiquetteStatement_format = db.StringProperty(default=DEFAULT_TEXT_FORMAT, indexed=False)
	
	welcomeMessage = db.TextProperty(default=DEFAULT_WELCOME_MESSAGE) # appears only on new member welcome page
	welcomeMessage_formatted = db.TextProperty()
	welcomeMessage_format = db.StringProperty(default=DEFAULT_TEXT_FORMAT, indexed=False)
	
	active = db.BooleanProperty(default=True)
	
	defaultTimeZoneName = db.StringProperty(default=DEFAULT_TIME_ZONE, indexed=False) # appears on member preferences page
	defaultTimeFormat = db.StringProperty(default=DEFAULT_TIME_FORMAT, indexed=False) # appears on member preferences page
	defaultDateFormat = db.StringProperty(default=DEFAULT_DATE_FORMAT, indexed=False) # appears on member preferences page
	
	created = TzDateTimeProperty(auto_now_add=True) 
	lastPublish = TzDateTimeProperty(default=None)
	firstPublish = TzDateTimeProperty(default=None)
	firstPublishSet = db.BooleanProperty(default=False) # whether the first publish date was set yet
	
	maxNumAttachments = db.IntegerProperty(choices=NUM_ATTACHMENT_CHOICES, default=DEFAULT_MAX_NUM_ATTACHMENTS, indexed=False)

	maxNudgePointsPerEntry = db.IntegerProperty(default=DEFAULT_MAX_NUDGE_POINTS_PER_ENTRY, indexed=False)
	memberNudgePointsPerEvent = db.ListProperty(int, default=DEFAULT_MEMBER_NUDGE_POINT_ACCUMULATIONS, indexed=False)
	nudgeCategories = db.StringListProperty(default=DEFAULT_NUDGE_CATEGORIES, indexed=False)
	nudgeCategoryQuestions = db.StringListProperty(default=DEFAULT_NUDGE_CATEGORY_QUESTIONS, indexed=False)

	entryActivityPointsPerEvent = db.ListProperty(int, default=DEFAULT_ARCTICLE_ACTIVITY_POINT_ACCUMULATIONS, indexed=False)
	
	allowCharacter = db.ListProperty(bool, default=DEFAULT_ALLOW_CHARACTERS, indexed=False)
	allowEditingAfterPublishing = db.ListProperty(bool, default=DEFAULT_ALLOW_EDITING_AFTER_PUBLISHING, indexed=False)
	allowNonManagerCuratorsToEditTags = db.BooleanProperty(default=False, indexed=False)
	
	roleReadmes = db.ListProperty(db.Text, default=[db.Text(DEFAULT_ROLE_READMES[0]), db.Text(DEFAULT_ROLE_READMES[1]), db.Text(DEFAULT_ROLE_READMES[2])])
	roleReadmes_formatted = db.ListProperty(db.Text, default=[db.Text(""), db.Text(""), db.Text("")])
	roleReadmes_formats = db.StringListProperty(default=DEFAULT_ROLE_READMES_FORMATS, indexed=False)
	
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
		
	def getActiveAndInactiveMembers(self):
		return Member.all().filter("community = ", self.key()).fetch(FETCH_NUMBER)
	
	def getActiveMembers(self):
		return Member.all().filter("community = ", self.key()).filter("active = ", True).fetch(FETCH_NUMBER)
	
	def getInactiveMembers(self):
		return Member.all().filter("community = ", self.key()).filter("active = ", False).fetch(FETCH_NUMBER)
	
	def getActiveOnlineMembers(self):
		return Member.all().filter("community = ", self.key()).filter("active = ", True).filter("isOnlineMember = ", True).fetch(FETCH_NUMBER)
	
	def getActiveOfflineMembers(self):
		return Member.all().filter("community = ", self.key()).filter("active = ", True).filter("isOnlineMember = ", False).fetch(FETCH_NUMBER)
	
	def getInactiveOfflineMembers(self):
		return Member.all().filter("community = ", self.key()).filter("active = ", False).filter("isOnlineMember = ", False).fetch(FETCH_NUMBER)
	
	def getActiveAndInactiveOfflineMembers(self):
		return Member.all().filter("community = ", self.key()).filter("active = ", False).filter("isOnlineMember = ", False).fetch(FETCH_NUMBER)
	
	def getGuides(self):
		result = []
		onlineMembers = Member.all().filter("community = ", self.key()).filter("active = ", True).filter("isOnlineMember = ", True).fetch(FETCH_NUMBER)
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
	
	def getActiveCharacters(self):
		return Character.all().filter("community = ", self.key()).filter("active = ", True).fetch(FETCH_NUMBER)
	
	def getInactiveCharacters(self):
		return Character.all().filter("community = ", self.key()).filter("active = ", False).fetch(FETCH_NUMBER)
	
	def hasAtLeastOneCharacterEntryAllowed(self, entryTypeIndex):
		return self.allowCharacter[entryTypeIndex] or len(self.getActiveCharacters()) > 0

	def hasActiveCharacters(self):
		return Character.all().filter("community = ", self.key()).filter("active = ", True).count() > 0
	
	# ENTRIES
	
	def getNonDraftEntries(self):
		return Entry.all().filter("community = ", self.key()).filter("draft = ", False).fetch(FETCH_NUMBER)
	
	def getNonDraftEntriesInReverseTimeOrder(self):
		return Entry.all().filter("community = ", self.key()).filter("draft = ", False).order("-published").fetch(FETCH_NUMBER)
	
	def getNonDraftEntriesInAlphabeticalOrder(self):
		return Entry.all().filter("community = ", self.key()).filter("draft = ", False).order("-title").fetch(FETCH_NUMBER)
	
	def getNonDraftStoriesInAlphabeticalOrder(self):
		return Entry.all().filter("community = ", self.key()).filter("type = ", "story").filter("draft = ", False).order("-title").fetch(FETCH_NUMBER)
	
	def getNonDraftEntriesAnnotationsAndAnswersInReverseTimeOrder(self):
		result = []
		entries = Entry.all().filter("community = ", self.key()).filter("draft = ", False).order("-published").fetch(FETCH_NUMBER)
		annotations = Annotation.all().filter("community = ", self.key()).filter("draft = ", False).order("-published").fetch(FETCH_NUMBER)
		answers = Answer.all().filter("community = ", self.key()).filter("draft = ", False).order("-published").fetch(FETCH_NUMBER)
		result.extend(entries)
		result.extend(annotations)
		result.extend(answers)
		result.sort(lambda a,b: cmp(b.published, a.published))
		return result
	
	def getNonDraftEntriesOfType(self, type):
		return Entry.all().filter("community = ", self.key()).filter("draft = ", False).filter("type = ", type).fetch(FETCH_NUMBER)
	
	def getNonDraftEntriesWithMissingMetadata(self):
		entriesWithoutTags = []
		entriesWithoutLinks = []
		entriesWithoutAnswers = []
		entriesWithoutComments = []
		invitationsWithoutResponses = []
		collagesWithoutInclusions = []
		for entry in self.getNonDraftEntries():
			if not Annotation.all().filter("entry = ", entry.key()).filter("type = ", "tag set").filter("draft = ", False).get():
				entriesWithoutTags.append(entry)
			if not Link.all().filter("entryFrom = ", entry.key()).get() and not Link.all().filter("entryTo = ", entry.key()).get():
				entriesWithoutLinks.append(entry)
			if not Answer.all().filter("referent = ", entry.key()).filter("draft = ", False).get():
				entriesWithoutAnswers.append(entry)
			if not Annotation.all().filter("entry = ", entry.key()).filter("type = ", "comment").filter("draft = ", False).get():
				entriesWithoutComments.append(entry)
		for invitation in self.getNonDraftEntriesOfType("invitation"):
			if not Link.all().filter("entryFrom = ", invitation.key()).filter("type = ", "responded").get():
				invitationsWithoutResponses.append(invitation)
		for collage in self.getNonDraftEntriesOfType("collage"):
			if not Link.all().filter("entryFrom = ", collage.key()).filter("type = ", "included").get():
				collagesWithoutInclusions.append(collage)
		return (entriesWithoutTags, entriesWithoutLinks, entriesWithoutAnswers, entriesWithoutComments, invitationsWithoutResponses, collagesWithoutInclusions)
	
	def getEntryActivityPointsForEvent(self, event):
		i = 0
		for eventType in EVENT_TYPES:
			if event == eventType:
				return self.entryActivityPointsPerEvent[i]
			i += 1
		return 0
	
	def getNonDraftNewMemberResources(self):
		return Entry.all().filter("community = ", self.key()). \
			filter("draft = ", False). \
			filter("type = ", "resource"). \
			filter("resourceForNewMemberPage =", True). \
			filter("resourceForManagersAndOwnersOnly = ", False). \
			fetch(FETCH_NUMBER)
	
	def getNonDraftHelpResources(self):
		return Entry.all().filter("community = ", self.key()). \
			filter("draft = ", False). \
			filter("type = ", "resource"). \
			filter("resourceForHelpPage = ", True). \
			filter("resourceForManagersAndOwnersOnly = ", False). \
			fetch(FETCH_NUMBER)
			
	def getNonDraftManagerOnlyHelpResources(self):
		return Entry.all().filter("community = ", self.key()). \
			filter("draft = ", False). \
			filter("type = ", "resource"). \
			filter("resourceForManagersAndOwnersOnly = ", True). \
			fetch(FETCH_NUMBER)
	
	# ENTRIES, ANNOTATIONS, ANSWERS, LINKS - EVERYTHING
	
	def getAllFlaggedItems(self):
		entries = Entry.all().filter("community = ", self.key()).filter("draft = ", False).filter("flaggedForRemoval = ", True).fetch(FETCH_NUMBER)
		annotations = Annotation.all().filter("community = ", self.key()).filter("draft = ", False).filter("flaggedForRemoval = ", True).fetch(FETCH_NUMBER)
		answers = Answer.all().filter("community = ", self.key()).filter("draft = ", False).filter("flaggedForRemoval = ", True).fetch(FETCH_NUMBER)
		links = Link.all().filter("community = ", self.key()).filter("flaggedForRemoval = ", True).fetch(FETCH_NUMBER)
		searches = SavedSearch.all().filter("community = ", self.key()).filter("flaggedForRemoval = ", True).fetch(FETCH_NUMBER)
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
		entries = Entry.all().filter("community = ", self.key()).filter("draft = ", False).fetch(FETCH_NUMBER)
		annotations = Annotation.all().filter("community = ", self.key()).filter("draft = ", False).fetch(FETCH_NUMBER)
		answers = Answer.all().filter("community = ", self.key()).filter("draft = ", False).fetch(FETCH_NUMBER)
		links = Link.all().filter("community = ", self.key()).filter("inBatchEntryBuffer = ", False).fetch(FETCH_NUMBER)
		return (entries, annotations, answers, links)
	
	def getAllEntriesAnnotationsAndAnswersAsOneList(self):
		result = []
		(entries, annotations, answers, links) = self.getAllItems()
		result.extend(entries)
		result.extend(answers)
		result.extend(annotations)
		return result

	def getEntryInImportBufferWithTitle(self, title):	
		return Entry.all().filter("community = ", self.key()).filter("inBatchEntryBuffer = ", True).filter("title = ", title).get()
										
	def getEntriesInImportBufferForLiaison(self, liaison):
		return Entry.all().filter("community = ", self.key()).filter("inBatchEntryBuffer = ", True).filter("liaison = ", liaison.key()).fetch(FETCH_NUMBER)
	
	def getCommentsInImportBufferForLiaison(self, liaison):
		return Annotation.all().filter("community = ", self.key()).filter("type = ", "comment").filter("inBatchEntryBuffer = ", True).filter("liaison = ", liaison.key()).fetch(FETCH_NUMBER)
		
	def getTagsetsInImportBufferForLiaison(self, liaison):
		return Annotation.all().filter("community = ", self.key()).filter("type = ", "tag set").filter("inBatchEntryBuffer = ", True).filter("liaison = ", liaison.key()).fetch(FETCH_NUMBER)
		
	def moveImportedEntriesOutOfBuffer(self, items):
		for item in items:
			item.draft = False
			item.inBatchEntryBuffer = False
			item.put()
			
	def getAttachmentsForAllNonDraftEntries(self):
		result = []
		entries = self.getNonDraftEntries()
		for entry in entries:
			attachments =  Attachment.all().filter('entry = ', entry.key())
			result.extend(attachments)
		return result
	
	def getNonDraftTagSets(self):
		return Annotation.all().filter("community = ", self.key()).filter("type = ", "tag set").filter("draft = ", False).fetch(FETCH_NUMBER)
	
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
		if self.firstPublishSet and self.firstPublish:
			# the reason this "padding" is needed is in the case of data being generated at community creation,
			# when the time of item creation may actually be slightly before the "firstPublish" flag is set
			# it won't hurt to have an extra second in otherwise, anyway
			return self.firstPublish - timedelta(seconds=1)
		else:
			return self.created
	
	# QUESTIONS
	
	def getAllQuestions(self):
		return Question.all().filter("community = ", self.key()).fetch(FETCH_NUMBER)
	
	def getActiveQuestions(self):
		return Question.all().filter("community = ", self.key()).filter("active = ", True).fetch(FETCH_NUMBER)
	
	def getActiveQuestionsOfType(self, type):
		return Question.all().filter("community = ", self.key()).filter("refersTo = ", type).filter("active = ", True).fetch(FETCH_NUMBER)
	
	def getInactiveQuestionsOfType(self, type):
		return Question.all().filter("community = ", self.key()).filter("refersTo = ", type).filter("active = ", False).fetch(FETCH_NUMBER)
	
	def getActiveMemberQuestions(self):
		return self.getActiveQuestionsOfType("member")
	
	def getActiveNonMemberQuestions(self):
		return Question.all().filter("community = ", self.key()).filter("refersTo !=", "member").filter("active = ", True).fetch(FETCH_NUMBER)
		
	def getActiveMemberAndCharacterQuestions(self):
		return Question.all().filter("community = ", self.key()).filter("refersTo IN ", ["character", "member"]).filter("active = ", True).fetch(FETCH_NUMBER)
	
	def hasActiveQuestionsOfType(self, type):
		return Question.all().filter("community = ", self.key()).filter("refersTo = ", type).filter("active = ", True).count() > 0
	
	def hasQuestionWithSameTypeAndName(self, question):
		allQuestions = self.getAllQuestions()
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
		
	# SEARCHES
	
	def getNonPrivateSavedSearches(self):
		return SavedSearch.all().filter("community = ", self.key()).filter("private = ", False).fetch(FETCH_NUMBER)
		
	# REMOVAL
	
	def removeAllDependents(self):
		entries = Entry.all().filter("community = ", self.key()).fetch(FETCH_NUMBER)
		for entry in entries:
			entry.removeAllDependents()
		db.delete(entries)
		db.delete(Member.all().filter("community = ", self.key()).fetch(FETCH_NUMBER))
		db.delete(PendingMember.all().filter("community = ", self.key()).fetch(FETCH_NUMBER))
		db.delete(Character.all().filter("community = ", self.key()).fetch(FETCH_NUMBER))
		db.delete(Question.all().filter("community = ", self.key()).fetch(FETCH_NUMBER))
		
	# EXPORT
	
	def getExportOfType(self, type):
		return Export.all().filter("community = ", self.key()).filter("type = ", type).get()

	def createOrRefreshExport(self, type, itemList=None, member=None):
		exportAlreadyThereForType = self.getExportOfType(type)
		if exportAlreadyThereForType:
			db.delete(exportAlreadyThereForType)
		export = Export(community=self.key(), type=type)
		if type == "entries":
			csvText = '"Export of entries, answers, annotations, attachments and links for community %s"\n' % self.name
			entries = self.getNonDraftEntries()
			csvText += "(entry columns)," + entries[0].csvLine(header=True) + "\n"
			for entry in entries:
				csvText += "\nentry," + entry.csvLine() + "\n"
				annotations = entry.getNonDraftAnnotations()
				if annotations:
					csvText += "(annotation columns)," + annotations[0].csvLine(header=True) + "\n"
				for annotation in annotations:
					csvText += "annotation," + annotation.csvLine() + "\n"
				answers = entry.getNonDraftAnswers()
				if answers:
					csvText += "(answer columns)," + answers[0].csvLine(header=True) + "\n"
				for answer in answers:
					csvText += "answer," + answer.csvLine() + "\n"
				attachments = entry.getAttachments()
				if attachments:
					csvText += "(attachment columns)," + attachments[0].csvLine(header=True) + "\n"
				for attachment in attachments:
					csvText += "attachment," + attachment.csvLine() + "\n"
				links = entry.getOutgoingLinks()
				if links:
					csvText = "(link columns)," + links[0].csvLine(header=True) + "\n"
				for link in links:
					csvText += "link," + link.csvLine() + "\n"
		elif type == "entries_with_answers":
			csvText = '"Export of entries with answers for community %s"\n' % self.name
			members = self.getActiveMembers()
			characters = self.getActiveCharacters()
			typeCount = 0
			for type in ENTRY_TYPES:
				entries = self.getNonDraftEntriesOfType(type)
				if entries:
					questions = self.getActiveQuestionsOfType(type)
					csvText += '%s\nNumber,Title,' % ENTRY_TYPES_PLURAL[typeCount].upper()
					for question in questions:
						csvText += question.name + ","
					csvText += '\n'
					i = 0
					for entry in entries:
						csvText += entry.csvLineWithAnswers(i+1, members, characters, questions) 
						i += 1
				typeCount += 1
		elif type == "community":
			csvText = '"Export of settings, questions and characters for community %s"\n' % self.name
			questions = self.getAllQuestions()
			if questions:
				csvText += "(question columns)," + questions[0].csvLine(header=True) + "\n"
			for question in questions:
				csvText += "question," + question.csvLine() + "\n"
			characters = self.getActiveCharacters()
			if characters:
				csvText += "(character columns)," + characters[0].csvLine(header=True) + "\n"
			for character in characters:
				csvText += "characters," + character.csvLine() + "\n"
			csvText += '(community columns),' + self.csvLine(header=True) + "\n"
			csvText += "community," + self.csvLine() + "\n"
		elif type == "liaisonPrint_simple":
			csvText = '<html><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8">'
			csvText += '<title>Printed from Rakontu</title></head><body>'
			if itemList:
				for item in itemList:
					try:
						csvText += item.PrintText()
					except: 
						pass
			elif member:
				if member.viewSearchResultList:
					for entry in self.getNonDraftEntries():
						if entry.key() in member.viewSearchResultList:
							try:
								csvText += entry.PrintText()
							except:
								pass
			csvText += "</body></html>"
		export.data = db.Text(csvText)
		export.put()
		return export

	def csvLine(self, header=False):
		parts = []
		if header:
			parts.append("name")
		else:
			parts.append(self.name)
			
		if header:
			parts.append("description")
		else:
			parts.append(self.description_formatted)

		if header:
			parts.append("etiquette statement")
		else:
			parts.append(self.etiquetteStatement_formatted)

		if header:
			parts.append("welcome message")
		else:
			parts.append(self.welcomeMessage_formatted)
			
		if header:
			parts.append("curator readme")
		else:
			parts.append(self.roleReadmes_formatted[0])

		if header:
			parts.append("guide readme")
		else:
			parts.append(self.roleReadmes_formatted[1])

		if header:
			parts.append("liaison readme")
		else:
			parts.append(self.roleReadmes_formatted[2])

		return CleanUpCSV(parts)
	
# ============================================================================================
# ============================================================================================
class Question(db.Model):
# ============================================================================================
# ============================================================================================

	community = db.ReferenceProperty(Community, collection_name="questions_to_community")
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
	
	def csvLine(self, header=False):
		parts = []
		if header:
			parts.append("name")
		else:
			parts.append(self.name)
			
		if header:
			parts.append("question")
		else:
			parts.append(self.text)
			
		if header:
			parts.append("refers to")
		else:
			parts.append(self.refersTo)

		if header:
			parts.append("type")
		else:
			parts.append(self.type)

		if header:
			parts.append("response if boolean")
		else:
			parts.append(self.responseIfBoolean)

		if header:
			parts.append("multiple?")
		else:
			parts.append(str(self.multiple))

		if header:
			parts.append("choices")
		else:
			parts.append(",".join(self.choices))
			
		if header:
			parts.append("help")
		else:
			parts.append(str(self.help_formatted))

		if header:
			parts.append("min and max if value")
		else:
			parts.append("%s,%s" % (self.minIfValue, self.maxIfValue))

		return CleanUpCSV(parts)
	
	def keyAsString(self):
		return "%s" % self.key()

# ============================================================================================
# ============================================================================================
class Member(db.Model):
# ============================================================================================
# ============================================================================================

	community = db.ReferenceProperty(Community, required=True, collection_name="members_to_community")
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
	
	guideIntro = db.TextProperty(default=None) # appears on the welcome and get help pages if the member is a guide
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
	
	joined = TzDateTimeProperty(auto_now_add=True)
	lastEnteredEntry = db.DateTimeProperty()
	lastEnteredAnnotation = db.DateTimeProperty()
	lastEnteredLink = db.DateTimeProperty()
	lastAnsweredQuestion = db.DateTimeProperty()
	lastReadAnything = db.DateTimeProperty()
	
	nudgePoints = db.IntegerProperty(default=DEFAULT_START_NUDGE_POINTS) # accumulated through participation
	
	viewTimeEnd = TzDateTimeProperty(auto_now_add=True, indexed=False)
	viewTimeFrameInSeconds = db.IntegerProperty(default=DAY_SECONDS, indexed=False)
	viewNudgeCategories = db.ListProperty(bool, default=[True] * NUM_NUDGE_CATEGORIES, indexed=False)
	viewSearch = db.ReferenceProperty(None, collection_name="member_to_search", indexed=False)
	viewDetails = db.BooleanProperty(default=False, indexed=False)
	viewSearchResultList = db.ListProperty(db.Key, indexed=False)
	
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
	
	def isLiaisonOrManagerOrOwner(self):
		return self.isLiaison() or self.isManagerOrOwner()
	
	def hasAnyHelpingRole(self):
		return self.helpingRoles[0] or self.helpingRoles[1] or self.helpingRoles[2]

	def canTakeOnAnyHelpingRole(self):
		return self.helpingRolesAvailable[0] or self.helpingRolesAvailable[1] or self.helpingRolesAvailable[2]
	
	def canEditTags(self):
		return (NUM_TAGS_IN_TAG_SET) and (self.isCurator() and self.isManagerOrOwner()) or (self.isCurator() and self.community.allowNonManagerCuratorsToEditTags)
	
	# BROWSING
	
	def getViewStartTime(self):
		return self.viewTimeEnd - timedelta(seconds=self.viewTimeFrameInSeconds)
			
	def setViewTimeFrameFromTimeFrameString(self, frame):
		for aFrame, seconds in TIME_FRAMES:
			if frame == aFrame:
				if aFrame == TIME_FRAME_EVERYTHING_STRING:
					self.viewTimeEnd = datetime.now(tz=pytz.utc)
					self.viewTimeFrameInSeconds = (self.viewTimeEnd - self.community.firstPublishOrCreatedWhicheverExists()).seconds
				else:
					self.viewTimeFrameInSeconds = seconds
				# caller should do the put
				break
			
	def getFrameStringForViewTimeFrame(self):
		for aFrame, seconds in TIME_FRAMES:
			if self.viewTimeFrameInSeconds == seconds:
				return aFrame
		return TIME_FRAME_EVERYTHING_STRING
			
	def setTimeFrameToStartAtFirstPublish(self):
		self.viewTimeEnd = self.community.firstPublish + timedelta(seconds=self.viewTimeFrameInSeconds)
		# caller should do the put
		
	# CONTRIBUTIONS
	
	def getAllItemsAttributedToMember(self):
		allItems = []
		allItems.extend(self.getNonDraftEntriesAttributedToMember())
		allItems.extend(self.getNonDraftAnnotationsAttributedToMember())
		allItems.extend(self.getNonDraftAnswersAboutEntriesAttributedToMember())
		return allItems
	
	def getAnswers(self):
		return Answer.all().filter("referent = ", self.key()).fetch(FETCH_NUMBER)
	
	def getNonDraftEntriesAttributedToMember(self):
		return Entry.all().filter("creator = ", self.key()).filter("draft = ", False).filter("character = ", None).fetch(FETCH_NUMBER)
	
	def getNonDraftAnnotationsAttributedToMember(self):
		return Annotation.all().filter("creator = ", self.key()).filter("draft = ", False).filter("character = ", None).fetch(FETCH_NUMBER)
	
	def getNonDraftAnswersAboutEntriesAttributedToMember(self):
		return Answer.all().filter("creator = ", self.key()).filter("draft = ", False).filter("character = ", None).filter("referentType = ", "entry").fetch(FETCH_NUMBER)
	
	def getNonDraftLiaisonedEntries(self):
		return Entry.all().filter("liaison = ", self.key()).filter("draft = ", False).fetch(FETCH_NUMBER)
	
	def getNonDraftLiaisonedAnnotations(self):
		return Annotation.all().filter("liaison = ", self.key()).filter("draft = ", False).fetch(FETCH_NUMBER)
	
	def getNonDraftLiaisonedAnswers(self):
		return Answer.all().filter("liaison = ", self.key()).filter("draft = ", False).filter("referentType = ", "entry").fetch(FETCH_NUMBER)
	
	def getLinksCreatedByMember(self):
		return Link.all().filter("creator = ", self.key()).fetch(FETCH_NUMBER)
	
	def getAnswerForQuestion(self, question):
		return Answer.all().filter("referent = ", self.key()).filter("question = ", question.key()).get()
		
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
			if not entries.has_key(answer.referent):
				entries[answer.referent] = 1
		return entries.keys()
	
	# DISPLAY
	
	def linkString(self):
		if self.isOnlineMember:
			offlineImageString = ""
		else:
			offlineImageString = '<img src="/images/offline.png" alt="offline member">'
		return '%s <a href="member?%s">%s</a>' % (offlineImageString, self.key(), self.nickname)
	
	def getSavedSearches(self):
		return SavedSearch.all().filter("creator = ", self.key()).fetch(FETCH_NUMBER)
	
	def getPrivateSavedSearches(self):
		return SavedSearch.all().filter("creator = ", self.key()).filter("private = ", True).fetch(FETCH_NUMBER)
	
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
	created = TzDateTimeProperty(auto_now_add=True)
	active = db.BooleanProperty(default=True)
	
	description = db.TextProperty(default=None) # appears on community page
	description_formatted = db.TextProperty()
	description_format = db.StringProperty(default=DEFAULT_TEXT_FORMAT, indexed=False)
	
	etiquetteStatement = db.TextProperty(default=None) # appears under "how to be [name]"
	etiquetteStatement_formatted = db.TextProperty()
	etiquetteStatement_format = db.StringProperty(default=DEFAULT_TEXT_FORMAT, indexed=False)
	
	image = db.BlobProperty(default=None) # optional
	
	def getAllItemsAttributedToCharacter(self):
		allItems = []
		allItems.extend(self.getNonDraftEntriesAttributedToCharacter())
		allItems.extend(self.getNonDraftAnnotationsAttributedToCharacter())
		allItems.extend(self.getNonDraftAnswersAboutEntriesAttributedToCharacter())
		return allItems
	
	def getNonDraftEntriesAttributedToCharacter(self):
		return Entry.all().filter("character = ", self.key()).filter("draft = ", False).fetch(FETCH_NUMBER)
	
	def getNonDraftAnnotationsAttributedToCharacter(self):
		return Annotation.all().filter("character = ", self.key()).filter("draft = ", False).fetch(FETCH_NUMBER)
	
	def getNonDraftAnswersAboutEntriesAttributedToCharacter(self):
		return Answer.all().filter("character = ", self.key()).filter("draft = ", False).filter("referentType = ", "entry").fetch(FETCH_NUMBER)

	def linkString(self):
		return '<a href="/visit/character?%s">%s</a>' % (self.key(), self.name)
		
	def getAnswers(self):
		return Answer.all().filter("referent = ", self.key()).fetch(FETCH_NUMBER)
	
	def getAnswerForQuestion(self, question):
		return Answer.all().filter("referent = ", self.key()).filter("question = ", question.key()).get()
		
	def csvLine(self, header=False):
		parts = []
		if header:
			parts.append("name")
		else:
			parts.append(self.name)
			
		if header:
			parts.append("description")
		else:
			parts.append(str(self.description_formatted))
			
		if header:
			parts.append("etiquette statement")
		else:
			parts.append(str(self.etiquetteStatement_formatted))
		return CleanUpCSV(parts)

# ============================================================================================
# ============================================================================================
class SavedSearch(db.Model):
# ============================================================================================
# ============================================================================================

	community = db.ReferenceProperty(Community, required=True, collection_name="searches_to_community")
	creator = db.ReferenceProperty(Member, required=True, collection_name="searches_to_member")
	private = db.BooleanProperty(default=True)
	created = TzDateTimeProperty(auto_now_add=True)
	name = db.StringProperty(default="Untitled search")
	
	flaggedForRemoval = db.BooleanProperty(default=False)
	flagComment = db.StringProperty(indexed=False)

	entryTypes = db.ListProperty(bool, default=[True] * len(ENTRY_TYPES))
	
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
		self.name = "Copy of " + search.name
		self.entryTypes = []
		self.entryTypes.extend(search.entrytTypes)
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
												community=self.community, 
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
	
# ============================================================================================
# ============================================================================================
class SavedSearchQuestionReference(db.Model):
# ============================================================================================
# ============================================================================================

	community = db.ReferenceProperty(Community, required=True, collection_name="searchrefs_to_community")
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

	community = db.ReferenceProperty(Community, collection_name="answers_to_community")
	question = db.ReferenceProperty(Question, collection_name="answers_to_questions")
	referent = db.ReferenceProperty(None, collection_name="answers_to_objects") # entry or member
	referentType = db.StringProperty(default="entry") # entry or member
	creator = db.ReferenceProperty(Member, collection_name="answers_to_creators") 
	
	collectedOffline = db.BooleanProperty(default=False)
	liaison = db.ReferenceProperty(Member, default=None, collection_name="answers_to_liaisons")
	character = db.ReferenceProperty(Character, default=None)
	
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
			self.creator.nudgePoints += self.community.getMemberNudgePointsForEvent("answering question")
			self.creator.lastAnsweredQuestion = datetime.now(pytz.utc)
			self.creator.put()
			self.community.lastPublish = self.published
			self.community.put()
				
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
				result += "yes"
			else:
				result += "no"
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
	
	def linkString(self):
		return self.displayString()
	
	def linkStringWithQuestionName(self):
		return self.displayString(includeQuestionName=True, includeQuestionText=False)
	
	def linkStringWithQuestionText(self):
		return self.displayString(includeQuestionName=False, includeQuestionText=True, )
	
	def linkStringWithQuestionNameAndReferentLink(self):
		return "%s for %s" % (self.linkStringWithQuestionName(), self.referent.linkString())
		
	def linkStringWithQuestionTextAndReferentLink(self):
		return "%s for %s" % (self.linkStringWithQuestionText(), self.referent.linkString())
	
	def PrintText(self):
		return '<p>The question "%s" was answered "%s" by %s.</p><hr>' \
			% (self.question.text, self.displayStringShort(), self.memberNickNameOrCharacterName())
		
	def csvLine(self, header=False):
		parts = []
		if header:
			parts.append("question and type")
		else:	
			parts.append("%s (%s)" % (self.question.text, self.question.type))
			
		if header:
			parts.append("by")
		else:	
			if self.character:
				parts.append(self.character.name)
			else:
				parts.append(self.creator.nickname)
			
		if header:
			parts.append("answer")
		else:	
			if self.type == "boolean":
				parts.append(self.answerIfBoolean)
			elif self.type == "text":
				parts.append(self.answerIfText)
			elif self.type == "ordinal" or self.type == "nominal":
				if self.multiple:
					parts.append(", ".join(self.answerIfMultiple))
				else:
					parts.append(self.answerIfText)
			elif self.type == "value":
				parts.append("%s" % self.answerIfValue)
		return CleanUpCSV(parts)
		
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

	type = db.StringProperty(choices=ENTRY_TYPES, required=True) 
	title = db.StringProperty(required=True, default=DEFAULT_UNTITLED_ENTRY_TITLE)
	text = db.TextProperty(default=NO_TEXT_IN_ENTRY)
	text_formatted = db.TextProperty()
	text_format = db.StringProperty(default=DEFAULT_TEXT_FORMAT, indexed=False)
	
	resourceForHelpPage = db.BooleanProperty(default=False)
	resourceForNewMemberPage = db.BooleanProperty(default=False)
	resourceForManagersAndOwnersOnly = db.BooleanProperty(default=False)
	resourceAtSystemLevel = db.BooleanProperty(default=False)

	community = db.ReferenceProperty(Community, required=True, collection_name="entries_to_community")
	creator = db.ReferenceProperty(Member, collection_name="entries")
	collectedOffline = db.BooleanProperty(default=False)
	liaison = db.ReferenceProperty(Member, default=None, collection_name="entries_to_liaisons")
	character = db.ReferenceProperty(Character, default=None)
	
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
		self.recordAction("added", self)
		self.put()
		self.creator.nudgePoints += self.community.getMemberNudgePointsForEvent("adding %s" % self.type)
		self.creator.lastEnteredEntry = datetime.now(pytz.utc)
		self.creator.put()
		for answer in self.getAnswersForMember(self.creator):
			answer.publish()
		self.community.lastPublish = self.published
		if not self.community.firstPublishSet:
			self.community.firstPublish = self.published
			self.community.firstPublishSet = True
		self.community.put()
		
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
		self.activityPoints += self.community.getEntryActivityPointsForEvent(eventType)
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
		
	def removeAllDependents(self):
		db.delete(self.getAttachments())
		db.delete(self.getAllLinks())
		db.delete(self.getAnswers())
		db.delete(self.getAnnotations())
		
	def satisfiesSearchCriteria(self, search, entryRefs, creatorRefs):
		i = 0
		for type in ENTRY_TYPES:
			if type == self.type:
				if not search.entryTypes[i]:
					return False
			i += 1
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
							if comparison == "contains":
								match = caseInsensitiveFind(answer.answerIfText, ref.answer)
							elif comparison == "is":
								match = answer.answerIfText.lower() == ref.answer.lower()
						elif ref.question.type == "value":
							if comparison == "is less than":
								try:
									answerValue = int(ref.answer)
									match = answer.answerIfValue < answerValue
								except:
									match = False
							elif comparison == "is greater than":
								try:
									answerValue = int(ref.answer)
									match = answer.answerIfValue > answerValue
								except:
									match = False
							elif comparison == "is":
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
			if locations[0]: #"in the entry text"
				match = match or caseInsensitiveFind(self.text, word) 
			if locations[0]: #"in a comment"
				match = match or self.wordIsFoundInAComment(word)
			if locations[0]: #"in a request"
				match = match or self.wordIsFoundInARequest(word)
			if locations[0]: #"in a nudge comment"
				match = match or self.wordIsFoundInANudgeComment(word)
			if locations[0]: #"in a link comment"
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
	
	def getNonDraftAnnotationsOfType(self, type):
		return Annotation.all().filter("entry =", self.key()).filter("type = ", type).filter("draft = ", False).fetch(FETCH_NUMBER)
	
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
	
	def getAnswersForCharacter(self, character):
		return Answer.all().filter("referent = ", self.key()).filter("creator = ", character.key()).fetch(FETCH_NUMBER)
	
	def getAnswerForMemberAndQuestion(self, member, question):
		return Answer.all().filter("referent = ", self.key()).filter("creator = ", member.key()).filter("question = ", question.key()).get()
	
	def getAnswerForCharacterAndQuestion(self, character, question):
		return Answer.all().filter("referent = ", self.key()).filter("character = ", character.key()).filter("question = ", question.key()).get()
	
	def getAllLinks(self):
		result = []
		outgoingLinks = Link.all().filter("entryFrom = ", self.key()).fetch(FETCH_NUMBER)
		incomingLinks = Link.all().filter("entryTo = ", self.key()).fetch(FETCH_NUMBER)
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
		return Link.all().filter("entryFrom = ", self.key()).filter("type = ", type).filter("inBatchEntryBuffer = ", False).fetch(FETCH_NUMBER)
	
	def getIncomingLinksOfType(self, type):
		return Link.all().filter("entryTo = ", self.key()).filter("type = ", type).filter("inBatchEntryBuffer = ", False).fetch(FETCH_NUMBER)
	
	def getOutgoingLinks(self):
		return Link.all().filter("entryFrom = ", self.key()).filter("inBatchEntryBuffer = ", False).fetch(FETCH_NUMBER)
	
	def getIncomingLinks(self):
		return Link.all().filter("entryTo = ", self.key()).filter("inBatchEntryBuffer = ", False).fetch(FETCH_NUMBER)
	
	def getIncomingLinksOfTypeFromType(self, type, fromType):
		result = []
		incomingLinks = self.getIncomingLinksOfType(type)
		for link in incomingLinks:
			if link.entryFrom.type == fromType:
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
	
	def csvLine(self, header=False):
		parts = []
		if header: 
			parts.append("type") 
		else: 
			parts.append(self.type)
			
		if header:
			parts.append("by")
		else:	
			if self.character:
				parts.append(self.character.name)
			else:
				parts.append(self.creator.nickname)
			
		if header:
			parts.append("title")
		else:
			parts.append(self.title)
			
		if header:
			parts.append("content")
		else:
			if self.text_formatted:
				parts.append(self.text_formatted)
			else:
				parts.append(self.text)
		return CleanUpCSV(parts)
	
	def csvLineWithAnswers(self, index, members, characters, questions):
		parts = []
		for member in members:
			if len(self.getAnswersForMember(member)):
				parts.append(str(index))
				parts.append(self.title)
				for question in questions:
					answer = self.getAnswerForMemberAndQuestion(member, question)
					if answer: 
						parts.append(answer.displayStringShort())
					else:
						parts.append("")
				parts.append('\n')
		for character in characters:
			if len(self.getAnswersForCharacter(character)):
				parts.append(str(index))
				parts.append(self.title)
				for question in questions:
					answer = self.getAnswerForCharacterAndQuestion(character, question)
					if answer: 
						parts.append(answer.displayStringShort())
					else:
						parts.append("")
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
	type = db.StringProperty(choices=LINK_TYPES, required=True) 
	# how links go: 
	#	related: either way
	#	retold: story to story
	# 	reminded: story or resource to story
	#   responded: invitation to story
	#	included: collage to story
	entryFrom = db.ReferenceProperty(Entry, collection_name="fromLinks", required=True)
	entryTo = db.ReferenceProperty(Entry, collection_name="toLinks", required=True)
	community = db.ReferenceProperty(Community, required=True, collection_name="links_to_community")
	creator = db.ReferenceProperty(Member, collection_name="links")
	
	# links cannot be in draft mode and cannot be entered in batch mode
	flaggedForRemoval = db.BooleanProperty(default=False)
	flagComment = db.StringProperty(indexed=False)
	
	published = TzDateTimeProperty(auto_now_add=True)
	inBatchEntryBuffer = db.BooleanProperty(default=False)
	
	comment = db.StringProperty(default="", indexed=False)
	
	entryNudgePointsWhenPublished = db.ListProperty(int, default=[0] * NUM_NUDGE_CATEGORIES)
	entryActivityPointsWhenPublished = db.IntegerProperty(default=0)
	
	# IMPORTANT METHODS
	
	def publish(self):
		self.published = datetime.now(pytz.utc)
		self.put()
		self.entryFrom.recordAction("added", self)
		self.entryTo.recordAction("added", self)
		for i in range(NUM_NUDGE_CATEGORIES):
			self.entryNudgePointsWhenPublished[i] = self.entryFrom.nudgePoints[i]
		self.entryActivityPointsWhenPublished = self.entryFrom.activityPoints
		self.put()
		self.creator.nudgePoints = self.entryFrom.community.getMemberNudgePointsForEvent("adding %s link" % self.type)
		self.creator.lastEnteredLink = datetime.now(pytz.utc)
		self.creator.put()
		self.entryFrom.community.lastPublish = self.published
		if not self.entryFrom.community.firstPublishSet:
			self.entryFrom.community.firstPublish = self.published
			self.entryFrom.community.firstPublishSet = True
		self.entryFrom.community.put()
		
	# MEMBERS
		
	def attributedToMember(self):
		return True
	
	# DISPLAY
		
	def getImageLinkForType(self):
		return'<img src="/images/link.png" alt="link" border="0">'
	
	def displayString(self):
		result = '<a href="read?%s">%s</a> (%s' % (self.entryTo.key(), self.entryTo.title, self.type)
		if self.comment:
			result += ", %s)" % self.comment
		else:
			result += ")"
		return result
	
	def linkString(self):
		return self.displayString()
	
	def csvLine(self, header=False):
		parts = []
		if header: 
			parts.append("from") 
		else: 
			parts.append(self.entryFrom.title)
			
		if header:
			parts.append("to")
		else:
			parts.append(self.entryTo.title)
			
		if header:
			parts.append("by")
		else:	
			parts.append(self.creator.nickname)
			
		if header:
			parts.append("comment")
		else:
			parts.append(self.comment)
		return CleanUpCSV(parts)

# ============================================================================================
# ============================================================================================
class Attachment(db.Model):								   # binary attachments to entries
# ============================================================================================
# ============================================================================================
	name = db.StringProperty()
	mimeType = db.StringProperty() # from ACCEPTED_ATTACHMENT_MIME_TYPES
	fileName = db.StringProperty() # as uploaded
	data = db.BlobProperty() # there is a practical limit on this size - cfk look at
	entry = db.ReferenceProperty(Entry, collection_name="attachments")
	
	def linkString(self):
		return '<a href="/visit/attachment?attachment_id=%s">%s</a>' % (self.key(), self.fileName)
	
	def isImage(self):
		return self.mimeType == "image/jpeg" or self.mimeType == "image/png"
	
	def csvLine(self, header=False):
		parts = []
		if header:
			parts.append("name")
		else:
			parts.append(self.name)
		
		if header:
			parts.append("type")
		else:	
			parts.append(self.mimeType)

		if header:
			parts.append("file name")
		else:	
			parts.append(self.fileName)
		return CleanUpCSV(parts)

# ============================================================================================
# ============================================================================================
class Annotation(db.Model):								# tag set, comment, request, nudge
# ============================================================================================
# ============================================================================================

	type = db.StringProperty(choices=ANNOTATION_TYPES, required=True)
	community = db.ReferenceProperty(Community, required=True, collection_name="annotations_to_community")
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

	collectedOffline = db.BooleanProperty(default=False)
	liaison = db.ReferenceProperty(Member, default=None, collection_name="annotations_liaisoned")
	character = db.ReferenceProperty(Character, default=None)

	collected = TzDateTimeProperty(default=None)
	created = TzDateTimeProperty(auto_now_add=True)
	edited = TzDateTimeProperty(auto_now_add=True)
	published = TzDateTimeProperty(auto_now_add=True)
	
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
					result.append("%s %s" % (self.valuesIfNudge[i], self.community.nudgeCategories[i]))
			if self.shortString:
				result.append("(%s)" % self.shortString)
			return ", ".join(result)
		
	def displayStringShortAndWithoutTags(self):
		return self.displayString(includeType=False)
	
	def PrintText(self):
		if self.isCommentOrRequest():
			return '<p>%s entered the %s labeled "%s" of <div style="padding: 0px 16px 0px 16px;">%s</div></p><hr>\n\n' % \
				(self.memberNickNameOrCharacterName(), self.type, self.shortString, self.longString_formatted)
		else:
			return '<p>A %s of "%s" was entered by %s.</p><hr>\n\n' % \
				(self.type, self.displayString(), self.memberNickNameOrCharacterName())
		
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
	
	# EXPORT
	
	def csvLine(self, header=False):
		parts = []
		if header: 
			parts.append("type") 
		else: 
			parts.append(self.type)
			
		if header:
			parts.append("by")
		else:	
			if self.character:
				parts.append(self.character.name)
			else:
				parts.append(self.creator.nickname)
			
		if header:
			parts.append("content")
		else:
			if self.type == "comment":
				parts.append("%s: %s" % (self.shortString, self.longString_formatted))
			elif self.type == "request":
				parts.append("%s (%s): %s" % (self.shortString, self.typeIfRequest, self.longString_formatted))
			else:
				parts.append(self.displayString())
		return CleanUpCSV(parts)
	
# ============================================================================================
# ============================================================================================
class Help(db.Model):		 # context-sensitive help string - appears as title hover on icon 
# ============================================================================================
# ============================================================================================

	type = db.StringProperty() # info, tip, caution
	name = db.StringProperty() # links to name in template
	text = db.StringProperty(indexed=False) # text to show user (plain text)
	
# ============================================================================================
# ============================================================================================
class Export(db.Model):		 # data prepared for export, in XML format
# ============================================================================================
# ============================================================================================
	
	community = db.ReferenceProperty(Community, required=True, collection_name="export_to_community")
	type = db.StringProperty()
	created = TzDateTimeProperty(auto_now_add=True)
	data = db.TextProperty()
