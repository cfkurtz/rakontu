# --------------------------------------------------------------------------------------------
# RAKONTU
# Description: Rakontu is open source story sharing software.
# Version: pre-0.1
# License: GPL 3.0
# Google Code Project: http://code.google.com/p/rakontu/
# --------------------------------------------------------------------------------------------

from utils import *
							 
class EnterEntryPage(ErrorHandlingRequestHander):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if isFirstVisit: self.redirect(member.firstVisitURL())
			queryEntry = GetObjectOfTypeFromURLQuery(self.request.query_string, "url_query_entry")
			if not queryEntry:
				if rakontu.hasTheMaximumNumberOfEntries():
					self.redirect(BuildResultURL("reachedMaxEntriesPerRakontu", rakontu))
					return
			queryVersion = GetObjectOfTypeFromURLQuery(self.request.query_string, "url_query_version")
			bookmark = GetBookmarkQueryWithCleanup(self.request.query_string)
			prev = None
			next = None
			# if this is a retelling, reminding or responding, the query entry is the item to link FROM, not the current entry
			if self.request.uri.find(URLS["url_retell"]) >= 0:
				type = "story"
				linkType = "retell"
				itemFrom = queryEntry
				entry = None
				entryName = None
				answers = None
				attachments = None
				entryTypeIndexForCharacters = STORY_ENTRY_TYPE_INDEX
			elif self.request.uri.find(URLS["url_remind"]) >= 0:
				type = "story"
				linkType = "remind"
				itemFrom = queryEntry
				entry = None
				entryName = None
				answers = None
				attachments = None
				entryTypeIndexForCharacters = STORY_ENTRY_TYPE_INDEX
			elif self.request.uri.find(URLS["url_respond"]) >= 0:
				type = "story"
				linkType = "respond"
				itemFrom = queryEntry
				entry = None
				entryName = None
				answers = None
				attachments = None
				entryTypeIndexForCharacters = STORY_ENTRY_TYPE_INDEX
			else:
				# otherwise, the query entry (if there is one) is the current entry
				linkType = ""
				itemFrom = None
				i = 0
				for aType in ENTRY_AND_ANNOTATION_TYPES_URLS:
					if self.request.uri.find(aType) >= 0:
						type = ENTRY_AND_ANNOTATION_TYPES[i]
						entryTypeIndexForCharacters = i
						break
					i += 1
				if queryEntry:
					entry = queryEntry
					entryName = entry.title
					answers = entry.getAnswers()
					attachments = entry.getAttachments()
				else:
					entry = None
					entryName = None
					answers = None
					attachments = None
			if type == "collage":
				if entry:
					includedLinksOutgoing = entry.getOutgoingLinksOfType("included")
				else:
					includedLinksOutgoing = []
				typeURL = ENTRY_TYPES_URLS[ENTRY_TYPE_INDEX_STORY]
				prev, entries, next = rakontu.getNonDraftEntriesOfType_WithPaging(typeURL, bookmark)
				entriesThatCanBeIncluded = self.reduceStoriesThatCanBeIncludedInCollage(entry, includedLinksOutgoing, entries)
				# if the list is reduced so far that there is nothing to show, make one attempt to add more entries
				if len(entries) > 0 and len(entriesThatCanBeIncluded) == 0:
					prev, moreEntries, next = entry.rakontu.getNonDraftEntriesOfType_WithPaging(typeURL, next)
					moreEntriesThatCanBeIncluded = self.reduceStoriesThatCanBeIncludedInCollage(entry, includedLinksOutgoing, moreEntries)
					entriesThatCanBeIncluded.extend(moreEntriesThatCanBeIncluded)
			else:
				entriesThatCanBeIncluded = None
				firstColumn = []
				secondColumn = []
				thirdColumn = []
				includedLinksOutgoing = None
			if type == "pattern":
				if entry:
					referencedLinksOutgoing = entry.getOutgoingLinksOfType("referenced")
				else:
					referencedLinksOutgoing = []
				searches = rakontu.getNonPrivateSavedSearches()
				searchesThatCanBeIncluded = []
				for aSearch in searches:
					found = False
					for link in referencedLinksOutgoing:
						if entry and str(link.itemTo.key()) == str(aSearch.key()):
							found = True
							break
					if not found:
						searchesThatCanBeIncluded.append(aSearch)
			else:
				searchesThatCanBeIncluded = []
				referencedLinksOutgoing = []
			if entryName:
				pageTitleExtra = "- %s" % entryName
			else:
				pageTitleExtra = ""
			typeDisplay = DisplayTypeForQuestionReferType(type)
			if queryVersion:
				versionTitle = queryVersion.title
				versionText = queryVersion.text
				versionFormat = queryVersion.text_format
			else:
				versionTitle = None
				versionText = None
				versionFormat = None
			if entry:
				versions = entry.getTextVersionsInReverseTimeOrder()
			else:
				versions = None
			if member.isLiaison() and not member.isManagerOrOwner():
				offlineOrAllMembers = rakontu.getActiveOfflineMembersForLiaison(member)
			elif member.isManagerOrOwner():
				offlineOrAllMembers = rakontu.getActiveMembers()
			else:
				offlineOrAllMembers = None
			sortedQuestions = rakontu.getActiveQuestionsOfType(type)
			sortedQuestions.sort(lambda a,b: cmp(a.order, b.order))
			if type == "resource":
				categories = rakontu.getResourceCategoryList()
			else:
				categories = None
			template_values = GetStandardTemplateDictionaryAndAddMore({
							   'title': typeDisplay.capitalize(), 
						   	   'title_extra': pageTitleExtra, 
							   'current_member': member,
							   'rakontu': rakontu, 
							   'skin': rakontu.getSkinDictionary(),
							   'entry_type': type,
							   'entry_type_display': DisplayTypeForEntryType(type),
							   'entry': entry,
							   'attachments': attachments,
							   'attachment_file_types': ACCEPTED_ATTACHMENT_FILE_TYPES,
							   # if loading old version, texts to fill in
							   'version': queryVersion,
							   'version_title': versionTitle,
							   'version_text': versionText,
							   'version_format': versionFormat,
							   'versions': versions,
							   # used by common_attribution
							   'attribution_referent_type': type,
							   'attribution_referent': entry,
							   'offline_members': offlineOrAllMembers,
							   'character_allowed': rakontu.allowCharacter[entryTypeIndexForCharacters],
							   # used by common_questions
							   'refer_type': type,
							   'refer_type_display': typeDisplay,
							   'questions': sortedQuestions,
							   'answers': answers,
							   # for a retold or remined story
							   'link_type': linkType,
							   'link_item_from': itemFrom,
							   # for a collage
							    'collage_entries': entriesThatCanBeIncluded, 
								'included_links_outgoing': includedLinksOutgoing,
								'bookmark': bookmark,
								'previous': prev,
							    'next': next,
								# for a pattern
								'referenced_links_outgoing': referencedLinksOutgoing,
							    'searches_that_can_be_added_to_pattern': searchesThatCanBeIncluded,
							    # for a resource
							    'categories_in_use': categories,
							   })
			if entry:
				template_values.update(entry.getLinksAsDictionaryWithTemplateReferenceNames())
			path = os.path.join(os.path.dirname(__file__), FindTemplate('visit/entry.html'))
			self.response.out.write(template.render(path, template_values))
		else:
			self.redirect(NoRakontuAndMemberURL())
			
	def reduceStoriesThatCanBeIncludedInCollage(self, entry, includedLinksOutgoing, entries):
		entriesThatCanBeIncluded = []
		for anEntry in entries:
			found = False
			for link in includedLinksOutgoing:
				if entry and str(link.itemTo.key()) == str(anEntry.key()):
					found = True
					break
			if not found:
				entriesThatCanBeIncluded.append(anEntry)
		return entriesThatCanBeIncluded
			
	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			for aType in ENTRY_TYPES:
				for argument in self.request.arguments():
					if argument.find(aType) >= 0:
						type = aType
						break
			entry = GetObjectOfTypeFromURLQuery(self.request.query_string, "url_query_entry")
			bookmark = GetBookmarkQueryWithCleanup(self.request.query_string)
			if entry and "loadVersion" in self.request.arguments():
				versionKeyName = self.request.get("versionToLoad")
				version = TextVersion.get_by_key_name(versionKeyName, parent=entry)
				if version:
					url = BuildURL("dir_visit", "%s?%s&%s" % (entry.typeAsURL(), entry.urlQuery(), version.urlQuery()))
					self.redirect(url)
			else:
				thingsToPublish = []
				thingsToPut = []
				thingsToDelete = []
				# get attribution info
				(collectedOffline, creator, liaison, dateCollected, character) = ProcessAttributionFromRequest(self.request, member)
				if collectedOffline and not creator:
					self.redirect(BuildResultURL("offlineMemberNotFound", rakontu=rakontu)) 
					return
				# if this was edited by somebody else who got permission to do so, don't change the creator to them!
				if entry and str(member.key()) != str(entry.creator.key()):
					creator = entry.creator
					character = entry.character
				# if new entry, create
				newEntry = False  
				if not entry:
					keyName = GenerateSequentialKeyName("entry")
					entry=Entry(
							key_name=keyName,
							id=keyName, 
							parent=creator, 
							rakontu=rakontu, 
							type=type, 
							title=DEFAULT_UNTITLED_ENTRY_TITLE)
					newEntry = True
				# main entry information
				entry.collectedOffline = collectedOffline
				entry.creator = creator
				entry.liaison = liaison
				entry.character = character
				entry.collected = dateCollected
				entry.edited = datetime.now(tz=pytz.utc)
				preview = False
				if "save|%s" % type in self.request.arguments():
					entry.draft = True
				elif "preview|%s" % type in self.request.arguments():
					entry.draft = True
					preview = True
				elif "publish|%s" % type in self.request.arguments():
					isFirstPublish = entry.draft 
					entry.draft = False
					entry.inBatchEntryBuffer = False
				if (entry.text and entry.text != NO_TEXT_IN_ENTRY):
					entry.addCurrentTextToPreviousVersions()
				if self.request.get("title"):
					entry.title = htmlEscape(self.request.get("title"))
				text = self.request.get("text")
				format = self.request.get("text_format").strip()
				entry.text = text
				entry.text_formatted = db.Text(InterpretEnteredText(text, format))
				entry.text_format = format
				if type == "resource":
					entry.resourceForHelpPage = self.request.get("resourceForHelpPage") == "yes"
					entry.resourceForNewMemberPage = self.request.get("resourceForNewMemberPage") == "yes"
					entry.resourceForManagersAndOwnersOnly = self.request.get("resourceForManagersAndOwnersOnly") == "yes"
					if self.request.get("categoryIfResource_list") != "none":
						entry.categoryIfResource = self.request.get("categoryIfResource_list")
					elif self.request.get("categoryIfResource_entered"):
						entry.categoryIfResource = self.request.get("categoryIfResource_entered")
				if not entry.draft:
					thingsToPublish.append(entry)
				thingsToPut.append(entry)
				# deal with INCOMING link created during entry creation - retelling, reminding, responding
				linkType = None
				if self.request.get("link_item_from"):
					itemFrom = db.get(self.request.get("link_item_from"))
					if itemFrom:
						if self.request.get("link_type") == "retell":
							linkType = "retold"
						elif self.request.get("link_type") == "remind":
							linkType = "reminded"
						elif self.request.get("link_type") == "respond":
							linkType = "responded"
						comment = htmlEscape(self.request.get("link_comment"))
						keyName = GenerateSequentialKeyName("link")
						link = Link(
								key_name=keyName, 
								id=keyName,
								parent=itemFrom,
								rakontu=rakontu,
								itemFrom=itemFrom, 
								itemTo=entry, 
								type=linkType, 
								creator=creator,
								liaison=liaison,
								comment=comment)
						if not entry.draft:
							thingsToPublish.append(link)
						thingsToPut.append(link)
				# deal with OUTGOING links created during entry creation - included (collage)
				if entry.isCollage():
					for link in entry.getOutgoingLinksOfType("included"):
						link.comment = self.request.get("linkComment|%s" % link.key())
						thingsToPut.append(link)
						if self.request.get("removeLink|%s" % link.key()) == "yes":
							thingsToDelete.append(link)
					prev, entries, next = rakontu.getNonDraftEntriesOfType_WithPaging(ENTRY_TYPES_URLS[ENTRY_TYPE_INDEX_STORY], bookmark)
					for anEntry in entries:
						if self.request.get("addLink|%s" % anEntry.key()) == "yes":
							comment = htmlEscape(self.request.get("linkComment|%s" % anEntry.key()))
							keyName = GenerateSequentialKeyName("link")
							link = Link(
								key_name=keyName, 
								id=keyName,
								parent=entry,
								rakontu=rakontu,
								itemFrom=entry, 
								itemTo=anEntry, 
								type="included", 
								comment=comment,
								creator=creator,
								liaison=liaison)
							if not entry.draft:
								thingsToPublish.append(link)
							thingsToPut.append(link)
				# deal with OUTGOING links created during entry creation - referenced (pattern)
				if entry.isPattern():
					for link in entry.getOutgoingLinksOfType("referenced"):
						link.comment = self.request.get("linkComment|%s" % link.key())
						thingsToPut.append(link)
						if self.request.get("removeLink|%s" % link.key()) == "yes":
							thingsToDelete.append(link)
					for aSearch in rakontu.getNonPrivateSavedSearches():
						comment = htmlEscape(self.request.get("linkComment|%s" % aSearch.key()))
						if self.request.get("addLink|%s" % aSearch.key()) == "yes":
							keyName = GenerateSequentialKeyName("link")
							link = Link(
								key_name=keyName, 
								id=keyName,
								parent=entry,
								rakontu=rakontu,
								itemFrom=entry, 
								itemTo=aSearch, 
								type="referenced", 
								comment=comment,
								creator=creator,
								liaison=liaison)
							if not entry.draft:
								thingsToPublish.append(link)
							thingsToPut.append(link)
				# deal with questions answered as part of entry creation
				questions = rakontu.getAllQuestionsOfReferType(type)
				for question in questions:
					queryText = "%s" % question.key()	
					response = self.request.get(queryText)
					foundAnswer = entry.getAnswerForQuestionAndMember(question, creator)
					keepAnswer = ShouldKeepAnswer(self.request, queryText, question)
					if keepAnswer:
						if foundAnswer:
							answerToEdit = foundAnswer
						else:
							keyName = GenerateSequentialKeyName("answer")
							answerToEdit = Answer(
												key_name=keyName,
												id=keyName,
												parent=entry,
												rakontu=rakontu, 
												question=question, 
												referent=entry, 
												referentType="entry")
						answerToEdit.setValueBasedOnResponse(question, self.request, queryText, response)
						answerToEdit.creator = creator
						answerToEdit.character = character
						answerToEdit.liaison = liaison
						answerToEdit.inBatchEntryBuffer = entry.inBatchEntryBuffer
						answerToEdit.collected = entry.collected
						if not entry.draft:
							thingsToPublish.append(answerToEdit)
						thingsToPut.append(answerToEdit)
					else: # not keepAnswer
						if foundAnswer:
							thingsToDelete.append(foundAnswer)
				foundAttachments = entry.getAttachments()
				for attachment in foundAttachments:
					for name, value in self.request.params.items():
						if value == "removeAttachment|%s" % attachment.key():
							thingsToDelete.append(attachment)
				thingsToPut.append(entry.creator)
				# finally, commit all changes to the database, except for new attachments
				def txn(thingsToPut, thingsToDelete, thingsToPublish):
					# publishing must be done inside the transaction 
					# because it updates counters which rely on a consistent state
					for thing in thingsToPublish:
						if thing is entry:
							thing.publish(isFirstPublish)
						else:
							thing.publish()
					db.put(thingsToPut)
					db.delete(thingsToDelete)
				db.run_in_transaction(txn, thingsToPut, thingsToDelete, thingsToPublish)
				if preview:
					self.redirect(BuildURL("dir_visit", "url_preview", entry.urlQuery()))
				elif entry.draft:
					if entry.collectedOffline:
						if entry.inBatchEntryBuffer:
							self.redirect(BuildURL("dir_liaise", "url_review", rakontu=rakontu))
						else: # not in batch entry buffer
							self.redirect(BuildURL("dir_visit", "url_drafts", entry.creator.urlQuery()))
					else: # not collected offline 
						self.redirect(BuildURL("dir_visit", "url_drafts", member.urlQuery()))
				else: # new entry
					self.redirect(BuildURL("dir_visit", "url_read", entry.urlQuery()))
		else: # no rakontu or member
			self.redirect(NoRakontuAndMemberURL())
			
