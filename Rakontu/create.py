# --------------------------------------------------------------------------------------------
# RAKONTU
# Description: Rakontu is open source story sharing software.
# Version: pre-0.1
# License: GPL 3.0
# Google Code Project: http://code.google.com/p/rakontu/
# --------------------------------------------------------------------------------------------

from utils import *
							 
class EnterEntryPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if isFirstVisit: self.redirect(member.firstVisitURL())
			queryEntry = GetObjectOfTypeFromURLQuery(self.request.query_string, "url_query_entry")
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
				entries = rakontu.getNonDraftStoriesInAlphabeticalOrder()
				entriesThatCanBeIncluded = []
				for anEntry in entries:
					found = False
					for link in includedLinksOutgoing:
						if entry and link.itemTo.key() == anEntry.key():
							found = True
							break
					if not found:
						entriesThatCanBeIncluded.append(anEntry)
				firstColumn = []
				secondColumn = []
				thirdColumn = []
				if entriesThatCanBeIncluded:
					numEntries = len(entriesThatCanBeIncluded)
					for i in range(numEntries):
						if i < numEntries // 3:
							firstColumn.append(entriesThatCanBeIncluded[i])
						elif i < 2 * numEntries // 3:
							secondColumn.append(entriesThatCanBeIncluded[i])
						else:
							thirdColumn.append(entriesThatCanBeIncluded[i])
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
							    'collage_first_column': firstColumn, 
								'collage_second_column': secondColumn, 
								'collage_third_column': thirdColumn, 
								'num_collage_rows': max(len(firstColumn), max(len(secondColumn), len(thirdColumn))),							   
								'included_links_outgoing': includedLinksOutgoing,
								# for a pattern
								'referenced_links_outgoing': referencedLinksOutgoing,
							    'searches_that_can_be_added_to_pattern': searchesThatCanBeIncluded,
							   })
			path = os.path.join(os.path.dirname(__file__), FindTemplate('visit/entry.html'))
			self.response.out.write(template.render(path, template_values))
		else:
			self.redirect(START)
			
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
			newEntry = False
			if not entry:
				entry=Entry(key_name=KeyName("entry"), rakontu=rakontu, type=type, title=DEFAULT_UNTITLED_ENTRY_TITLE)
				newEntry = True
			entry.edited = datetime.now(tz=pytz.utc)
			preview = False
			if "save|%s" % type in self.request.arguments():
				entry.draft = True
			elif "preview|%s" % type in self.request.arguments():
				entry.draft = True
				preview = True
			elif "publish|%s" % type in self.request.arguments():
				entry.draft = False
				entry.inBatchEntryBuffer = False
				entry.published = datetime.now(tz=pytz.utc)
			if self.request.get("title"):
				entry.title = htmlEscape(self.request.get("title"))
			text = self.request.get("text")
			format = self.request.get("text_format").strip()
			entry.text = text
			entry.text_formatted = db.Text(InterpretEnteredText(text, format))
			entry.text_format = format
			entry.collectedOffline = self.request.get("collectedOffline") == "yes"
			if entry.collectedOffline and member.isLiaison():
				foundMember = False
				for aMember in rakontu.getActiveOfflineMembers():
					if self.request.get("offlineSource") == str(aMember.key()):
						entry.creator = aMember
						foundMember = True
						break
				if not foundMember:
					self.redirect(BuildResultURL("offlineMemberNotFound", rakontu=rakontu)) 
					return
				entry.liaison = member
				entry.collected = parseDate(self.request.get("year"), self.request.get("month"), self.request.get("day"))
			else:
				entry.creator = member
			if entry.collectedOffline:
				attributionQueryString = "offlineAttribution"
			else:
				attributionQueryString = "attribution"
			if self.request.get(attributionQueryString) != "member":
				entry.character = Character.get(self.request.get(attributionQueryString))
			else:
				entry.character = None
			if type == "resource":
				entry.resourceForHelpPage = self.request.get("resourceForHelpPage") == "yes"
				entry.resourceForNewMemberPage = self.request.get("resourceForNewMemberPage") == "yes"
				entry.resourceForManagersAndOwnersOnly = self.request.get("resourceForManagersAndOwnersOnly") == "yes"
			entry.put()
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
					link = Link(key_name=KeyName("link"), 
							rakontu=rakontu,
							itemFrom=itemFrom, 
							itemTo=entry, 
							type=linkType, 
							creator=member,
							comment=comment)
					link.put()
					link.publish()
			if entry.isCollage():
				linksToRemove = []
				for link in entry.getOutgoingLinksOfType("included"):
					link.comment = self.request.get("linkComment|%s" % link.key())
					link.put()
					if self.request.get("removeLink|%s" % link.key()) == "yes":
						linksToRemove.append(link)
				for link in linksToRemove:
					db.delete(link)
				for anEntry in rakontu.getNonDraftEntriesOfType("story"):
					if self.request.get("addLink|%s" % anEntry.key()) == "yes":
						link = Link(key_name=KeyName("link"), 
							rakontu=rakontu,
							itemFrom=entry, 
							itemTo=anEntry, 
							type="included", 
							creator=member)
						link.put()
						if not entry.draft:
							link.publish()
			if entry.isPattern():
				linksToRemove = []
				for link in entry.getOutgoingLinksOfType("referenced"):
					link.comment = self.request.get("linkComment|%s" % link.key())
					link.put()
					if self.request.get("removeLink|%s" % link.key()) == "yes":
						linksToRemove.append(link)
				for link in linksToRemove:
					db.delete(link)
				for aSearch in rakontu.getNonPrivateSavedSearches():
					if self.request.get("addLink|%s" % aSearch.key()) == "yes":
						link = Link(key_name=KeyName("link"), 
							rakontu=rakontu,
							itemFrom=entry, 
							itemTo=aSearch, 
							type="referenced", 
							creator=member)
						link.put()
						if not entry.draft:
							link.publish()
			questions = Question.all().filter("rakontu = ", rakontu).filter("refersTo = ", type).fetch(FETCH_NUMBER)
			for question in questions:
				foundAnswers = Answer.all().filter("question = ", question.key()).filter("referent =", entry.key()).filter("creator = ", member.key()).fetch(FETCH_NUMBER)
				if foundAnswers:
					answerToEdit = foundAnswers[0]
				else:
					answerToEdit = Answer(
										key_name=KeyName("answer"),
										rakontu=rakontu, 
										question=question, 
										creator=member,
										referent=entry, 
										referentType="entry")
				if (question.type == "nominal" or question.type == "ordinal") and question.multiple:
					keepAnswer = False
					answerToEdit.answerIfMultiple = []
					for choice in question.choices:
						if self.request.get("%s|%s" % (question.key(), choice)) == "yes":
							answerToEdit.answerIfMultiple.append(choice)
							keepAnswer = True
				else:
					queryText = "%s" % question.key()
					response = self.request.get(queryText).strip()
					if question.type == "boolean":
						keepAnswer = queryText in self.request.params.keys()
					else:
						keepAnswer = len(response) > 0 and response != "None"
					if keepAnswer:
						if question.type == "text":
							answerToEdit.answerIfText = htmlEscape(response)
						elif question.type == "value":
							oldValue = answerToEdit.answerIfValue
							try:
								answerToEdit.answerIfValue = int(response)
							except:
								answerToEdit.answerIfValue = oldValue
						elif question.type == "boolean":
							answerToEdit.answerIfBoolean = response == "yes"
						elif (question.type == "nominal" or question.type == "ordinal") and not question.multiple:
							answerToEdit.answerIfText = response
				if keepAnswer:
					answerToEdit.creator = member
					answerToEdit.character = entry.character
					answerToEdit.draft = entry.draft
					answerToEdit.inBatchEntryBuffer = entry.inBatchEntryBuffer
					answerToEdit.collected = entry.collected
					answerToEdit.put()
					if not answerToEdit.draft:
						answerToEdit.publish()
				else:
					db.delete(answerToEdit)
			foundAttachments = Attachment.all().filter("entry = ", entry.key()).fetch(FETCH_NUMBER)
			attachmentsToRemove = []
			for attachment in foundAttachments:
				for name, value in self.request.params.items():
					if value == "removeAttachment|%s" % attachment.key():
						attachmentsToRemove.append(attachment)
			if attachmentsToRemove:
				for attachment in attachmentsToRemove:
					db.delete(attachment)
			foundAttachments = Attachment.all().filter("entry = ", entry.key()).fetch(FETCH_NUMBER)
			for i in range(rakontu.maxNumAttachments):
				for name, value in self.request.params.items():
					if name == "attachment%s" % i:
						if value != None and value != "":
							filename = value.filename
							if len(foundAttachments) > i:
								attachmentToEdit = foundAttachments[i]
							else:
								attachmentToEdit = Attachment(key_name=KeyName("attachment"), entry=entry, rakontu=rakontu)
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
								blob = db.Blob(str(self.request.get("attachment%s" % i)))
								attachmentToEdit.data = blob
								try:
									attachmentToEdit.put()
								except:
									self.redirect(BuildResultURL("attachmentsTooLarge", rakontu=rakontu))
									return
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
				# this is the one time when I'll manipulate the member's time view
				# they want to see the story they made
				member.viewTimeEnd = entry.published + timedelta(seconds=1)
				member.put()
				self.redirect(BuildURL("dir_visit", "url_read", entry.urlQuery()))
		else: # no rakontu or member
			self.redirect(START)
			
