# --------------------------------------------------------------------------------------------
# RAKONTU
# Description: Rakontu is open source story sharing software.
# Version: pre-0.1
# License: GPL 3.0
# Google Code Project: http://code.google.com/p/rakontu/
# --------------------------------------------------------------------------------------------

from utils import *

class ChangeMemberProfilePage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		community, member = GetCurrentCommunityAndMemberFromSession()
		if community and member:
			liaison = None
			if not member.isOnlineMember:
				try:
					liaison = community.getMemberForGoogleAccountId(member.liaisonAccountID)
				except:
					liaison = None
			draftAnswerArticles = member.getArticlesWithDraftAnswers()
			firstDraftAnswerForEachArticle = []
			for article in draftAnswerArticles:
				answers = member.getDraftAnswersForArticle(article)
				firstDraftAnswerForEachArticle.append(answers[0])
			template_values = {
							   'title': "Profile of", 
						   	   'title_extra': member.nickname, 
							   'community': community, 
							   'current_user': users.get_current_user(), 
							   'current_member': member,
							   'questions': community.getMemberQuestions(),
							   'answers': member.getAnswers(),
							   'draft_articles': member.getDraftArticles(),
							   'draft_annotations': member.getDraftAnnotations(),
							   'first_draft_answer_per_article': firstDraftAnswerForEachArticle,
							   'liaison': liaison,
							   'time_zone_names': pytz.all_timezones,
							   'date_formats': DateFormatStrings(),
							   'time_formats': TimeFormatStrings(),
							   'helping_role_names': HELPING_ROLE_TYPES,
							   'refer_type': "member",
							   'text_formats': TEXT_FORMATS,
							   'user_is_admin': users.is_current_user_admin(),
							   'logout_url': users.create_logout_url("/"),
							   }
			path = os.path.join(os.path.dirname(__file__), 'templates/visit/profile.html')
			self.response.out.write(template.render(path, template_values))
		else:
			self.redirect('/')
							 
	@RequireLogin 
	def post(self):
		community, member = GetCurrentCommunityAndMemberFromSession()
		if community and member:
			member.nickname = cgi.escape(self.request.get("nickname"))
			member.nicknameIsRealName = self.request.get('nickname_is_real_name') =="yes"
			member.acceptsMessages = self.request.get("acceptsMessages") == "yes"
			text = self.request.get("profileText")
			format = self.request.get("profileText_format").strip()
			member.profileText = text
			member.profileText_formatted = db.Text(InterpretEnteredText(text, format))
			member.profileText_format = format
			if self.request.get("removeProfileImage") == "yes":
				member.profileImage = None
			elif self.request.get("img"):
				member.profileImage = db.Blob(images.resize(str(self.request.get("img")), 100, 60))
			member.timeZoneName = self.request.get("timeZoneName")
			member.dateFormat = self.request.get("dateFormat")
			member.timeFormat = self.request.get("timeFormat")
			for i in range(3):
				member.helpingRoles[i] = self.request.get("helpingRole%s" % i) == "helpingRole%s" % i
			text = self.request.get("guideIntro")
			format = self.request.get("guideIntro_format").strip()
			member.guideIntro = text
			member.guideIntro_formatted = db.Text(InterpretEnteredText(text, format))
			member.guideIntro_format = format
			member.put()
			for article in member.getDraftArticles():
				if self.request.get("remove|%s" % article.key()) == "yes":
					db.delete(article)
			for annotation in member.getDraftAnnotations():
				if self.request.get("remove|%s" % annotation.key()) == "yes":
					db.delete(annotation)
			for article in member.getArticlesWithDraftAnswers():
				if self.request.get("removeAnswers|%s" % article.key()) == "yes":
					answers = member.getDraftAnswersForArticle(article)
					for answer in answers:
						db.delete(answer)
			questions = Question.all().filter("community = ", community).filter("refersTo = ", "member").fetch(FETCH_NUMBER)
			for question in questions:
				foundAnswers = Answer.all().filter("question = ", question.key()).filter("referent =", member.key()).fetch(FETCH_NUMBER)
				if foundAnswers:
					answerToEdit = foundAnswers[0]
				else:
					answerToEdit = Answer(question=question, community=community, referent=member, referentType="member")
				if question.type == "text":
					answerToEdit.answerIfText = cgi.escape(self.request.get("%s" % question.key()))
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
		self.redirect('/visit/look')
		
