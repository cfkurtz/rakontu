# --------------------------------------------------------------------------------------------
# RAKONTU
# Description: Rakontu is open source story sharing software.
# Version: pre-0.1
# License: GPL 3.0
# Google Code Project: http://code.google.com/p/rakontu/
# --------------------------------------------------------------------------------------------

from utils import *

class ReviewOfflineMembersPage(ErrorHandlingRequestHander):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isLiaison():
				template_values = GetStandardTemplateDictionaryAndAddMore({
								   'title': TITLES["REVIEW_OFFLINE_MEMBERS"], 
								   'rakontu': rakontu, 
								   'skin': rakontu.getSkinDictionary(),
								   'current_member': member,
								   'active_members': rakontu.getActiveOfflineMembers(),
								   'inactive_members': rakontu.getInactiveOfflineMembers(),
								   'other_liaisons': rakontu.getLiaisonsOtherThanMember(member),
								   })
				path = os.path.join(os.path.dirname(__file__), FindTemplate('liaise/members.html'))
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect(NotAuthorizedURL("liaison", rakontu))
		else:
			self.redirect(NoRakontuAndMemberURL())
			
	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isLiaison():
				offlineMembers = rakontu.getActiveOfflineMembers()
				# changes to existing members
				membersToPut = []
				for aMember in offlineMembers:
					if self.request.get("take|%s" % aMember.key()) == "yes":
						aMember.liaisonIfOfflineMember = member
						membersToPut.append(aMember)
				otherLiaisons = rakontu.getLiaisonsOtherThanMember(member)
				if otherLiaisons:
					for liaison in otherLiaisons:
						for aMember in offlineMembers:
							if self.request.get("reassign|%s" % aMember.key()) == "%s" % liaison.key():
								aMember.liaisonIfOfflineMember = liaison
								membersToPut.append(aMember)
				for aMember in offlineMembers:
					if self.request.get("remove|%s" % aMember.key()) == "yes":
						aMember.active = False
						membersToPut.append(aMember)
				# new members
				memberNicknamesToAdd = htmlEscape(self.request.get("newMemberNicknames")).split('\n')
				for nickname in memberNicknamesToAdd:
					if nickname.strip():
						existingMember = rakontu.memberWithNickname(nickname.strip())
						if existingMember:
							existingMember.active = True
							membersToPut.append(existingMember)
						else:
							keyName = GenerateSequentialKeyName("member")
							newMember = Member(
											key_name=keyName, 
											rakontu=rakontu, 
											nickname=nickname.strip(),
											isOnlineMember = False,
											liaisonIfOfflineMember = member,
											googleAccountID = None,
											googleAccountEmail = None)
							membersToPut.append(newMember)
				if membersToPut:
					db.put(membersToPut)
				self.redirect(BuildURL("dir_liaise", "url_members", rakontu=rakontu))
			else:
				self.redirect(NotAuthorizedURL("liaison", rakontu))
		else:
			self.redirect(NoRakontuAndMemberURL())
			
class PrintSearchPage(ErrorHandlingRequestHander):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isLiaison():
				export = rakontu.createOrRefreshExport("liaisonPrint_simple", "search", member=member, fileFormat="txt")
				self.redirect(BuildURL(None, "url_export", export.urlQuery()))
			else:
				self.redirect(NotAuthorizedURL("liaison", rakontu))
		else:
			self.redirect(NoRakontuAndMemberURL())
			
class PrintEntryAnnotationsPage(ErrorHandlingRequestHander):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isLiaison():
				entry = GetObjectOfTypeFromURLQuery(self.request.query_string, "url_query_entry")
				if entry:
					export = rakontu.createOrRefreshExport("liaisonPrint_simple", "entry", member=member, entry=entry, fileFormat="txt")
					url = BuildURL(None, "url_export", export.urlQuery())
					self.redirect(url)
				else:
					self.redirect(NotFoundURL(rakontu))
			else:
				self.redirect(NotAuthorizedURL("liaison", rakontu))
		else:
			self.redirect(NoRakontuAndMemberURL())
			
class PrintMemberEntriesAndAnnotationsPage(ErrorHandlingRequestHander):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isLiaison():
				memberToSee = GetObjectOfTypeFromURLQuery(self.request.query_string, "url_query_member")
				if memberToSee:
					export = rakontu.createOrRefreshExport("liaisonPrint_simple", "member", member=member, memberToSee=memberToSee, fileFormat="txt")
					url = BuildURL(None, "url_export", export.urlQuery())
					self.redirect(url)
				else:
					self.redirect(NotFoundURL(rakontu))
			else:
				self.redirect(NotAuthorizedURL("liaison", rakontu))
		else:
			self.redirect(NoRakontuAndMemberURL())
			
