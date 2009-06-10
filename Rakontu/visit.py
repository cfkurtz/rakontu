# --------------------------------------------------------------------------------------------
# RAKONTU
# Description: Rakontu is open source story sharing software.
# Version: pre-0.1
# License: GPL 3.0
# Google Code Project: http://code.google.com/p/rakontu/
# --------------------------------------------------------------------------------------------

from utils import *

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
						   'title': None,
						   'title_extra': None,
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
							newMember.initialize()
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
		elif "generateSystemQuestions" in self.request.arguments():
			GenerateSystemQuestions()
			self.redirect("/")
		elif "generateHelps" in self.request.arguments():
			GenerateHelps()
			self.redirect("/")
			
class NewMemberPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		community, member = GetCurrentCommunityAndMemberFromSession()
		if community and member:
			template_values = {
							'title': "Welcome",
							'title_extra': member.nickname,
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
				numRows = 25
				numCols = member.viewNumTimeColumns
				nudgeStep = max(1, (maxNudgePoints - minNudgePoints) // numRows)
				timeStep = (maxTime - minTime) // numCols
				
				textsForGrid = []
				rowHeaders = []
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
							rowHeaders.append(RelativeTimeDisplayString(startTime, member))
						for article in articles:
							shouldBeInRow = article.nudgePointsCombined() >= startNudgePoints and article.nudgePointsCombined() < endNudgePoints
							if article.lastAnnotatedOrAnsweredOrLinked:
								timeToCheck = article.lastAnnotatedOrAnsweredOrLinked
							else:
								timeToCheck = article.published
							shouldBeInCol = timeToCheck >= startTime and timeToCheck < endTime
							if shouldBeInRow and shouldBeInCol:
								fontSizePercent = min(200, 90 + article.activityPoints - minActivityPoints)
								if article.attributedToMember():
									if article.creator.active:
										nameString = '<a href="member?%s">%s</a>' % (article.creator.key(), article.creator.nickname)
									else:
										nameString = article.creator.nickname
								else:
									nameString = '<a href="character?%s">%s</a>' % (article.character.key(), article.character.name)
								text = '<p>%s <span style="font-size:%s%%"><a href="/visit/read?%s">%s</a> (%s)</span></p>' % \
									(article.getImageLinkForType(), fontSizePercent, article.key(), article.title, nameString)
								textsInThisCell.append(text)
						textsInThisRow.append(textsInThisCell)
					textsForGrid.append(textsInThisRow)
				textsForGrid.reverse()
			else:
				textsForGrid = []
			template_values = {
							'title': community.name,
						   	'title_extra': None,
							'community': community, 
							'current_member': member, 
							'articles': articles, 
							'rows_cols': textsForGrid, 
							'row_headers': rowHeaders, 
							'time_frames': TIME_FRAMES, 
							'article_types': ARTICLE_TYPES, 
							'1_to_31': range(1, 31, 1), 
							'3_to_10': range(3, 11, 1), 
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
						member.viewTimeEnd = community.lastPublish + timedelta(seconds=10)
					else:
						member.viewTimeEnd = datetime.now(tz=pytz.utc)
				elif "setToFirst" in self.request.arguments():
					if community.firstPublish:
						member.setTimeFrameToStartAtFirstPublish()
					else:
						member.viewTimeEnd = datetime.now(tz=pytz.utc)
				elif "moveTimeBack" in self.request.arguments() or "moveTimeForward" in self.request.arguments():
					changeSeconds = member.viewTimeFrameInSeconds * member.viewNumTimeFrames
					if "moveTimeBack" in self.request.arguments():
						member.viewTimeEnd = member.viewTimeEnd - timedelta(seconds=changeSeconds)
					else:
						member.viewTimeEnd = member.viewTimeEnd + timedelta(seconds=changeSeconds)
				if community.firstPublish and member.getViewStartTime() < community.firstPublish:
				 	member.setTimeFrameToStartAtFirstPublish()
				if member.viewTimeEnd > datetime.now(tz=pytz.utc):
					member.viewTimeEnd = datetime.now(tz=pytz.utc)
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
				curating = self.request.uri.find("curate") >= 0
				allItems = []
				allItems.extend(article.getNonDraftAnnotations())
				allItems.extend(article.getNonDraftAnswers())
				allItems.extend(article.getAllLinks())
				haveContent = False
				if allItems:
					maxTime = article.lastAnnotatedOrAnsweredOrLinked
					minTime = article.published
					maxNudgePoints = -9999999
					minNudgePoints = -9999999
					minActivityPoints = -9999999
					maxActivityPoints = -9999999
					for item in allItems:
						nudgePoints = 0
						for i in range(5):
							nudgePoints += item.articleNudgePointsWhenPublished[i]
						if minNudgePoints == -9999999:
							minNudgePoints = nudgePoints
						elif nudgePoints < minNudgePoints:
							minNudgePoints = nudgePoints
						if maxNudgePoints == -9999999:
							maxNudgePoints = nudgePoints
						elif nudgePoints > maxNudgePoints:
							maxNudgePoints = nudgePoints
						activityPoints = item.articleActivityPointsWhenPublished
						if minActivityPoints == -9999999:
							minActivityPoints = activityPoints
						elif activityPoints < minActivityPoints:
							minActivityPoints = activityPoints
						if maxActivityPoints == -9999999:
							maxActivityPoints = activityPoints
						elif activityPoints > maxActivityPoints:
							maxActivityPoints = activityPoints
					numRows = 20
					numCols = 6
					nudgeStep = max(1, (maxNudgePoints - minNudgePoints) // numRows)
					timeStep = (maxTime - minTime) // numCols
					
					textsForGrid = []
					rowHeaders = []
					haveContent = False
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
								rowHeaders.append(RelativeTimeDisplayString(startTime, member))
							for item in allItems:
								nudgePoints = 0
								for i in range(5):
									nudgePoints += item.articleNudgePointsWhenPublished[i]
								shouldBeInRow = nudgePoints >= startNudgePoints and nudgePoints < endNudgePoints
								shouldBeInCol = item.published >= startTime and item.published < endTime
								if shouldBeInRow and shouldBeInCol:
									fontSizePercent = min(200, 90 + item.articleActivityPointsWhenPublished - minActivityPoints)
									timeLoss = (item.published - article.published).seconds // 60
									fontSizePercent -= timeLoss
									if item.attributedToMember():
										if item.creator.active:
											nameString = '<a href="member?%s">%s</a>' % (item.creator.key(), item.creator.nickname)
										else:
											nameString = item.creator.nickname
									else:
										nameString = '<a href="character?%s">%s</a>' % (item.character.key(), item.character.name)
									if curating:
										if item.flaggedForRemoval:
											curateString = '<a href="flag?%s" class="imagelight"><img src="../images/flag_red.png" alt="flag" border="0"></a>' % item.key()
										else:
											curateString = '<a href="flag?%s" class="imagelight"><img src="../images/flag_green.png" alt="flag" border="0"></a>' % item.key()
									else:
										curateString = ""
									text = '<p>%s %s (%s) %s</p>' % (item.getImageLinkForType(), item.linkString(), nameString, curateString)
									textsInThisCell.append(text)
							haveContent = haveContent or len(textsInThisCell) > 0
							textsInThisRow.append(textsInThisCell)
						textsForGrid.append(textsInThisRow)
					textsForGrid.reverse()
				else:
					textsForGrid = None
					rowHeaders = None
				if not haveContent:
					textsForGrid = None
				if not article.memberCanNudge(member):
					nudgePointsMemberCanAssign = 0
				else:
					nudgePointsMemberCanAssign = max(0, community.maxNudgePointsPerArticle - article.getTotalNudgePointsForMember(member))
				communityHasQuestionsForThisArticleType = len(community.getQuestionsOfType(article.type)) > 0
				memberCanAnswerQuestionsAboutThisArticle = len(article.getAnswersForMember(member)) == 0
				memberCanAddNudgeToThisArticle = nudgePointsMemberCanAssign > 0
				thingsUserCanDo = {}
				if article.isStory():
					thingsUserCanDo["Tell another version of what happened"] = "retell?%s" % article.key()
				if article.isStory() or article.isResource():
					thingsUserCanDo["Tell a story this %s reminds me of" % article.type] = "remind?%s" % article.key()
				if communityHasQuestionsForThisArticleType and memberCanAnswerQuestionsAboutThisArticle:
					thingsUserCanDo["Answer questions about this %s" % article.type] = "answers?%s" % article.key()
				if article.isInvitation():
					thingsUserCanDo["Respond to this invitation with a story"] = "respond?%s" % article.key()
				thingsUserCanDo["Add a comment about this %s" % article.type] = "comment?%s" % article.key()
				thingsUserCanDo["Add some tags about this %s" % article.type] = "tagset?%s" % article.key()
				if memberCanAddNudgeToThisArticle:
					thingsUserCanDo["Nudge this %s up or down" % article.type] = "nudge?%s" % article.key()
				thingsUserCanDo["Make a request about this %s" % article.type] = "request?%s" % article.key()
				thingsUserCanDo["Add or remove relations to this %s" % article.type] = "relate?%s" % article.key()
				if member.isCuratorOrManagerOrOwner():
					thingsUserCanDo["Curate this %s and its annotations" % article.type] = "curate?%s" % article.key()
				template_values = {
								   'title': article.title, 
						   		   'title_extra': None,
								   'community': community, 
								   'current_member': member,
								   'current_member_key': member.key(),
								   'curating': curating,
								   'article': article,
								   'rows_cols': textsForGrid, 
							       'row_headers': rowHeaders, 
							       'things_member_can_do': thingsUserCanDo,
								   'member_can_answer_questions': memberCanAnswerQuestionsAboutThisArticle,
								   'member_can_add_nudge': memberCanAddNudgeToThisArticle,
								   'community_has_questions_for_this_article_type': communityHasQuestionsForThisArticleType,
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
								   'links_incoming_from_invitations': article.getIncomingLinksOfTypeFromType("responded", "invitation"),
								   'links_incoming_from_collages': article.getIncomingLinksOfTypeFromType("included", "collage"),
								   'included_links_outgoing': article.getOutgoingLinksOfType("included"),
								   }
				member.lastReadAnything = datetime.now(tz=pytz.utc)
				member.nudgePoints += community.getMemberNudgePointsForEvent("reading")
				member.put()
				path = os.path.join(os.path.dirname(__file__), 'templates/visit/read.html')
				self.response.out.write(template.render(path, template_values))
		else:
			self.redirect('/')
			
	@RequireLogin 
	def post(self):
		community, member = GetCurrentCommunityAndMemberFromSession()
		if community and member:
			self.redirect(self.request.get("nextAction"))
		else:
			self.redirect("/visit/look")
			
class ReadAnnotationPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		community, member = GetCurrentCommunityAndMemberFromSession()
		if community and member:
			annotation = db.get(self.request.query_string)
			if annotation:
				template_values = {
								   'title': annotation.displayString, 
						   		   'title_extra': None,
								   'community': community, 
								   'current_member': member,
								   'current_member_key': member.key(),
								   'annotation': annotation,
								   'included_links_outgoing': annotation.article.getOutgoingLinksOfType("included"),
								   'user_is_admin': users.is_current_user_admin(),
								   'logout_url': users.create_logout_url("/"),
								   }
				member.lastReadAnything = datetime.now(tz=pytz.utc)
				member.nudgePoints += community.getNudgePointsPerActivityForActivityName("reading")
				member.put()
				path = os.path.join(os.path.dirname(__file__), 'templates/visit/readAnnotation.html')
				self.response.out.write(template.render(path, template_values))
		else:
			self.redirect('/')

class SeeCommunityPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		community, member = GetCurrentCommunityAndMemberFromSession()
		if community and member:
				template_values = {
								   'title': "About", 
						   		   'title_extra': community.name, 
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
								   'title': "Members of", 
						   		   'title_extra': community.name, 
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
								   'title': "Member", 
						   		   'title_extra': member.nickname, 
						   		   'community': community, 
						   		   'current_member': member,
						   		   'member': memberToSee,
						   		   'articles': memberToSee.getNonDraftArticlesAttributedToMember(),
						   		   'annotations': memberToSee.getNonDraftAnnotationsAttributedToMember(),
						   		   'answers': memberToSee.getNonDraftAnswersAboutArticlesAttributedToMember(),
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
				message.sender = community.contactEmail
				message.subject = cgi.escape(self.request.get("subject"))
				message.to = messageMember.googleAccountEmail
				message.body = cgi.escape(self.request.get("message"))
				message.send()
   
class SeeCharacterPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		community, member = GetCurrentCommunityAndMemberFromSession()
		if community and member:
				characterKey = self.request.query_string
				character = db.get(characterKey)
				if character:
					template_values = {
								   	   'title': "Character", 
						   		   	   'title_extra': character.name, 
									   'community': community, 
									   'current_member': member,
									   'character': character,
									   'user_is_admin': users.is_current_user_admin(),
									   'logout_url': users.create_logout_url("/"),								   
									   }
					path = os.path.join(os.path.dirname(__file__), 'templates/visit/character.html')
					self.response.out.write(template.render(path, template_values))
				else:
					self.redirect('/visit/look')
		else:
			self.redirect('/')