class AnswerQuestionsAboutEntryPage(webapp.RequestHandler):
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
				self.redirect(rakontu.linkURL())
		else:
			self.redirect(START)
				
	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			entry = GetObjectOfTypeFromURLQuery(self.request.query_string, "url_query_entry")
			if entry:
				newAnswers = False
				preview = False
				setAsDraft = False
				if "save" in self.request.arguments():
					setAsDraft = True
				elif "preview" in self.request.arguments():
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
				questions = Question.all().filter("rakontu = ", rakontu).filter("refersTo = ", entry.type).fetch(FETCH_NUMBER)
				for question in questions:
					foundAnswers = Answer.all().filter("question = ", question.key()).filter("referent =", entry.key()).filter("creator = ", member.key()).fetch(FETCH_NUMBER)
					if foundAnswers:
						answerToEdit = foundAnswers[0]
					else:
						answerToEdit = Answer(
											key_name=KeyName("answer"), 
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
					if (question.type == "nominal" or question.type == "ordinal") and question.multiple:
						keepAnswer = False
						answerToEdit.answerIfMultiple = []
						for choice in question.choices:
							if self.request.get("%s|%s" % (question.key(), choice)) == "yes":
								answerToEdit.answerIfMultiple.append(choice)
								keepAnswer = True
					else:		
						queryText = "%s" % question.key()	
						response = self.request.get(queryText)
						if question.type == "boolean":
							keepAnswer = queryText in self.request.params.keys()
						else:
							keepAnswer = len(response) > 0 and response != "None"
						if keepAnswer:
							if question.type == "text":
								answerToEdit.answerIfText = htmlEscape(response)
							elif question.type == "value":
								oldValue = answerToEdit.answerIfValue
								try:
									answerToEdit.answerIfValue = int(response)
								except:
									answerToEdit.answerIfValue = oldValue
							elif question.type == "boolean":
								answerToEdit.answerIfBoolean = response == "yes"
							elif (question.type == "nominal" or question.type == "ordinal") and not question.multiple:
								answerToEdit.answerIfText = response
					answerToEdit.draft = setAsDraft
					if keepAnswer:
						if setAsDraft:
							answerToEdit.edited = datetime.now(tz=pytz.utc)
							answerToEdit.put()
						else:
							answerToEdit.publish()
					else:
						db.delete(answerToEdit)
				if preview:
					self.redirect(BuildURL("dir_visit", "url_preview_answers", entry.urlQuery()))
				elif setAsDraft:
					self.redirect(BuildURL("dir_visit", "url_drafts", creator.urlQuery()))
				else:
					self.redirect(BuildURL("dir_visit", "url_read", entry.urlQuery()))
			else:
				self.redirect(BuildURL("dir_visit", "url_read", entry.urlQuery()))
		else:
			self.redirect(START)
			
class PreviewAnswersPage(webapp.RequestHandler):
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
			self.redirect(START)
		
	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			entry = Entry.get(self.request.query_string)
			if entry:
				if "edit" in self.request.arguments():
					self.redirect(BuildURL("dir_visit", "url_answers", entry.urlQuery()))
				elif "profile" in self.request.arguments():
					self.redirect(BuildURL("dir_visit", "url_preferences", member.urlQuery()))
				elif "publish" in self.request.arguments():
					answers = entry.getAnswersForMember(member)
					for answer in answers:
						answer.draft = False
						answer.published = datetime.now(tz=pytz.utc)
					db.put(answers)
					self.redirect(rakontu.linkURL())

class EnterAnnotationPage(webapp.RequestHandler):
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
				self.redirect(rakontu.linkURL())
		else:
			self.redirect(START)
			
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
				if not annotation:
					annotation = Annotation(key_name=KeyName("annotation"), 
										rakontu=rakontu, 
										type=type, 
										entry=entry)
					newAnnotation = True
				preview = False
				annotation.edited = datetime.now(tz=pytz.utc)
				if "save|%s" % type in self.request.arguments():
					annotation.draft = True
				elif "preview|%s" % type in self.request.arguments():
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
				if self.request.get(attributionQueryString) != "member":
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
						category = rakontu.nudgeCategories[i]
						if category:
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
							category = rakontu.nudgeCategories[i]
							if category:
								overLimit = totalNudgePointsAllocated + nudgeValuesTheyWantToSet[i] > maximumAllowedInThisInstance
								if not overLimit:
									adjustedValues.append(nudgeValuesTheyWantToSet[i])
									totalNudgePointsAllocated += abs(nudgeValuesTheyWantToSet[i])
								else:
									break
					else:
						adjustedValues.extend(nudgeValuesTheyWantToSet)
					annotation.valuesIfNudge = [0,0,0,0,0]
					i = 0
					for value in adjustedValues:
						annotation.valuesIfNudge[i] = value
						i += 1
					annotation.shortString = htmlEscape(self.request.get("shortString"))
					newTotalNudgePointsInThisNudge = annotation.totalNudgePointsAbsolute()
					member.nudgePoints += oldTotalNudgePointsInThisNudge
					member.nudgePoints -= newTotalNudgePointsInThisNudge
					member.put()
				annotation.put()
				if not annotation.draft:
					annotation.publish()
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
			self.redirect(START)
			
class PreviewPage(webapp.RequestHandler):
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
			self.redirect(START)
		
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
					annotation.publish()
					self.redirect(BuildURL("dir_visit", "url_read", annotation.entry.urlQuery()))
			else:
				if "edit" in self.request.arguments():
					self.redirect(BuildURL("dir_visit", URLForEntryType(entry.type), entry.urlQuery()))
				elif "publish" in self.request.arguments():
					entry.publish()
					self.redirect(rakontu.linkURL())
		else:
			self.redirect(START)
					
class RelateEntryPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if isFirstVisit: self.redirect(member.firstVisitURL())
			entry = GetObjectOfTypeFromURLQuery(self.request.query_string, "url_query_entry")
			if entry:
				links = entry.getLinksOfType("related")
				entries = rakontu.getNonDraftEntriesInAlphabeticalOrder()
				entriesThatCanBeRelated = []
				for anEntry in entries:
					found = False
					for link in links:
						if link.itemTo.key() == anEntry.key() or link.itemFrom.key() == anEntry.key():
							found = True
					if not found and anEntry.key() != entry.key():
						entriesThatCanBeRelated.append(anEntry)
				if entriesThatCanBeRelated:
					firstColumn = []
					secondColumn = []
					thirdColumn = []
					numEntries = len(entriesThatCanBeRelated)
					for i in range(numEntries):
						if i < numEntries // 3:
							firstColumn.append(entriesThatCanBeRelated[i])
						elif i < 2 * numEntries // 3:
							secondColumn.append(entriesThatCanBeRelated[i])
						else:
							thirdColumn.append(entriesThatCanBeRelated[i])
					template_values = GetStandardTemplateDictionaryAndAddMore({
									'title': TITLES["RELATE_TO"],
								   	'title_extra': entry.title,
									'rakontu': rakontu, 
									'skin': rakontu.getSkinDictionary(),
									'current_member': member, 
									'entry': entry,
									'entries_first_column': firstColumn, 
									'entries_second_column': secondColumn, 
									'entries_third_column': thirdColumn, 
									'num_rows': max(len(firstColumn), max(len(secondColumn), len(thirdColumn))),
									'related_links': links,
									})
					path = os.path.join(os.path.dirname(__file__), FindTemplate('visit/relate.html'))
					self.response.out.write(template.render(path, template_values))
				else:
					self.redirect(BuildResultURL("noEntriesToRelate", rakontu=rakontu))
			else:
				self.redirect(START)
					
	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			entry = GetObjectOfTypeFromURLQuery(self.request.query_string, "url_query_entry")
			if entry:
				linksToRemove = []
				for link in entry.getLinksOfType("related"):
					if self.request.get("linkComment|%s" % link.key()):
						link.comment = self.request.get("linkComment|%s" % link.key())
						link.put()
					if self.request.get("removeLink|%s" % link.key()) == "yes":
						linksToRemove.append(link)
				for link in linksToRemove:
					db.delete(link)
				for anEntry in rakontu.getNonDraftEntries():
					if self.request.get("addLink|%s" % anEntry.key()) == "yes":
						comment = htmlEscape(self.request.get("linkComment|%s" % anEntry.key()))
						link = Link(key_name=KeyName("link"), 
								rakontu=rakontu,
								itemFrom=entry, 
								itemTo=anEntry, 
								type="related", 
								creator=member, 
								comment=comment)
						link.put()
						link.publish()
				self.redirect(BuildURL("dir_visit", "url_read", entry.urlQuery()))
			else:
				self.redirect(rakontu.linkURL())
		else:
			self.redirect(START)
			