class ManageEntryAttachmentsPage(ErrorHandlingRequestHander):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if isFirstVisit: self.redirect(member.firstVisitURL())
			entry = GetObjectOfTypeFromURLQuery(self.request.query_string, "url_query_entry")
			if entry and entry.memberCanEditMe(member):
				attachments = entry.getAttachments()
				canAddMoreAttachments = len(attachments) < rakontu.maxNumAttachments
				template_values = GetStandardTemplateDictionaryAndAddMore({
							   	   'title': TITLES["ATTACHMENTS_TO"], 
						   	   	   'title_extra': entry.title, 
								   'current_member': member,
								   'rakontu': rakontu, 
								   'skin': rakontu.getSkinDictionary(),
								   'entry': entry,
								   'attachments': attachments,
								   'can_add_more_attachments': canAddMoreAttachments,
								   })
				path = os.path.join(os.path.dirname(__file__), FindTemplate('visit/attachments.html'))
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect(NotFoundURL(rakontu))
		else:
			self.redirect(NoRakontuAndMemberURL())
				
	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			entry = GetObjectOfTypeFromURLQuery(self.request.query_string, "url_query_entry")
			if entry:
				# cannot use transactions in this case because it can create a RequestTooLargeError if you do them all together
				foundAttachments = entry.getAttachments()
				for attachment in foundAttachments:
					attachment.name = self.request.get("attachmentName|%s" % attachment.key())
					attachment.put()
				entry.edited = datetime.now(tz=pytz.utc)
				entry.put()
				for attachment in foundAttachments:
					if self.request.get("remove|%s" % attachment.key()):
						db.delete(attachment)
				self.redirect(self.request.uri)
			else:
				self.redirect(NotFoundURL(rakontu))
		else:
			self.redirect(NoRakontuAndMemberURL())
			
