# --------------------------------------------------------------------------------------------
# RAKONTU
# Description: Rakontu is open source story sharing software.
# Version: pre-0.1
# License: GPL 3.0
# Google Code Project: http://code.google.com/p/rakontu/
# --------------------------------------------------------------------------------------------

from utils import *

def ItemDisplayStringForGrid(item, curating, includeName=True):
	if includeName:
		if item.attributedToMember():
			if item.creator.isOnlineMember:
				if item.creator.active:
					nameString = ' (<a href="member?%s">%s</a>)' % (item.creator.key(), item.creator.nickname)
				else:
					nameString = ' (%s)' % item.creator.nickname
			else:
				if item.creator.active:
					nameString = ' (<img src="/images/offline.png" alt="offline member"><a href="member?%s">%s</a>)' % (item.creator.key(), item.creator.nickname)
				else:
					nameString = ' (<img src="/images/offline.png" alt="offline member"> %s)' % item.creator.nickname
		else:
			if item.character.active:
				nameString = ' (<a href="character?%s">%s</a>)' % (item.character.key(), item.character.name)
			else:
				nameString = ' (%s)' % item.character.name
	else:
		nameString = ""
	if curating:
		if item.flaggedForRemoval:
			curateString = '<a href="flag?%s" class="imagelight"><img src="../images/flag_red.png" alt="flag" border="0"></a>' % item.key()
		else:
			curateString = '<a href="flag?%s" class="imagelight"><img src="../images/flag_green.png" alt="flag" border="0"></a>' % item.key()
	else:
		curateString = ""
	return '<p>%s %s %s%s</p>' % (item.getImageLinkForType(), curateString, item.linkString(), nameString)

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
		template_values = GetStandardTemplateDictionaryAndAddMore({
						   'title': None,
						   'title_extra': None,
						   'user': user, 
						   'communities_member_of': communitiesTheyAreAMemberOf,
						   'communities_invited_to': communitiesTheyAreInvitedTo,
						   'DEVELOPMENT': DEVELOPMENT,
						   'login_url': users.create_login_url("/"),
						   'logout_url': users.create_logout_url("/"),
						   })
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
			template_values = GetStandardTemplateDictionaryAndAddMore({
							'title': "Welcome",
							'title_extra': member.nickname,
							'community': community, 
							'current_member': member,
							})
			path = os.path.join(os.path.dirname(__file__), 'templates/visit/new.html')
			self.response.out.write(template.render(path, template_values))
		else:
			self.redirect('/')
			
class BrowseEntriesPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		community, member = GetCurrentCommunityAndMemberFromSession()
		if community and member:
			entries = community.getNonDraftEntries()
			if entries:
				maxTime = member.viewTimeEnd
				minTime = member.getViewStartTime()
				maxNudgePoints = -9999999
				minNudgePoints = -9999999
				minActivityPoints = -9999999
				maxActivityPoints = -9999999
				for entry in entries:
					nudgePoints = entry.nudgePointsCombined()
					if minNudgePoints == -9999999:
						minNudgePoints = nudgePoints
					elif nudgePoints < minNudgePoints:
						minNudgePoints = nudgePoints
					if maxNudgePoints == -9999999:
						maxNudgePoints = nudgePoints
					elif nudgePoints > maxNudgePoints:
						maxNudgePoints = nudgePoints
					activityPoints = entry.activityPoints
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
						for entry in entries:
							shouldBeInRow = entry.nudgePointsCombined() >= startNudgePoints and entry.nudgePointsCombined() < endNudgePoints
							if entry.lastAnnotatedOrAnsweredOrLinked:
								timeToCheck = entry.lastAnnotatedOrAnsweredOrLinked
							else:
								timeToCheck = entry.published
							shouldBeInCol = timeToCheck >= startTime and timeToCheck < endTime
							if shouldBeInRow and shouldBeInCol:
								fontSizePercent = min(200, 90 + entry.activityPoints - minActivityPoints)
								if entry.attributedToMember():
									if entry.creator.active:
										nameString = '<a href="member?%s">%s</a>' % (entry.creator.key(), entry.creator.nickname)
									else:
										nameString = entry.creator.nickname
								else:
									if entry.character.active:
										nameString = '<a href="character?%s">%s</a>' % (entry.character.key(), entry.character.name)
									else:
										nameString = entry.character.name
								text = '<p>%s <span style="font-size:%s%%"><a href="/visit/read?%s" %s>%s</a></span> (%s)</p>' % \
									(entry.getImageLinkForType(), fontSizePercent, entry.key(), entry.getTooltipText(), entry.title, nameString)
								textsInThisCell.append(text)
						textsInThisRow.append(textsInThisCell)
					textsForGrid.append(textsInThisRow)
				textsForGrid.reverse()
			else:
				textsForGrid = []
			template_values = GetStandardTemplateDictionaryAndAddMore({
							'title': "Main page",
						   	'title_extra': None,
							'community': community, 
							'current_member': member, 
							'entries': entries, 
							'rows_cols': textsForGrid, 
							'row_headers': rowHeaders, 
							'1_to_31': range(1, 31, 1), 
							'3_to_10': range(3, 11, 1), 
							})
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
			
class ReadEntryPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		community, member = GetCurrentCommunityAndMemberFromSession()
		if community and member:
			entry = db.get(self.request.query_string)
			if entry:
				curating = self.request.uri.find("curate") >= 0
				allItems = []
				allItems.extend(entry.getNonDraftAnnotations())
				allItems.extend(entry.getNonDraftAnswers())
				allItems.extend(entry.getAllLinks())
				haveContent = False
				if allItems:
					maxTime = entry.lastAnnotatedOrAnsweredOrLinked
					minTime = entry.published
					maxNudgePoints = -9999999
					minNudgePoints = -9999999
					minActivityPoints = -9999999
					maxActivityPoints = -9999999
					for item in allItems:
						nudgePoints = 0
						for i in range(NUM_NUDGE_CATEGORIES):
							nudgePoints += item.entryNudgePointsWhenPublished[i]
						if minNudgePoints == -9999999:
							minNudgePoints = nudgePoints
						elif nudgePoints < minNudgePoints:
							minNudgePoints = nudgePoints
						if maxNudgePoints == -9999999:
							maxNudgePoints = nudgePoints
						elif nudgePoints > maxNudgePoints:
							maxNudgePoints = nudgePoints
						activityPoints = item.entryActivityPointsWhenPublished
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
								for i in range(NUM_NUDGE_CATEGORIES):
									nudgePoints += item.entryNudgePointsWhenPublished[i]
								shouldBeInRow = nudgePoints >= startNudgePoints and nudgePoints < endNudgePoints
								shouldBeInCol = item.published >= startTime and item.published < endTime
								if shouldBeInRow and shouldBeInCol:
									text = ItemDisplayStringForGrid(item, curating)
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
				if not entry.memberCanNudge(member):
					nudgePointsMemberCanAssign = 0
				else:
					nudgePointsMemberCanAssign = max(0, community.maxNudgePointsPerEntry - entry.getTotalNudgePointsForMember(member))
				communityHasQuestionsForThisEntryType = len(community.getQuestionsOfType(entry.type)) > 0
				memberCanAnswerQuestionsAboutThisEntry = len(entry.getAnswersForMember(member)) == 0
				memberCanAddNudgeToThisEntry = nudgePointsMemberCanAssign > 0
				thingsUserCanDo = {}
				if entry.isStory():
					thingsUserCanDo["Tell another version of what happened"] = "retell?%s" % entry.key()
				if entry.isStory() or entry.isResource():
					thingsUserCanDo["Tell a story this %s reminds me of" % entry.type] = "remind?%s" % entry.key()
				if communityHasQuestionsForThisEntryType and memberCanAnswerQuestionsAboutThisEntry:
					thingsUserCanDo["Answer questions about this %s" % entry.type] = "answers?%s" % entry.key()
				if communityHasQuestionsForThisEntryType and member.isLiaison():
					thingsUserCanDo["Enter answers about this %s for an off-line member" % entry.type] = "answers?%s" % entry.key()
				if entry.isInvitation():
					thingsUserCanDo["Respond to this invitation with a story"] = "respond?%s" % entry.key()
				thingsUserCanDo["Comment on this %s" % entry.type] = "comment?%s" % entry.key()
				thingsUserCanDo["Tag this %s" % entry.type] = "tagset?%s" % entry.key()
				if memberCanAddNudgeToThisEntry:
					thingsUserCanDo["Nudge this %s up or down" % entry.type] = "nudge?%s" % entry.key()
				thingsUserCanDo["Request something about this %s" % entry.type] = "request?%s" % entry.key()
				thingsUserCanDo["Relate this %s to others" % entry.type] = "relate?%s" % entry.key()
				if member.isCurator():
					thingsUserCanDo["Curate this %s" % entry.type] = "curate?%s" % entry.key()
				if entry.creator.key() == member.key() and community.allowsPostPublishEditOfEntryType(entry.type):
					thingsUserCanDo["Change this %s" % entry.type] = "%s?%s" % (entry.type, entry.key())
				template_values = GetStandardTemplateDictionaryAndAddMore({
								   'title': entry.title, 
						   		   'title_extra': None,
								   'community': community, 
								   'current_member': member,
								   'current_member_key': member.key(),
								   'curating': curating,
								   'entry': entry,
								   'rows_cols': textsForGrid, 
							       'row_headers': rowHeaders, 
							       'text_to_display_before_grid': "Annotations to this %s" % entry.type,
							       'things_member_can_do': thingsUserCanDo,
								   'member_can_answer_questions': memberCanAnswerQuestionsAboutThisEntry,
								   'member_can_add_nudge': memberCanAddNudgeToThisEntry,
								   'community_has_questions_for_this_entry_type': communityHasQuestionsForThisEntryType,
								   'answers': entry.getNonDraftAnswers(),
								   'questions': community.getQuestionsOfType(entry.type),
								   'attachments': entry.getAttachments(),
								   'requests': entry.getNonDraftAnnotationsOfType("request"),
								   'comments': entry.getNonDraftAnnotationsOfType("comment"),
								   'tag_sets': entry.getNonDraftAnnotationsOfType("tag set"),
								   'nudges': entry.getNonDraftAnnotationsOfType("nudge"),
								   'retold_links_incoming': entry.getIncomingLinksOfType("retold"),
								   'retold_links_outgoing': entry.getOutgoingLinksOfType("retold"),
								   'reminded_links_incoming': entry.getIncomingLinksOfType("reminded"),
								   'reminded_links_outgoing': entry.getOutgoingLinksOfType("reminded"),
								   'related_links': entry.getLinksOfType("related"),
								   'links_incoming_from_invitations': entry.getIncomingLinksOfTypeFromType("responded", "invitation"),
								   'links_incoming_from_collages': entry.getIncomingLinksOfTypeFromType("included", "collage"),
								   'included_links_outgoing': entry.getOutgoingLinksOfType("included"),
								   })
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
				template_values = GetStandardTemplateDictionaryAndAddMore({
								   'title': annotation.displayString, 
						   		   'title_extra': None,
								   'community': community, 
								   'current_member': member,
								   'current_member_key': member.key(),
								   'annotation': annotation,
								   'included_links_outgoing': annotation.entry.getOutgoingLinksOfType("included"),
								   })
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
				template_values = GetStandardTemplateDictionaryAndAddMore({
								   'title': "About", 
						   		   'title_extra': community.name, 
								   'community': community, 
								   'current_member': member,
								   'community_members': community.getActiveMembers(),
								   'characters': community.getActiveCharacters(),
								   })
				path = os.path.join(os.path.dirname(__file__), 'templates/visit/community.html')
				self.response.out.write(template.render(path, template_values))
		else:
			self.redirect('/')
			
class SeeCommunityMembersPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		community, member = GetCurrentCommunityAndMemberFromSession()
		if community and member:
				template_values = GetStandardTemplateDictionaryAndAddMore({
								   'title': "Members of", 
						   		   'title_extra': community.name, 
								   'community': community, 
								   'current_member': member,
								   'community_members': community.getActiveMembers(),
								   })
				path = os.path.join(os.path.dirname(__file__), 'templates/visit/members.html')
				self.response.out.write(template.render(path, template_values))
		else:
			self.redirect('/')
   
class SeeMemberPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		community, member = GetCurrentCommunityAndMemberFromSession()
		if community and member:
				keyAndCurate = self.request.query_string.split("&")
				memberKey = keyAndCurate[0]
				memberToSee = db.get(memberKey)
				if memberToSee:
					curating = member.isCurator() and len(keyAndCurate) > 1 and keyAndCurate[1] == "curate"
					allItems = memberToSee.getAllItemsAttributedToMember()
					allItems.extend(memberToSee.getNonDraftLiaisonedEntries())
					allItems.extend(memberToSee.getNonDraftLiaisonedAnnotations())
					allItems.extend(memberToSee.getNonDraftLiaisonedAnswers())
					if allItems:
						maxTime = datetime.now(tz=pytz.utc)
						minTime = memberToSee.joined
						numRows = 1
						numCols = 6
						timeStep = (maxTime - minTime) // numCols
						textsForGrid = []
						rowHeaders = []
						for row in range(numRows):
							textsInThisRow = []
							for col in range(numCols):
								textsInThisCell = []
								startTime = minTime + timeStep * col
								endTime = minTime + timeStep * (col+1)
								if row == numRows - 1:
									rowHeaders.append(RelativeTimeDisplayString(startTime, member))
								for item in allItems:
									shouldBeInRow = True
									shouldBeInCol = item.published >= startTime and item.published < endTime
									if shouldBeInRow and shouldBeInCol:
										text = ItemDisplayStringForGrid(item, curating, includeName=memberToSee.isLiaison())
										textsInThisCell.append(text)
								textsInThisRow.append(textsInThisCell)
							textsForGrid.append(textsInThisRow)
						textsForGrid.reverse()
					else:
						textsForGrid = None
						rowHeaders = None
					template_values = GetStandardTemplateDictionaryAndAddMore({
								   'title': "Member", 
						   		   'title_extra': member.nickname, 
						   		   'community': community, 
						   		   'current_member': member,
						   		   'member': memberToSee,
						   		   'answers': memberToSee.getAnswers(),
						   		   'rows_cols': textsForGrid,
						   		   'row_headers': rowHeaders,
						   		   'text_to_display_before_grid': "%s's entries" % memberToSee.nickname,
						   		   'no_profile_text': NO_PROFILE_TEXT,
						   		   })
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
				keyAndCurate = self.request.query_string.split("&")
				characterKey = keyAndCurate[0]
				character = db.get(characterKey)
				if character:
					curating = member.isCurator() and len(keyAndCurate) > 1 and keyAndCurate[1] == "curate"
					allItems = character.getAllItemsAttributedToCharacter()
					if allItems:
						maxTime = datetime.now(tz=pytz.utc)
						minTime = character.created
						numRows = 1
						numCols = 6
						timeStep = (maxTime - minTime) // numCols
						textsForGrid = []
						rowHeaders = []
						for row in range(numRows):
							textsInThisRow = []
							for col in range(numCols):
								textsInThisCell = []
								startTime = minTime + timeStep * col
								endTime = minTime + timeStep * (col+1)
								if row == numRows - 1:
									rowHeaders.append(RelativeTimeDisplayString(startTime, member))
								for item in allItems:
									shouldBeInRow = True
									shouldBeInCol = item.published >= startTime and item.published < endTime
									if shouldBeInRow and shouldBeInCol:
										text = ItemDisplayStringForGrid(item, curating, includeName=False)
										textsInThisCell.append(text)
								textsInThisRow.append(textsInThisCell)
							textsForGrid.append(textsInThisRow)
						textsForGrid.reverse()
					else:
						textsForGrid = None
						rowHeaders = None
					DebugPrint(character.getAnswers())
					template_values = GetStandardTemplateDictionaryAndAddMore({
								   	   'title': "Character", 
						   		   	   'title_extra': character.name, 
									   'community': community, 
									   'current_member': member,
									   'character': character,
									   'answers': character.getAnswers(),
						   		   	   'rows_cols': textsForGrid,
						   		   	   'text_to_display_before_grid': "%s's entries" % character.name,
						   		   	   'row_headers': rowHeaders,
									   })
					path = os.path.join(os.path.dirname(__file__), 'templates/visit/character.html')
					self.response.out.write(template.render(path, template_values))
				else:
					self.redirect('/visit/look')
		else:
			self.redirect('/')

