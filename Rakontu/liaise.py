# --------------------------------------------------------------------------------------------
# RAKONTU
# Description: Rakontu is open source story sharing software.

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
								   'changes_saved': GetChangesSavedState(member),
								   })
				path = os.path.join(os.path.dirname(__file__), FindTemplate('liaise/members.html'))
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect(RoleNotFoundURL("liaison", rakontu))
		else:
			self.redirect(NoAccessURL(rakontu, member, users.is_current_user_admin()))
			
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
							CreateMemberFromInfo(rakontu, None, None, nickname.strip(), "member", isOnline=False, liaison=member)
				def txn(membersToPut):
					db.put(membersToPut)
				db.run_in_transaction(txn, membersToPut)
				SetChangesSaved(member)
				self.redirect(BuildURL("dir_liaise", "url_members", rakontu=rakontu))
			else:
				self.redirect(RoleNotFoundURL("liaison", rakontu))
		else:
			self.redirect(NoAccessURL(rakontu, member, users.is_current_user_admin()))
			
class PrintFilteredItemsPage(ErrorHandlingRequestHander):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isLiaison():
				export = rakontu.createOrRefreshExport("liaisonPrint_simple", "filter", member=member, fileFormat="txt")
				self.redirect(BuildURL(None, "url_export", export.urlQuery()))
			else:
				self.redirect(RoleNotFoundURL("liaison", rakontu))
		else:
			self.redirect(NoAccessURL(rakontu, member, users.is_current_user_admin()))
			
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
				self.redirect(RoleNotFoundURL("liaison", rakontu))
		else:
			self.redirect(NoAccessURL(rakontu, member, users.is_current_user_admin()))
			
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
				self.redirect(RoleNotFoundURL("liaison", rakontu))
		else:
			self.redirect(NoAccessURL(rakontu, member, users.is_current_user_admin()))
			
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
				self.redirect(RoleNotFoundURL("liaison", rakontu))
		else:
			self.redirect(NoAccessURL(rakontu, member, users.is_current_user_admin()))
			
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
								   'blurbs': BLURBS,
								   'changes_saved': GetChangesSavedState(member),
								   })
				path = os.path.join(os.path.dirname(__file__), FindTemplate('liaise/review.html'))
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect(RoleNotFoundURL("liaison", rakontu))
		else:
			self.redirect(NoAccessURL(rakontu, member, users.is_current_user_admin()))

	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isLiaison():
				if "addMore" in self.request.arguments():
					self.redirect(BuildURL("dir_liaise", "url_batch", rakontu=rakontu))
				else:
					entries = rakontu.getEntriesInImportBufferForLiaison(member)
					def txn(entries):
						entriesToFinalize = []
						entriesToDelete = []
						itemsToPut = []
						for entry in entries:
							yearString = self.request.get("year|%s" % entry.key())
							monthString = self.request.get("month|%s" % entry.key())
							dayString = self.request.get("day|%s" % entry.key())
							date = parseDate(yearString, monthString, dayString, datetime.now(tz=pytz.utc))
							if entry.collected != date:
								entry.collected = date
								itemsToPut.append(entry)
								for annotation in Annotation.all().ancestor(entry):
									annotation.collected = entry.collected
									itemsToPut.append(annotation)
								for answer in Answer.all().ancestor(entry):
									answer.collected = entry.collected
									itemsToPut.append(answer)
							if self.request.get("remove|%s" % entry.key()) == "yes":
								entriesToDelete.append(entry)
							elif self.request.get("import|%s" % entry.key()) == "yes":
								entriesToFinalize.append(entry)
						if entriesToFinalize:
							for entry in entriesToFinalize:
								entry.publish()
								entry.inBatchEntryBuffer = False
								itemsToPut.append(entry)
								if entry.character:
									itemsToPut.append(entry.character)
								itemsToPut.append(entry.creator)
								for annotation in Annotation.all().ancestor(entry):
									annotation.publish()
									itemsToPut.append(annotation)
								for answer in Answer.all().ancestor(entry):
									if str(answer.creator.key()) == str(entry.creator.key()):
										answer.publish()
										itemsToPut.append(answer)
						db.put(itemsToPut)
						db.delete(entriesToDelete)
					db.run_in_transaction(txn, entries)
					SetChangesSaved(member)
					self.redirect(BuildURL("dir_liaise", "url_review", rakontu=rakontu))
			else:
				self.redirect(RoleNotFoundURL("liaison", rakontu))
		else:
			self.redirect(NoAccessURL(rakontu, member, users.is_current_user_admin()))