class AddOneAttachmentPage(ErrorHandlingRequestHander):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if isFirstVisit: self.redirect(member.firstVisitURL())
			entry = GetObjectOfTypeFromURLQuery(self.request.query_string, "url_query_entry")
			if entry and entry.memberCanEditMe(member):
				template_values = GetStandardTemplateDictionaryAndAddMore({
							   	   'title': TITLES["ADD_ATTACHMENT_TO"], 
						   	   	   'title_extra': entry.title, 
								   'current_member': member,
								   'rakontu': rakontu, 
								   'skin': rakontu.getSkinDictionary(),
								   'entry': entry,
								   'attachment_file_types': ACCEPTED_ATTACHMENT_FILE_TYPES,
								   })
				path = os.path.join(os.path.dirname(__file__), FindTemplate('visit/attachment.html'))
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect(NotFoundURL(rakontu))
		else:
			self.redirect(NoRakontuAndMemberURL())
				
	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			entry = GetObjectOfTypeFromURLQuery(self.request.query_string, "url_query_entry")
			if entry:
				for name, value in self.request.params.items():
					if name == "attachment":
						if value != None and value != "":
							filename = value.filename
							keyName = GenerateSequentialKeyName("attachment")
							newAttachment = Attachment(
											key_name=keyName, 
											id=keyName, 
											parent=entry, 
											entry=entry, 
											rakontu=rakontu)
							j = 0
							mimeType = None
							for type in ACCEPTED_ATTACHMENT_FILE_TYPES:
								if filename.lower().find(".%s" % type.lower()) >= 0:
									mimeType = ACCEPTED_ATTACHMENT_MIME_TYPES[j]
								j += 1
							if mimeType:
								newAttachment.mimeType = mimeType
								newAttachment.fileName = filename
								newAttachment.name = htmlEscape(self.request.get("attachmentName"))
								blob = db.Blob(self.request.POST.get("attachment").file.read())
								newAttachment.data = blob
								try:
									newAttachment.put()
									entry.edited = datetime.now(tz=pytz.utc)
									entry.put()
								except:
									self.redirect(AttachmentTooLargeURL(rakontu))
									return
							else:
								self.redirect(AttachmentNotOfAcceptedFileTypeURL(rakontu))
								return
				self.redirect(BuildURL("dir_visit", "url_attachments", entry.urlQuery()))
			else:
				self.redirect(NotFoundURL(rakontu))
		else:
			self.redirect(NoRakontuAndMemberURL())
			