class ChangeMemberProfilePage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		community, member = GetCurrentCommunityAndMemberFromSession()
		if community and member:
			try:
				offlineMember = db.get(self.request.query_string)
			except:
				offlineMember = None
			if offlineMember:
				memberToEdit = offlineMember
			else:
				memberToEdit = member
			draftAnswerEntries = memberToEdit.getEntriesWithDraftAnswers()
			firstDraftAnswerForEachEntry = []
			for entry in draftAnswerEntries:
				answers = memberToEdit.getDraftAnswersForEntry(entry)
				firstDraftAnswerForEachEntry.append(answers[0])
			template_values = GetStandardTemplateDictionaryAndAddMore({
							   'title': "Profile of", 
						   	   'title_extra': member.nickname, 
							   'community': community, 
							   'member': memberToEdit,
							   'current_member': member,
							   'questions': community.getMemberQuestions(),
							   'answers': memberToEdit.getAnswers(),
							   'draft_entries': memberToEdit.getDraftEntries(),
							   'draft_annotations': memberToEdit.getDraftAnnotations(),
							   'first_draft_answer_per_entry': firstDraftAnswerForEachEntry,
							   'refer_type': "member",
							   })
			path = os.path.join(os.path.dirname(__file__), 'templates/visit/profile.html')
			self.response.out.write(template.render(path, template_values))
		else:
			self.redirect('/')
							 
	@RequireLogin 
	def post(self):
		community, member = GetCurrentCommunityAndMemberFromSession()
		if community and member:
			goAhead = True
			offlineMember = None
			for argument in self.request.arguments():
				if argument.find("|") >= 0:
					for aMember in community.getActiveOfflineMembers():
						if argument == "changeSettings|%s" % aMember.key():
							try:
								offlineMember = aMember
							except: 
								offlineMember = None
								goAhead = False
							break
			if goAhead:
				if offlineMember:
					memberToEdit = offlineMember
				else:
					memberToEdit = member
				memberToEdit.nickname = cgi.escape(self.request.get("nickname")).strip()
				memberToEdit.nicknameIsRealName = self.request.get('nickname_is_real_name') =="yes"
				memberToEdit.acceptsMessages = self.request.get("acceptsMessages") == "yes"
				text = self.request.get("profileText")
				format = self.request.get("profileText_format").strip()
				memberToEdit.profileText = text
				memberToEdit.profileText_formatted = db.Text(InterpretEnteredText(text, format))
				memberToEdit.profileText_format = format
				if self.request.get("removeProfileImage") == "yes":
					memberToEdit.profileImage = None
				elif self.request.get("img"):
					memberToEdit.profileImage = db.Blob(images.resize(str(self.request.get("img")), 100, 60))
				memberToEdit.timeZoneName = self.request.get("timeZoneName")
				memberToEdit.dateFormat = self.request.get("dateFormat")
				memberToEdit.timeFormat = self.request.get("timeFormat")
				if memberToEdit.isOnlineMember:
					for i in range(3):
						memberToEdit.helpingRoles[i] = self.request.get("helpingRole%s" % i) == "helpingRole%s" % i
					text = self.request.get("guideIntro")
					format = self.request.get("guideIntro_format").strip()
					memberToEdit.guideIntro = text
					memberToEdit.guideIntro_formatted = db.Text(InterpretEnteredText(text, format))
					memberToEdit.guideIntro_format = format
				memberToEdit.put()
				for entry in memberToEdit.getDraftEntries():
					if self.request.get("remove|%s" % entry.key()) == "yes":
						db.delete(entry)
				for annotation in memberToEdit.getDraftAnnotations():
					if self.request.get("remove|%s" % annotation.key()) == "yes":
						db.delete(annotation)
				for entry in memberToEdit.getEntriesWithDraftAnswers():
					if self.request.get("removeAnswers|%s" % entry.key()) == "yes":
						answers = memberToEdit.getDraftAnswersForEntry(entry)
						for answer in answers:
							db.delete(answer)
				questions = Question.all().filter("community = ", community).filter("refersTo = ", "member").fetch(FETCH_NUMBER)
				for question in questions:
					foundAnswers = Answer.all().filter("question = ", question.key()).filter("referent =", memberToEdit.key()).fetch(FETCH_NUMBER)
					if foundAnswers:
						answerToEdit = foundAnswers[0]
					else:
						answerToEdit = Answer(question=question, community=community, referent=memberToEdit, referentType="member")
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
					answerToEdit.creator = memberToEdit
					answerToEdit.put()
				if offlineMember:
					self.redirect('/liaise/members')
				else:
					self.redirect('/visit/member?%s' % memberToEdit.key())
			else:
				self.redirect("/visit/look")
		else:
			self.redirect("/")
		
class ResultFeedbackPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		community, member = GetCurrentCommunityAndMemberFromSession()
		if community and member:
			template_values = GetStandardTemplateDictionaryAndAddMore({
						   	   'title': "Message", 
					   	   	   'title_extra': None, 
							   'community': community, 
							   'message': self.request.query_string,
							   "linkback": self.request.headers["Referer"],
							   'current_member': member,
							   })
			path = os.path.join(os.path.dirname(__file__), 'templates/result.html')
			self.response.out.write(template.render(path, template_values))
		else:
			self.redirect("/")
				