class BatchEntryPage(ErrorHandlingRequestHander):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isLiaison():
				if rakontu.hasWithinTenOfTheMaximumNumberOfEntries():
					self.redirect(BuildResultURL("reachedMaxEntriesPerRakontu", rakontu))
					return
				sortedQuestions = rakontu.getActiveQuestionsOfType("story")
				sortedQuestions.sort(lambda a,b: cmp(a.order, b.order))
				template_values = GetStandardTemplateDictionaryAndAddMore({
							   	   'title': TITLES["BATCH_ENTRY"], 
								   'rakontu': rakontu, 
								   'skin': rakontu.getSkinDictionary(),
								   'num_entries': NUM_ENTRIES_PER_BATCH_PAGE,
								   'character_allowed': rakontu.allowCharacter[STORY_ENTRY_TYPE_INDEX],
								   'questions': sortedQuestions,
								   'my_offline_members': rakontu.getActiveOfflineMembersForLiaison(member),
								   'offline_members': rakontu.getActiveOfflineMembers(),
								   'online_members': rakontu.getActiveOnlineMembers(),
								   'current_member': member,
								   'blurbs': BLURBS,
								   })
				path = os.path.join(os.path.dirname(__file__), FindTemplate('liaise/batch.html'))
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect(RoleNotFoundURL("liaison", rakontu))
		else:
			self.redirect(NoAccessURL(rakontu, member, users.is_current_user_admin()))
			
	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isLiaison():
				if "importEntriesFromCSV" in self.request.arguments():
					if self.request.get("import"):
						rakontu.addEntriesFromCSV(str(self.request.get("import")), member)
				else:
					itemsToPut = []
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
								keyName = GenerateSequentialKeyName("entry", rakontu)
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
									character = Character.get(self.request.get("attribution|%s" % i))
								else:
									character = None
								entry.character = character
								itemsToPut.append(entry)
								# put attachments separately, so if some are too large and fail the others
								# will still come in
								for j in range(rakontu.maxNumAttachments):
									for name, value in self.request.params.items():
										if name == "attachment|%s|%s" % (i, j):
											if value != None and value != "":
												filename = value.filename
												keyName = GenerateSequentialKeyName("attachment", rakontu)
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
													try:
														attachment.put()
													except:
														pass 
								questions = rakontu.getAllQuestionsOfReferType("story")
								for question in questions:
									queryText = "%s|%s" % (i, question.key())
									response = self.request.get(queryText)
									keepAnswer = ShouldKeepAnswer(self.request, queryText, question)
									if keepAnswer:
										keyName = GenerateSequentialKeyName("answer", rakontu)
										answer = Answer(
													key_name=keyName, 
													id=keyName,
													parent=entry,
													rakontu=rakontu, 
													question=question, 
													questionType=question.type,
													creator=memberToAttribute, 
													referent=entry, 
													referentType="entry")
										answer.setValueBasedOnResponse(question, self.request, queryText, response)
										answer.character = character
										answer.liaison = member
										answer.collected = entry.collected
										answer.inBatchEntryBuffer = True
										answer.collectedOffline = not memberToAttribute.isOnlineMember
										itemsToPut.append(answer)
								if self.request.get("comment|%s" % i):
									subject = self.request.get("commentSubject|%s" % i)
									if not len(subject.strip()):
										subject = TERMS["term_no_subject"]
									text = self.request.get("comment|%s" % i)
									format = self.request.get("commentFormat|%s" % i)
									keyName = GenerateSequentialKeyName("annotation", rakontu)
									comment = Annotation(key_name=keyName, 
														parent=entry,
														id=keyName,
														rakontu=rakontu, 
														type="comment", 
														creator=memberToAttribute, 
														entry=entry)
									comment.shortString = subject
									comment.character = character
									comment.longString = text
									comment.longString_format = format
									comment.longString_formatted = db.Text(InterpretEnteredText(text, format))
									comment.inBatchEntryBuffer = True
									comment.liaison = member
									comment.collected = entry.collected
									comment.collectedOffline = not memberToAttribute.isOnlineMember
									itemsToPut.append(comment)
								tags = []
								for j in range(NUM_TAGS_IN_TAG_SET):
									queryString = "tag|%s|%s" % (i, j)
									if self.request.get(queryString):
										tags.append(self.request.get(queryString))
								if tags:
									keyName = GenerateSequentialKeyName("annotation", rakontu)
									tagset = Annotation(key_name=keyName, 
													parent=entry,
													id=keyName,
													rakontu=rakontu, 
													type="tag set", 
													creator=memberToAttribute, 
													entry=entry)
									tagset.tagsIfTagSet = []
									tagset.tagsIfTagSet.extend(tags)
									tagset.character = character
									tagset.inBatchEntryBuffer = True
									tagset.liaison = member
									tagset.collected = entry.collected
									tagset.collectedOffline = not memberToAttribute.isOnlineMember
									itemsToPut.append(tagset)
					def txn(itemsToPut):
						db.put(itemsToPut)
					db.run_in_transaction(txn, itemsToPut)
				self.redirect(BuildURL("dir_liaise", "url_review", rakontu=rakontu))
			else:
				self.redirect(RoleNotFoundURL("liaison", rakontu))
		else:
			self.redirect(NoAccessURL(rakontu, member, users.is_current_user_admin()))