class ManageAdditionalEntryEditorsPage(ErrorHandlingRequestHander):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if isFirstVisit: self.redirect(member.firstVisitURL())
			entry = GetObjectOfTypeFromURLQuery(self.request.query_string, "url_query_entry")
			if entry and str(entry.creator.key()) == str(member.key()):
				template_values = GetStandardTemplateDictionaryAndAddMore({
							   	   'title': TITLES["ADDITIONAL_EDITORS_FOR"], 
						   	   	   'title_extra': entry.title, 
								   'current_member': member,
								   'rakontu': rakontu, 
								   'skin': rakontu.getSkinDictionary(),
								   'entry': entry,
								   'editor_types': ADDITIONAL_EDITOR_TYPES,
								   'editor_types_display': ADDITIONAL_EDITOR_TYPES_DISPLAY,
								   'editor_types_included': entry.getAdditionalEditorTypes(),
								   'editor_keys_included': entry.getAdditionalEditorKeys(),
								   'rakontu_members': rakontu.getActiveOnlineMembers(),
								   'max_num_additional_editors': MAX_NUM_ADDITIONAL_EDITORS,
								   })
				path = os.path.join(os.path.dirname(__file__), FindTemplate('visit/editors.html'))
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect(NotFoundURL(rakontu))
		else:
			self.redirect(NoRakontuAndMemberURL())
				
	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			entry = GetObjectOfTypeFromURLQuery(self.request.query_string, "url_query_entry")
			if entry:
				entry.additionalEditors = []
				for editorType in ADDITIONAL_EDITOR_TYPES:
					if self.request.get("editors|%s" % editorType) == "yes":
						entry.additionalEditors.append(editorType)
				for aMember in rakontu.getActiveOnlineMembers():
					if self.request.get("key|%s" % aMember.key()) == "yes":
						entry.additionalEditors.append(str(aMember.key()))
				entry.put()
				if entry.draft:
					self.redirect(BuildURL("dir_visit", "url_drafts", member.urlQuery()))
				else:
					self.redirect(BuildURL("dir_visit", "url_read", entry.urlQuery()))
			else:
				self.redirect(NotFoundURL(rakontu))
		else:
			self.redirect(NoRakontuAndMemberURL())
		
