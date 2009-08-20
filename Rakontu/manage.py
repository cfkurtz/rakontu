# --------------------------------------------------------------------------------------------
# RAKONTU
# Description: Rakontu is open source story sharing software.
# Version: pre-0.1
# License: GPL 3.0
# Google Code Project: http://code.google.com/p/rakontu/
# --------------------------------------------------------------------------------------------

from utils import *

class FirstOwnerVisitPage(webapp.RequestHandler):
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
								})
				path = os.path.join(os.path.dirname(__file__), FindTemplate('manage/first.html'))
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect(rakontu.linkURL())
		else:
			self.redirect(START)
		
class ManageRakontuMembersPage(webapp.RequestHandler):
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
				self.redirect(rakontu.linkURL())
		else:
			self.redirect(START)
				
	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isManagerOrOwner():
				rakontuMembers = rakontu.getActiveMembers()
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
					aMember.put()
				for aMember in rakontuMembers:
					if self.request.get("remove|%s" % aMember.key()) == "yes":
						aMember.active = False
						aMember.put()
				for pendingMember in rakontu.getPendingMembers():
					pendingMember.email = htmlEscape(self.request.get("email|%s" % pendingMember.key()))
					pendingMember.put()
					if self.request.get("removePendingMember|%s" % pendingMember.key()):
						db.delete(pendingMember)
				memberEmailsToAdd = htmlEscape(self.request.get("newMemberEmails")).split('\n')
				for email in memberEmailsToAdd:
					if email.strip():
						if not rakontu.hasMemberWithGoogleEmail(email.strip()):
							newPendingMember = PendingMember(key_name=KeyName("pendingmember"), rakontu=rakontu, email=email.strip())
							newPendingMember.put()
				self.redirect(BuildURL("dir_manage", "url_members", rakontu=rakontu))
			else:
				self.redirect(rakontu.linkURL())
		else:
			self.redirect(START)
				
class ManageRakontuSettingsPage(webapp.RequestHandler):
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
							nudgePointIncludes.append('<td>%s</td>' % EVENT_TYPES_DISPLAY[i])
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
							activityPointIncludes.append('<td>%s</td>' % EVENT_TYPES_DISPLAY[i])
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
				i = 0
				for entryType in ENTRY_TYPES:
					editingIncludes.append('<input type="checkbox" name="editing|%s" value="yes" %s id="editing|%s"/><label for="editing|%s">%s</label>' \
							% (entryType, checkedBlank(rakontu.allowEditingAfterPublishing[i]), entryType, entryType, ENTRY_TYPES_DISPLAY[i]))
					i += 1
				template_values = GetStandardTemplateDictionaryAndAddMore({
								   'title': TITLES["MANAGE_SETTINGS"], 
								   'rakontu': rakontu, 
								   'skin': rakontu.getSkinDictionary(),
								   'current_member': member,
								   'current_date': datetime.now(tz=pytz.utc),
								   'character_includes': characterIncludes,
								   'editing_includes': editingIncludes,
								   'nudge_point_includes': nudgePointIncludes,
								   'activity_point_includes': activityPointIncludes,
								   'site_allows_attachments': DEFAULT_MAX_NUM_ATTACHMENTS > 0,
								   'skin_names': GetSkinNames(),
								   })
				path = os.path.join(os.path.dirname(__file__), FindTemplate('manage/settings.html'))
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect(rakontu.linkURL())
		else:
			self.redirect(START)
	
	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isManagerOrOwner():
				rakontu.name = htmlEscape(self.request.get("name"))
				rakontu.tagline = htmlEscape(self.request.get("tagline"))
				rakontu.skinName = self.request.get("skinName")
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
				text = self.request.get("etiquetteStatement")
				format = self.request.get("etiquetteStatement_format").strip()
				rakontu.etiquetteStatement = text
				rakontu.etiquetteStatement_formatted = db.Text(InterpretEnteredText(text, format))
				rakontu.etiquetteStatement_format = format
				rakontu.contactEmail = self.request.get("contactEmail")
				rakontu.defaultTimeZoneName = self.request.get("defaultTimeZoneName")
				rakontu.defaultDateFormat = self.request.get("defaultDateFormat")
				rakontu.defaultTimeFormat = self.request.get("defaultTimeFormat")
				rakontu.allowNonManagerCuratorsToEditTags = self.request.get("allowNonManagerCuratorsToEditTags") == "yes"
				if self.request.get("img"):
					rakontu.image = db.Blob(images.resize(str(self.request.get("img")), 100, 60))
				if self.request.get("removeImage"):
					rakontu.image = None
				i = 0
				for entryType in ENTRY_AND_ANNOTATION_TYPES:
					rakontu.allowCharacter[i] = self.request.get("character|%s" % entryType) == "yes"
					i += 1
				i = 0
				for entryType in ENTRY_TYPES:
					rakontu.allowEditingAfterPublishing[i] = self.request.get("editing|%s" % entryType) == "yes"
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
				for i in range(3):
					rakontu.roleReadmes[i] = db.Text(self.request.get("readme%s" % i))
					rakontu.roleReadmes_formatted[i] = db.Text(InterpretEnteredText(self.request.get("readme%s" % i), self.request.get("roleReadmes_formats%s" % i)))
					rakontu.roleReadmes_formats[i] = self.request.get("roleReadmes_formats%s" % i)
				rakontu.put()
			self.redirect(rakontu.linkURL())
		else:
			self.redirect(START)
		
class ManageRakontuQuestionsListPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if isFirstVisit: self.redirect(member.firstVisitURL())
			if member.isManagerOrOwner():
				counts = []
				for type in QUESTION_REFERS_TO:
					questions = rakontu.getActiveQuestionsOfType(type)
					countsForThisType = []
					for question in questions:
						countsForThisType.append((question.text, question.getAnswerCount()))
					counts.append(countsForThisType)
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
				self.redirect(rakontu.linkURL())
		else:
			self.redirect(START)
				
class ManageRakontuQuestionsPage(webapp.RequestHandler):
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
				rakontuQuestionsOfType = rakontu.getActiveQuestionsOfType(type)
				inactiveQuestionsOfType = rakontu.getInactiveQuestionsOfType(type)
				systemQuestionsOfType = SystemQuestionsOfType(type)
				template_values = GetStandardTemplateDictionaryAndAddMore({
								   'title': TITLES["MANAGE_QUESTIONS_ABOUT"], 
							   	   'title_extra': DisplayTypePluralForQuestionRefersTo(type), 
								   'rakontu': rakontu, 
								   'skin': rakontu.getSkinDictionary(),
								   'current_member': member,
								   'questions': rakontuQuestionsOfType,
								   'inactive_questions': inactiveQuestionsOfType,
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
				self.redirect(rakontu.linkURL())
		else:
			self.redirect(START)
	
	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isManagerOrOwner():
				for aType in QUESTION_REFERS_TO:
					for argument in self.request.arguments():
						if argument == "changesTo|%s" % aType:
							type = aType
							break
				rakontuQuestionsOfType = rakontu.getActiveQuestionsOfType(type)
				systemQuestionsOfType = SystemQuestionsOfType()
				for question in rakontuQuestionsOfType:
					question.name = htmlEscape(self.request.get("name|%s" % question.key()))
					if not question.name:
						question.name = DEFAULT_QUESTION_NAME
					question.text = htmlEscape(self.request.get("text|%s" % question.key()))
					question.help = htmlEscape(self.request.get("help|%s" % question.key()))
					question.type = self.request.get("type|%s" % question.key())
					question.choices = []
					for i in range(10):
						question.choices.append(htmlEscape(self.request.get("choice%s|%s" % (i, question.key()))))
					oldValue = question.minIfValue
					try:
						question.minIfValue = int(self.request.get("minIfValue|%s" % question.key()))
					except:
						question.minIfValue = oldValue
					oldValue = question.maxIfValue
					try:
						question.maxIfValue = int(self.request.get("maxIfValue|%s" % question.key()))
					except:
						question.maxIfValue = oldValue
					question.responseIfBoolean = self.request.get("responseIfBoolean|%s" % question.key())
					question.multiple = self.request.get("multiple|%s" % question.key()) == "multiple|%s" % question.key()
				db.put(rakontuQuestionsOfType)
				for question in rakontuQuestionsOfType:
					if self.request.get("inactivate|%s" % question.key()):
						question.active = False
						question.put()
				questionNamesToAdd = htmlEscape(self.request.get("newQuestionNames")).split('\n')
				for name in questionNamesToAdd:
					if name.strip():
						foundQuestion = False
						for oldQuestion in rakontu.getInactiveQuestionsOfType(type):
							if oldQuestion.name == name.strip():
								foundQuestion = True
								oldQuestion.active = True
								oldQuestion.put()
								break
						if not foundQuestion:
							question = Question(
											key_name=KeyName("question"), 
											rakontu=rakontu, 
											name=name, 
											refersTo=type, 
											text=name)
							question.put()
				for sysQuestion in systemQuestionsOfType:
					if self.request.get("copy|%s" % sysQuestion.key()) == "copy|%s" % sysQuestion.key():
						rakontu.AddCopyOfQuestion(sysQuestion)
				if self.request.get("import"):
					rakontu.addQuestionsOfTypeFromCSV(type, str(self.request.get("import")))
				self.redirect(BuildURL("dir_manage", "url_questions_list", rakontu=rakontu))
			else:
				self.redirect(rakontu.linkURL())
		else:
			self.redirect(START)
		
class WriteQuestionsToCSVPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if isFirstVisit: self.redirect(member.firstVisitURL())
			if member.isManagerOrOwner():
				type = GetStringOfTypeFromURLQuery(self.request.query_string, "url_query_export_type")
				if type in QUESTION_REFERS_TO:
					export = rakontu.createOrRefreshExport("exportQuestions", itemList=None, member=None, questionType=type, fileFormat="csv")
					self.redirect(BuildURL(None, "url_export", export.urlQuery()))
				else:
					self.redirect(BuildResultURL("noQuestionsToExport", rakontu=rakontu))
			else:
				self.redirect(rakontu.linkURL())
		else:
			self.redirect(START)
			
class ManageCharactersPage(webapp.RequestHandler):
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
				self.redirect(rakontu.linkURL())
		else:
			self.redirect(START)
				
	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isManagerOrOwner():
				for character in rakontu.getActiveCharacters():
					if self.request.get("remove|%s" % character.key()):
						character.active = False
						character.put()
				namesToAdd = htmlEscape(self.request.get("newCharacterNames")).split('\n')
				for name in namesToAdd:
					if name.strip():
						foundCharacter = False
						for oldCharacter in rakontu.getInactiveCharacters():
							if oldCharacter.name == name.strip():
								foundCharacter = True
								oldCharacter.active = True
								oldCharacter.put()
								break
						if not foundCharacter:
							newCharacter = Character(key_name=KeyName("character"), name=name, rakontu=rakontu)
							newCharacter.put()
				self.redirect(BuildURL("dir_manage", "url_characters", rakontu=rakontu))
			else:
				self.redirect(rakontu.linkURL())
		else:
			self.redirect(START)
		
class ManageCharacterPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if isFirstVisit: self.redirect(member.firstVisitURL())
			if member.isManagerOrOwner():
				character = GetObjectOfTypeFromURLQuery(self.request.query_string, "url_query_character")
				template_values = GetStandardTemplateDictionaryAndAddMore({
								   'title': TITLES["MANAGE_CHARACTER"],
							   	   'title_extra': character.name, 
								   'rakontu': rakontu, 
								   'skin': rakontu.getSkinDictionary(),
								   'character': character,
								   'current_member': member,
								   'questions': rakontu.getActiveQuestionsOfType("character"),
								   'answers': character.getAnswers(),
								   'refer_type': "character",
								   'refer_type_display': DisplayTypeForQuestionReferType("character"),
								   })
				path = os.path.join(os.path.dirname(__file__), FindTemplate('manage/character.html'))
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect(rakontu.linkURL())
		else:
			self.redirect(START)
							 
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
						character.image = db.Blob(images.resize(str(self.request.get("img")), 100, 60))
					character.put()
					questions = rakontu.getActiveQuestionsOfType("character")
					for question in questions:
						foundAnswer = character.getAnswerForQuestion()
						if foundAnswers:
							answerToEdit = foundAnswer
						else:
							answerToEdit = Answer(
												key_name=KeyName("answer"), 
												rakontu=rakontu, 
												question=question, 
												referent=character, 
												referentType="character")
						if question.type == "text":
							answerToEdit.answerIfText = htmlEscape(self.request.get("%s" % question.key()))
						elif question.type == "value":
							oldValue = answerToEdit.answerIfValue
							try:
								answerToEdit.answerIfValue = int(self.request.get("%s" % question.key()))
							except:
								answerToEdit.answerIfValue = oldValue
						elif question.type == "boolean":
							answerToEdit.answerIfBoolean = self.request.get("%s" % question.key()) == "%s" % question.key()
						elif question.type == "nominal" or question.type == "ordinal":
							if question.multiple:
								answerToEdit.answerIfMultiple = []
								for choice in question.choices:
									if self.request.get("%s|%s" % (question.key(), choice)) == "yes":
										answerToEdit.answerIfMultiple.append(choice)
							else:
								answerToEdit.answerIfText = self.request.get("%s" % (question.key()))
						answerToEdit.creator = member
						answerToEdit.put()
					self.redirect(BuildURL("dir_manage", "url_characters", rakontu=rakontu))
			else:
				self.redirect(rakontu.linkURL())
		else:
			self.redirect(START)
		
class ManageRakontuTechnicalPage(webapp.RequestHandler):
	pass

class ExportRakontuDataPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isManagerOrOwner():
				template_values = GetStandardTemplateDictionaryAndAddMore({
								   	   'title': TITLES["EXPORT_DATA"], 
									   'rakontu': rakontu,
									   'skin': rakontu.getSkinDictionary(),
									   'current_member': member,
									   'xml_export': rakontu.getExportOfType("xml_export"),
									   'csv_export': rakontu.getExportOfType("csv_export_all"),
									   })
				path = os.path.join(os.path.dirname(__file__), FindTemplate('manage/export.html'))
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect(START)
		else:
			self.redirect(START)
				
	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isManagerOrOwner():
				if "csv_export" in self.request.arguments():
					rakontu.createOrRefreshExport(type="csv_export_all", fileFormat="csv")
				elif "xml_export" in self.request.arguments():
					rakontu.createOrRefreshExport(type="xml_export", fileFormat="xml")
				self.redirect(self.request.uri)
			else:
				self.redirect(rakontu.linkURL())
		else:
			self.redirect(START)

class ExportSearchPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isManagerOrOwner():
				if member.viewEntriesList:
					export = rakontu.createOrRefreshExport("csv_export_search", itemList=None, member=member, fileFormat="csv")
					self.redirect(BuildURL(None, "url_export", export.urlQuery()))
				else:
					self.redirect(BuildResultURL("noSearchResultForExport", rakontu=rakontu))
			else:
				self.redirect(rakontu.linkURL())
		else:
			self.redirect(START)
		
class InactivateRakontuPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access: 
			if member.isOwner():
				template_values = GetStandardTemplateDictionaryAndAddMore({
								   'title': TITLES["INACTIVATE"], 
								   'rakontu': rakontu, 
								   'skin': rakontu.getSkinDictionary(),
								   'current_member': member,
								   "blurbs": BLURBS,
								   })
				path = os.path.join(os.path.dirname(__file__), FindTemplate('manage/inactivate.html'))
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect(rakontu.linkURL())
		else:
			self.redirect(START)
			
	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isOwner():
				if "inactivate|%s" % member.key() in self.request.arguments():
					rakontu.active = False
					rakontu.put()
					self.redirect(START)
				else:
					self.redirect(BuildURL("dir_manage", "url_settings", rakontu=rakontu))
			else:
				self.redirect(rakontu.linkURL())
		else:
			self.redirect(START)
