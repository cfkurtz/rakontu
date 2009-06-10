# --------------------------------------------------------------------------------------------
# RAKONTU
# Description: Rakontu is open source story sharing software.
# Version: pre-0.1
# License: GPL 3.0
# Google Code Project: http://code.google.com/p/rakontu/
# --------------------------------------------------------------------------------------------

from utils import *

							 
class CreateCommunityPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		user = users.get_current_user()
		template_values = {
						   'title': "Create community",
						   'title_extra': None,
						   'text_formats': TEXT_FORMATS,
						   'user': users.get_current_user(),
						   'logout_url': users.create_logout_url("/"),
						   }
		path = os.path.join(os.path.dirname(__file__), 'templates/createCommunity.html')
		self.response.out.write(template.render(path, template_values))
			
	@RequireLogin 
	def post(self):
		user = users.get_current_user()
		community = Community(name=cgi.escape(self.request.get('name')))
		community.put()
		member = Member(
			googleAccountID=user.user_id(),
			googleAccountEmail=user.email(),
			active=True,
			community=community,
			governanceType="owner",
			nickname = cgi.escape(self.request.get('nickname')))
		member.initialize()
		member.put()
		self.redirect('/')
		
class EnterArticlePage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		community, member = GetCurrentCommunityAndMemberFromSession()
		if community and member:
			if self.request.uri.find("retell") >= 0:
				type = "story"
				linkType = "retell"
				articleFromKey = self.request.query_string
				articleFrom = db.get(articleFromKey)
				article = None
				entryTypeIndexForCharacters = STORY_ENTRY_TYPE_INDEX
				articleName = None
			elif self.request.uri.find("remind") >= 0:
				type = "story"
				linkType = "remind"
				articleFromKey = self.request.query_string
				articleFrom = db.get(articleFromKey)
				article = None
				entryTypeIndexForCharacters = STORY_ENTRY_TYPE_INDEX
				articleName = None
			elif self.request.uri.find("respond") >= 0:
				type = "story"
				linkType = "respond"
				articleFromKey = self.request.query_string
				articleFrom = db.get(articleFromKey)
				article = None
				entryTypeIndexForCharacters = STORY_ENTRY_TYPE_INDEX
				articleName = None
			else:
				linkType = ""
				articleFrom = None
				i = 0
				for aType in ARTICLE_TYPES:
					if self.request.uri.find(aType) >= 0:
						type = aType
						entryTypeIndexForCharacters = i
						break
					i += 1
				if not self.request.uri.find("?") >= 0:
					article = None
					articleName = None
				else:
					articleKey = self.request.query_string
					article = db.get(articleKey)
					articleName = article.title
			if article:
				answers = article.getAnswers()
				attachments = article.getAttachments()
			else:
				answers = None
				attachments = None
			if type == "collage":
				if article:
					includedLinksOutgoing = article.getOutgoingLinksOfType("included")
				else:
					includedLinksOutgoing = []
				articles = community.getNonDraftArticlesOfType("story")
				articlesThatCanBeIncluded = []
				for anArticle in articles:
					found = False
					for link in includedLinksOutgoing:
						if article and link.articleTo.key() == anArticle.key():
							found = True
							break
					if not found:
						articlesThatCanBeIncluded.append(anArticle)
			else:
				articlesThatCanBeIncluded = None
				includedLinksOutgoing = None
			template_values = {
							   'title': type.capitalize(), 
						   	   'title_extra': articleName, 
							   'user': users.get_current_user(),
							   'current_member': member,
							   'community': community, 
							   'article_type': type,
							   'article': article,
							   'questions': community.getQuestionsOfType(type),
							   'answers': answers,
							   'attachments': attachments,
							   'community_members': community.getActiveMembers(),
							   'offline_members': community.getOfflineMembers(),
							   'character_allowed': community.allowCharacter[entryTypeIndexForCharacters],
							   'link_type': linkType,
							   'article_from': articleFrom,
							   'articles_that_can_be_linked_to_by_collage': articlesThatCanBeIncluded,
							   'included_links_outgoing': includedLinksOutgoing,
							   'text_formats': TEXT_FORMATS,
							   'refer_type': type,
							   'user_is_admin': users.is_current_user_admin(),
							   'logout_url': users.create_logout_url("/"),
							   }
			path = os.path.join(os.path.dirname(__file__), 'templates/visit/article.html')
			self.response.out.write(template.render(path, template_values))
		else:
			self.redirect("/")
			
	@RequireLogin 
	def post(self):
		community, member = GetCurrentCommunityAndMemberFromSession()
		if community and member:
			for aType in ARTICLE_TYPES:
				for argument in self.request.arguments():
					if argument.find(aType) >= 0:
						type = aType
						break
			if not self.request.uri.find("?") >= 0:
				article = None
			else:
				articleKey = self.request.query_string
				article = db.get(articleKey)
			newArticle = False
			if not article:
				article=Article(community=community, type=type, creator=member, title="Untitled")
				newArticle = True
			preview = False
			if "save|%s" % type in self.request.arguments():
				article.draft = True
				article.edited = datetime.now(tz=pytz.utc)
			elif "preview|%s" % type in self.request.arguments():
				article.draft = True
				preview = True
			elif "publish|%s" % type in self.request.arguments():
				article.draft = False
				article.published = datetime.now(tz=pytz.utc)
			if self.request.get("title"):
				article.title = cgi.escape(self.request.get("title"))
			text = self.request.get("text")
			format = self.request.get("text_format").strip()
			article.text = text
			article.text_formatted = db.Text(InterpretEnteredText(text, format))
			article.text_format = format
			article.collectedOffline = self.request.get("collectedOffline") == "yes"
			if article.collectedOffline and member.isLiaison():
				for aMember in community.getActiveMembers():
					if self.request.get("offlineSource") == aMember.key():
						article.creator = aMember
						article.liaison = member
						break
			if self.request.get("attribution") != "member":
				article.character = Character.get(characterKey)
			else:
				article.character = None
			article.put()
			linkType = None
			if self.request.get("article_from"):
				articleFrom = db.get(self.request.get("article_from"))
				if articleFrom:
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
					link = Link(articleFrom=articleFrom, articleTo=article, type=linkType, \
								creator=member, community=community, \
								comment=cgi.escape(self.request.get("link_comment")))
					link.put()
					link.publish()
			if article.isCollage():
				linksToRemove = []
				for link in article.getOutgoingLinksOfType("included"):
					link.comment = self.request.get("linkComment|%s" % link.key())
					link.put()
					if self.request.get("removeLink|%s" % link.key()) == "yes":
						linksToRemove.append(link)
				for link in linksToRemove:
					db.delete(link)
				for anArticle in community.getNonDraftArticlesOfType("story"):
					if self.request.get("addLink|%s" % anArticle.key()) == "yes":
						link = Link(articleFrom=article, articleTo=anArticle, type="included", 
									creator=member, community=community,
									comment=cgi.escape(self.request.get("linkComment|%s" % anArticle.key())))
						link.put()
						link.publish()
			questions = Question.all().filter("community = ", community).filter("refersTo = ", type).fetch(FETCH_NUMBER)
			for question in questions:
				foundAnswers = Answer.all().filter("question = ", question.key()).filter("referent =", article.key()).filter("creator = ", member.key()).fetch(FETCH_NUMBER)
				if foundAnswers:
					answerToEdit = foundAnswers[0]
				else:
					answerToEdit = Answer(question=question, community=community, creator=member, referent=article, referentType="article")
					keepAnswer = False
					queryText = "%s" % question.key()
					if question.type == "text":
						keepAnswer = len(self.request.get(queryText)) > 0
						if keepAnswer:
							answerToEdit.answerIfText = cgi.escape(self.request.get(queryText))
					elif question.type == "value":
						keepAnswer = len(self.request.get(queryText)) > 0
						if keepAnswer:
							oldValue = answerToEdit.answerIfValue
							try:
								answerToEdit.answerIfValue = int(self.request.get(queryText))
							except:
								answerToEdit.answerIfValue = oldValue
					elif question.type == "boolean":
						keepAnswer = queryText in self.request.params.keys()
						if keepAnswer:
							answerToEdit.answerIfBoolean = self.request.get(queryText) == queryText
					elif question.type == "nominal" or question.type == "ordinal":
						if question.multiple:
							answerToEdit.answerIfMultiple = []
							for choice in question.choices:
								if self.request.get("%s|%s" % (question.key(), choice)) == "yes":
									answerToEdit.answerIfMultiple.append(choice)
									keepAnswer = True
						else:
							keepAnswer = len(self.request.get(queryText)) > 0
							if keepAnswer:
								answerToEdit.answerIfText = self.request.get(queryText)
					answerToEdit.creator = member
					answerToEdit.draft = article.draft
					if keepAnswer:
						answerToEdit.put()
						if not answerToEdit.draft:
							answerToEdit.publish()
			foundAttachments = Attachment.all().filter("article = ", article.key()).fetch(FETCH_NUMBER)
			attachmentsToRemove = []
			for attachment in foundAttachments:
				for name, value in self.request.params.items():
					if value == "removeAttachment|%s" % attachment.key():
						attachmentsToRemove.append(attachment)
			if attachmentsToRemove:
				for attachment in attachmentsToRemove:
					db.delete(attachment)
			foundAttachments = Attachment.all().filter("article = ", article.key()).fetch(FETCH_NUMBER)
			for i in range(3):
				for name, value in self.request.params.items():
					if name == "attachment%s" % i:
						if value != None and value != "":
							filename = value.filename
							if len(foundAttachments) > i:
								attachmentToEdit = foundAttachments[i]
							else:
								attachmentToEdit = Attachment(article=article)
							j = 0
							mimeType = None
							for type in ACCEPTED_ATTACHMENT_FILE_TYPES:
								if filename.find(".%s" % type) >= 0:
									mimeType = ACCEPTED_ATTACHMENT_MIME_TYPES[j]
								j += 1
							if mimeType:
								attachmentToEdit.mimeType = mimeType
								attachmentToEdit.fileName = filename
								attachmentToEdit.name = cgi.escape(self.request.get("attachmentName%s" % i))
								attachmentToEdit.data = db.Blob(str(self.request.get("attachment%s" % i)))
								attachmentToEdit.put()
			if not article.draft:
				article.publish()
			if preview:
				self.redirect("/visit/preview?%s" % article.key())
			elif article.draft:
				self.redirect("/visit/profile?%s" % member.key())
			else:
				member.viewTimeEnd = article.published + timedelta(seconds=1)
				member.put()
				self.redirect("/visit/look")#read?%s" % article.key())
		else:
			self.redirect("/visit/look")
			