class AnswerQuestionsAboutEntryPage(ErrorHandlingRequestHander):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if isFirstVisit: self.redirect(member.firstVisitURL())
			entry = GetObjectOfTypeFromURLQuery(self.request.query_string, "url_query_entry")
			if entry:
				answers = entry.getAnswersForMember(member)
				if len(answers):
					answerRefForQuestions =  answers[0]
				else:
					answerRefForQuestions = None
				sortedQuestions = rakontu.getActiveQuestionsOfType(entry.type)
				sortedQuestions.sort(lambda a,b: cmp(a.order, b.order))
				template_values = GetStandardTemplateDictionaryAndAddMore({
							   	   'title': TITLES["ANSWERS_FOR"], 
						   	   	   'title_extra': entry.title, 
								   'current_member': member,
								   'rakontu': rakontu, 
								   'skin': rakontu.getSkinDictionary(),
								   'entry': entry,
							   	   'attribution_referent_type': TERMS["term_answer_set"],
							       'attribution_referent': answerRefForQuestions,
								   'refer_type': entry.type,
								   'refer_type_display': DisplayTypeForQuestionReferType(entry.type),
								   'questions': sortedQuestions,
								   'answers': answers,
								   'rakontu_members': rakontu.getActiveMembers(),
								   'offline_members': rakontu.getOfflineMembers(),
								   'character_allowed': rakontu.allowCharacter[ANSWERS_ENTRY_TYPE_INDEX],
								   })
				template_values.update(entry.getLinksAsDictionaryWithTemplateReferenceNames())
				path = os.path.join(os.path.dirname(__file__), FindTemplate('visit/answers.html'))
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect(NotFoundURL(rakontu))
		else:
			self.redirect(NoRakontuAndMemberURL())
				
	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			entry = GetObjectOfTypeFromURLQuery(self.request.query_string, "url_query_entry")
			if entry:
				thingsToPublish = []
				thingsToPut = []
				thingsToDelete = []
				newAnswers = False
				preview = "preview" in self.request.arguments()
				# get attribution info
				(collectedOffline, creator, liaison, dateCollected, character) = ProcessAttributionFromRequest(self.request, member)
				if collectedOffline and not creator:
					self.redirect(BuildResultURL("offlineMemberNotFound", rakontu=rakontu)) 
					return
				# process answers
				questions = rakontu.getAllQuestionsOfReferType(entry.type)
				for question in questions:
					queryText = "%s" % question.key()	
					response = self.request.get(queryText)
					keepAnswer = ShouldKeepAnswer(self.request, queryText, question)
					foundAnswer = entry.getAnswerForQuestionAndMember(question, member)
					if keepAnswer:
						if foundAnswer:
							answerToEdit = foundAnswer
						else:
							keyName = GenerateSequentialKeyName("answer")
							answerToEdit = Answer(
												key_name=keyName, 
												id=keyName,
												parent=entry,
												rakontu=rakontu, 
												question=question, 
												referent=entry, 
												referentType="entry")
							newAnswers = True
						answerToEdit.setValueBasedOnResponse(question, self.request, queryText, response)
						answerToEdit.creator = creator
						answerToEdit.liaison = liaison
						answerToEdit.collected = dateCollected
						answerToEdit.character = character
						thingsToPublish.append(answerToEdit)
						thingsToPut.append(answerToEdit)
					else: # not keepAnswer
						if foundAnswer:
							thingsToDelete.append(foundAnswer)
				thingsToPut.append(entry)
				thingsToPut.append(creator)
				def txn(thingsToPut, thingsToDelete, thingsToPublish):
					for thing in thingsToPublish:
						thing.publish()
					db.put(thingsToPut)
					db.delete(thingsToDelete)
				db.run_in_transaction(txn, thingsToPut, thingsToDelete, thingsToPublish)
				if preview:
					self.redirect(BuildURL("dir_visit", "url_preview_answers", entry.urlQuery()))
				else:
					self.redirect(BuildURL("dir_visit", "url_read", entry.urlQuery()))
			else:
				self.redirect(BuildURL("dir_visit", "url_read", entry.urlQuery()))
		else:
			self.redirect(NoRakontuAndMemberURL())
			
class PreviewAnswersPage(ErrorHandlingRequestHander):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if isFirstVisit: self.redirect(member.firstVisitURL())
			entry = GetObjectOfTypeFromURLQuery(self.request.query_string, "url_query_entry")
			if entry:
				answers = entry.getAnswersForMember(member)
			else:
				answers = None
			if entry and answers:
				sortedQuestions = rakontu.getActiveQuestionsOfType(entry.type)
				sortedQuestions.sort(lambda a,b: cmp(a.order, b.order))
				template_values = GetStandardTemplateDictionaryAndAddMore({
							   	   'title': TITLES["PREVIEW_OF"], 
						   	   	   'title_extra': "%s %s " % (TITLES["ANSWERS_FOR"], entry.title), 
								   'current_member': member,
								   'rakontu': rakontu, 
								   'skin': rakontu.getSkinDictionary(),
								   'entry': entry,
								   'rakontu_has_questions_for_this_entry_type': rakontu.hasActiveQuestionsOfType(entry.type),
								   'questions': sortedQuestions,
								   'answers': answers,
								   })
				template_values.update(entry.getLinksAsDictionaryWithTemplateReferenceNames())
				path = os.path.join(os.path.dirname(__file__), FindTemplate('visit/previewAnswers.html'))
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect(NotFoundURL(rakontu))
		else:
			self.redirect(NoRakontuAndMemberURL())
		
	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			entry = GetObjectOfTypeFromURLQuery(self.request.query_string, "url_query_entry")
			if entry:
				if "edit" in self.request.arguments():
					self.redirect(BuildURL("dir_visit", "url_answers", entry.urlQuery()))
				elif "publish" in self.request.arguments():
					answers = entry.getAnswersForMember(member)
					def txn(answers, entry):
						for answer in answers:
							answer.publish()
						db.put(answers)
						entry.put()
						answers[0].creator.put()
					db.run_in_transaction(txn, answers, entry)
					self.redirect(BuildURL("dir_visit", "url_read", entry.urlQuery()))
			else:
				self.redirect(NotFoundURL(rakontu))
		else:
			self.redirect(NoRakontuAndMemberURL())

