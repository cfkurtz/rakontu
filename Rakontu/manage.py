# --------------------------------------------------------------------------------------------
# RAKONTU
# Description: Rakontu is open source story sharing software.
# Version: beta (0.9+)
# License: GPL 3.0
# Google Code Project: http://code.google.com/p/rakontu/
# --------------------------------------------------------------------------------------------

from utils import *

class FirstOwnerVisitPage(ErrorHandlingRequestHander):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isManagerOrOwner():
				template_values = GetStandardTemplateDictionaryAndAddMore({
								'title': TITLES["WELCOME"],
								'rakontu': rakontu, 
								'skin': rakontu.getSkinDictionary(),
								'current_member': member,
								"blurbs": BLURBS,
								'resources': rakontu.getNonDraftNewMemberResourcesAsDictionaryByCategory(),
								'manager_resources': rakontu.getNonDraftNewMemberManagerResourcesAsDictionaryByCategory(),
								})
				path = os.path.join(os.path.dirname(__file__), FindTemplate('manage/first.html'))
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect(ManagersOnlyURL(rakontu))
		else:
			self.redirect(NoAccessURL(rakontu, member, users.is_current_user_admin()))
		
class ManageRakontuMembersPage(ErrorHandlingRequestHander):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if isFirstVisit: self.redirect(member.firstVisitURL())
			if member.isManagerOrOwner():
				template_values = GetStandardTemplateDictionaryAndAddMore({
								   'title': TITLES["MANAGE_MEMBERS"], 
								   'rakontu': rakontu, 
								   'skin': rakontu.getSkinDictionary(),
								   'current_member': member,
								   'rakontu_members': rakontu.getActiveMembers(),
								   'pending_members': rakontu.getPendingMembers(),
								   'inactive_members': rakontu.getInactiveMembers(),
								   })
				path = os.path.join(os.path.dirname(__file__), FindTemplate('manage/members.html'))
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect(ManagersOnlyURL(rakontu))
		else:
			self.redirect(NoAccessURL(rakontu, member, users.is_current_user_admin()))
				
	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isManagerOrOwner():
				for pendingMember in rakontu.getPendingMembers():
					if "sendInvitationEmail|%s" % pendingMember.key() in self.request.arguments():
						# maybe they changed the email and gov type then clicked on send invitation
						pendingMember.email = htmlEscape(self.request.get("email|%s" % pendingMember.key()))
						pendingMember.governanceType = self.request.get("pendingMember_governanceType|%s" % pendingMember.key())
						pendingMember.put()
						memcache.add("sendInvitationMessage:%s" % member.key(), pendingMember, HOUR_SECONDS)
						self.redirect(BuildURL("dir_manage", "url_invitation_message", member.urlQuery()))
						return
				rakontuMembers = rakontu.getActiveMembers()
				thingsToPut = []
				thingsToDelete = []
				for aMember in rakontuMembers:
					for name, value in self.request.params.items():
						if aMember.googleAccountID and value.find(aMember.googleAccountID) >= 0:
							(newType, id) = value.split("|") 
							okayToSet = False
							if newType != aMember.governanceType:
								if newType == "member":
									if not aMember.isOwner() or not rakontu.memberIsOnlyOwner(aMember):
										okayToSet = True
								elif newType == "manager":
									if not aMember.isOwner() or not rakontu.memberIsOnlyOwner(aMember):
										okayToSet = True
								elif newType == "owner":
									okayToSet = True
							if okayToSet:
								aMember.governanceType = newType
					if aMember.isRegularMember():
						for i in range(3):
							aMember.helpingRolesAvailable[i] = self.request.get("%sAvailable|%s" % (HELPING_ROLE_TYPES[i], aMember.key())) == "yes"
					else:
						for i in range(3):
							aMember.helpingRolesAvailable[i] = True
					thingsToPut.append(aMember)
				for aMember in rakontuMembers:
					if self.request.get("remove|%s" % aMember.key()) == "yes":
						aMember.active = False
						thingsToPut.append(aMember)
				for pendingMember in PendingMember.all().ancestor(rakontu):
					pendingMember.email = htmlEscape(self.request.get("email|%s" % pendingMember.key()))
					pendingMember.governanceType = self.request.get("pendingMember_governanceType|%s" % pendingMember.key())
					thingsToPut.append(pendingMember)
					if self.request.get("removePendingMember|%s" % pendingMember.key()):
						thingsToDelete.append(pendingMember)
				def txn(thingsToPut, thingsToDelete):
					db.put(thingsToPut)
					db.delete(thingsToDelete)
				db.run_in_transaction(txn, thingsToPut, thingsToDelete)
				# do these separately
				memberEmailsToAdd = htmlEscape(self.request.get("newMemberEmails")).split('\n')
				for email in memberEmailsToAdd:
					if email.strip():
						if not rakontu.hasMemberWithGoogleEmail(email.strip()):
							CreatePendingMemberFromInfo(rakontu, email.strip(), "member")
				self.redirect(BuildURL("dir_manage", "url_members", rakontu=rakontu))
			else:
				self.redirect(ManagersOnlyURL(rakontu))
		else:
			self.redirect(NoAccessURL(rakontu, member, users.is_current_user_admin()))
			