# --------------------------------------------------------------------------------------------
# Manage community
# --------------------------------------------------------------------------------------------
								
class ManageCommunityMembersPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		community, member = GetCurrentCommunityAndMemberFromSession()
		if community and member:
			communityMembers = Member.all().filter("community = ", community).fetch(FETCH_NUMBER)
			template_values = {
							   'title': "Manage members of", 
						   	   'title_extra': community.name, 
							   'community': community, 
							   'current_user': users.get_current_user(), 
							   'current_member': member,
							   'community_members': community.getActiveMembers(),
							   'pending_members': community.getPendingMembers(),
							   'inactive_members': community.getInactiveMembers(),
							   'user_is_admin': users.is_current_user_admin(),
							   'logout_url': users.create_logout_url("/"),
							   }
			path = os.path.join(os.path.dirname(__file__), 'templates/manage/members.html')
			self.response.out.write(template.render(path, template_values))
		else:
			self.redirect('/')
				
	@RequireLogin 
	def post(self):
		community, member = GetCurrentCommunityAndMemberFromSession()
		if community and member:
			communityMembers = community.getActiveMembers()
			for aMember in communityMembers:
				for name, value in self.request.params.items():
					if value.find(aMember.googleAccountID) >= 0:
						(newType, id) = value.split("|") 
						okayToSet = False
						if newType != aMember.governanceType:
							if newType == "member":
								if not aMember.isOwner() or not community.memberIsOnlyOwner(aMember):
									okayToSet = True
							elif newType == "manager":
								if not aMember.isOwner() or not community.memberIsOnlyOwner(aMember):
									okayToSet = True
							elif newType == "owner":
								okayToSet = True
						if okayToSet:
							aMember.governanceType = newType
							aMember.put()
				if aMember.isRegularMember():
					for i in range(3):
						aMember.helpingRolesAvailable[i] = self.request.get("%sAvailable|%s" % (HELPING_ROLE_TYPES[i], aMember.key())) == "yes"
				else:
					for i in range(3):
						aMember.helpingRolesAvailable[i] = True
				aMember.put()
			for aMember in communityMembers:
				if self.request.get("remove|%s" % aMember.key()) == "yes":
					aMember.active = False
					aMember.put()
			for pendingMember in community.getPendingMembers():
				pendingMember.email = cgi.escape(self.request.get("email|%s" % pendingMember.key()))
				pendingMember.put()
				if self.request.get("removePendingMember|%s" % pendingMember.key()):
					db.delete(pendingMember)
			memberEmailsToAdd = cgi.escape(self.request.get("newMemberEmails")).split('\n')
			for email in memberEmailsToAdd:
				if email.strip():
					if not community.hasMemberWithGoogleEmail(email.strip()):
						newPendingMember = PendingMember(community=community, email=email.strip())
						newPendingMember.put()
		self.redirect('/manage/members')
				
class ManageCommunitySettingsPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		community, member = GetCurrentCommunityAndMemberFromSession()
		if community and member:
			nudgePointIncludes = []
			nudgePointIncludes.append('<tr>')
			i = 0
			for eventType in EVENT_TYPES:
				if eventType != EVENT_TYPES[0]: # leave time out for nudge accumulations
					nudgePointIncludes.append('<td>%s</td>' % eventType)
				i += 1
			i = 0
			nudgePointIncludes.append('</tr><tr>')
			for eventType in EVENT_TYPES:
				if eventType != EVENT_TYPES[0]: # leave time out for nudge accumulations
					nudgePointIncludes.append('<td><input type="text" name="member|%s" size="3" value="%s"/></td>' \
						% (eventType, community.memberNudgePointsPerEvent[i]))
				i += 1
			nudgePointIncludes.append('</tr>')
			activityPointIncludes = []
			activityPointIncludes.append('<tr>')
			i = 0
			for eventType in EVENT_TYPES:
				activityPointIncludes.append('<td>%s</td>' % eventType)
				i += 1
			i = 0
			activityPointIncludes.append('</tr><tr>')
			for eventType in EVENT_TYPES:
				activityPointIncludes.append('<td><input type="text" name="article|%s" size="3" value="%s"/></td>' \
					% (eventType, community.articleActivityPointsPerEvent[i]))
				i += 1
			activityPointIncludes.append('</tr>')
			characterIncludes = []
			i = 0
			for entryType in ENTRY_TYPES:
				characterIncludes.append('<input type="checkbox" name="%s" value="%s" %s id="%s"/><label for="%s">%s</label>' \
						% (entryType, entryType, checkedBlank(community.allowCharacter[i]), entryType, entryType, entryType))
				i += 1
			template_values = {
							   'title': "Manage settings for", 
						   	   'title_extra': community.name, 
							   'community': community, 
							   'current_user': users.get_current_user(), 
							   'current_member': member,
							   'time_zone_names': pytz.all_timezones,
							   'date_formats': DateFormatStrings(),
							   'time_formats': TimeFormatStrings(),
							   'current_date': datetime.now(tz=pytz.utc),
							   'character_includes': characterIncludes,
							   'nudge_point_includes': nudgePointIncludes,
							   'activity_point_includes': activityPointIncludes,
							   'text_formats': TEXT_FORMATS,
							   'user_is_admin': users.is_current_user_admin(),
							   'logout_url': users.create_logout_url("/"),
							   }
			path = os.path.join(os.path.dirname(__file__), 'templates/manage/settings.html')
			self.response.out.write(template.render(path, template_values))
		else:
			self.redirect("/")
	
	@RequireLogin 
	def post(self):
		community, member = GetCurrentCommunityAndMemberFromSession()
		if community and member:
			community.name = cgi.escape(self.request.get("name"))
			community.tagline = cgi.escape(self.request.get("tagline"))
			text = self.request.get("description")
			format = self.request.get("description_format").strip()
			community.description = text
			community.description_formatted = db.Text(InterpretEnteredText(text, format))
			community.description_format = format
			text = self.request.get("welcomeMessage")
			format = self.request.get("welcomeMessage_format").strip()
			community.welcomeMessage = text
			community.welcomeMessage_formatted = db.Text(InterpretEnteredText(text, format))
			community.welcomeMessage_format = format
			text = self.request.get("etiquetteStatement")
			format = self.request.get("etiquetteStatement_format").strip()
			community.etiquetteStatement = text
			community.etiquetteStatement_formatted = db.Text(InterpretEnteredText(text, format))
			community.etiquetteStatement_format = format
			community.contactEmail = self.request.get("contactEmail")
			community.defaultTimeZoneName = self.request.get("defaultTimeZoneName")
			community.defaultDateFormat = self.request.get("defaultDateFormat")
			community.defaultTimeFormat = self.request.get("defaultTimeFormat")
			if self.request.get("img"):
				community.image = db.Blob(images.resize(str(self.request.get("img")), 100, 60))
			i = 0
			for entryType in ENTRY_TYPES:
				community.allowCharacter[i] = self.request.get(entryType) == entryType
				i += 1
			oldValue = community.maxNudgePointsPerArticle
			try:
				community.maxNudgePointsPerArticle = int(self.request.get("maxNudgePointsPerArticle"))
			except:
				community.maxNudgePointsPerArticle = oldValue
			for i in range(5):
				community.nudgeCategories[i] = cgi.escape(self.request.get("nudgeCategory%s" % i))
			oldValue = community.maxNumAttachments
			try:
				community.maxNumAttachments = int(self.request.get("maxNumAttachments"))
			except:
				community.maxNumAttachments = oldValue
			i = 0
			for eventType in EVENT_TYPES:
				if eventType != EVENT_TYPES[0]: # leave time out for nudge accumulations
					oldValue = community.memberNudgePointsPerEvent[i]
					try:
						community.memberNudgePointsPerEvent[i] = int(self.request.get("member|%s" % eventType))
					except:
						community.memberNudgePointsPerEvent[i] = oldValue
				i += 1
			i = 0
			for eventType in EVENT_TYPES:
				oldValue = community.articleActivityPointsPerEvent[i]
				try:
					community.articleActivityPointsPerEvent[i] = int(self.request.get("article|%s" % eventType))
				except:
					community.articleActivityPointsPerEvent[i] = oldValue
				i += 1
			for i in range(3):
				community.roleReadmes[i] = db.Text(self.request.get("readme%s" % i))
				community.roleReadmes_formatted[i] = db.Text(InterpretEnteredText(self.request.get("readme%s" % i), self.request.get("roleReadmes_formats%s" % i)))
				community.roleReadmes_formats[i] = self.request.get("roleReadmes_formats%s" % i)
				community.roleAgreements[i] = self.request.get("agreement%s" % i) == ("agreement%s" % i)
			community.put()
		self.redirect('/visit/look')
				
class ManageCommunityQuestionsPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		community, member = GetCurrentCommunityAndMemberFromSession()
		if community and member:
			i = 0
			for aType in QUESTION_REFERS_TO:
				if self.request.uri.find(aType) >= 0:
					type = aType
					typePlural = QUESTION_REFERS_TO_PLURAL[i]
					break
				i += 1
			communityQuestionsOfType = community.getQuestionsOfType(type)
			systemQuestionsOfType = Question.all().filter("community = ", None).filter("refersTo = ", type).fetch(FETCH_NUMBER)
			template_values = {
							   'title': "Manage %s" % type, 
						   	   'title_extra': "questions", 
							   'community': community, 
							   'current_user': users.get_current_user(), 
							   'current_member': member,
							   'questions': communityQuestionsOfType,
							   'question_types': QUESTION_TYPES,
							   'system_questions': systemQuestionsOfType,
							   'refer_type': type,
							   'refer_type_plural': typePlural,
							   'question_refer_types': QUESTION_REFERS_TO,
							   'user_is_admin': users.is_current_user_admin(),
							   'logout_url': users.create_logout_url("/"),
							   }
			path = os.path.join(os.path.dirname(__file__), 'templates/manage/questions.html')
			self.response.out.write(template.render(path, template_values))
		else:
			self.redirect("/")
	
	@RequireLogin 
	def post(self):
		community, member = GetCurrentCommunityAndMemberFromSession()
		if community and member:
			for aType in QUESTION_REFERS_TO:
				for argument in self.request.arguments():
					if argument == "changesTo|%s" % aType:
						type = aType
						break
			communityQuestionsOfType = community.getQuestionsOfType(type)
			systemQuestionsOfType = Question.all().filter("community = ", None).filter("refersTo = ", type).fetch(FETCH_NUMBER)
			for question in communityQuestionsOfType:
				question.name = cgi.escape(self.request.get("name|%s" % question.key()))
				question.text = cgi.escape(self.request.get("text|%s" % question.key()))
				question.help = cgi.escape(self.request.get("help|%s" % question.key()))
				question.type = self.request.get("type|%s" % question.key())
				question.choices = []
				for i in range(10):
					question.choices.append(cgi.escape(self.request.get("choice%s|%s" % (i, question.key()))))
				oldValue = question.lengthIfText
				try:
					question.lengthIfText = int(self.request.get("lengthIfText|%s" % question.key()))
				except:
					question.lengthIfText = oldValue
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
				question.put()
			questionsToRemove = []
			for question in communityQuestionsOfType:
				if self.request.get("remove|%s" % question.key()):
					questionsToRemove.append(question)
			if questionsToRemove:
				for question in questionsToRemove:
					answersWithThisQuestion = Answer().all().filter("question = ", question.key()).fetch(FETCH_NUMBER)
					for answer in answersWithThisQuestion:
						db.delete(answer)
					db.delete(question)
			questionNamesToAdd = cgi.escape(self.request.get("newQuestionNames")).split('\n')
			for name in questionNamesToAdd:
				if name.strip():
					question = Question(name=name, refersTo=type, community=community)
					question.put()
			for sysQuestion in systemQuestionsOfType:
				if self.request.get("copy|%s" % sysQuestion.key()) == "copy|%s" % sysQuestion.key():
					community.AddCopyOfQuestion(sysQuestion)
		self.redirect(self.request.uri)
		
class ManageCommunityCharactersPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		community, member = GetCurrentCommunityAndMemberFromSession()
		if community and member:
			characters = Character.all().filter("community = ", community).fetch(FETCH_NUMBER)
			template_values = {
							   'title': "Manage characters for", 
						   	   'title_extra': community.name, 
							   'community': community, 
							   'current_user': users.get_current_user(), 
							   'current_member': member,
							   'characters': characters,
							   'text_formats': TEXT_FORMATS,
							   'user_is_admin': users.is_current_user_admin(),
							   'logout_url': users.create_logout_url("/"),
							   }
			path = os.path.join(os.path.dirname(__file__), 'templates/manage/characters.html')
			self.response.out.write(template.render(path, template_values))
		else:
			self.redirect('/')
				
	@RequireLogin 
	def post(self):
		community, member = GetCurrentCommunityAndMemberFromSession()
		if community and member:
			characters = Character.all().filter("community = ", community).fetch(FETCH_NUMBER)
			charactersToRemove = []
			for character in characters:
				character.name = cgi.escape(self.request.get("name|%s" % character.key()))
				text = self.request.get("description|%s" % character.key())
				format = self.request.get("description_format|%s" % character.key()).strip()
				character.description = text
				character.description_formatted = db.Text(InterpretEnteredText(text, format))
				character.description_format = format
				text = self.request.get("etiquetteStatement|%s" % character.key())
				format = self.request.get("etiquetteStatement_format|%s" % character.key()).strip()
				character.etiquetteStatement = text
				character.etiquetteStatement_formatted = db.Text(InterpretEnteredText(text, format))
				character.etiquetteStatement_format = format
				imageQueryKey = "image|%s" % character.key()
				if self.request.get(imageQueryKey):
					character.image = db.Blob(images.resize(str(self.request.get(imageQueryKey)), 100, 60))
				character.put()
				if self.request.get("remove|%s" % character.key()):
					charactersToRemove.append(character)
			if charactersToRemove:
				for character in charactersToRemove:
					db.delete(character)
			namesToAdd = cgi.escape(self.request.get("newCharacterNames")).split('\n')
			for name in namesToAdd:
				if name.strip():
					newCharacter = Character(name=name, community=community)
					newCharacter.put()
			community.put()
		self.redirect('/visit/community')
		
class ManageCommunityTechnicalPage(webapp.RequestHandler):
	pass
	
# --------------------------------------------------------------------------------------------
# Site admin
# --------------------------------------------------------------------------------------------
		