class EnterAnnotationPage(ErrorHandlingRequestHander):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if isFirstVisit: self.redirect(member.firstVisitURL())
			i = 0
			for aType in ANNOTATION_TYPES_URLS:
				if self.request.uri.find(aType) >= 0:
					type = ANNOTATION_TYPES[i]
					break
				i += 1
			i = 0
			for aType in ENTRY_AND_ANNOTATION_TYPES_URLS:
				if self.request.uri.find(aType) >= 0:
					entryTypeIndex = i
					break
				i += 1
			entry, annotation = GetEntryAndAnnotationFromURLQuery(self.request.query_string)
			if entry:
				if str(member.key()) == str(entry.creator.key()):
					nudgePointsMemberCanAssign = 0
				else:
					nudgePointsMemberCanAssign = max(0, rakontu.maxNudgePointsPerEntry - entry.getTotalNudgePointsForMember(member))
			else:
				nudgePointsMemberCanAssign = rakontu.maxNudgePointsPerEntry
			if entry:
				typeDisplay = DisplayTypeForAnnotationType(type)
				template_values = GetStandardTemplateDictionaryAndAddMore({
							   	   'title': "%s for" % typeDisplay.capitalize(), 
						   	   	   'title_extra': entry.title, 
								   'current_member': member,
								   'rakontu': rakontu, 
								   'skin': rakontu.getSkinDictionary(),
								   'annotation_type': type,
								   'annotation': annotation,
							   	   'attribution_referent_type': type,
							       'attribution_referent': annotation,
								   'rakontu_members': rakontu.getActiveMembers(),
								   'offline_members': rakontu.getOfflineMembers(),
								   'entry': entry,
								   'nudge_categories': rakontu.nudgeCategories,
								   'nudge_points_member_can_assign': nudgePointsMemberCanAssign,
								   'character_allowed': rakontu.allowCharacter[entryTypeIndex],
								   'already_there_tags': rakontu.getTags(),
								   })
				template_values.update(entry.getLinksAsDictionaryWithTemplateReferenceNames())
				path = os.path.join(os.path.dirname(__file__), FindTemplate('visit/annotation.html'))
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect(NotFoundURL(rakontu))
		else:
			self.redirect(NoRakontuAndMemberURL())
			
	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			for aType in ANNOTATION_TYPES:
				for argument in self.request.arguments():
					if argument.find(aType) >= 0:
						type = aType
						break
			newAnnotation = False
			entry, annotation = GetEntryAndAnnotationFromURLQuery(self.request.query_string)
			if entry:
				thingsToPut = []
				thingsToDelete = []
				if not annotation:
					keyName = GenerateSequentialKeyName("annotation")
					annotation = Annotation(key_name=keyName, parent=entry, id=keyName, rakontu=rakontu, type=type, entry=entry)
					newAnnotation = True
				preview = False
				annotation.edited = datetime.now(tz=pytz.utc)
				if "preview|%s" % type in self.request.arguments():
					preview = True
				elif "publish|%s" % type in self.request.arguments():
					annotation.inBatchEntryBuffer = False
				# get attribution info
				(collectedOffline, creator, liaison, dateCollected, character) = ProcessAttributionFromRequest(self.request, member)
				if collectedOffline and not creator:
					self.redirect(BuildResultURL("offlineMemberNotFound", rakontu=rakontu)) 
					return
				annotation.collectedOffline = collectedOffline
				annotation.creator = creator
				annotation.liaison = liaison
				annotation.collected = dateCollected
				annotation.character = character
				if type == "tag set":
					annotation.tagsIfTagSet = []
					for i in range (NUM_TAGS_IN_TAG_SET):
						if self.request.get("tag%s" % i):
							annotation.tagsIfTagSet.append(htmlEscape(self.request.get("tag%s" % i)))
						elif self.request.get("alreadyThereTag%i" %i) and self.request.get("alreadyThereTag%i" %i) != "none":
							annotation.tagsIfTagSet.append(htmlEscape(self.request.get("alreadyThereTag%s" % i)))
				elif type == "comment":
					annotation.shortString = htmlEscape(self.request.get("shortString"))
					if not len(annotation.shortString.strip()):
						annotation.shortString = TERMS["term_no_subject"]
					text = self.request.get("longString")
					format = self.request.get("longString_format").strip()
					annotation.longString = text
					annotation.longString_formatted = db.Text(InterpretEnteredText(text, format))
					annotation.longString_format = format
				elif type == "request":
					annotation.shortString = htmlEscape(self.request.get("shortString"))
					if not len(annotation.shortString.strip()):
						annotation.shortString = TERMS["term_no_subject"]
					text = self.request.get("longString")
					format = self.request.get("longString_format").strip()
					annotation.longString = text
					annotation.longString_formatted = db.Text(InterpretEnteredText(text, format))
					annotation.longString_format = format
					if self.request.get("typeIfRequest") in REQUEST_TYPES:
						annotation.typeIfRequest = self.request.get("typeIfRequest")
					else:
						annotation.typeIfRequest = REQUEST_TYPES[-1]
				elif type == "nudge":
					nudgeValuesTheyWantToSet = [0] * NUM_NUDGE_CATEGORIES
					totalNudgeValuesTheyWantToSet = 0
					for i in range(NUM_NUDGE_CATEGORIES):
						if rakontu.nudgeCategoryIndexHasContent(i):
							try:
								nudgeValuesTheyWantToSet[i] = int(self.request.get("nudge%s" % i))
							except:
								nudgeValuesTheyWantToSet[i] = annotation.valuesIfNudge[i]
							totalNudgeValuesTheyWantToSet += abs(nudgeValuesTheyWantToSet[i])
					# if they put in more total values than they could, strip off the last ones
					adjustedValues = [0] * NUM_NUDGE_CATEGORIES
					nudgePointsMemberCanAssignToThisEntry = max(0, rakontu.maxNudgePointsPerEntry - entry.getTotalNudgePointsForMember(member))
					maximumAllowedInThisInstance = min(member.nudgePoints, nudgePointsMemberCanAssignToThisEntry)
					if totalNudgeValuesTheyWantToSet > maximumAllowedInThisInstance:
						totalNudgePointsAllocated = 0
						for i in range(NUM_NUDGE_CATEGORIES):
							if rakontu.nudgeCategoryIndexHasContent(i):
								overLimit = totalNudgePointsAllocated + nudgeValuesTheyWantToSet[i] > maximumAllowedInThisInstance
								if not overLimit:
									adjustedValues[i] = nudgeValuesTheyWantToSet[i]
									totalNudgePointsAllocated += abs(nudgeValuesTheyWantToSet[i])
								else:
									break
					else:
						adjustedValues = []
						adjustedValues.extend(nudgeValuesTheyWantToSet)
					annotation.valuesIfNudge = [0] * NUM_NUDGE_CATEGORIES
					for i in range(NUM_NUDGE_CATEGORIES):
						if rakontu.nudgeCategoryIndexHasContent(i):
							annotation.valuesIfNudge[i] = adjustedValues[i]
					annotation.shortString = htmlEscape(self.request.get("shortString"))
				def txn(annotation, entry):
					annotation.publish()
					annotation.put()
					entry.put()
					annotation.creator.put()
				db.run_in_transaction(txn, annotation, entry)
				if preview:
					self.redirect(BuildURL("dir_visit", "url_preview", annotation.urlQuery()))
				elif annotation.collectedOffline:
					self.redirect(BuildURL("dir_liaise", "url_review", rakontu=rakontu))
				else:
					self.redirect(BuildURL("dir_visit", "url_read", entry.urlQuery()))
			else: # new entry
				self.redirect(rakontu.linkURL())
		else: # no rakontu or member
			self.redirect(NoRakontuAndMemberURL())
			