class AnswerQuestionsAboutArticlePage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		community, member = GetCurrentCommunityAndMemberFromSession()
		if community and member:
			article = None
			if self.request.query_string:
				article = Article.get(self.request.query_string)
			if article:
				template_values = {
							   	   'title': "Answers for", 
						   	   	   'title_extra': article.title, 
								   'user': users.get_current_user(),
								   'current_member': member,
								   'community': community, 
								   'article': article,
								   'article_type': article.type,
								   'refer_type': article.type,
								   'questions': community.getQuestionsOfType(article.type),
								   'answers': article.getAnswersForMember(member),
								   'community_members': community.getActiveMembers(),
								   'offline_members': community.getOfflineMembers(),
								   'character_allowed': community.allowCharacter[ANSWERS_ENTRY_TYPE_INDEX],
								   'user_is_admin': users.is_current_user_admin(),
								   'logout_url': users.create_logout_url("/"),
								   }
				path = os.path.join(os.path.dirname(__file__), 'templates/visit/answers.html')
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect("/visit/look")
		else:
			self.redirect("/")
				
	@RequireLogin 
	def post(self):
		community, member = GetCurrentCommunityAndMemberFromSession()
		if community and member:
			articleKey = self.request.query_string
			article = db.get(articleKey)
			if article:
				character = None
				if self.request.get("attribution") != "member":
					characterKey = self.request.get("attribution")
					character = Character.get(characterKey)
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
				questions = Question.all().filter("community = ", community).filter("refersTo = ", article.type).fetch(FETCH_NUMBER)
				for question in questions:
					foundAnswers = Answer.all().filter("question = ", question.key()).filter("referent =", article.key()).filter("creator = ", member.key()).fetch(FETCH_NUMBER)
					if foundAnswers:
						answerToEdit = foundAnswers[0]
					else:
						answerToEdit = Answer(question=question, community=community, referent=article, referentType="article")
						newAnswers = True
					answerToEdit.character = character
					keepAnswer = False
					queryText = "%s" % question.key()
					if question.type == "text":
						keepAnswer = len(self.request.get(queryText)) > 0
						if keepAnswer:
							answerToEdit.answerIfText = cgi.escape(self.request.get(queryText))
					elif question.type == "value":
						keepAnswer = len(self.request.get(queryText)) > 0
						if keepAnswer:
							oldValue = answerToEdit.answerIfValue
							try:
								answerToEdit.answerIfValue = int(self.request.get(queryText))
							except:
								answerToEdit.answerIfValue = oldValue
					elif question.type == "boolean":
						keepAnswer = queryText in self.request.params.keys()
						if keepAnswer:
							answerToEdit.answerIfBoolean = self.request.get(queryText) == queryText
					elif question.type == "nominal" or question.type == "ordinal":
						if question.multiple:
							answerToEdit.answerIfMultiple = []
							for choice in question.choices:
								if self.request.get("%s|%s" % (question.key(), choice)) == "yes":
									answerToEdit.answerIfMultiple.append(choice)
									keepAnswer = True
						else:
							keepAnswer = len(self.request.get(queryText)) > 0
							if keepAnswer:
								answerToEdit.answerIfText = self.request.get(queryText)
					answerToEdit.creator = member
					answerToEdit.draft = setAsDraft
					if keepAnswer:
						if setAsDraft:
							answerToEdit.edited = datetime.now(tz=pytz.utc)
							answerToEdit.put()
						else:
							answerToEdit.publish()
				if preview:
					self.redirect("/visit/previewAnswers?%s" % article.key())
				elif setAsDraft:
					self.redirect("/visit/profile?%s" % member.key())
				else:
					self.redirect("/visit/read?%s" % article.key())
		else:
			self.redirect("/visit/look")
			
class PreviewAnswersPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		community, member = GetCurrentCommunityAndMemberFromSession()
		if community and member:
			article = None
			if self.request.query_string:
				article = Article.get(self.request.query_string)
				answers = article.getAnswersForMember(member)
			if article and answers:
				template_values = {
							   	   'title': "Preview of", 
						   	   	   'title_extra': "Answers for %s " % article.title, 
								   'user': users.get_current_user(),
								   'current_member': member,
								   'community': community, 
								   'article': article,
								   'community_has_questions_for_this_article_type': len(community.getQuestionsOfType(article.type)) > 0,
								   'questions': community.getQuestionsOfType(article.type),
								   'answers': answers,
								   'user_is_admin': users.is_current_user_admin(),
								   'logout_url': users.create_logout_url("/"),
								   }
			path = os.path.join(os.path.dirname(__file__), 'templates/visit/previewAnswers.html')
			self.response.out.write(template.render(path, template_values))
		else:
			self.redirect("/")
		
	@RequireLogin 
	def post(self):
		community, member = GetCurrentCommunityAndMemberFromSession()
		if community and member:
			article = None
			if self.request.query_string:
				article = Article.get(self.request.query_string)
				if article:
					if "edit" in self.request.arguments():
						self.redirect("/visit/answers?%s" % article.key())
					elif "profile" in self.request.arguments():
						self.redirect("/visit/profile?%s" % member.key())
					elif "publish" in self.request.arguments():
						answers = article.getAnswersForMember(member)
						for answer in answers:
							answer.draft = False
							answer.published = datetime.now(tz=pytz.utc)
							answer.put()
						self.redirect("/visit/look")

class EnterAnnotationPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		community, member = GetCurrentCommunityAndMemberFromSession()
		if community and member:
			i = 0
			for aType in ANNOTATION_TYPES_URLS:
				if self.request.uri.find(aType) >= 0:
					type = ANNOTATION_TYPES[i]
					break
				i += 1
			i = 0
			for aType in ENTRY_TYPES_URLS:
				if self.request.uri.find(aType) >= 0:
					entryTypeIndex = i
					break
				i += 1
			article = None
			annotation = None
			if self.request.query_string:
				try:
					article = Article.get(self.request.query_string)
				except:
					annotation = Annotation.get(self.request.query_string)
					article = annotation.article
			if article:
				if not article.memberCanNudge(member):
					nudgePointsMemberCanAssign = 0
				else:
					nudgePointsMemberCanAssign = max(0, community.maxNudgePointsPerArticle - article.getTotalNudgePointsForMember(member))
			else:
				nudgePointsMemberCanAssign = community.maxNudgePointsPerArticle
			if article:
				template_values = {
							   	   'title': "%s for" % type.capitalize(), 
						   	   	   'title_extra': article.title, 
								   'user': users.get_current_user(),
								   'current_member': member,
								   'community': community, 
								   'annotation_type': type,
								   'annotation': annotation,
								   'community_members': community.getActiveMembers(),
								   'offline_members': community.getOfflineMembers(),
								   'article': article,
								   'nudge_categories': community.nudgeCategories,
								   'nudge_points_member_can_assign': nudgePointsMemberCanAssign,
								   'character_allowed': community.allowCharacter[entryTypeIndex],
								   'included_links_outgoing': article.getOutgoingLinksOfType("included"),
								   'text_formats': TEXT_FORMATS,
								   'user_is_admin': users.is_current_user_admin(),
								   'logout_url': users.create_logout_url("/"),
								   }
				path = os.path.join(os.path.dirname(__file__), 'templates/visit/annotation.html')
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect("/visit/look")
		else:
			self.redirect("/")
			
	@RequireLogin 
	def post(self):
		community, member = GetCurrentCommunityAndMemberFromSession()
		if community and member:
			for aType in ANNOTATION_TYPES:
				for argument in self.request.arguments():
					if argument.find(aType) >= 0:
						type = aType
						break
			article = None
			annotation = None
			newAnnotation = False
			if self.request.query_string:
				try:
					article = Article.get(self.request.query_string)
				except:
					annotation = Annotation.get(self.request.query_string)
					article = annotation.article
			if article:
				if not annotation:
					annotation = Annotation(community=community, type=type, creator=member, article=article)
					newAnnotation = True
				preview = False
				if "save|%s" % type in self.request.arguments():
					annotation.draft = True
					annotation.edited = datetime.now(tz=pytz.utc)
				elif "preview|%s" % type in self.request.arguments():
					annotation.draft = True
					preview = True
				elif "publish|%s" % type in self.request.arguments():
					annotation.draft = False
					annotation.published = datetime.now(tz=pytz.utc)
				annotation.collectedOffline = self.request.get("collectedOffline") == "yes"
				if annotation.collectedOffline and member.isLiaison():
					for aMember in community.getActiveMembers():
						if self.request.get("offlineSource") == aMember.key():
							annotation.creator = aMember
							annotation.liaison = member
							break
				if self.request.get("attribution") != "member":
					characterKey = self.request.get("attribution")
					character = Character.get(characterKey)
					annotation.character = character
				else:
					annotation.character = None
				if type == "tag set":
					annotation.tagsIfTagSet = []
					for i in range (5):
						if self.request.get("tag%s" % i):
							annotation.tagsIfTagSet.append(cgi.escape(self.request.get("tag%s" % i)))
				elif type == "comment":
					annotation.shortString = cgi.escape(self.request.get("shortString"))
					text = self.request.get("longString")
					format = self.request.get("longString_format").strip()
					annotation.longString = text
					annotation.longString_formatted = db.Text(InterpretEnteredText(text, format))
					annotation.longString_format = format
				elif type == "request":
					annotation.shortString = cgi.escape(self.request.get("shortString"))
					text = self.request.get("longString")
					format = self.request.get("longString_format").strip()
					annotation.longString = text
					annotation.longString_formatted = db.Text(InterpretEnteredText(text, format))
					annotation.longString_format = format
				elif type == "nudge":
					oldTotalNudgePointsInThisNudge = annotation.totalNudgePointsAbsolute()
					nudgeValuesTheyWantToSet = []
					totalNudgeValuesTheyWantToSet = 0
					for i in range(5):
						category = community.nudgeCategories[i]
						if category:
							oldValue = annotation.valuesIfNudge[i]
							try:
								nudgeValuesTheyWantToSet.append(int(self.request.get("nudge%s" % i)))
							except:
								nudgeValuesTheyWantToSet.append(oldValue)
							totalNudgeValuesTheyWantToSet += abs(nudgeValuesTheyWantToSet[i])
					adjustedValues = []
					maximumAllowedInThisInstance = min(member.nudgePoints, community.maxNudgePointsPerArticle)
					if totalNudgeValuesTheyWantToSet > maximumAllowedInThisInstance:
						totalNudgePointsAllocated = 0
						for i in range(5):
							category = community.nudgeCategories[i]
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
					annotation.shortString = cgi.escape(self.request.get("shortString"))
					newTotalNudgePointsInThisNudge = annotation.totalNudgePointsAbsolute()
					member.nudgePoints += oldTotalNudgePointsInThisNudge
					member.nudgePoints -= newTotalNudgePointsInThisNudge
					member.put()
				annotation.put()
				if not annotation.draft:
					annotation.publish()
				if preview:
					self.redirect("/visit/preview?%s" % annotation.key())
				elif annotation.draft:
					self.redirect("/visit/profile?%s" % member.key())
				else:
					self.redirect("/visit/read?%s" % article.key())
			else:
				self.redirect("/visit/look")
		else:
			self.redirect("/")
			
class PreviewPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		community, member = GetCurrentCommunityAndMemberFromSession()
		if community and member:
			article = None
			annotation = None
			if self.request.query_string:
				try:
					article = Article.get(self.request.query_string)
				except:
					annotation = Annotation.get(self.request.query_string)
					article = annotation.article
			if article:
				template_values = {
							   	   'title': "Preview", 
						   	   	   'title_extra': article.title, 
								   'user': users.get_current_user(),
								   'current_member': member,
								   'community': community, 
								   'annotation': annotation,
								   'article': article,
								   'included_links_outgoing': article.getOutgoingLinksOfType("included"),
								   'community_has_questions_for_this_article_type': len(community.getQuestionsOfType(article.type)) > 0,
								   'questions': community.getQuestionsOfType(article.type),
								   'answers_with_article': article.getAnswersForMember(member),
								   'nudge_categories': community.nudgeCategories,
								   'user_is_admin': users.is_current_user_admin(),
								   'logout_url': users.create_logout_url("/"),
								   }
			path = os.path.join(os.path.dirname(__file__), 'templates/visit/preview.html')
			self.response.out.write(template.render(path, template_values))
		else:
			self.redirect("/")
		
	@RequireLogin 
	def post(self):
		community, member = GetCurrentCommunityAndMemberFromSession()
		if community and member:
			article = None
			annotation = None
			if self.request.query_string:
				try:
					article = Article.get(self.request.query_string)
				except:
					annotation = Annotation.get(self.request.query_string)
					article = annotation.article
			if "profile" in self.request.arguments():
				self.redirect("/visit/profile?%s" % member.key())
			elif annotation:
				if "edit" in self.request.arguments():
					self.redirect("/visit/%s?%s" % (annotation.typeAsURL(), annotation.key()))
				elif "publish" in self.request.arguments():
					annotation.publish()
					self.redirect("/visit/look?%s" % annotation.article.key())
			else:
				if "edit" in self.request.arguments():
					self.redirect("/visit/%s?%s" % (article.type, article.key()))
				elif "publish" in self.request.arguments():
					article.publish()
					self.redirect("/visit/look")
		else:
			self.redirect("/")
					