class ShowAllCommunities(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		community, member = GetCurrentCommunityAndMemberFromSession()
		if community and member:
			if users.is_current_user_admin():
				template_values = {
							   	   'title': "All communities", 
						   	   	   'title_extra': None, 
								   'communities': Community.all().fetch(FETCH_NUMBER), 
								   'members': Member.all().fetch(FETCH_NUMBER),
								   'community': community, 
								   'current_user': users.get_current_user(), 
								   'current_member': member,
								   'user_is_admin': users.is_current_user_admin(),
								   'logout_url': users.create_logout_url("/"),
								   }
				path = os.path.join(os.path.dirname(__file__), 'templates/admin/showAllCommunities.html')
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect('/')

class ShowAllMembers(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		community, member = GetCurrentCommunityAndMemberFromSession()
		if community and member:
			if users.is_current_user_admin():
				template_values = {
							   	   'title': "All members", 
						   	   	   'title_extra': None, 
								   'members': Member.all().fetch(FETCH_NUMBER),
								   'community': community, 
								   'current_user': users.get_current_user(), 
								   'current_member': member,
								   'user_is_admin': users.is_current_user_admin(),
								   'logout_url': users.create_logout_url("/"),
								   }
				path = os.path.join(os.path.dirname(__file__), 'templates/admin/showAllMembers.html')
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect('/')
				
class GenerateSystemQuestionsPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		community, member = GetCurrentCommunityAndMemberFromSession()
		if community and member:
			if users.is_current_user_admin():
				GenerateSystemQuestions()
				self.redirect(self.request.headers["Referer"])
			else:
				self.redirect('/')
				
class GenerateHelpsPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		community, member = GetCurrentCommunityAndMemberFromSession()
		if community and member:
			if users.is_current_user_admin():
				GenerateHelps()
				self.redirect(self.request.headers["Referer"])
			else:
				self.redirect('/')
				
class FlagOrUnflagItemPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		community, member = GetCurrentCommunityAndMemberFromSession()
		if community and member:
			item = None
			if self.request.query_string:
				try:
					item = db.get(self.request.query_string)
				except:
					item = None
			if item:
				item.flaggedForRemoval = not item.flaggedForRemoval
				item.put()
				self.redirect(self.request.headers["Referer"])
			else:
				self.redirect("/visit/look")
		else:
			self.redirect("/")
	
class CurateFlagsPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		community, member = GetCurrentCommunityAndMemberFromSession()
		if community and member:
			if member.isCurator():
				(articles, annotations, answers, links) = community.getAllFlaggedItems()
				template_values = {
							   	   'title': "Review flags", 
						   	   	   'title_extra': None, 
								   'community': community, 
								   'articles': articles,
								   'annotations': annotations,
								   'answers': answers,
								   'links': links,
								   'current_user': users.get_current_user(), 
								   'current_member': member,
								   'user_is_admin': users.is_current_user_admin(),
								   'logout_url': users.create_logout_url("/"),
								   }
				path = os.path.join(os.path.dirname(__file__), 'templates/curate/flags.html')
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect('/visit/look')
		else:
			self.redirect("/")
				
	@RequireLogin 
	def post(self):
		community, member = GetCurrentCommunityAndMemberFromSession()
		if community and member:
			items = community.getAllFlaggedItemsAsOneList()
			for item in items:
				 if self.request.get("unflag|%s" % item.key()) == "yes":
				 	item.flaggedForRemoval = False
				 	item.put()
			if member.isManagerOrOwner():
				for item in items:
					if self.request.get("removeComment|%s" % item.key()) == "yes":
						if item.__class__.__name__ == "Annotation": # nudge
							item.shortString = ""
						elif item.__class__.__name__ == "Link":
							item.comment = ""
						item.put()
					elif self.request.get("remove|%s" % item.key()) == "yes":
						if item.__class__.__name__ == "Article":
							item.removeAllDependents()
						db.delete(item)
				self.redirect('/result?changessaved')
			elif member.isCurator():
				itemsToSendMessageAbout = []
				for item in items:
					if self.request.get("notify|%s" % item.key()) == "yes":
						itemsToSendMessageAbout.append(item)
				if itemsToSendMessageAbout:
					subject = "Reminder about flagged items from %s" % member.nickname
					URL = self.request.headers["Host"]
					messageLines = []
					messageLines.append("The curator %s wanted you to know that these items require your attention.\n" % member.nickname)
					itemsToSendMessageAbout.reverse()
					for item in itemsToSendMessageAbout:
						if item.__class__.__name__ == "Article":
							linkKey = item.key()
							displayString = 'A %s called "%s"' % (item.type, item.title)
						elif item.__class__.__name__ == "Annotation":
							linkKey = item.article.key()
							if item.shortString:
								shortString = " (%s)" % item.shortString
							else:
								shortString = ""
							displayString = 'A %s%s for the %s called "%s"' % (item.type, shortString, item.article.type, item.article.title)
 						elif item.__class__.__name__ == "Answer":
							linkKey = item.referent.key()
							displayString = 'An answer (%s) for the %s called "%s"' % (item.displayString(), item.referent.type, item.referent.title)
						elif item.__class__.__name__ == "Link":
							linkKey = item.articleFrom.key()
							if item.comment:
								commentString = " (%s)" % item.comment
							else:
								commentString = ""
							displayString = 'A link%s from the %s called "%s" to the %s called "%s"' % \
								(commentString, item.articleFrom.type, item.articleFrom.title, item.articleTo.type, item.articleTo.title)
						messageLines.append('* %s\n\n    http://%s/visit/curate?%s\n' % (displayString, URL, linkKey))
					messageLines.append("Thank you for your attention.\n")
					messageLines.append("Sincerely,")
					messageLines.append("    Your Rakontu site")
					message = "\n".join(messageLines)
					ownersAndManagers = community.getManagersAndOwners()
					for ownerOrManager in ownersAndManagers:
						messageLines.insert(0, "Dear manager %s:\n" % ownerOrManager.nickname)
						messageBody = "\n".join(messageLines)
						message = mail.EmailMessage()
						message.sender = community.contactEmail
						message.subject = subject
						message.to = ownerOrManager.googleAccountEmail
						message.body = messageBody
						DebugPrint(messageBody)
						# CFK FIX
						# not putting this last line in until I can start testing it, either locally or on the real server
						#message.send()
					self.redirect('/result?messagesent')
			else:
				self.redirect("/visit/look")
		else:
			self.redirect("/")
			
class ResultFeedbackPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		community, member = GetCurrentCommunityAndMemberFromSession()
		if community and member:
			template_values = {
						   	   'title': "Action successful", 
					   	   	   'title_extra': None, 
							   'community': community, 
							   'message': self.request.query_string,
							   "linkback": self.request.headers["Referer"],
							   'current_user': users.get_current_user(), 
							   'current_member': member,
							   'user_is_admin': users.is_current_user_admin(),
							   'logout_url': users.create_logout_url("/"),
							   }
			path = os.path.join(os.path.dirname(__file__), 'templates/result.html')
			self.response.out.write(template.render(path, template_values))
		else:
			self.redirect("/")
				