class SendInvitationMessagePage(ErrorHandlingRequestHander):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isManagerOrOwner():
				if isFirstVisit: self.redirect(member.firstVisitURL())
				try:
					pendingMember = memcache.get("sendInvitationMessage:%s" % member.key())
				except:
					pendingMember = None
				if pendingMember:
					subject = "%s %s" % (TEMPLATE_TERMS["template_invitation_to_join"], rakontu.name)
					url = "%s/%s/%s?%s" % (self.request.headers["Host"], DIRS["dir_visit"], URLS["url_home"], rakontu.urlQuery())
					body = "%s\n\n%s" % (rakontu.invitationMessage, url)
					template_values = GetStandardTemplateDictionaryAndAddMore({
								   'title': TITLES["SEND_MESSAGE"], 
						   		   'rakontu': rakontu, 
						   		   'skin': rakontu.getSkinDictionary(),
						   		   'current_member': member,
						   		   'pending_member_to_send_message_to': pendingMember,
						   		   'subject': subject,
						   		   'body': body,
						   		   'email': pendingMember.email,
						   		   })
					path = os.path.join(os.path.dirname(__file__), FindTemplate('manage/invitation_message.html'))
					self.response.out.write(template.render(path, template_values))
				else:
					self.redirect(NotFoundURL(rakontu))
			else:
				self.redirect(ManagersOnlyURL(rakontu))
		else:
			self.redirect(NoAccessURL(rakontu, member, users.is_current_user_admin()))
			
	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isManagerOrOwner():
				try:
					pendingMember = memcache.get("sendInvitationMessage:%s" % member.key())
				except:
					pendingMember = None
				if pendingMember and mail.is_email_valid(pendingMember.email):
					message = mail.EmailMessage()
					message.sender = member.googleAccountEmail
					message.reply_to = member.googleAccountEmail
					message.subject = self.request.get("subject")
					message.to = pendingMember.email 
					message.body = self.request.get("message")
					try:
						message.send()
					except:
						self.redirect(BuildResultURL("couldNotSendMessage", rakontu=rakontu))
						return
					self.redirect(BuildResultURL("messagesent", rakontu=rakontu))
				else:
					self.redirect(BuildResultURL("memberNotFound", rakontu=rakontu))
			else:
				self.redirect(ManagersOnlyURL(rakontu))
		else:
			self.redirect(NoAccessURL(rakontu, member, users.is_current_user_admin()))
				
class ManageRakontuAppearancePage(ErrorHandlingRequestHander):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if isFirstVisit: self.redirect(member.firstVisitURL())
			if member.isManagerOrOwner():
				template_values = GetStandardTemplateDictionaryAndAddMore({
								   'title': TITLES["MANAGE_APPEARANCE"], 
								   'rakontu': rakontu, 
								   'skin': rakontu.getSkinDictionary(),
								   'current_member': member,
								   'skin_names': GetSkinNames(),
								   'time_zone_names': pytz.all_timezones,
								   })
				path = os.path.join(os.path.dirname(__file__), FindTemplate('manage/appearance.html'))
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect(ManagersOnlyURL(rakontu))
		else:
			self.redirect(NoAccessURL(rakontu, member, users.is_current_user_admin()))
	
	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isManagerOrOwner():
				rakontu.name = htmlEscape(self.request.get("name"))
				rakontu.tagline = htmlEscape(self.request.get("tagline"))
				rakontu.skinName = self.request.get("skinName")
				if rakontu.skinName == TERMS["term_custom"]:
					rakontu.customSkin = db.Text(self.request.get("customSkin"))
				url = self.request.get("externalStyleSheetURL")
				if url and url != "None":
					rakontu.externalStyleSheetURL = url
				else:
					rakontu.externalStyleSheetURL = None
				text = self.request.get("description")
				format = self.request.get("description_format").strip()
				rakontu.description = text
				rakontu.description_formatted = db.Text(InterpretEnteredText(text, format))
				rakontu.description_format = format
				text = self.request.get("welcomeMessage")
				format = self.request.get("welcomeMessage_format").strip()
				rakontu.welcomeMessage = text
				rakontu.welcomeMessage_formatted = db.Text(InterpretEnteredText(text, format))
				rakontu.welcomeMessage_format = format
				rakontu.invitationMessage = htmlEscape(self.request.get("invitationMessage"))
				text = self.request.get("etiquetteStatement")
				format = self.request.get("etiquetteStatement_format").strip()
				rakontu.etiquetteStatement = text
				rakontu.etiquetteStatement_formatted = db.Text(InterpretEnteredText(text, format))
				rakontu.etiquetteStatement_format = format
				rakontu.defaultTimeZoneName = self.request.get("defaultTimeZoneName")
				rakontu.defaultDateFormat = self.request.get("defaultDateFormat")
				rakontu.defaultTimeFormat = self.request.get("defaultTimeFormat")
				if self.request.get("img"):
					rakontu.image = db.Blob(images.resize(str(self.request.get("img")), THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT))
				if self.request.get("removeImage"):
					rakontu.image = None
				for i in range(3):
					rakontu.roleReadmes[i] = db.Text(self.request.get("readme%s" % i))
					rakontu.roleReadmes_formatted[i] = db.Text(InterpretEnteredText(self.request.get("readme%s" % i), self.request.get("roleReadmes_formats%s" % i)))
					rakontu.roleReadmes_formats[i] = self.request.get("roleReadmes_formats%s" % i)
				rakontu.put()
				self.redirect(self.request.uri)
			else:
				self.redirect(ManagersOnlyURL(rakontu))
		else:
			self.redirect(NoAccessURL(rakontu, member, users.is_current_user_admin()))
		
