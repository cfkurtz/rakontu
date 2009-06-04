# --------------------------------------------------------------------------------------------
# RAKONTU
# Description: Rakontu is open source story sharing software.
# Version: pre-0.1
# License: GPL 3.0
# Google Code Project: http://code.google.com/p/rakontu/
# --------------------------------------------------------------------------------------------

from models import *
import systemquestions

def RequireLogin(func):
	def check_login(request):
		if not users.get_current_user():
			loginURL = users.create_login_url("/")
			request.redirect(loginURL)
			return
		func(request)
	return check_login 

def GetCurrentCommunityAndMemberFromSession():
	session = Session()
	if session and session.has_key('community_key'):
		community_key = session['community_key']
	else:
		community_key = None
	if session and session.has_key('member_key'):
		member_key = session['member_key']
	else:
		member_key = None
	if community_key: 
		community = db.get(community_key) 
	else:
		community = None
	if member_key:
		member = db.get(member_key)
		if not member.community.key() == community.key():
			member = None
	else:
		member = None
	return community, member

def RelativeTimeDisplayString(when):
	delta = datetime.datetime.now() - when
	if delta.days < 1 and delta.seconds < 1: 
		return "Now"
	elif delta.days < 1 and delta.seconds < 60: 
		return "Moments ago"
	elif delta.days < 1 and delta.seconds < 3600:
		return "%s minutes ago" % (delta.seconds // 60)
	elif delta.days < 1:
		return "Today at %s" % when.strftime("%I:%M")
	elif delta.days < 2:
		return "Yesterday at %s" % when.strftime("%I:%M %p")
	elif delta.days < 7:
		return when.strftime("%A at %I:%M %p")
	else:
		return when.strftime("%A %B %d, %Y at %I:%M %p")

def MakeSomeFakeData():
	user = users.get_current_user()
	community = Community(name="Test community", description="Test description")
	community.put()
	member = Member(googleAccountID=user.user_id(), googleAccountEmail=user.email(), nickname="Tester", community=community, governanceType="owner")
	member.put()
	Character(name="Little Bird", community=community).put()
	Character(name="Old Coot", community=community).put()
	Character(name="Blooming Idiot", community=community).put()
	article = Article(community=community, type="story", creator=member, title="The dog", text="The dog sat on a log.", draft=False)
	article.put()
	article.publish()
	annotation = Annotation(community=community, type="comment", creator=member, article=article, shortString="Great!", longString="Wonderful!", draft=False)
	annotation.put()
	annotation.publish()
	annotation = Annotation(community=community, type="comment", creator=member, article=article, shortString="Dumb", longString="Silly", draft=False)
	annotation.put()
	annotation.publish()
	article = Article(community=community, type="story", creator=member, title="The circus", text="I went the the circus. It was great.", draft=False)
	article.put()
	article.publish()

# --------------------------------------------------------------------------------------------
# Startup page
# --------------------------------------------------------------------------------------------
		
class StartPage(webapp.RequestHandler):
	def get(self):
		user = users.get_current_user()
		communitiesTheyAreAMemberOf = []
		communitiesTheyAreInvitedTo = []
		if user:
			members = Member.all().filter("googleAccountID = ", user.user_id()).fetch(FETCH_NUMBER)
			for member in members:
				try:
					if member.active:
						communitiesTheyAreAMemberOf.append(member.community)
				except:
					pass # if can't link to community don't use it
			pendingMembers = PendingMember.all().filter("email = ", user.email()).fetch(FETCH_NUMBER)
			for pendingMember in pendingMembers:
				try:
					communitiesTheyAreInvitedTo.append(pendingMember.community)
				except:
					pass # if can't link to community don't use it
		template_values = {
						   'user': user, 
						   'communities_member_of': communitiesTheyAreAMemberOf,
						   'communities_invited_to': communitiesTheyAreInvitedTo,
						   'DEVELOPMENT': DEVELOPMENT,
						   'login_url': users.create_login_url("/"),
						   'logout_url': users.create_logout_url("/"),
						   }
		path = os.path.join(os.path.dirname(__file__), 'templates/startPage.html')
		self.response.out.write(template.render(path, template_values))

	def post(self):
		user = users.get_current_user()
		if "visitCommunity" in self.request.arguments():
			community_key = self.request.get('community_key')
			if community_key:
				community = db.get(community_key) 
				if community:
					session = Session()
					session['community_key'] = community_key
					matchingMembers = Member.all().filter("community = ", community).filter("googleAccountID = ", user.user_id()).fetch(FETCH_NUMBER)
					if matchingMembers:
						session['member_key'] = matchingMembers[0].key()
						if matchingMembers[0].active:
							self.redirect('/visit/look')
						else:
							matchingMembers[0].active = True
							matchingMembers[0].put()
							pendingMembers = PendingMember.all().filter("community = ", community.key()).filter("email = ", user.email()).fetch(FETCH_NUMBER)
							if pendingMembers:
								db.delete(pendingMembers[0])
							self.redirect("/visit/new")
					else:
						pendingMembers = PendingMember.all().filter("community = ", community.key()).filter("email = ", user.email()).fetch(FETCH_NUMBER)
						if pendingMembers:
							newMember = Member(
								nickname=user.email(),
								googleAccountID=user.user_id(),
								googleAccountEmail=user.email(),
								community=community,
								active=True,
								governanceType="member")
							newMember.put()
							db.delete(pendingMembers[0])
							session['member_key'] = newMember.key()
							self.redirect("/visit/new")
						else:
							self.redirect('/')
				else:
					self.redirect('/')
			else:
				self.redirect('/')
		elif "createCommunity" in self.request.arguments():
			self.redirect("/createCommunity")
		elif "makeFakeData" in self.request.arguments():
			MakeSomeFakeData()
			self.redirect("/")
			
class NewMemberPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		community, member = GetCurrentCommunityAndMemberFromSession()
		if community and member:
			template_values = {
							   'community': community, 
							   'current_user': users.get_current_user(), 
							   'current_member': member,
							   'user_is_admin': users.is_current_user_admin(),
							   'logout_url': users.create_logout_url("/"),
							   }
			path = os.path.join(os.path.dirname(__file__), 'templates/visit/new.html')
			self.response.out.write(template.render(path, template_values))
		else:
			self.redirect('/')
							 
# --------------------------------------------------------------------------------------------
# Create new community
# --------------------------------------------------------------------------------------------
		
class CreateCommunityPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		template_values = {
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
		member.put()
		self.redirect('/')
		
# --------------------------------------------------------------------------------------------
# Browse and read
# --------------------------------------------------------------------------------------------
						
class BrowseArticlesPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		community, member = GetCurrentCommunityAndMemberFromSession()
		if community and member:
			articles = community.getNonDraftArticles()
			if articles:
				maxTime = member.viewTimeEnd
				minTime = member.getViewStartTime()
				maxNudgePoints = -9999999
				minNudgePoints = -9999999
				minActivityPoints = -9999999
				maxActivityPoints = -9999999
				for article in articles:
					nudgePoints = article.nudgePointsCombined()
					if minNudgePoints == -9999999:
						minNudgePoints = nudgePoints
					elif nudgePoints < minNudgePoints:
						minNudgePoints = nudgePoints
					if maxNudgePoints == -9999999:
						maxNudgePoints = nudgePoints
					elif nudgePoints > maxNudgePoints:
						maxNudgePoints = nudgePoints
					activityPoints = article.activityPoints
					if minActivityPoints == -9999999:
						minActivityPoints = activityPoints
					elif activityPoints < minActivityPoints:
						minActivityPoints = activityPoints
					if maxActivityPoints == -9999999:
						maxActivityPoints = activityPoints
					elif activityPoints > maxActivityPoints:
						maxActivityPoints = activityPoints
				numRows = 10
				numCols = member.viewNumTimeColumns
				nudgeStep = max(1, (maxNudgePoints - minNudgePoints) // numRows)
				timeStep = (maxTime - minTime) // numCols
				
				textsForGrid = []
				rowHeaders = []
				timeFormat = "%A %B %d, %Y at %H:%M"
				for row in range(numRows):
					textsInThisRow = []
					startNudgePoints = minNudgePoints + nudgeStep * row
					if row == numRows - 1:
						endNudgePoints = 100000000
					else:
						endNudgePoints = minNudgePoints + nudgeStep * (row+1)
					for col in range(numCols):
						textsInThisCell = []
						startTime = minTime + timeStep * col
						endTime = minTime + timeStep * (col+1)
						if row == numRows - 1:
							rowHeaders.append(RelativeTimeDisplayString(startTime))
						for article in articles:
							shouldBeInRow = article.nudgePointsCombined() >= startNudgePoints and article.nudgePointsCombined() < endNudgePoints
							if article.lastAnnotatedOrAnsweredOrLinked:
								timeToCheck = article.lastAnnotatedOrAnsweredOrLinked
							else:
								timeToCheck = article.published
							shouldBeInCol = timeToCheck >= startTime and timeToCheck < endTime
							if shouldBeInRow and shouldBeInCol:
								fontSizePercent = min(200, 90 + article.activityPoints - minActivityPoints)
								text = '<p>%s <span style="font-size:%s%%"><a href="/visit/read?%s">%s</a></span></p>' % \
									(article.getImageLinkForType(), fontSizePercent, article.key(), article.title)
								textsInThisCell.append(text)
							"""
							# experiment with putting name in when first published, too confusing
							if article.lastAnnotatedOrAnsweredOrLinked:
								shouldBeInRowForPublish = 0 >= startNudgePoints and 0 < endNudgePoints
								shouldBeInColForPublish = article.published >= startTime and article.published < endTime
								if shouldBeInRowForPublish and shouldBeInColForPublish:
									fontSizePercent = 80
									text = '<p><span style="font-size:%s%%">%s</span></p>' % \
									(fontSizePercent, article.title)
									textsInThisCell.append(text)
							"""
						textsInThisRow.append(textsInThisCell)
					textsForGrid.append(textsInThisRow)
				textsForGrid.reverse()
			else:
				textsForGrid = []
			template_values = {
							   'community': community, 
							   'current_member': member,
							   'articles': articles,
							   'rows_cols': textsForGrid,
							   'row_headers': rowHeaders,
							   'time_frames': TIME_FRAMES,
							   'article_types': ARTICLE_TYPES,
							   '1_to_31': range(1, 31, 1),
							   '1_to_10': range(1, 11, 1),
							   'user_is_admin': users.is_current_user_admin(),
							   'logout_url': users.create_logout_url("/"),
							   }
			path = os.path.join(os.path.dirname(__file__), 'templates/visit/look.html')
			self.response.out.write(template.render(path, template_values))
		else:
			self.redirect('/')
			
	@RequireLogin 
	def post(self):
		community, member = GetCurrentCommunityAndMemberFromSession()
		if community and member:
			if "changeTimeFrame" in self.request.arguments():
				member.setViewTimeFrameFromTimeUnitString(self.request.get("timeFrame"))
				oldValue = member.viewNumTimeFrames
				try:
					member.viewNumTimeFrames = int(self.request.get("numberOf"))
				except:
					member.viewNumTimeFrames = oldValue
				oldValue = member.viewNumTimeColumns
				try:
					member.viewNumTimeColumns = int(self.request.get("numColumns"))
				except:
					member.viewNumTimeColumns = oldValue

			else:
				if "setToLast" in self.request.arguments():
					if community.lastPublish:
						member.viewTimeEnd = community.lastPublish + datetime.timedelta(seconds=10)
					else:
						member.viewTimeEnd = datetime.datetime.now()
				elif "setToFirst" in self.request.arguments():
					if community.firstPublish:
						member.setTimeFrameToStartAtFirstPublish()
					else:
						member.viewTimeEnd = datetime.datetime.now()
				else:
					changeSeconds = member.viewTimeFrameInSeconds * member.viewNumTimeFrames
					if "moveTimeBack" in self.request.arguments():
						member.viewTimeEnd = member.viewTimeEnd - datetime.timedelta(seconds=changeSeconds)
					else:
						member.viewTimeEnd = member.viewTimeEnd + datetime.timedelta(seconds=changeSeconds)
				if community.firstPublish and member.getViewStartTime() < community.firstPublish:
				 	member.setTimeFrameToStartAtFirstPublish()
				if member.viewTimeEnd > datetime.datetime.now():
					member.viewTimeEnd = datetime.datetime.now()
			member.put()
			self.redirect("/visit/look")
		else:
			self.redirect("/")
			
class ReadArticlePage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		community, member = GetCurrentCommunityAndMemberFromSession()
		if community and member:
			article = db.get(self.request.query_string)
			if article:
				template_values = {
								   'community': community, 
								   'current_member': member,
								   'article': article,
								   'member_can_answer_questions': len(article.getAnswersForMember(member)) == 0,
								   'member_can_add_nudge': article.memberCanNudge(member) and len(article.getNudgesForMember(member)) == 0,
								   'community_has_questions_for_this_article_type': len(community.getQuestionsOfType(article.type)) > 0,
								   'user_is_admin': users.is_current_user_admin(),
								   'logout_url': users.create_logout_url("/"),
								   'answers': article.getNonDraftAnswers(),
								   'questions': community.getQuestionsOfType(article.type),
								   'attachments': article.getAttachments(),
								   'requests': article.getNonDraftAnnotationsOfType("request"),
								   'comments': article.getNonDraftAnnotationsOfType("comment"),
								   'tag_sets': article.getNonDraftAnnotationsOfType("tag set"),
								   'nudges': article.getNonDraftAnnotationsOfType("nudge"),
								   'retold_links_incoming': article.getIncomingLinksOfType("retold"),
								   'retold_links_outgoing': article.getOutgoingLinksOfType("retold"),
								   'reminded_links_incoming': article.getIncomingLinksOfType("reminded"),
								   'reminded_links_outgoing': article.getOutgoingLinksOfType("reminded"),
								   'related_links': article.getLinksOfType("related"),
								   'included_links_incoming_from_invitations': article.getIncomingLinksOfTypeFromType("included", "invitation"),
								   'included_links_incoming_from_patterns': article.getIncomingLinksOfTypeFromType("included", "pattern"),
								   'included_links_incoming_from_collages': article.getIncomingLinksOfTypeFromType("included", "collage"),
								   'included_links_outgoing': article.getOutgoingLinksOfType("included"),
								   'history': article.getHistory(),
								   }
				member.lastReadAnything = datetime.datetime.now()
				member.nudgePoints += community.getNudgePointsPerActivityForActivityName("reading")
				member.put()
				path = os.path.join(os.path.dirname(__file__), 'templates/visit/read.html')
				self.response.out.write(template.render(path, template_values))
		else:
			self.redirect('/')
			
class SeeCommunityPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		community, member = GetCurrentCommunityAndMemberFromSession()
		if community and member:
				template_values = {
								   'community': community, 
								   'current_member': member,
								   'community_members': community.getActiveMembers(),
								   'characters': community.getCharacters(),
								   'user_is_admin': users.is_current_user_admin(),
								   'logout_url': users.create_logout_url("/"),								   
								   }
				path = os.path.join(os.path.dirname(__file__), 'templates/visit/community.html')
				self.response.out.write(template.render(path, template_values))
		else:
			self.redirect('/')
			
class SeeCommunityMembersPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		community, member = GetCurrentCommunityAndMemberFromSession()
		if community and member:
				template_values = {
								   'community': community, 
								   'current_member': member,
								   'community_members': community.getActiveMembers(),
								   'user_is_admin': users.is_current_user_admin(),
								   'logout_url': users.create_logout_url("/"),								   
								   }
				path = os.path.join(os.path.dirname(__file__), 'templates/visit/members.html')
				self.response.out.write(template.render(path, template_values))
		else:
			self.redirect('/')
   
class SeeMemberPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		community, member = GetCurrentCommunityAndMemberFromSession()
		if community and member:
				memberKey = self.request.query_string
				memberToSee = db.get(memberKey)
				if memberToSee:
					template_values = {
									   'community': community, 
									   'current_member': member,
									   'member': memberToSee,
									   'history': member.getHistory(),
									   'user_is_admin': users.is_current_user_admin(),
									   'logout_url': users.create_logout_url("/"),								   
									   }
					path = os.path.join(os.path.dirname(__file__), 'templates/visit/member.html')
					self.response.out.write(template.render(path, template_values))
				else:
					self.redirect('/visit/look')
		else:
			self.redirect('/')

	@RequireLogin 
	def post(self):
		community, member = GetCurrentCommunityAndMemberFromSession()
		if community and member:
			messageMember = None
			for aMember in community.getActiveMembers():
				for argument in self.request.arguments():
					if argument.find(aMember.key()) >= 0:
						messageMember = aMember
						break
			if messageMember:
				message = mail.EmailMessage()
				# CFK FIX
				#message.sender= # NEED TO STORE SYS ADMIN EMAIL !! (how to do that?)
				message.subject=cgi.escape(self.request.get("subject"))
				message.to=messageMember.googleAccountEmail
				message.body=MakeTextSafeWithMinimalHTML(self.request.get("message"))
				message.send()
   
class SeeCharacterPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		community, member = GetCurrentCommunityAndMemberFromSession()
		if community and member:
				characterKey = self.request.query_string
				characterToSee = db.get(characterKey)
				if characterToSee:
					template_values = {
									   'community': community, 
									   'current_member': member,
									   'character': characterToSee,
									   'history': characterToSee.getHistory(),
									   'user_is_admin': users.is_current_user_admin(),
									   'logout_url': users.create_logout_url("/"),								   
									   }
					path = os.path.join(os.path.dirname(__file__), 'templates/visit/character.html')
					self.response.out.write(template.render(path, template_values))
				else:
					self.redirect('/visit/look')
		else:
			self.redirect('/')
			
# --------------------------------------------------------------------------------------------
# Add or change article
# --------------------------------------------------------------------------------------------
   
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
			elif self.request.uri.find("remind") >= 0:
				type = "story"
				linkType = "remind"
				articleFromKey = self.request.query_string
				articleFrom = db.get(articleFromKey)
				article = None
				entryTypeIndexForCharacters = STORY_ENTRY_TYPE_INDEX
			elif self.request.uri.find("respond") >= 0:
				type = "story"
				linkType = "respond"
				articleFromKey = self.request.query_string
				articleFrom = db.get(articleFromKey)
				article = None
				entryTypeIndexForCharacters = STORY_ENTRY_TYPE_INDEX
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
				else:
					articleKey = self.request.query_string
					article = db.get(articleKey)
			if article:
				answers = article.getAnswers()
				attachments = article.getAttachments()
			else:
				answers = None
				attachments = None
			template_values = {
							   'user': users.get_current_user(),
							   'current_member': member,
							   'community': community, 
							   'article_type': type,
							   'article': article,
							   'questions': community.getQuestionsOfType(type),
							   'answers': answers,
							   'attachments': attachments,
							   'community_members': community.getActiveMembers(),
							   'character_allowed': community.allowCharacter[entryTypeIndexForCharacters],
							   'link_type': linkType,
							   'article_from': articleFrom,
							   'text_formats': TEXT_FORMATS,
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
				article.edited = datetime.datetime.now()
			elif "preview|%s" % type in self.request.arguments():
				article.draft = True
				preview = True
			elif "publish|%s" % type in self.request.arguments():
				article.draft = False
				article.published = datetime.datetime.now()
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
			if self.request.get("attribution"):
				characterKey = self.request.get("attribution")
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
						activity = "retelling"
					elif self.request.get("link_type") == "remind":
						linkType = "reminded"
						activity = "reminding"
					elif self.request.get("link_type") == "respond":
						linkType = "included"
						activity = "including"
					elif self.request.get("link_type") == "relate":
						linkType = "related"
						activity = "relating"
					elif self.request.get("link_type") == "include":
						linkType = "included"
						activity = "including"
					link = Link(articleFrom=articleFrom, articleTo=article, type=linkType, \
								creator=member, comment=cgi.escape(self.request.get("link_comment")))
					link.put()
					member.nudgePoints += community.getNudgePointsPerActivityForActivityName(activity)
			questions = Question.all().filter("community = ", community).filter("refersTo = ", type).fetch(FETCH_NUMBER)
			for question in questions:
				foundAnswers = Answer.all().filter("question = ", question.key()).filter("referent =", article.key()).filter("creator = ", member.key()).fetch(FETCH_NUMBER)
				if foundAnswers:
					answerToEdit = foundAnswers[0]
				else:
					answerToEdit = Answer(question=question, community=community, creator=member, referent=article, referentType="article")
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
							if self.request.get("%s|%s" % (question.key(), choice)):
								answerToEdit.answerIfMultiple.append(choice)
					else:
						answerToEdit.answerIfText = self.request.get("%s" % (question.key()))
				answerToEdit.creator = member
				answerToEdit.draft = article.draft
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
				self.redirect("/visit/read?%s" % article.key())
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
								   'user': users.get_current_user(),
								   'current_member': member,
								   'community': community, 
								   'article': article,
								   'article_type': article.type,
								   'questions': community.getQuestionsOfType(article.type),
								   'answers': article.getAnswersForMember(member),
								   'community_members': community.getActiveMembers(),
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
				if self.request.get("attribution"):
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
								if self.request.get("%s|%s" % (question.key(), choice)):
									answerToEdit.answerIfMultiple.append(choice)
						else:
							answerToEdit.answerIfText = self.request.get("%s" % (question.key()))
					answerToEdit.creator = member
					answerToEdit.draft = setAsDraft
					if setAsDraft:
						answerToEdit.edited = datetime.datetime.now()
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
							answer.published = datetime.datetime.now()
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
				template_values = {
								   'user': users.get_current_user(),
								   'current_member': member,
								   'community': community, 
								   'annotation_type': type,
								   'annotation': annotation,
								   'community_members': community.getActiveMembers(),
								   'article': article,
								   'request_types': REQUEST_TYPES,
								   'nudge_categories': community.nudgeCategories,
								   'character_allowed': community.allowCharacter[entryTypeIndex],
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
					annotation.edited = datetime.datetime.now()
				elif "preview|%s" % type in self.request.arguments():
					annotation.draft = True
					preview = True
				elif "publish|%s" % type in self.request.arguments():
					annotation.draft = False
					annotation.published = datetime.datetime.now()
				annotation.collectedOffline = self.request.get("collectedOffline") == "yes"
				if annotation.collectedOffline and member.isLiaison():
					for aMember in community.getActiveMembers():
						if self.request.get("offlineSource") == aMember.key():
							annotation.creator = aMember
							annotation.liaison = member
							break
				if self.request.get("attribution"):
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
					annotation.typeIfRequest = self.request.get("typeIfRequest")
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
								   'user': users.get_current_user(),
								   'current_member': member,
								   'community': community, 
								   'annotation': annotation,
								   'article': article,
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

# --------------------------------------------------------------------------------------------
# Manage memberhip
# --------------------------------------------------------------------------------------------
   
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
							   'community': community, 
							   'current_user': users.get_current_user(), 
							   'current_member': member,
							   'questions': community.getMemberQuestions(),
							   'answers': member.getAnswers(),
							   'draft_articles': member.getDraftArticles(),
							   'draft_annotations': member.getDraftAnnotations(),
							   'first_draft_answer_per_article': firstDraftAnswerForEachArticle,
							   'liaison': liaison,
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
							if self.request.get("%s|%s" % (question.key(), choice)):
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
			i = 0
			for pointType in ACTIVITIES_GERUND:
				if DEFAULT_NUDGE_POINT_ACCUMULATIONS[i] != 0: # if zero, not appropriate for nudge point accumulation
					nudgePointIncludes.append('<tr><td align="right">%s</td><td align="left"><input type="text" name="%s" size="4" value="%s"/></td></tr>' \
						% (pointType, pointType, community.nudgePointsPerActivity[i]))
				i += 1
			characterIncludes = []
			i = 0
			for entryType in ENTRY_TYPES:
				characterIncludes.append('<input type="checkbox" name="%s" value="%s" %s id="%s"/><label for="%s">%s</label>' \
						% (entryType, entryType, checkedBlank(community.allowCharacter[i]), entryType, entryType, entryType))
				i += 1
			template_values = {
							   'community': community, 
							   'current_user': users.get_current_user(), 
							   'current_member': member,
							   'character_includes': characterIncludes,
							   'nudge_point_includes': nudgePointIncludes,
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
			for pointType in ACTIVITIES_GERUND:
				if DEFAULT_NUDGE_POINT_ACCUMULATIONS[i] != 0: # if zero, not appropriate for nudge point accumulation
					oldValue = community.nudgePointsPerActivity[i]
					try:
						community.nudgePointsPerActivity[i] = int(self.request.get(pointType))
					except:
						community.nudgePointsPerActivity[i] = oldValue
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
			path = os.path.join(os.path.dirname(__file__), 'templates/manage/questions/questions.html')
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
				question.text = MakeTextSafeWithMinimalHTML(self.request.get("text|%s" % question.key()))
				question.help = MakeTextSafeWithMinimalHTML(self.request.get("help|%s" % question.key()))
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
		self.redirect('/visit/look')
		
class ManageCommunityCharactersPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		community, member = GetCurrentCommunityAndMemberFromSession()
		if community and member:
			characters = Character.all().filter("community = ", community).fetch(FETCH_NUMBER)
			template_values = {
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
			
# --------------------------------------------------------------------------------------------
# Non-text handling
# --------------------------------------------------------------------------------------------
		
class ImageHandler(webapp.RequestHandler):
	def get(self):
		if self.request.get("member_id"):
			member = db.get(self.request.get("member_id"))
			if member and member.profileImage:
				self.response.headers['Content-Type'] = "image/jpg"
				self.response.out.write(member.profileImage)
			else:
				self.error(404)
		elif self.request.get("community_id"):
			community = db.get(self.request.get("community_id"))
			if community and community.image:
				self.response.headers['Content-Type'] = "image/jpg"
				self.response.out.write(community.image)
			else:
				self.error(404)
		elif self.request.get("article_id"):
			article = db.get(self.request.get("article_id"))
			if article and article.type == "pattern" and article.screenshotIfPattern:
				self.response.headers['Content-Type'] = "image/jpg"
				self.response.out.write(article.screenshotIfPattern)
		elif self.request.get("character_id"):
			character = db.get(self.request.get("character_id"))
			if character:
				self.response.headers['Content-Type'] = "image/jpg"
				self.response.out.write(character.image)
			   
class AttachmentHandler(webapp.RequestHandler):
	def get(self):
		if self.request.get("attachment_id"):
			attachment = db.get(self.request.get("attachment_id"))
			if attachment and attachment.data:
				if attachment.mimeType in ["image/jpeg", "image/png", "text/html", "text/plain"]:
					self.response.headers.add_header('Content-Disposition', 'filename="%s"' % attachment.fileName)
				else:
					self.response.headers.add_header('Content-Disposition', 'attachment; filename="%s"' % attachment.fileName)
				self.response.headers.add_header('Content-Type', attachment.mimeType)
				self.response.out.write(attachment.data)
			else:
				self.error(404)
				
# --------------------------------------------------------------------------------------------
# Application and main
# --------------------------------------------------------------------------------------------

application = webapp.WSGIApplication(
									 [('/', StartPage),
									  
									  # visiting
									  ('/visit', BrowseArticlesPage),
									  ('/visit/', BrowseArticlesPage),
									  ('/visit/look', BrowseArticlesPage),
									  ('/visit/read', ReadArticlePage),
									  ('/visit/members', SeeCommunityMembersPage),
									  ('/visit/member', SeeMemberPage),
									  ('/visit/character', SeeCharacterPage),
									  ('/visit/community', SeeCommunityPage),
									  ('/visit/new', NewMemberPage),
									  ('/visit/profile', ChangeMemberProfilePage),
									  
									  # entering articles
									  ('/visit/story', EnterArticlePage),
									  ('/visit/retell', EnterArticlePage),
									  ('/visit/remind', EnterArticlePage),
									  ('/visit/respond', EnterArticlePage),
									  ('/visit/pattern', EnterArticlePage),
									  ('/visit/collage', EnterArticlePage),
									  ('/visit/invitation', EnterArticlePage),
									  ('/visit/resource', EnterArticlePage),
									  ('/visit/article', EnterArticlePage),
									  
									  # answering questions
									  ('/visit/answers', AnswerQuestionsAboutArticlePage),
									  ('/visit/preview', PreviewPage),
									  ('/visit/previewAnswers', PreviewPage),
									  
									  # entering annotations
									  ('/visit/request', EnterAnnotationPage),
									  ('/visit/tagset', EnterAnnotationPage),
									  ('/visit/comment', EnterAnnotationPage),
									  ('/visit/nudge', EnterAnnotationPage),
									  ('/visit/annotation', EnterAnnotationPage),
									  
									  # managing
									  ('/createCommunity', CreateCommunityPage),
									  ('/manage/members', ManageCommunityMembersPage),
									  ('/manage/settings', ManageCommunitySettingsPage),
									  ('/manage/questions/story', ManageCommunityQuestionsPage),
									  ('/manage/questions/pattern', ManageCommunityQuestionsPage),
									  ('/manage/questions/collage', ManageCommunityQuestionsPage),
									  ('/manage/questions/invitation', ManageCommunityQuestionsPage),
									  ('/manage/questions/resource', ManageCommunityQuestionsPage),
									  ('/manage/questions/member', ManageCommunityQuestionsPage),
									  ('/manage/questions/questions', ManageCommunityQuestionsPage),
									  ('/manage/characters', ManageCommunityCharactersPage),
									  ('/manage/technical', ManageCommunityTechnicalPage),
									  
									  # file handlers
									  ('/img', ImageHandler),
									  ('/visit/img', ImageHandler),
									  ('/manage/img', ImageHandler),
									  ('/visit/attachment', AttachmentHandler),
									  
									  # site admin
									  ('/admin/showAllCommunities', ShowAllCommunities),
									  ('/admin/showAllMembers', ShowAllMembers)],
									 debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	systemquestions.AddSystemQuestionsToDataStore()
	main()
