# --------------------------------------------------------------------------------------------
# RAKONTU
# Description: Rakontu is open source story sharing software.
# Version: pre-0.1
# License: GPL 3.0
# Google Code Project: http://code.google.com/p/rakontu/
# --------------------------------------------------------------------------------------------

from utils import *

class ReviewOfflineMembersPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isLiaison():
				template_values = GetStandardTemplateDictionaryAndAddMore({
								   'title': TITLES["REVIEW_OFFLINE_MEMBERS"], 
								   'rakontu': rakontu, 
								   'colors': rakontu.colorDictionary(),
								   'current_member': member,
								   'active_members': rakontu.getActiveOfflineMembers(),
								   'inactive_members': rakontu.getInactiveOfflineMembers(),
								   })
				path = os.path.join(os.path.dirname(__file__), FindTemplate('liaise/members.html'))
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect(rakontu.linkURL())
		else:
			self.redirect(START)
			
	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isLiaison():
				offlineMembers = rakontu.getActiveOfflineMembers()
				for aMember in offlineMembers:
					if self.request.get("remove|%s" % aMember.key()) == "yes":
						aMember.active = False
						aMember.put()
				memberNicknamesToAdd = htmlEscape(self.request.get("newMemberNicknames")).split('\n')
				for nickname in memberNicknamesToAdd:
					if nickname.strip():
						if not rakontu.hasMemberWithNickname(nickname.strip()):
							newMember = Member(
											key_name=KeyName("member"), 
											rakontu=rakontu, 
											nickname=nickname.strip(),
											isOnlineMember = False,
											liaisonIfOfflineMember = member,
											googleAccountID = None,
											googleAccountEmail = None)
							newMember.put()
			self.redirect(BuildURL("dir_liaise", "url_members", rakontu=rakontu))
			
class PrintSearchPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isLiaison():
				if member.viewSearchResultList:
					export = rakontu.createOrRefreshExport("liaisonPrint_simple", itemList=None, member=member, fileFormat="txt")
					self.redirect(BuildURL(None, "url_export", export.urlQuery()))
				else:
					self.redirect(BuildResultURL("noSearchResultForPrinting", rakontu=rakontu))
			else:
				self.redirect(rakontu.linkURL())
		else:
			self.redirect(START)
			
class PrintEntryAnnotationsPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isLiaison():
				entry = GetObjectOfTypeFromURLQuery(self.request.query_string, "url_query_entry")
				DebugPrint(entry)
				if entry:
					entryAndItems = []
					entryAndItems.extend(entry.getNonDraftAnswers())
					entryAndItems.extend(entry.getNonDraftAnnotations())
					entryAndItems.insert(0, entry)
					export = rakontu.createOrRefreshExport("liaisonPrint_simple", itemList=entryAndItems, member=None, fileFormat="txt")
					url = BuildURL(None, "url_export", export.urlQuery())
					DebugPrint(url)
					self.redirect(url)
				else:
					self.redirect(rakontu.linkURL())
			else:
				self.redirect(rakontu.linkURL())
		else:
			self.redirect(START)
			
class ReviewBatchEntriesPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isLiaison():
				template_values = GetStandardTemplateDictionaryAndAddMore({
							   	   'title': TITLES["REVIEW_BATCH_ENTRIES"], 
								   'rakontu': rakontu, 
								   'colors': rakontu.colorDictionary(),
								   'character_allowed': rakontu.allowCharacter[STORY_ENTRY_TYPE_INDEX],
								   'batch_entries': rakontu.getEntriesInImportBufferForLiaison(member),
								   'batch_comments': rakontu.getCommentsInImportBufferForLiaison(member),
								   'batch_tagsets': rakontu.getTagsetsInImportBufferForLiaison(member),
								   'offline_members': rakontu.getActiveOfflineMembers(),
								   'current_member': member,
								   })
				path = os.path.join(os.path.dirname(__file__), FindTemplate('liaise/review.html'))
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect(rakontu.linkURL())
		else:
			self.redirect(START)

	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isLiaison():
				if "addMore" in self.request.arguments():
					self.redirect(BuildURL("dir_liaise", "url_batch", rakontu=rakontu))
				else:
					entriesToFinalize = []
					entries = rakontu.getEntriesInImportBufferForLiaison(member)
					for entry in entries:
						date = parseDate(self.request.get("year|%s" % entry.key()), self.request.get("month|%s" % entry.key()), self.request.get("day|%s" % entry.key()))
						entry.collected = date
						entry.put()
						entry.copyCollectedDateToAllAnswersAndAnnotations()
						if self.request.get("remove|%s" % entry.key()) == "yes":
							db.delete(entry)
						elif self.request.get("import|%s" % entry.key()) == "yes":
							entriesToFinalize.append(entry)
					if entriesToFinalize:
						rakontu.moveImportedEntriesOutOfBuffer(entriesToFinalize)
					self.redirect(BuildURL("dir_liaise", "url_review", rakontu=rakontu))

class BatchEntryPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isLiaison():
				template_values = GetStandardTemplateDictionaryAndAddMore({
							   	   'title': TITLES["BATCH_ENTRY"], 
								   'rakontu': rakontu, 
								   'colors': rakontu.colorDictionary(),
								   'num_entries': NUM_ENTRIES_PER_BATCH_PAGE,
								   'character_allowed': rakontu.allowCharacter[STORY_ENTRY_TYPE_INDEX],
								   'questions': rakontu.getActiveQuestionsOfType("story"),
								   'offline_members': rakontu.getActiveOfflineMembers(),
								   'online_members': rakontu.getActiveOnlineMembers(),
								   'current_member': member,
								   })
				path = os.path.join(os.path.dirname(__file__), FindTemplate('liaise/batch.html'))
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect(rakontu.linkURL())
		else:
			self.redirect(START)
			
	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isLiaison():
				if "importEntriesFromCSV" in self.request.arguments():
					if self.request.get("import"):
						rakontu.addEntriesFromCSV(str(self.request.get("import")), member)
				else:
					for i in range(NUM_ENTRIES_PER_BATCH_PAGE):
						if self.request.get("title|%s" % i):
							offlineMembers = rakontu.getActiveOfflineMembers()
							memberToAttribute = None
							for aMember in offlineMembers:
								if self.request.get("source|%s" % i) == "%s" % aMember.key():
									memberToAttribute = aMember
									break
							if member.isManagerOrOwner():
								onlineMembers = rakontu.getActiveOnlineMembers()
								for aMember in onlineMembers:
									if self.request.get("source|%s" % i) == "%s" % aMember.key():
										memberToAttribute = aMember
										break
							if memberToAttribute:
								title = self.request.get("title|%s" % i)
								text = self.request.get("text|%s" % i)
								textFormat = self.request.get("textFormat|%s" % i)
								yearString = self.request.get("year|%s" % i)
								monthString = self.request.get("month|%s" % i)
								dayString = self.request.get("day|%s" % i)
								date = datetime.now(tz=pytz.utc)
								if yearString and monthString and dayString:
									try:
										year = int(yearString)
										month = int(monthString)
										day = int(dayString)
										date = datetime(year, month, day, tzinfo=pytz.utc)
									except:
										pass
								entry = Entry(key_name=KeyName("entry"), rakontu=rakontu, type="story", title=title, text=text, text_format=textFormat)
								entry.creator = memberToAttribute
								entry.collected = date
								entry.text_formatted = db.Text(InterpretEnteredText(text, format))
								entry.text_format = format
								entry.draft = True
								entry.inBatchEntryBuffer = True
								entry.collectedOffline = not memberToAttribute.isOnlineMember
								entry.liaison = member
								if self.request.get("attribution|%s" % i) != "member":
									entry.character = Character.get(self.request.get("attribution|%s" % i))
								else:
									entry.character = None
								entry.put()
								for j in range(rakontu.maxNumAttachments):
									for name, value in self.request.params.items():
										if name == "attachment|%s|%s" % (i, j):
											if value != None and value != "":
												filename = value.filename
												attachment = Attachment(key_name=KeyName("attachment"), entry=entry, rakontu=rakontu)
												k = 0
												mimeType = None
												for type in ACCEPTED_ATTACHMENT_FILE_TYPES:
													if filename.find(".%s" % type) >= 0:
														mimeType = ACCEPTED_ATTACHMENT_MIME_TYPES[k]
													k += 1
												if mimeType:
													attachment.mimeType = mimeType
													attachment.fileName = filename
													attachment.name = htmlEscape(self.request.get("attachmentName|%s|%s" % (i, j)))
													attachment.data = db.Blob(str(self.request.get("attachment|%s|%s" % (i, j))))
													attachment.put()
								questions = Question.all().filter("rakontu = ", rakontu).filter("refersTo = ", "story").fetch(FETCH_NUMBER)
								for question in questions:
									answer = Answer(
												key_name=KeyName("answer"), 
												rakontu=rakontu, 
												question=question, 
												creator=memberToAttribute, 
												referent=entry, 
												referentType="entry")
									keepAnswer = False
									queryText = "%s|%s" % (i, question.key())
									if question.type == "text":
										keepAnswer = len(self.request.get(queryText)) > 0 and self.request.get(queryText) != "None"
										if keepAnswer:
											answer.answerIfText = htmlEscape(self.request.get(queryText))
									elif question.type == "value":
										keepAnswer = len(self.request.get(queryText)) > 0 and self.request.get(queryText) != "None"
										if keepAnswer:
											oldValue = answer.answerIfValue
											try:
												answer.answerIfValue = int(self.request.get(queryText))
											except:
												answer.answerIfValue = oldValue
									elif question.type == "boolean":
										keepAnswer = queryText in self.request.params.keys()
										if keepAnswer:
											answer.answerIfBoolean = self.request.get(queryText) == queryText
									elif question.type == "nominal" or question.type == "ordinal":
										if question.multiple:
											answer.answerIfMultiple = []
											for choice in question.choices:
												if self.request.get("%s|%s|%s" % (i, question.key(), choice)) == "yes":
													answer.answerIfMultiple.append(choice)
													keepAnswer = True
										else:
											keepAnswer = len(self.request.get(queryText)) > 0 and self.request.get(queryText) != "None"
											if keepAnswer:
												answer.answerIfText = self.request.get(queryText)
									if keepAnswer:
										answer.creator = memberToAttribute
										answer.liaison = member
										answer.draft = True
										answer.collected = entry.collected
										answer.inBatchEntryBuffer = True
										answer.collectedOffline = not memberToAttribute.isOnlineMember
										answer.put()
								if self.request.get("comment|%s" % i):
									subject = self.request.get("commentSubject|%s" % i, default_value="No subject")
									text = self.request.get("comment|%s" % i)
									format = self.request.get("commentFormat|%s" % i)
									comment = Annotation(key_name=KeyName("annotation"), 
														rakontu=rakontu, 
														type="comment", 
														creator=memberToAttribute, 
														entry=entry)
									comment.shortString = subject
									comment.longString = text
									comment.longString_format = format
									comment.draft = True
									comment.inBatchEntryBuffer = True
									comment.liaison = member
									comment.collected = entry.collected
									comment.collectedOffline = not memberToAttribute.isOnlineMember
									comment.put()
								tags = []
								for j in range(NUM_TAGS_IN_TAG_SET):
									queryString = "tag|%s|%s" % (i, j)
									if self.request.get(queryString):
										tags.append(self.request.get(queryString))
								if tags:
									tagset = Annotation(key_name=KeyName("annotation"), 
													rakontu=rakontu, 
													type="tag set", 
													creator=memberToAttribute, 
													entry=entry)
									tagset.tagsIfTagSet = []
									tagset.tagsIfTagSet.extend(tags)
									tagset.draft = True
									tagset.inBatchEntryBuffer = True
									tagset.liaison = member
									tagset.collected = entry.collected
									tagset.collectedOffline = not memberToAttribute.isOnlineMember
									tagset.put()
		self.redirect(BuildURL("dir_liaise", "url_review", rakontu=rakontu))