class PreviewPage(ErrorHandlingRequestHander):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if isFirstVisit: self.redirect(member.firstVisitURL())
			entry, annotation = GetEntryAndAnnotationFromURLQuery(self.request.query_string)
			if entry:
				sortedQuestions = rakontu.getActiveQuestionsOfType(entry.type)
				sortedQuestions.sort(lambda a,b: cmp(a.order, b.order))
				template_values = GetStandardTemplateDictionaryAndAddMore({
							   	   'title': TITLES["PREVIEW_OF"], 
						   	   	   'title_extra': entry.title, 
								   'current_member': member,
								   'rakontu': rakontu, 
								   'skin': rakontu.getSkinDictionary(),
								   'annotation': annotation,
								   'entry': entry,
								   'rakontu_has_questions_for_this_entry_type': len(rakontu.getActiveQuestionsOfType(entry.type)) > 0,
								   'questions': sortedQuestions,
								   'answers_with_entry': entry.getAnswersForMember(member),
								   'nudge_categories': rakontu.nudgeCategories,
								   })
				template_values.update(entry.getLinksAsDictionaryWithTemplateReferenceNames())
				path = os.path.join(os.path.dirname(__file__), FindTemplate('visit/preview.html'))
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect(NotFoundURL(rakontu))
		else:
			self.redirect(NoRakontuAndMemberURL())
		
	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			entry, annotation = GetEntryAndAnnotationFromURLQuery(self.request.query_string)
			if "batch" in self.request.arguments():
				if member.isLiaison():
					self.redirect(BuildURL("dir_liaise", "url_review", rakontu=rakontu))
				else:
					self.redirect(rakontu.linkURL())
			elif "profile" in self.request.arguments():
				self.redirect(BuildURL("dir_visit", "url_drafts", member.urlQuery()))
			elif annotation:
				if "edit" in self.request.arguments():
					self.redirect(BuildURL("dir_visit", URLForAnnotationType(annotation.type), annotation.urlQuery()))
				elif "publish" in self.request.arguments():
					def txn(annotation):
						annotation.publish()
						annotation.put()
						annotation.entry.put()
						annotation.creator.put()
					db.run_in_transaction(txn, annotation)
					self.redirect(BuildURL("dir_visit", "url_read", annotation.entry.urlQuery()))
			elif entry:
				if "edit" in self.request.arguments():
					self.redirect(BuildURL("dir_visit", URLForEntryType(entry.type), entry.urlQuery()))
				elif "publish" in self.request.arguments():
					thingsToPublish = []
					thingsToPut = []
					thingsToPublish.append(entry)
					thingsToPut.append(entry)
					for answer in entry.getAnswersForMember(entry.creator):
						thingsToPublish.append(answer)
						thingsToPut.append(answer)
					for link in entry.getOutgoingLinks():
						thingsToPublish.append(link)
						thingsToPut.append(link)
					thingsToPut.append(entry.creator)
					def txn(thingsToPut, thingsToPublish):
						for thing in thingsToPublish:
							thing.publish()
						db.put(thingsToPut)
					db.run_in_transaction(txn, thingsToPut, thingsToPublish)
					self.redirect(rakontu.linkURL())
				else:
					self.redirect(NotFoundURL(rakontu))
			else:
				self.redirect(NotFoundURL(rakontu))
		else:
			self.redirect(NoRakontuAndMemberURL())
					