class RelateArticlePage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		community, member = GetCurrentCommunityAndMemberFromSession()
		if community and member:
			article = None
			if self.request.query_string:
				try:
					article = Article.get(self.request.query_string)
				except:
					article = None
			if article:
				links = article.getLinksOfType("related")
				articles = community.getNonDraftArticles()
				articlesThatCanBeRelated = []
				for anArticle in articles:
					found = False
					for link in links:
						if link.articleTo.key() == anArticle.key() or link.articleFrom.key() == anArticle.key():
							found = True
					if not found and anArticle.key() != article.key():
						articlesThatCanBeRelated.append(anArticle)
				if articlesThatCanBeRelated:
					template_values = {
									'title': "Relate articles to",
								   	'title_extra': article.title,
									'community': community, 
									'current_member': member, 
									'article': article,
									'articles': articlesThatCanBeRelated, 
									'related_links': links,
									'user_is_admin': users.is_current_user_admin(), 
									'logout_url': users.create_logout_url("/"), 
									}
					path = os.path.join(os.path.dirname(__file__), 'templates/visit/relate.html')
					self.response.out.write(template.render(path, template_values))
				else:
					self.redirect("read?%s" % article.key()) # should not have link in this case CFK FIX
			else:
				self.redirect('/')
					
	@RequireLogin 
	def post(self):
		community, member = GetCurrentCommunityAndMemberFromSession()
		if community and member:
				article = None
				if self.request.query_string:
					try:
						article = Article.get(self.request.query_string)
					except:
						article = None
				if article:
					linksToRemove = []
					for link in article.getLinksOfType("related"):
						if self.request.get("linkComment|%s" % link.key()):
							link.comment = self.request.get("linkComment|%s" % link.key())
							link.put()
						if self.request.get("removeLink|%s" % link.key()) == "yes":
							linksToRemove.append(link)
					for link in linksToRemove:
						db.delete(link)
					for anArticle in community.getNonDraftArticles():
						if self.request.get("addLink|%s" % anArticle.key()) == "yes":
							link = Link(articleFrom=article, articleTo=anArticle, type="related", \
										creator=member, community=community,
										comment=cgi.escape(self.request.get("linkComment|%s" % anArticle.key())))
							link.put()
							link.publish()
					self.redirect("read?%s" % article.key())
				else:
					self.redirect("/visit/look")
		else:
			self.redirect("/")
			