class ManageRakontuSettingsPage(ErrorHandlingRequestHander):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if isFirstVisit: self.redirect(member.firstVisitURL())
			if member.isManagerOrOwner():
				nudgePointIncludes = []
				for level in [0, len(EVENT_TYPES) // 2]:
					if level == 0:
						nextLevel = len(EVENT_TYPES) // 2
					else:
						nextLevel = len(EVENT_TYPES)
					nudgePointIncludes.append('<tr>')
					i = 0
					for eventType in EVENT_TYPES:
						if i >= level and i < nextLevel:
							nudgePointIncludes.append('<th>%s</th>' % EVENT_TYPES_DISPLAY[i])
						i += 1
					nudgePointIncludes.append('</tr><tr>')
					i = 0
					for eventType in EVENT_TYPES:
						if i >= level and i < nextLevel: 
							if i == 0: 
								nudgePointIncludes.append("<td>(%s)</td>" % TERMS["term_does_not_apply"])
							else:
								nudgePointIncludes.append('<td><input type="text" name="member|%s" size="2" value="%s" maxlength="{{maxlength_number}}"/></td>' \
									% (eventType, rakontu.memberNudgePointsPerEvent[i]))
						i += 1
					nudgePointIncludes.append('</tr>')
				
				activityPointIncludes = []
				for level in [0, len(EVENT_TYPES) // 2]:
					if level == 0:
						nextLevel = len(EVENT_TYPES) // 2
					else:
						nextLevel = len(EVENT_TYPES)				
					activityPointIncludes.append('<tr>')
					i = 0
					for eventType in EVENT_TYPES:
						if i >= level and i < nextLevel:
							activityPointIncludes.append('<th>%s</th>' % EVENT_TYPES_DISPLAY[i])
						i += 1
					i = 0
					activityPointIncludes.append('</tr><tr>')
					for eventType in EVENT_TYPES:
						if i >= level and i < nextLevel:
							activityPointIncludes.append('<td><input type="text" name="entry|%s" size="3" value="%s" maxlength="{{maxlength_number}}"/></td>' \
														% (eventType, rakontu.entryActivityPointsPerEvent[i]))
						i += 1 
					activityPointIncludes.append('</tr>')
				
				characterIncludes = []
				i = 0
				for entryType in ENTRY_AND_ANNOTATION_TYPES:
					characterIncludes.append('<input type="checkbox" name="character|%s" value="yes" %s id="character|%s"/><label for="character|%s">%s</label>' \
							% (entryType, checkedBlank(rakontu.allowCharacter[i]), entryType, entryType, ENTRY_AND_ANNOTATION_TYPES_DISPLAY[i]))
					i += 1
					
				editingIncludes = []
				template_values = GetStandardTemplateDictionaryAndAddMore({
								   'title': TITLES["MANAGE_SETTINGS"], 
								   'rakontu': rakontu, 
								   'skin': rakontu.getSkinDictionary(),
								   'current_member': member,
								   'character_includes': characterIncludes,
								   'nudge_point_includes': nudgePointIncludes,
								   'activity_point_includes': activityPointIncludes,
								   'site_allows_attachments': DEFAULT_MAX_NUM_ATTACHMENTS > 0,
								   'num_attachment_choices': NUM_ATTACHMENT_CHOICES,
								   })
				path = os.path.join(os.path.dirname(__file__), FindTemplate('manage/settings.html'))
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect(ManagersOnlyURL(rakontu))
		else:
			self.redirect(NoAccessURL(rakontu, member, users.is_current_user_admin()))
	
	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isManagerOrOwner():
				rakontu.allowNonManagerCuratorsToEditTags = self.request.get("allowNonManagerCuratorsToEditTags") == "yes"
				i = 0
				for entryType in ENTRY_AND_ANNOTATION_TYPES:
					rakontu.allowCharacter[i] = self.request.get("character|%s" % entryType) == "yes"
					i += 1
				oldValue = rakontu.maxNudgePointsPerEntry
				try:
					rakontu.maxNudgePointsPerEntry = int(self.request.get("maxNudgePointsPerEntry"))
				except:
					rakontu.maxNudgePointsPerEntry = oldValue
				for i in range(NUM_NUDGE_CATEGORIES):
					rakontu.nudgeCategories[i] = htmlEscape(self.request.get("nudgeCategory%s" % i))
				for i in range(NUM_NUDGE_CATEGORIES):
					rakontu.nudgeCategoryQuestions[i] = htmlEscape(self.request.get("nudgeCategoryQuestion%s" % i))
				oldValue = rakontu.maxNumAttachments
				try:
					rakontu.maxNumAttachments = int(self.request.get("maxNumAttachments"))
				except:
					rakontu.maxNumAttachments = oldValue
				i = 0
				for eventType in EVENT_TYPES:
					if eventType != EVENT_TYPES[0]: # leave time out for nudge accumulations
						oldValue = rakontu.memberNudgePointsPerEvent[i]
						try:
							rakontu.memberNudgePointsPerEvent[i] = int(self.request.get("member|%s" % eventType))
						except:
							rakontu.memberNudgePointsPerEvent[i] = oldValue
					i += 1
				i = 0
				for eventType in EVENT_TYPES:
					oldValue = rakontu.entryActivityPointsPerEvent[i]
					try:
						rakontu.entryActivityPointsPerEvent[i] = int(self.request.get("entry|%s" % eventType))
					except:
						rakontu.entryActivityPointsPerEvent[i] = oldValue
					i += 1
				rakontu.put()
				self.redirect(self.request.uri)
			else:
				self.redirect(ManagersOnlyURL(rakontu))
		else:
			self.redirect(NoAccessURL(rakontu, member, users.is_current_user_admin()))
		
class ManageRakontuQuestionsListPage(ErrorHandlingRequestHander):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if isFirstVisit: self.redirect(member.firstVisitURL())
			if member.isManagerOrOwner():
				counts = rakontu.getQuestionCountsForAllTypes()
				template_values = GetStandardTemplateDictionaryAndAddMore({
								   'title': TITLES["MANAGE_QUESTIONS"], 
								   'rakontu': rakontu, 
								   'skin': rakontu.getSkinDictionary(),
								   'current_member': member,
								   'counts': counts,
								   'refer_types': QUESTION_REFERS_TO,
								   'refer_types_display': QUESTION_REFERS_TO_DISPLAY,
								   'refer_types_urls': QUESTION_REFERS_TO_URLS,
								   'refer_types_plural': QUESTION_REFERS_TO_PLURAL,
								   'refer_types_plural_display': QUESTION_REFERS_TO_PLURAL_DISPLAY,
								   'num_types': len(QUESTION_REFERS_TO),
								   })
				path = os.path.join(os.path.dirname(__file__), FindTemplate('manage/questionsList.html'))
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect(ManagersOnlyURL(rakontu))
		else:
			self.redirect(NoAccessURL(rakontu, member, users.is_current_user_admin()))
				
class ManageRakontuQuestionsPage(ErrorHandlingRequestHander):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if isFirstVisit: self.redirect(member.firstVisitURL())
			if member.isManagerOrOwner():
				i = 0
				for aType in QUESTION_REFERS_TO_URLS:
					if self.request.uri.find(aType) >= 0:
						type = aType
						typePlural = QUESTION_REFERS_TO_PLURAL[i]
						typeURL = QUESTION_REFERS_TO_URLS[i]
						typeDisplay = QUESTION_REFERS_TO_DISPLAY[i]
						typePluralDisplay = QUESTION_REFERS_TO_PLURAL_DISPLAY[i]
						break
					i += 1
				sortedQuestions = rakontu.getQuestionsOfType(type)
				sortedQuestions.sort(lambda a,b: cmp(a.order, b.order))
				systemQuestionsOfType = SystemQuestionsOfType(type)
				template_values = GetStandardTemplateDictionaryAndAddMore({
								   'title': TITLES["MANAGE_QUESTIONS_ABOUT"], 
							   	   'title_extra': DisplayTypePluralForQuestionRefersTo(type), 
								   'rakontu': rakontu, 
								   'skin': rakontu.getSkinDictionary(),
								   'current_member': member,
								   'questions': sortedQuestions,
								   'question_types': QUESTION_TYPES,
								   'question_types_display': QUESTION_TYPES_DISPLAY,
								   'system_questions': systemQuestionsOfType,
								   'max_num_choices': MAX_NUM_CHOICES_PER_QUESTION,
								   'refer_type': type,
								   'refer_type_url': typeURL,
								   'refer_type_display': typeDisplay,
								   'refer_type_plural': typePlural,
								   'refer_type_plural_display': typePluralDisplay,
								   })
				path = os.path.join(os.path.dirname(__file__), FindTemplate('manage/questions.html'))
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect(ManagersOnlyURL(rakontu))
		else:
			self.redirect(NoAccessURL(rakontu, member, users.is_current_user_admin()))
	
	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isManagerOrOwner():
				i = 0
				for aType in QUESTION_REFERS_TO_URLS:
					if self.request.uri.find(aType) >= 0:
						type = aType
						break
					i += 1
				rakontuQuestionsOfType = rakontu.getQuestionsOfType(type)
				systemQuestionsOfType = SystemQuestionsOfType(type)
				questionsToPut = []
				for question in rakontuQuestionsOfType:
					if "moveUp|%s" % question.key() in self.request.arguments():
						MoveItemWithOrderFieldUpOrDownInList(question, rakontuQuestionsOfType, -1)
					elif "moveDown|%s" % question.key() in self.request.arguments():
						MoveItemWithOrderFieldUpOrDownInList(question, rakontuQuestionsOfType, 1)
					elif "activate|%s" % question.key() in self.request.arguments():
						question.active = True
					elif "inactivate|%s" % question.key() in self.request.arguments():
						question.active = False
				questionsToPut.extend(rakontuQuestionsOfType)
				for question in rakontuQuestionsOfType:
					if self.request.get("inactivate|%s" % question.key()):
						question.active = False
						questionsToPut.append(question)
				questionNamesToAdd = htmlEscape(self.request.get("newQuestionNames")).split('\n')
				for name in questionNamesToAdd:
					if name.strip():
						foundQuestion = False
						for oldQuestion in rakontu.getInactiveQuestionsOfType(type):
							if oldQuestion.name == name.strip():
								foundQuestion = True
								oldQuestion.active = True
								questionsToPut.append(oldQuestion)
								break
						if not foundQuestion:
							keyName = GenerateSequentialKeyName("question", rakontu)
							question = Question(
											key_name=keyName, 
											parent=rakontu,
											id=keyName,
											rakontu=rakontu, 
											name=name, 
											refersTo=type, 
											text=name)
							questionsToPut.append(question)
				for sysQuestion in systemQuestionsOfType:
					if self.request.get("copy|%s" % sysQuestion.key()) == "copy|%s" % sysQuestion.key():
						newQuestion = rakontu.GenerateCopyOfQuestion(sysQuestion)
						questionsToPut.append(newQuestion)
				if self.request.get("import"):
					newQuestions = rakontu.GenerateQuestionsOfTypeFromCSV(type, str(self.request.get("import")))
					questionsToPut.extend(newQuestions)
				def txn(questionsToPut):
					db.put(questionsToPut)
				db.run_in_transaction(txn, questionsToPut)
				self.redirect(self.request.uri)
			else:
				self.redirect(ManagersOnlyURL(rakontu))
		else:
			self.redirect(NoAccessURL(rakontu, member, users.is_current_user_admin()))
		
class ManageOneQuestionPage(ErrorHandlingRequestHander):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if isFirstVisit: self.redirect(member.firstVisitURL())
			if member.isManagerOrOwner():
				question = GetObjectOfTypeFromURLQuery(self.request.query_string, "url_query_question")
				if question:
					answerCounts = question.getAnswersReport()
					template_values = GetStandardTemplateDictionaryAndAddMore({
									   'title': TITLES["MANAGE_QUESTION"], 
								   	   'title_extra': question.name,
									   'rakontu': rakontu, 
									   'skin': rakontu.getSkinDictionary(),
									   'current_member': member,
									   'question': question,
									   'question_types': QUESTION_TYPES,
									   'question_types_display': QUESTION_TYPES_DISPLAY,
									   'answer_counts': answerCounts,
									   'refer_type': CorrespondingItemFromMatchedOrderList(question.refersTo, QUESTION_REFERS_TO, QUESTION_REFERS_TO_URLS)
									   })
					path = os.path.join(os.path.dirname(__file__), FindTemplate('manage/question.html'))
					self.response.out.write(template.render(path, template_values))
				else:
					self.redirect(NotFoundURL(rakontu))
			else:
				self.redirect(ManagersOnlyURL(rakontu))
		else:
			self.redirect(NoAccessURL(rakontu, member, users.is_current_user_admin()))
	
	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isManagerOrOwner():
				question = GetObjectOfTypeFromURLQuery(self.request.query_string, "url_query_question")
				i = 0
				for aType in QUESTION_REFERS_TO_URLS:
					if question.refersTo == aType:
						typeURL = QUESTION_REFERS_TO_URLS[i]
						break
					i += 1
				if question and typeURL:
					question.name = htmlEscape(self.request.get("name"))
					if not question.name:
						question.name = DEFAULT_QUESTION_NAME
					question.text = htmlEscape(self.request.get("text"))
					question.help = htmlEscape(self.request.get("help"))
					if self.request.get("type"):
						question.type = self.request.get("type")
					if self.request.get("choices"):
						question.choices = []
						choicesToAdd = htmlEscape(self.request.get("choices")).split('\n')
						for choice in choicesToAdd:
							if choice.strip():
								question.choices.append(choice.strip())
					if self.request.get("minIfValue"):
						oldValue = question.minIfValue
						try:
							question.minIfValue = int(self.request.get("minIfValue"))
						except:
							question.minIfValue = oldValue
					if self.request.get("maxIfValue"):
						oldValue = question.maxIfValue
						try:
							question.maxIfValue = int(self.request.get("maxIfValue"))
						except:
							question.maxIfValue = oldValue
					if self.request.get("positiveResponseIfBoolean"):
						question.positiveResponseIfBoolean = self.request.get("positiveResponseIfBoolean")
					if self.request.get("negativeResponseIfBoolean"):
						question.negativeResponseIfBoolean = self.request.get("negativeResponseIfBoolean")
					if self.request.get("multiple"):
						question.multiple = self.request.get("multiple") == "yes"
					question.put()
					if question.getUnlinkedAnswerChoices():
						self.redirect(BuildURL("dir_manage", "url_unlinked_answers", question.urlQuery(), rakontu=rakontu))
					else:
						self.redirect(self.request.uri)
				else:
					self.redirect(NotFoundURL(rakontu))
			else:
				self.redirect(ManagersOnlyURL(rakontu))
		else:
			self.redirect(NoAccessURL(rakontu, member, users.is_current_user_admin()))
		
class FixHangingAnswersPage(ErrorHandlingRequestHander):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if isFirstVisit: self.redirect(member.firstVisitURL())
			if member.isManagerOrOwner():
				question = GetObjectOfTypeFromURLQuery(self.request.query_string, "url_query_question")
				if question:
					unlinkedAnswerChoices = question.getUnlinkedAnswerChoices()
					template_values = GetStandardTemplateDictionaryAndAddMore({
									   'title': TITLES["FIX_HANGING_ANSWERS_FOR"], 
								   	   'title_extra': question.name,
									   'rakontu': rakontu, 
									   'skin': rakontu.getSkinDictionary(),
									   'current_member': member,
									   'question': question,
									   'unlinked_answer_choices': unlinkedAnswerChoices,
									   })
					path = os.path.join(os.path.dirname(__file__), FindTemplate('manage/question_unlinkedAnswerChoices.html'))
					self.response.out.write(template.render(path, template_values))
				else:
					self.redirect(NotFoundURL(rakontu))
			else:
				self.redirect(ManagersOnlyURL(rakontu))
		else:
			self.redirect(NoAccessURL(rakontu, member, users.is_current_user_admin()))
	
	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isManagerOrOwner():
				question = GetObjectOfTypeFromURLQuery(self.request.query_string, "url_query_question")
				if question:
					unlinkedAnswerChoices = question.getUnlinkedAnswerChoices()
					oldAndNewChoices = []
					for unlinkedChoice in unlinkedAnswerChoices:
						response = self.request.get("change|%s" % unlinkedChoice)
						if response and response != "none":
							oldAndNewChoices.append((unlinkedChoice, response))
					if oldAndNewChoices:
						for oldNewPair in oldAndNewChoices:
							answers = question.getAnswers()
							for answer in answers:
								if question.multiple:
									newAnswerChoices = {} # dict because there could be duplication caused by renaming
									for i in range(len(answer.answerIfMultiple)):
										if answer.answerIfMultiple[i] == oldNewPair[0]:
											newAnswerChoices[oldNewPair[1]] = 1
										else:
											newAnswerChoices[answer.answerIfMultiple[i]] = 1
									answer.answerIfMultiple = []
									answer.answerIfMultiple.extend(newAnswerChoices.keys())
								else:
									if answer.answerIfText == oldNewPair[0]:
										answer.answerIfText = oldNewPair[1]
						db.put(answers)
					self.redirect(BuildURL("dir_manage", "url_question", question.urlQuery(), rakontu=rakontu))
				else:
					self.redirect(NotFoundURL(rakontu))
			else:
				self.redirect(ManagersOnlyURL(rakontu))
		else:
			self.redirect(NoAccessURL(rakontu, member, users.is_current_user_admin()))
		
class WriteQuestionsToCSVPage(ErrorHandlingRequestHander):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if isFirstVisit: self.redirect(member.firstVisitURL())
			if member.isManagerOrOwner():
				displayType = GetStringOfTypeFromURLQuery(self.request.query_string, "url_query_export_type")
				type = None
				i = 0
				for aDisplayType in QUESTION_REFERS_TO_PLURAL_DISPLAY:
					if displayType == aDisplayType:
						type = QUESTION_REFERS_TO[i]
						break
					i += 1
				if type:
					export = rakontu.createOrRefreshExport("exportQuestions", "questions", member=member, questionType=type, fileFormat="csv")
					self.redirect(BuildURL(None, "url_export", export.urlQuery()))
				else:
					self.redirect(BuildResultURL("noQuestionsToExport", rakontu=rakontu))
			else:
				self.redirect(ManagersOnlyURL(rakontu))
		else:
			self.redirect(NoAccessURL(rakontu, member, users.is_current_user_admin()))
			
class ManageCharactersPage(ErrorHandlingRequestHander):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if isFirstVisit: self.redirect(member.firstVisitURL())
			if member.isManagerOrOwner():
				template_values = GetStandardTemplateDictionaryAndAddMore({
								   'title': TITLES["MANAGE_CHARACTERS"], 
								   'rakontu': rakontu, 
								   'skin': rakontu.getSkinDictionary(),
								   'current_member': member,
								   'characters': rakontu.getActiveCharacters(),
								   'inactive_characters': rakontu.getInactiveCharacters(),
								   })
				path = os.path.join(os.path.dirname(__file__), FindTemplate('manage/characters.html'))
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect(ManagersOnlyURL(rakontu))
		else:
			self.redirect(NoAccessURL(rakontu, member, users.is_current_user_admin()))
				
	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isManagerOrOwner():
				charactersToPut = []
				for character in rakontu.getActiveCharacters():
					if self.request.get("remove|%s" % character.key()):
						character.active = False
						charactersToPut.append(character)
				namesToAdd = htmlEscape(self.request.get("newCharacterNames")).split('\n')
				for name in namesToAdd:
					if name.strip():
						foundCharacter = False
						for oldCharacter in rakontu.getInactiveCharacters():
							if oldCharacter.name == name.strip():
								foundCharacter = True
								oldCharacter.active = True
								charactersToPut.append(oldCharacter)
								break
						if not foundCharacter:
							keyName = GenerateSequentialKeyName("character", rakontu)
							newCharacter = Character(
													key_name=keyName, 
													parent=rakontu,
													id=keyName,
													rakontu=rakontu,
													name=name)
							charactersToPut.append(newCharacter)
				def txn(charactersToPut):
					db.put(charactersToPut)
				db.run_in_transaction(txn, charactersToPut)
				self.redirect(self.request.uri)
			else:
				self.redirect(ManagersOnlyURL(rakontu))
		else:
			self.redirect(NoAccessURL(rakontu, member, users.is_current_user_admin()))
		
class ManageCharacterPage(ErrorHandlingRequestHander):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if isFirstVisit: self.redirect(member.firstVisitURL())
			if member.isManagerOrOwner():
				character = GetObjectOfTypeFromURLQuery(self.request.query_string, "url_query_character")
				sortedQuestions = rakontu.getActiveQuestionsOfType("character")
				sortedQuestions.sort(lambda a,b: cmp(a.order, b.order))
				template_values = GetStandardTemplateDictionaryAndAddMore({
								   'title': TITLES["MANAGE_CHARACTER"],
							   	   'title_extra': character.name, 
								   'rakontu': rakontu, 
								   'skin': rakontu.getSkinDictionary(),
								   'character': character,
								   'current_member': member,
								   'questions': sortedQuestions,
								   'answers': character.getAnswers(),
								   'refer_type': "character",
								   'refer_type_display': DisplayTypeForQuestionReferType("character"),
								   })
				path = os.path.join(os.path.dirname(__file__), FindTemplate('manage/character.html'))
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect(ManagersOnlyURL(rakontu))
		else:
			self.redirect(NoAccessURL(rakontu, member, users.is_current_user_admin()))
							 
	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isManagerOrOwner():
				goAhead = True
				for argument in self.request.arguments():
					if argument.find("|") >= 0:
						for aCharacter in rakontu.getActiveCharacters():
							if argument == "changeSettings|%s" % aCharacter.key():
								try:
									character = aCharacter
								except: 
									character = None
									goAhead = False
								break
				if goAhead:
					thingsToPut = []
					thingsToDelete = []
					character.name = htmlEscape(self.request.get("name")).strip()
					text = self.request.get("description")
					format = self.request.get("description_format").strip()
					character.description = text
					character.description_formatted = db.Text(InterpretEnteredText(text, format))
					character.description_format = format
					text = self.request.get("etiquetteStatement")
					format = self.request.get("etiquetteStatement_format").strip()
					character.etiquetteStatement = text
					character.etiquetteStatement_formatted = db.Text(InterpretEnteredText(text, format))
					character.etiquetteStatement_format = format
					if self.request.get("removeImage") == "yes":
						character.image = None
					elif self.request.get("img"):
						character.image = db.Blob(images.resize(str(self.request.get("img")), THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT))
					thingsToPut.append(character)
					questions = rakontu.getActiveQuestionsOfType("character")
					answersToPut = []
					for question in questions:
						queryText = "%s" % question.key()
						response = self.request.get(queryText)
						keepAnswer = ShouldKeepAnswer(self.request, queryText, question)
						foundAnswer = character.getAnswerForQuestion(question)
						if keepAnswer:
							if foundAnswer:
								answerToEdit = foundAnswer
							else:
								keyName = GenerateSequentialKeyName("answer", rakontu)
								answerToEdit = Answer(
													key_name=keyName, 
													id=keyName,
													parent=character,
													rakontu=rakontu, 
													question=question, 
													questionType=question.type,
													referent=character, 
													referentType="character")
							answerToEdit.setValueBasedOnResponse(question, self.request, queryText, response)
							answerToEdit.creator = member
							thingsToPut.append(answerToEdit)
						else:
							if foundAnswer:
								thingsToDelete.append(foundAnswer)
					def txn(thingsToPut, thingsToDelete):
						db.put(thingsToPut)
						db.delete(thingsToDelete)
					db.run_in_transaction(txn, thingsToPut, thingsToDelete)
					self.redirect(BuildURL("dir_manage", "url_characters", rakontu=rakontu))
			else:
				self.redirect(ManagersOnlyURL(rakontu))
		else:
			self.redirect(NoAccessURL(rakontu, member, users.is_current_user_admin()))
		
class ExportRakontuDataPage(ErrorHandlingRequestHander):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isManagerOrOwner():
				choices = ["rakontu"]
				displayChoices = ["Rakontu"]
				numMembers = rakontu.numActiveMembers()
				if numMembers < EXPORT_RANGE_XML:
					memberRanges = None
				else:
					memberRanges = []
					numRanges = numMembers // EXPORT_RANGE_XML + 1
					for i in range(numRanges):
						rangeStart = i * EXPORT_RANGE_XML + 1
						rangeEnd = (i+1) * EXPORT_RANGE_XML 
						if rangeEnd > numMembers:
							rangeEnd = numMembers
						memberRanges.append("%s-%s" % (rangeStart, rangeEnd))
				if memberRanges:
					for aRange in memberRanges:
						displayChoices.append("%s %s" % (TEMPLATE_TERMS["template_members"], aRange))
						choices.append("%s|%s" % ("members", aRange))
				else:
					displayChoices.append("%s (%s)" % (TEMPLATE_TERMS["template_members"], numMembers))
					choices.append("members")
				typeCount = 0
				for type in ENTRY_TYPES:
					numEntries = rakontu.numNonDraftEntriesOfType(type)
					if numEntries:
						if numEntries <= EXPORT_RANGE_XML:
							ranges = None
						else:
							ranges = []
							if numEntries % EXPORT_RANGE_XML == 0:
								numRanges = numEntries // EXPORT_RANGE_XML
							else:
								numRanges = numEntries // EXPORT_RANGE_XML + 1
							for i in range(numRanges):
								rangeStart = i * EXPORT_RANGE_XML + 1
								rangeEnd = (i+1) * EXPORT_RANGE_XML 
								if rangeEnd > numEntries:
									rangeEnd = numEntries
								ranges.append("%s-%s" % (rangeStart, rangeEnd))
						displayName = ENTRY_TYPES_PLURAL_DISPLAY[typeCount].capitalize()
						internalName = ENTRY_TYPES[typeCount]
						if ranges:
							for aRange in ranges:
								displayChoices.append("%s %s" % (displayName, aRange))
								choices.append("%s|%s" % (ENTRY_TYPES[typeCount], aRange))
						else:
							displayChoices.append("%s (%s)" % (displayName, numEntries))
							choices.append(internalName)
					typeCount += 1
				csvChoices = []
				for choice in choices:
					if not choice.find("rakontu") >= 0 and not choice.find("members") >= 0:
						csvChoices.append(choice)
				csvDisplayChoices = []
				for choice in displayChoices:
					if not choice.find("Rakontu") >= 0 and not choice.find(TEMPLATE_TERMS["template_members"]) >= 0:
						csvDisplayChoices.append(choice)
				template_values = GetStandardTemplateDictionaryAndAddMore({
								   	   'title': TITLES["EXPORT_DATA"], 
									   'rakontu': rakontu,
									   'skin': rakontu.getSkinDictionary(),
									   'current_member': member,
									   'xml_export': rakontu.getExportOfType("xml_export"),
									   'csv_export': rakontu.getExportOfType("csv_export_all"),
									   'choices': choices,
									   'display_choices': displayChoices,
									   'csv_choices': csvChoices,
									   'display_csv_choices': csvDisplayChoices,
									   })
				path = os.path.join(os.path.dirname(__file__), FindTemplate('manage/export.html'))
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect(ManagersOnlyURL(rakontu))
		else:
			self.redirect(NoAccessURL(rakontu, member, users.is_current_user_admin()))
				
	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isManagerOrOwner():
				if "csv_export" in self.request.arguments():
					subtypeAndRange = self.request.get("exportWhatToCSV")
					subtypeAndRangeArray = subtypeAndRange.split("|")
					subtype = subtypeAndRangeArray[0]
					if len(subtypeAndRangeArray) > 1 and subtypeAndRangeArray[1]:
						startNumberString, endNumberString = subtypeAndRangeArray[1].split("-")
						startNumber = int(startNumberString) - 1
						endNumber = int(endNumberString) - 1
						if endNumber == startNumber:
							endNumber += 1 
					else:
						startNumber = None
						endNumber = None
					export = rakontu.createOrRefreshExport(type="csv_export_all", member=member, subtype=subtype, startNumber=startNumber, endNumber=endNumber, fileFormat="csv")
					self.redirect(BuildURL(None, "url_export", export.urlQuery()))
				elif "xml_export" in self.request.arguments():
					subtypeAndRange = self.request.get("exportWhatToXML")
					subtypeAndRangeArray = subtypeAndRange.split("|")
					subtype = subtypeAndRangeArray[0]
					if len(subtypeAndRangeArray) > 1 and subtypeAndRangeArray[1]:
						startNumberString, endNumberString = subtypeAndRangeArray[1].split("-")
						startNumber = int(startNumberString) - 1
						endNumber = int(endNumberString) - 1
					else:
						startNumber = None
						endNumber = None
					export = rakontu.createOrRefreshExport(type="xml_export", member=member, subtype=subtype, startNumber=startNumber, endNumber=endNumber, fileFormat="xml")
					self.redirect(BuildURL(None, "url_export", export.urlQuery()))
			else:
				self.redirect(ManagersOnlyURL(rakontu))
		else:
			self.redirect(NoAccessURL(rakontu, member, users.is_current_user_admin()))

class ExportFilteredItemsPage(ErrorHandlingRequestHander):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isManagerOrOwner():
				export = rakontu.createOrRefreshExport("csv_export_filter", subtype="filter", member=member, fileFormat="csv")
				self.redirect(BuildURL(None, "url_export", export.urlQuery()))
			else:
				self.redirect(ManagersOnlyURL(rakontu))
		else:
			self.redirect(NoAccessURL(rakontu, member, users.is_current_user_admin()))
		
class SetRakontuAvailabilityPage(ErrorHandlingRequestHander):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access: 
			if member.isManagerOrOwner():
				template_values = GetStandardTemplateDictionaryAndAddMore({
								   'title': TITLES["SET_RAKONTU_AVAILABILITY"], 
								   'title_extra': rakontu.name,
								   'rakontu': rakontu, 
								   'skin': rakontu.getSkinDictionary(),
								   'current_member': member,
						   	   	   'rakontu_access_states': RAKONTU_ACCESS_STATES,
						   	  	   'rakontu_access_states_display': RAKONTU_ACCESS_STATES_DISPLAY,
								   })
				path = os.path.join(os.path.dirname(__file__), FindTemplate('manage/setAvailability.html'))
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect(ManagersOnlyURL(rakontu))
		else:
			self.redirect(NoAccessURL(rakontu, member, users.is_current_user_admin()))
			
	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isManagerOrOwner():
				if "changeAccess" in self.request.arguments():
					rakontu.access = self.request.get("access")
					rakontu.accessMessage = self.request.get("accessMessage")
					rakontu.put()
				self.redirect(self.request.uri)
			else:
				self.redirect(ManagersOnlyURL(rakontu))
		else:
			self.redirect(NoAccessURL(rakontu, member, users.is_current_user_admin()))