class RelateEntryPage(ErrorHandlingRequestHander):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if isFirstVisit: self.redirect(member.firstVisitURL())
			entry = GetObjectOfTypeFromURLQuery(self.request.query_string, "url_query_entry")
			bookmark = GetBookmarkQueryWithCleanup(self.request.query_string)
			type = GetStringOfTypeFromURLQuery(self.request.query_string, "url_query_type")
			if not type:
				type = ENTRY_TYPES_URLS[0] # story
			if entry:
				prev, entries, next = entry.rakontu.getNonDraftEntriesOfType_WithPaging(type, bookmark)
				links = entry.getLinksOfType("related")
				entriesThatCanBeRelated = self.reduceEntriesForRelationsAlreadyThere(entry, links, entries)
				# if the list is reduced so far that there is nothing to show, make one attempt to add more entries
				if len(entries) > 0 and len(entriesThatCanBeRelated) == 0:
					prev, moreEntries, next = entry.rakontu.getNonDraftEntriesOfType_WithPaging(type, next)
					moreEntriesThatCanBeRelated = self.reduceEntriesForRelationsAlreadyThere(entry, links, moreEntries)
					entriesThatCanBeRelated.extend(moreEntriesThatCanBeRelated)
				if len(entriesThatCanBeRelated):
					template_values = GetStandardTemplateDictionaryAndAddMore({
									'title': TITLES["RELATE_TO"],
								   	'title_extra': entry.title,
									'rakontu': rakontu, 
									'skin': rakontu.getSkinDictionary(),
									'current_member': member, 
									'entry': entry,
									'entries': entriesThatCanBeRelated, 
									'related_links': links,
								   'bookmark': bookmark,
								   'previous': prev,
								   'next': next,
								   'type': type,
									})
					path = os.path.join(os.path.dirname(__file__), FindTemplate('visit/relate.html'))
					self.response.out.write(template.render(path, template_values))
				else:
					self.redirect(BuildResultURL("noEntriesToRelate", rakontu=rakontu))
			else:
				self.redirect(NotFoundURL(rakontu))
		else:
			self.redirect(NoRakontuAndMemberURL())
			
	def reduceEntriesForRelationsAlreadyThere(self, entry, links, entries):
		entriesThatCanBeRelated = []
		for anEntry in entries:
			found = False
			for link in links:
				if str(link.itemTo.key()) == str(anEntry.key()) or str(link.itemFrom.key()) == str(anEntry.key()):
					found = True
			if not found and str(anEntry.key()) != str(entry.key()):
				entriesThatCanBeRelated.append(anEntry)
		return entriesThatCanBeRelated
					
	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			entry = GetObjectOfTypeFromURLQuery(self.request.query_string, "url_query_entry")
			bookmark = GetBookmarkQueryWithCleanup(self.request.query_string)
			typeURL = GetStringOfTypeFromURLQuery(self.request.query_string, "url_query_type")
			if entry:
				if "changeSelections" in self.request.arguments():
					typeURL = self.request.get("entry_type")
					bookmark = None
				else:
					thingsToPublish = []
					thingsToPut = []
					thingsToDelete = []
					for link in entry.getLinksOfType("related"):
						if self.request.get("linkComment|%s" % link.key()):
							link.comment = self.request.get("linkComment|%s" % link.key())
							thingsToPut.append(link)
						if self.request.get("removeLink|%s" % link.key()) == "yes":
							thingsToDelete.append(link)
					prev, entries, next = rakontu.getNonDraftEntriesOfType_WithPaging(typeURL, bookmark)
					atLeastOneLinkCreated = False
					for anEntry in entries:
						if self.request.get("addLink|%s" % anEntry.key()) == "yes":
							comment = htmlEscape(self.request.get("linkComment|%s" % anEntry.key()))
							keyName = GenerateSequentialKeyName("link")
							link = Link(
									key_name=keyName,
									id=keyName, 
									parent=entry,
									rakontu=rakontu,
									itemFrom=entry, 
									itemTo=anEntry, 
									type="related", 
									creator=member, 
									comment=comment)
							thingsToPublish.append(link)
							thingsToPut.append(link)
							thingsToPut.append(entry)
							thingsToPut.append(anEntry)
							atLeastOneLinkCreated = True
					if atLeastOneLinkCreated:
						bookmark = None
					def txn(thingsToPut, thingsToDelete, thingsToPublish):
						for thing in thingsToPublish:
							thing.publish()
						db.put(thingsToPut)
						db.delete(thingsToDelete)
					db.run_in_transaction(txn, thingsToPut, thingsToDelete, thingsToPublish)
				if bookmark:
					# bookmark must be last, because of the extra == the PageQuery puts on it
					query = "%s&%s=%s&%s=%s" % (entry.urlQuery(), URL_OPTIONS["url_query_type"], typeURL, URL_OPTIONS["url_query_bookmark"], bookmark)
				else:
					query = "%s&%s=%s" % (entry.urlQuery(), URL_OPTIONS["url_query_type"], typeURL)
				self.redirect(BuildURL("dir_visit", "url_relate", query))
			else:
				self.redirect(NotFoundURL(rakontu))
		else:
			self.redirect(NoRakontuAndMemberURL())
			
