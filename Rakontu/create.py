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
				prev, entries, next = rakontu.getNonDraftEntriesOfType_WithPaging("story", bookmark)
				entriesThatCanBeIncluded = self.reduceStoriesThatCanBeIncludedInCollage(entry, includedLinksOutgoing, entries)
				# if the list is reduced so far that there is nothing to show, make one attempt to add more entries
				if len(entries) > 0 and len(entriesThatCanBeIncluded) == 0:
					prev, moreEntries, next = entry.rakontu.getNonDraftEntriesOfType_WithPaging("story", next)
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
						if entry and link.itemTo.key() == aSearch.key():
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
			template_values = GetStandardTemplateDictionaryAndAddMore({
							   'title': typeDisplay.capitalize(), 
						   	   'title_extra': pageTitleExtra, 
							   'current_member': member,
							   'rakontu': rakontu, 
							   'skin': rakontu.getSkinDictionary(),
							   'entry_type': type,
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
							   'offline_members': rakontu.getActiveOfflineMembers(),
							   'character_allowed': rakontu.allowCharacter[entryTypeIndexForCharacters],
							   # used by common_questions
							   'refer_type': type,
							   'refer_type_display': typeDisplay,
							   'questions': rakontu.getActiveQuestionsOfType(type),
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
							   })
			path = os.path.join(os.path.dirname(__file__), FindTemplate('visit/entry.html'))
			self.response.out.write(template.render(path, template_values))
		else:
			self.redirect(NoRakontuAndMemberURL())
			
	def reduceStoriesThatCanBeIncludedInCollage(self, entry, includedLinksOutgoing, entries):
		entriesThatCanBeIncluded = []
		for anEntry in entries:
			found = False
			for link in includedLinksOutgoing:
				if entry and link.itemTo.key() == anEntry.key():
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
				thingsToPut = []
				thingsToDelete = []
				incomingLinksToPutAfterward = []
				collectedOffline = self.request.get("collectedOffline") == "yes"
				if collectedOffline and member.isLiaison():
					foundMember = False
					for aMember in rakontu.getActiveOfflineMembers():
						if self.request.get("offlineSource") == str(aMember.key()):
							creator = aMember
							foundMember = True
							break
					if not foundMember:
						self.redirect(BuildResultURL("offlineMemberNotFound", rakontu=rakontu)) 
						return
					liaison = member
					dateCollected = parseDate(self.request.get("year"), self.request.get("month"), self.request.get("day"))
				else:
					creator = member
					liaison = None
					dateCollected = None
				newEntry = False  
				if not entry:
					keyName = GenerateSequentialKeyName("entry")
					entry=Entry(key_name=keyName, parent=creator, rakontu=rakontu, id=keyName, type=type, title=DEFAULT_UNTITLED_ENTRY_TITLE)
					newEntry = True
				entry.collectedOffline = collectedOffline
				entry.creator = creator
				if liaison:
					entry.liaison = liaison
				if dateCollected:
					entry.collected = dateCollected
				entry.edited = datetime.now(tz=pytz.utc)
				preview = False
				if "save|%s" % type in self.request.arguments():
					if not newEntry and not entry.draft: # was published before
						entry.unPublish()
					entry.draft = True
				elif "preview|%s" % type in self.request.arguments():
					entry.draft = True
					preview = True
				elif "publish|%s" % type in self.request.arguments():
					entry.draft = False
					entry.inBatchEntryBuffer = False
					entry.published = datetime.now(tz=pytz.utc)
				if (entry.text and entry.text != NO_TEXT_IN_ENTRY):
					entry.addCurrentTextToPreviousVersions()
				if self.request.get("title"):
					entry.title = htmlEscape(self.request.get("title"))
				text = self.request.get("text")
				format = self.request.get("text_format").strip()
				entry.text = text
				entry.text_formatted = db.Text(InterpretEnteredText(text, format))
				entry.text_format = format
				if entry.collectedOffline:
					attributionQueryString = "offlineAttribution"
				else:
					attributionQueryString = "attribution"
				if self.request.get(attributionQueryString) and self.request.get(attributionQueryString) != "member":
					entry.character = Character.get(self.request.get(attributionQueryString))
				else:
					entry.character = None
				if type == "resource":
					entry.resourceForHelpPage = self.request.get("resourceForHelpPage") == "yes"
					entry.resourceForNewMemberPage = self.request.get("resourceForNewMemberPage") == "yes"
					entry.resourceForManagersAndOwnersOnly = self.request.get("resourceForManagersAndOwnersOnly") == "yes"
				thingsToPut.append(entry)
				if not entry.draft:
					entry.publish()
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
						elif self.request.get("link_type") == "relate":
							linkType = "related"
						elif self.request.get("link_type") == "include":
							linkType = "included"
						elif self.request.get("link_type") == "reference":
							linkType = "referenced"
						comment = htmlEscape(self.request.get("link_comment"))
						link = Link(key_name=GenerateSequentialKeyName("link"), 
								parent=itemFrom,
								rakontu=rakontu,
								itemFrom=itemFrom, 
								itemTo=entry, 
								type=linkType, 
								creator=member,
								comment=comment)
						incomingLinksToPutAfterward.append(link)
						link.publish()
				if entry.isCollage():
					for link in entry.getOutgoingLinksOfType("included"):
						link.comment = self.request.get("linkComment|%s" % link.key())
						thingsToPut.append(link)
						if self.request.get("removeLink|%s" % link.key()) == "yes":
							thingsToDelete.append(link)
					prev, entries, next = rakontu.getNonDraftEntriesOfType_WithPaging("story", bookmark)
					for anEntry in entries:
						if self.request.get("addLink|%s" % anEntry.key()) == "yes":
							comment = htmlEscape(self.request.get("linkComment|%s" % anEntry.key()))
							keyName = GenerateSequentialKeyName("link")
							link = Link(key_name=keyName, 
								parent=entry,
								rakontu=rakontu,
								itemFrom=entry, 
								itemTo=anEntry, 
								type="included", 
								comment=comment,
								creator=member)
							thingsToPut.append(link)
							if not entry.draft:
								link.publish()
				if entry.isPattern():
					for link in entry.getOutgoingLinksOfType("referenced"):
						link.comment = self.request.get("linkComment|%s" % link.key())
						thingsToPut.append(link)
						if self.request.get("removeLink|%s" % link.key()) == "yes":
							thingsToDelete.append(link)
					for aSearch in rakontu.getNonPrivateSavedSearches():
						comment = htmlEscape(self.request.get("linkComment|%s" % aSearch.key()))
						if self.request.get("addLink|%s" % aSearch.key()) == "yes":
							link = Link(key_name=GenerateSequentialKeyName("link"), 
								parent=entry,
								rakontu=rakontu,
								itemFrom=entry, 
								itemTo=aSearch, 
								type="referenced", 
								comment=comment,
								creator=member)
							thingsToPut.append(link)
							if not entry.draft:
								link.publish()
				questions = rakontu.getAllQuestionsOfReferType(type)
				for question in questions:
					foundAnswers = entry.getAnswersForQuestionAndMember(question, member)
					if foundAnswers:
						answerToEdit = foundAnswers[0]
					else:
						keyName = GenerateSequentialKeyName("answer")
						answerToEdit = Answer(
											key_name=keyName,
											parent=entry,
											rakontu=rakontu, 
											question=question, 
											creator=member,
											referent=entry, 
											referentType="entry")
					queryText = "%s" % question.key()	
					response = self.request.get(queryText)
					keepAnswer = answerToEdit.shouldKeepMe(self.request, question)
					if keepAnswer:
						answerToEdit.setValueBasedOnResponse(question, self.request, response)
						answerToEdit.creator = member
						answerToEdit.character = entry.character
						answerToEdit.draft = entry.draft
						answerToEdit.inBatchEntryBuffer = entry.inBatchEntryBuffer
						answerToEdit.collected = entry.collected
						thingsToPut.append(answerToEdit)
						if not answerToEdit.draft:
							answerToEdit.publish()
					else:
						thingsToDelete.append(answerToEdit)
				foundAttachments = entry.getAttachments()
				for attachment in foundAttachments:
					for name, value in self.request.params.items():
						if value == "removeAttachment|%s" % attachment.key():
							thingsToDelete.append(attachment)
				thingsToPut.append(entry.creator)
				def txn(thingsToPut, thingsToDelete):
					if thingsToPut:
						db.put(thingsToPut)
					if thingsToDelete:
						db.delete(thingsToDelete)
				db.run_in_transaction(txn, thingsToPut, thingsToDelete)
				# second transaction for incoming links which have different parents
				def txn(incomingLinksToPutAfterward):
					if incomingLinksToPutAfterward:
						db.put(incomingLinksToPutAfterward)
				db.run_in_transaction(txn, incomingLinksToPutAfterward)
				# do attachments separately - in same entity group, but want to let them fail separately so that 
				# some might still attach even if one doesn't
				foundAttachments = entry.getAttachments()
				for i in range(rakontu.maxNumAttachments):
					for name, value in self.request.params.items():
						if name == "attachment%s" % i:
							if value != None and value != "":
								filename = value.filename
								if len(foundAttachments) > i:
									attachmentToEdit = foundAttachments[i]
								else:
									keyName = GenerateSequentialKeyName("attachment")
									attachmentToEdit = Attachment(key_name=keyName, parent=entry, id=keyName, entry=entry, rakontu=rakontu)
								j = 0
								mimeType = None
								for type in ACCEPTED_ATTACHMENT_FILE_TYPES:
									if filename.lower().find(".%s" % type.lower()) >= 0:
										mimeType = ACCEPTED_ATTACHMENT_MIME_TYPES[j]
									j += 1
								if mimeType:
									attachmentToEdit.mimeType = mimeType
									attachmentToEdit.fileName = filename
									attachmentToEdit.name = htmlEscape(self.request.get("attachmentName%s" % i))
									blob = db.Blob(self.request.POST.get("attachment%s" % i).file.read())
									attachmentToEdit.data = blob
									try:
										attachmentToEdit.put()
									except:
										pass # no way to tell user ? the attachment will just not get added
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
								   'questions': rakontu.getActiveQuestionsOfType(entry.type),
								   'answers': answers,
								   'rakontu_members': rakontu.getActiveMembers(),
								   'offline_members': rakontu.getOfflineMembers(),
								   'character_allowed': rakontu.allowCharacter[ANSWERS_ENTRY_TYPE_INDEX],
								   })
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
				thingsToPut = []
				thingsToDelete = []
				newAnswers = False
				preview = False
				setAsDraft = False
				if "preview" in self.request.arguments():
					setAsDraft = True
					preview = True
				elif "publish" in self.request.arguments():
					setAsDraft = False
				collectedOffline = self.request.get("collectedOffline") == "yes"
				if collectedOffline and member.isLiaison():
					foundMember = False
					for aMember in rakontu.getActiveOfflineMembers():
						if self.request.get("offlineSource") == str(aMember.key()):
							answersAlreadyInPlace = aMember.getDraftAnswersForEntry(entry)
							if answersAlreadyInPlace:
								self.redirect(BuildResultURL("offlineMemberAlreadyAnsweredQuestions", rakontu=rakontu))
								return
							creator = aMember
							foundMember = True
							break
					if not foundMember:
						self.redirect(BuildResultURL("offlineMemberNotFound", rakontu=rakontu))
						return
					liaison = member
					collected = parseDate(self.request.get("year"), self.request.get("month"), self.request.get("day"))
				else:
					creator = member
				if collectedOffline:
					attributionQueryString = "offlineAttribution"
				else:
					attributionQueryString = "attribution"
				character = None
				if self.request.get(attributionQueryString) != "member":
					characterKey = self.request.get(attributionQueryString)
					character = Character.get(characterKey)
				questions = rakontu.getAllQuestionsOfReferType(entry.type)
				for question in questions:
					foundAnswers = entry.getAnswersForQuestionAndMember(question, member)
					if foundAnswers:
						answerToEdit = foundAnswers[0]
					else:
						keyName = GenerateSequentialKeyName("answer")
						answerToEdit = Answer(
											key_name=keyName, 
											parent=entry,
											rakontu=rakontu, 
											question=question, 
											referent=entry, 
											referentType="entry")
						newAnswers = True
					answerToEdit.creator = creator
					if collectedOffline:
						answerToEdit.liaison = liaison
						answerToEdit.collected = collected
					answerToEdit.character = character
					queryText = "%s" % question.key()	
					response = self.request.get(queryText)
					keepAnswer = answerToEdit.shouldKeepMe(self.request, question)
					if keepAnswer:
						answerToEdit.setValueBasedOnResponse(question, self.request, response)
						answerToEdit.draft = setAsDraft
						if setAsDraft:
							answerToEdit.edited = datetime.now(tz=pytz.utc)
						else:
							answerToEdit.publish()
						thingsToPut.append(answerToEdit)
					else:
						thingsToDelete.append(answerToEdit)
				thingsToPut.append(entry)
				def txn(thingsToPut, thingsToDelete):
					if thingsToPut:
						db.put(thingsToPut)
					if thingsToDelete:
						db.delete(thingsToDelete)
				db.run_in_transaction(txn, thingsToPut, thingsToDelete)
				# cannot put creator in same transaction, because they might be answering questions about another person's entry
				# which is a different path
				creator.put()
				if preview:
					self.redirect(BuildURL("dir_visit", "url_preview_answers", entry.urlQuery()))
				elif setAsDraft:
					self.redirect(BuildURL("dir_visit", "url_drafts", creator.urlQuery()))
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
				template_values = GetStandardTemplateDictionaryAndAddMore({
							   	   'title': TITLES["PREVIEW_OF"], 
						   	   	   'title_extra': "%s %s " % (TITLES["ANSWERS_FOR"], entry.title), 
								   'current_member': member,
								   'rakontu': rakontu, 
								   'skin': rakontu.getSkinDictionary(),
								   'entry': entry,
								   'rakontu_has_questions_for_this_entry_type': len(rakontu.getActiveQuestionsOfType(entry.type)) > 0,
								   'questions': rakontu.getActiveQuestionsOfType(entry.type),
								   'answers': answers,
								   })
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
				elif "profile" in self.request.arguments():
					self.redirect(BuildURL("dir_visit", "url_preferences", member.urlQuery()))
				elif "publish" in self.request.arguments():
					answers = entry.getAnswersForMember(member)
					def txn(answers, entry):
						for answer in answers:
							answer.draft = False
							answer.publish()
						db.put(answers)
						entry.put()
					db.run_in_transaction(txn, answers, entry)
					# cannot put creator in same transaction, because they might be answering questions about another person's entry
					# which is a different path
					if answers:
						answers[0].creator.put()
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
				if not entry.memberCanNudge(member):
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
								   'included_links_outgoing': entry.getOutgoingLinksOfType("included"),
								   'already_there_tags': rakontu.getNonDraftTags(),
								   })
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
					annotation.draft = True
					preview = True
				elif "publish|%s" % type in self.request.arguments():
					annotation.draft = False
					annotation.inBatchEntryBuffer = False
					annotation.published = datetime.now(tz=pytz.utc)
				annotation.collectedOffline = self.request.get("collectedOffline") == "yes"
				if annotation.collectedOffline and member.isLiaison():
					foundMember = False
					for aMember in rakontu.getActiveOfflineMembers():
						if self.request.get("offlineSource") == str(aMember.key()):
							annotation.creator = aMember
							foundMember = True
							break
					if not foundMember:
						self.redirect(BuildResultURL("offlineMemberNotFound", rakontu=rakontu))
						return
					annotation.liaison = member
					annotation.collected = parseDate(self.request.get("year"), self.request.get("month"), self.request.get("day"))
				else:
					annotation.creator = member
				if annotation.collectedOffline:
					attributionQueryString = "offlineAttribution"
				else:
					attributionQueryString = "attribution"
				if self.request.get(attributionQueryString) and self.request.get(attributionQueryString) != "member":
					characterKey = self.request.get(attributionQueryString)
					character = Character.get(characterKey)
					annotation.character = character
				else:
					annotation.character = None
				if type == "tag set":
					annotation.tagsIfTagSet = []
					for i in range (NUM_TAGS_IN_TAG_SET):
						if self.request.get("tag%s" % i):
							annotation.tagsIfTagSet.append(htmlEscape(self.request.get("tag%s" % i)))
						elif self.request.get("alreadyThereTag%i" %i) and self.request.get("alreadyThereTag%i" %i) != "none":
							annotation.tagsIfTagSet.append(htmlEscape(self.request.get("alreadyThereTag%s" % i)))
				elif type == "comment":
					annotation.shortString = htmlEscape(self.request.get("shortString", default_value="No subject"))
					text = self.request.get("longString")
					format = self.request.get("longString_format").strip()
					annotation.longString = text
					annotation.longString_formatted = db.Text(InterpretEnteredText(text, format))
					annotation.longString_format = format
				elif type == "request":
					annotation.shortString = htmlEscape(self.request.get("shortString", default_value="No subject"))
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
					oldTotalNudgePointsInThisNudge = annotation.totalNudgePointsAbsolute()
					nudgeValuesTheyWantToSet = []
					totalNudgeValuesTheyWantToSet = 0
					for i in range(NUM_NUDGE_CATEGORIES):
						if rakontu.nudgeCategoryIndexHasContent(i):
							oldValue = annotation.valuesIfNudge[i]
							try:
								nudgeValuesTheyWantToSet.append(int(self.request.get("nudge%s" % i)))
							except:
								nudgeValuesTheyWantToSet.append(oldValue)
							totalNudgeValuesTheyWantToSet += abs(nudgeValuesTheyWantToSet[i])
					adjustedValues = []
					maximumAllowedInThisInstance = min(member.nudgePoints, rakontu.maxNudgePointsPerEntry)
					if totalNudgeValuesTheyWantToSet > maximumAllowedInThisInstance:
						totalNudgePointsAllocated = 0
						for i in range(NUM_NUDGE_CATEGORIES):
							if rakontu.nudgeCategoryIndexHasContent(i):
								overLimit = totalNudgePointsAllocated + nudgeValuesTheyWantToSet[i] > maximumAllowedInThisInstance
								if not overLimit:
									adjustedValues.append(nudgeValuesTheyWantToSet[i])
									totalNudgePointsAllocated += abs(nudgeValuesTheyWantToSet[i])
								else:
									break
					else:
						adjustedValues.extend(nudgeValuesTheyWantToSet)
					annotation.valuesIfNudge = [0,0,0,0,0]
					for i in range(NUM_NUDGE_CATEGORIES):
						if rakontu.nudgeCategoryIndexHasContent(i):
							annotation.valuesIfNudge[i] = adjustedValues[i]
					annotation.shortString = htmlEscape(self.request.get("shortString"))
					newTotalNudgePointsInThisNudge = annotation.totalNudgePointsAbsolute()
					member.nudgePoints += oldTotalNudgePointsInThisNudge
					member.nudgePoints -= newTotalNudgePointsInThisNudge
				if not annotation.draft:
					annotation.publish()
				def txn(annotation, entry):
					annotation.put()
					entry.put()
				db.run_in_transaction(txn, annotation, entry)
				# yes this is silly, but I can't get the ancestor query to work so it will go inside the transaction
				if annotation.type == "nudge":
					entry.updateNudgePoints()
					entry.put()
				# cannot put member into transaction because it might not be their entry, hence they are not in the group
				annotation.creator.put()
				if preview:
					self.redirect(BuildURL("dir_visit", "url_preview", annotation.urlQuery()))
				elif annotation.draft:
					if annotation.collectedOffline:
						if entry.inBatchEntryBuffer:
							self.redirect(BuildURL("dir_liaise", "url_review", rakontu=rakontu))
						else: # not in batch entry 
							self.redirect(BuildURL("dir_visit", "url_drafts", annotation.creator.urlQuery()))
					else: # not collected offline
						self.redirect(BuildURL("dir_visit", "url_drafts", member.urlQuery()))
				else: # not draft
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
				template_values = GetStandardTemplateDictionaryAndAddMore({
							   	   'title': TITLES["PREVIEW_OF"], 
						   	   	   'title_extra': entry.title, 
								   'current_member': member,
								   'rakontu': rakontu, 
								   'skin': rakontu.getSkinDictionary(),
								   'annotation': annotation,
								   'entry': entry,
								   'included_links_outgoing': entry.getOutgoingLinksOfType("included"),
								   'rakontu_has_questions_for_this_entry_type': len(rakontu.getActiveQuestionsOfType(entry.type)) > 0,
								   'questions': rakontu.getActiveQuestionsOfType(entry.type),
								   'answers_with_entry': entry.getAnswersForMember(member),
								   'nudge_categories': rakontu.nudgeCategories,
								   })
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
						annnotation.entry.put()
						annotation.creator.put()
					db.run_in_transaction(txn, annotation)
					self.redirect(BuildURL("dir_visit", "url_read", annotation.entry.urlQuery()))
			elif entry:
				if "edit" in self.request.arguments():
					self.redirect(BuildURL("dir_visit", URLForEntryType(entry.type), entry.urlQuery()))
				elif "publish" in self.request.arguments():
					thingsToPut = []
					entry.publish()
					thingsToPut.append(entry)
					for answer in entry.getAnswersForMember(entry.creator):
						answer.publish()
						thingsToPut.append(answer)
					for link in entry.getOutgoingLinks():
						link.publish()
						thingsToPut.append(link)
					thingsToPut.append(entry.creator)
					def txn(thingsToPut):
						if thingsToPut:
							db.put(thingsToPut)
					db.run_in_transaction(txn, thingsToPut)
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
				type = "story"
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
				if link.itemTo.key() == anEntry.key() or link.itemFrom.key() == anEntry.key():
					found = True
			if not found and anEntry.key() != entry.key():
				entriesThatCanBeRelated.append(anEntry)
		return entriesThatCanBeRelated
					
	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			entry = GetObjectOfTypeFromURLQuery(self.request.query_string, "url_query_entry")
			bookmark = GetBookmarkQueryWithCleanup(self.request.query_string)
			type = GetStringOfTypeFromURLQuery(self.request.query_string, "url_query_type")
			if entry:
				if "changeSelections" in self.request.arguments():
					type = self.request.get("entry_type")
					bookmark = None
				else:
					linksToPut = []
					linksToDelete = []
					for link in entry.getLinksOfType("related"):
						if self.request.get("linkComment|%s" % link.key()):
							link.comment = self.request.get("linkComment|%s" % link.key())
							linksToPut.append(link)
						if self.request.get("removeLink|%s" % link.key()) == "yes":
							linksToDelete.append(link)
					prev, entries, next = rakontu.getNonDraftEntriesOfType_WithPaging(type, bookmark)
					atLeastOneLinkCreated = False
					for anEntry in entries:
						if self.request.get("addLink|%s" % anEntry.key()) == "yes":
							comment = htmlEscape(self.request.get("linkComment|%s" % anEntry.key()))
							keyName = GenerateSequentialKeyName("link")
							link = Link(key_name=keyName, 
									parent=entry,
									rakontu=rakontu,
									itemFrom=entry, 
									itemTo=anEntry, 
									type="related", 
									creator=member, 
									comment=comment)
							link.publish()
							linksToPut.append(link)
							linksToPut.append(entry)
							linksToPut.append(anEntry)
							atLeastOneLinkCreated = True
					if atLeastOneLinkCreated:
						bookmark = None
					# cannot do transaction because entries are all mixed together
					if linksToPut:
						db.put(linksToPut)
					if linksToDelete:
						db.delete(linksToDelete)
				if bookmark:
					# bookmark must be last, because of the extra == the PageQuery puts on it
					query = "%s&%s=%s&%s=%s" % (entry.urlQuery(), URL_OPTIONS["url_query_type"], type, URL_OPTIONS["url_query_bookmark"], bookmark)
				else:
					query = "%s&%s=%s" % (entry.urlQuery(), URL_OPTIONS["url_query_type"], type)
				self.redirect(BuildURL("dir_visit", "url_relate", query))
			else:
				self.redirect(NotFoundURL(rakontu))
		else:
			self.redirect(NoRakontuAndMemberURL())
			