class PrintCharacterEntriesAndAnnotationsPage(ErrorHandlingRequestHander):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isLiaison():
				character = GetObjectOfTypeFromURLQuery(self.request.query_string, "url_query_character")
				if character:
					export = rakontu.createOrRefreshExport("liaisonPrint_simple", "character", member=member, character=character, fileFormat="txt")
					url = BuildURL(None, "url_export", export.urlQuery())
					self.redirect(url)
				else:
					self.redirect(NotFoundURL(rakontu))
			else:
				self.redirect(NotAuthorizedURL("liaison", rakontu))
		else:
			self.redirect(NoRakontuAndMemberURL())
			
class ReviewBatchEntriesPage(ErrorHandlingRequestHander):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isLiaison():
				template_values = GetStandardTemplateDictionaryAndAddMore({
							   	   'title': TITLES["REVIEW_BATCH_ENTRIES"], 
								   'rakontu': rakontu, 
								   'skin': rakontu.getSkinDictionary(),
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
				self.redirect(NotAuthorizedURL("liaison", rakontu))
		else:
			self.redirect(NoRakontuAndMemberURL())

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
					# not lumping puts here because of copying collected dates, etc 
					# this is not frequently done so it can be messier
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
			else:
				self.redirect(NotAuthorizedURL("liaison", rakontu))
		else:
			self.redirect(NoRakontuAndMemberURL())

class BatchEntryPage(ErrorHandlingRequestHander):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isLiaison():
				if rakontu.hasWithinTenOfTheMaximumNumberOfEntries():
					self.redirect(BuildResultURL("reachedMaxEntriesPerRakontu", rakontu))
					return
				template_values = GetStandardTemplateDictionaryAndAddMore({
							   	   'title': TITLES["BATCH_ENTRY"], 
								   'rakontu': rakontu, 
								   'skin': rakontu.getSkinDictionary(),
								   'num_entries': NUM_ENTRIES_PER_BATCH_PAGE,
								   'character_allowed': rakontu.allowCharacter[STORY_ENTRY_TYPE_INDEX],
								   'questions': rakontu.getActiveQuestionsOfType("story"),
								   'my_offline_members': rakontu.getActiveOfflineMembersForLiaison(member),
								   'offline_members': rakontu.getActiveOfflineMembers(),
								   'online_members': rakontu.getActiveOnlineMembers(),
								   'current_member': member,
								   })
				path = os.path.join(os.path.dirname(__file__), FindTemplate('liaise/batch.html'))
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect(NotAuthorizedURL("liaison", rakontu))
		else:
			self.redirect(NoRakontuAndMemberURL())
			
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
								format = self.request.get("textFormat|%s" % i)
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
								keyName = GenerateSequentialKeyName("entry")
								entry = Entry(key_name=keyName, parent=memberToAttribute, id=keyName, rakontu=rakontu, type="story", title=title, text=text, text_format=format)
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
												keyName = GenerateSequentialKeyName("attachment")
												attachment = Attachment(key_name=keyName, parent=entry, id=keyName, entry=entry, rakontu=rakontu)
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
								questions = rakontu.getAllQuestionsOfReferType("story")
								for question in questions:
									keyName = GenerateSequentialKeyName("answer")
									answer = Answer(
												key_name=keyName, 
												parent=entry,
												rakontu=rakontu, 
												question=question, 
												creator=memberToAttribute, 
												referent=entry, 
												referentType="entry")
									queryText = "%s|%s" % (i, question.key())
									response = self.request.get(queryText)
									keepAnswer = answer.shouldKeepMe(self.request, question)
									if keepAnswer:
										answer.setValueBasedOnResponse(question, self.request, response)
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
									keyName = GenerateSequentialKeyName("annotation")
									comment = Annotation(key_name=keyName, 
														parent=entry,
														id=keyName,
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
									keyName = GenerateSequentialKeyName("annotation")
									tagset = Annotation(key_name=keyName, 
													parent=entry,
													id=keyName,
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
			else:
				self.redirect(NotAuthorizedURL("liaison", rakontu))
		else:
			self.redirect(NoRakontuAndMemberURL())
