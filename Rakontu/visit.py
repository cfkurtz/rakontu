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
		rakontusTheyAreAMemberOf = []
		rakontusTheyAreInvitedTo = []
		if user:
			members = Member.all().filter("googleAccountID = ", user.user_id()).fetch(FETCH_NUMBER)
			for member in members:
				try:
					if member.active:
						rakontusTheyAreAMemberOf.append(member.rakontu)
				except:
					pass # if can't link to rakontu don't use it
			pendingMembers = PendingMember.all().filter("email = ", user.email()).fetch(FETCH_NUMBER)
			for pendingMember in pendingMembers:
				try:
					rakontusTheyAreInvitedTo.append(pendingMember.rakontu)
				except:
					pass # if can't link to rakontu don't use it
		template_values = GetStandardTemplateDictionaryAndAddMore({
						   'title': None,
						   'title_extra': None,
						   'user': user, 
						   'rakontus_member_of': rakontusTheyAreAMemberOf,
						   'rakontus_invited_to': rakontusTheyAreInvitedTo,
						   'DEVELOPMENT': DEVELOPMENT,
						   'login_url': users.create_login_url("/"),
						   'logout_url': users.create_logout_url("/"),
						   })
		path = os.path.join(os.path.dirname(__file__), 'templates/start.html')
		self.response.out.write(template.render(path, template_values))

	def post(self):
		user = users.get_current_user()
		if not users.is_current_user_admin():
			password = self.request.get("entryPassword")
			if not password == "testingRakontu":
				self.redirect("/")
				return
		if "visitRakontu" in self.request.arguments():
			rakontu_key = self.request.get('rakontu_key')
			if rakontu_key:
				rakontu = db.get(rakontu_key) 
				if rakontu:
					session = Session()
					session['rakontu_key'] = rakontu_key
					matchingMember = Member.all().filter("rakontu = ", rakontu).filter("googleAccountID = ", user.user_id()).get()
					if matchingMember:
						session['member_key'] = matchingMember.key()
						matchingMember.viewSearchResultList = []
						matchingMember.put()
						if matchingMember.active:
							if not rakontu.firstVisit:
								rakontu.firstVisit = datetime.now(tz=pytz.utc)
								rakontu.put()
								self.redirect('/manage/first')
							else:
								self.redirect('/visit/home')
						else:
							matchingMember.active = True
							matchingMember.put()
							pendingMember = PendingMember.all().filter("rakontu = ", rakontu.key()).filter("email = ", user.email()).get()
							if pendingMember:
								db.delete(pendingMember)
							self.redirect("/visit/new")
					else:
						pendingMember = PendingMember.all().filter("rakontu = ", rakontu.key()).filter("email = ", user.email()).get()
						if pendingMember:
							newMember = Member(
								nickname=user.email(),
								googleAccountID=user.user_id(),
								googleAccountEmail=user.email(),
								rakontu=rakontu,
								active=True,
								governanceType="member")
							newMember.initialize()
							newMember.put()
							db.delete(pendingMember)
							session['member_key'] = newMember.key()
							self.redirect("/visit/new")
						else:
							self.redirect('/')
				else:
					self.redirect('/')
			else:
				self.redirect('/')
		elif "createRakontu" in self.request.arguments():
			self.redirect("/create")
		elif "reviewAllRakontus" in self.request.arguments():
			self.redirect("/admin/rakontus")
		elif "makeFakeData" in self.request.arguments():
			MakeSomeFakeData()
			self.redirect("/")
		elif "generateSystemQuestions" in self.request.arguments():
			GenerateSampleQuestions()
			self.redirect("/")
		elif "generateSystemResources" in self.request.arguments():
			GenerateSystemResources()
			self.redirect("/")
		elif "generateHelps" in self.request.arguments():
			GenerateHelps()
			self.redirect("/")
			
class NewMemberPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		rakontu, member, access = GetCurrentRakontuAndMemberFromSession()
		if access:
			template_values = GetStandardTemplateDictionaryAndAddMore({
							'title': "Welcome",
							'title_extra': member.nickname,
							'rakontu': rakontu, 
							'current_member': member,
							'resources': rakontu.getNonDraftNewMemberResources(),
							})
			path = os.path.join(os.path.dirname(__file__), 'templates/visit/new.html')
			self.response.out.write(template.render(path, template_values))
		else:
			self.redirect('/')
			
class GetHelpPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		rakontu, member, access = GetCurrentRakontuAndMemberFromSession()
		if access:
			if member.isManagerOrOwner():
				managerResources = rakontu.getNonDraftManagerOnlyHelpResources()
			else:
				managerResources = None
			template_values = GetStandardTemplateDictionaryAndAddMore({
							'title': "Help",
							'rakontu': rakontu, 
							'current_member': member,
							'resources': rakontu.getNonDraftHelpResources(),
							'manager_resources': managerResources,
							'guides': rakontu.getGuides(),
							})
			path = os.path.join(os.path.dirname(__file__), 'templates/visit/help.html')
			self.response.out.write(template.render(path, template_values))
		else:
			self.redirect('/')
			
class BrowseEntriesPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		rakontu, member, access = GetCurrentRakontuAndMemberFromSession()
		if access:
			currentSearch = GetCurrentSearchForMember(member)
			querySearch = None
			if self.request.query_string:
				try:
					querySearch = db.get(self.request.query_string)
				except:
					pass
			if querySearch:
				currentSearch = querySearch
				member.viewSearch = querySearch
				member.viewSearchResultList = []
				member.put()
			textsForGrid = []
			colHeaders = []
			rowColors = []
			entries = rakontu.getNonDraftEntriesInReverseTimeOrder()
			if entries:
				(textsForGrid, colHeaders, rowColors) = self.buildGrid(rakontu, member, entries, currentSearch)
			template_values = GetStandardTemplateDictionaryAndAddMore({
							'title': "Main page",
						   	'title_extra': None,
							'rakontu': rakontu, 
							'current_member': member, 
							'rows_cols': textsForGrid, 
							'col_headers': colHeaders, 
							'row_colors': rowColors,
							'has_entries': len(entries) > 0,
							'shared_searches': rakontu.getNonPrivateSavedSearches(),
							'member_searches': member.getPrivateSavedSearches(),
							'current_search': currentSearch,
							'member_time_frame_string': member.getFrameStringForViewTimeFrame(),
							})
			path = os.path.join(os.path.dirname(__file__), 'templates/visit/home.html')
			self.response.out.write(template.render(path, template_values))
		else:
			self.redirect('/')
			
	def buildGrid(self, rakontu, member, entries, currentSearch):
		if currentSearch:
			entryRefs = currentSearch.getEntryQuestionRefs()
			creatorRefs = currentSearch.getCreatorQuestionRefs()
		else:
			entryRefs = None
			creatorRefs = None
		maxTime = member.viewTimeEnd
		minTime = member.getViewStartTime()
		maxNudgePoints = -9999999
		minNudgePoints = -9999999
		minActivityPoints = -9999999
		maxActivityPoints = -9999999
		for entry in entries:
			nudgePoints = entry.nudgePointsForMemberViewOptions(member.viewNudgeCategories)
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
		numRows = BROWSE_NUM_ROWS
		numCols = BROWSE_NUM_COLS
		nudgeStep = max(1, (maxNudgePoints - minNudgePoints) // numRows)
		timeStep = (maxTime - minTime) // numCols
		
		textsForGrid = []
		colHeaders = []
		rowColors = []
		entriesThatMatchSearch = []
		entriesToShow = []
		for entry in entries:
			if currentSearch:
				if member.viewSearchResultList:
					goAhead = entry.key() in member.viewSearchResultList
				else:
					goAhead = entry.satisfiesSearchCriteria(currentSearch, entryRefs, creatorRefs)
					if goAhead:
						entriesThatMatchSearch.append(entry)
						entriesToShow.append(entry)
			else:
				entriesToShow.append(entry)
		for row in range(numRows):
			rowColors.append(HexColorStringForRowIndex(row))
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
					colHeaders.append(RelativeTimeDisplayString(startTime, member))
				for entry in entries:
					if currentSearch:
						if member.viewSearchResultList:
							goAhead = entry.key() in member.viewSearchResultList
						else:
							goAhead = entry in entriesToShow
					else:
						goAhead = True
					if goAhead:
						nudgePoints = entry.nudgePointsForMemberViewOptions(member.viewNudgeCategories)
						shouldBeInRow = nudgePoints >= startNudgePoints and nudgePoints < endNudgePoints
						if entry.lastAnnotatedOrAnsweredOrLinked:
							timeToCheck = entry.lastAnnotatedOrAnsweredOrLinked
						else:
							timeToCheck = entry.published
						shouldBeInCol = timeToCheck >= startTime and timeToCheck < endTime  
						if shouldBeInRow and shouldBeInCol:
							fontSizePercent = min(200, 90 + entry.activityPoints - minActivityPoints)
							downdrift = rakontu.getEntryActivityPointsForEvent("downdrift")
							if downdrift:
								daysSinceTouched = 1.0 * (datetime.now(tz=pytz.utc) - entry.lastTouched()).seconds / DAY_SECONDS
								timeLoss = daysSinceTouched * downdrift
								fontSizePercent += timeLoss
								fontSizePercent = int(max(MIN_BROWSE_FONT_SIZE_PERCENT, min(fontSizePercent, MAX_BROWSE_FONT_SIZE_PERCENT)))
							if member.viewDetails:
								if entry.attributedToMember():
									if entry.creator.active:
										nameString = ' (<a href="member?%s">%s</a>)' % (entry.creator.key(), entry.creator.nickname)
									else:
										nameString = " (%s)" % entry.creator.nickname
								else:
									if entry.character.active:
										nameString = ' (<a href="character?%s">%s</a>)' % (entry.character.key(), entry.character.name)
									else:
										nameString = " (%s)" % entry.character.name
								if entry.text_formatted:
									textString = ": %s" % upToWithLink(stripTags(entry.text_formatted), DEFAULT_DETAILS_TEXT_LENGTH, '/visit/read?%s' % entry.key())
								else:
									textString = ""
							else:
								nameString = ""
								textString = ""
							text = '<p>%s <span style="font-size:%s%%"><a href="/visit/read?%s" %s>%s</a></span>%s%s</p>' % \
								(entry.getImageLinkForType(), fontSizePercent, entry.key(), entry.getTooltipText(), entry.title, nameString, textString)
							textsInThisCell.append(text)
				textsInThisRow.append(textsInThisCell)
			textsForGrid.append(textsInThisRow)
		textsForGrid.reverse()
		if entriesThatMatchSearch:
			member.viewSearchResultList = []
			for entry in entriesThatMatchSearch:
				member.viewSearchResultList.append(entry.key())
			member.put()
		return (textsForGrid, colHeaders, rowColors)
			
	@RequireLogin 
	def post(self):
		rakontu, member, access = GetCurrentRakontuAndMemberFromSession()
		if access:
			search = GetCurrentSearchForMember(member)
			if "changeNudgeCategoriesShowing" in self.request.arguments():
				member.viewNudgeCategories = []
				for i in range(NUM_NUDGE_CATEGORIES):
					member.viewNudgeCategories.append(self.request.get("showCategory|%s" % i) == "yes")
				member.put()
				self.redirect("/visit/home")
			elif "changeTimeFrame" in self.request.arguments():
				member.setViewTimeFrameFromTimeFrameString(self.request.get("timeFrame"))
				member.put()
				self.redirect("/visit/home")
			elif "refreshView" in self.request.arguments():
				if rakontu.lastPublish:
					member.viewTimeEnd = rakontu.lastPublish + timedelta(seconds=10)
				else:
					member.viewTimeEnd = datetime.now(tz=pytz.utc)
				member.put()
				self.redirect("/visit/home")
			elif "toggleShowDetails" in self.request.arguments():
				member.viewDetails = not member.viewDetails
				member.put()
				self.redirect("/visit/home")
			elif "loadAndApplySavedSearch" in self.request.arguments():
				searchKey = self.request.get("savedSearch")
				if searchKey:
					search = SavedSearch.get(searchKey)
					if search:
						member.viewSearch = search
						member.viewSearchResultList = []
						member.put()
						self.redirect("/visit/home")
						return
				else:
					self.redirect("/visit/home")
			elif "makeNewSavedSearch" in self.request.arguments():
				member.viewSearch = None
				member.viewSearchResultList = []
				member.put()
				self.redirect('/visit/filter')
			elif "doSomethingWithSearch" in self.request.arguments():
				response = self.request.get("doWithSearch")
				if response =="clearSearch":
					member.viewSearch = None
					member.viewSearchResultList = []
					member.put()
					self.redirect("/visit/home")
				elif response =="copySearchAs":
					newSearch = SavedSearch(rakontu=rakontu, creator=member)
					newSearch.copyDataFromOtherSearchAndPut(search)
					member.viewSearch = newSearch
					member.viewSearchResultList = []
					member.put()
					self.redirect('/visit/filter')
				elif response == "printSearchResults":
					self.redirect('/liaise/printSearch')
				elif response == "exportSearchResults":
					self.redirect("/manage/exportSearch")
				elif response == "changeSearch":
					if search:
						self.redirect("/visit/filter")
					else:
						member.viewSearch = None
						member.viewSearchResultList = []
						member.put()
						self.redirect('/visit/filter')
			else:
				if "setToLast" in self.request.arguments():
					if rakontu.lastPublish:
						member.viewTimeEnd = rakontu.lastPublish + timedelta(seconds=10)
					else:
						member.viewTimeEnd = datetime.now(tz=pytz.utc)
				elif "setToFirst" in self.request.arguments():
					if rakontu.firstPublish:
						member.setTimeFrameToStartAtFirstPublish()
					else:
						member.viewTimeEnd = datetime.now(tz=pytz.utc)
				elif "moveTimeBack" in self.request.arguments() or "moveTimeForward" in self.request.arguments():
					if "moveTimeBack" in self.request.arguments():
						member.viewTimeEnd = member.viewTimeEnd - timedelta(seconds=member.viewTimeFrameInSeconds)
					else:
						member.viewTimeEnd = member.viewTimeEnd + timedelta(seconds=member.viewTimeFrameInSeconds)
				if rakontu.firstPublish and member.getViewStartTime() < rakontu.firstPublish:
				 	member.setTimeFrameToStartAtFirstPublish()
				if member.viewTimeEnd > datetime.now(tz=pytz.utc):
					member.viewTimeEnd = datetime.now(tz=pytz.utc)
				member.put()
				self.redirect("/visit/home")
		else:
			self.redirect("/")
			
class ReadEntryPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		rakontu, member, access = GetCurrentRakontuAndMemberFromSession()
		if access:
			try:
				entry = db.get(self.request.query_string)
			except:
				entry = None
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
							if member.viewNudgeCategories[i]:
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
					numRows = BROWSE_NUM_ROWS
					numCols = BROWSE_NUM_COLS
					nudgeStep = max(1, (maxNudgePoints - minNudgePoints) // numRows)
					timeStep = (maxTime - minTime) // numCols
					
					textsForGrid = []
					colHeaders = []
					rowColors = []
					haveContent = False
					rowIndex = 0
					for row in range(numRows):
						rowColors.append(HexColorStringForRowIndex(rowIndex))
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
								colHeaders.append(RelativeTimeDisplayString(startTime, member))
							for item in allItems:
								nudgePoints = 0
								for i in range(NUM_NUDGE_CATEGORIES):
									if member.viewNudgeCategories[i]:
										nudgePoints += item.entryNudgePointsWhenPublished[i]
								shouldBeInRow = nudgePoints >= startNudgePoints and nudgePoints < endNudgePoints
								shouldBeInCol = item.published >= startTime and item.published < endTime
								if shouldBeInRow and shouldBeInCol:
									text = ItemDisplayStringForGrid(item, curating, showingMember=False, showDetails=member.viewDetails)
									textsInThisCell.append(text)
							haveContent = haveContent or len(textsInThisCell) > 0
							textsInThisRow.append(textsInThisCell)
						textsForGrid.append(textsInThisRow)
						rowIndex += 1
					textsForGrid.reverse()
				else:
					textsForGrid = None
					colHeaders = None
					rowColors = []
				if not haveContent:
					textsForGrid = None
				if not entry.memberCanNudge(member):
					nudgePointsMemberCanAssign = 0
				else:
					nudgePointsMemberCanAssign = max(0, rakontu.maxNudgePointsPerEntry - entry.getTotalNudgePointsForMember(member))
				rakontuHasQuestionsForThisEntryType = len(rakontu.getActiveQuestionsOfType(entry.type)) > 0
				memberCanAnswerQuestionsAboutThisEntry = len(entry.getAnswersForMember(member)) == 0
				memberCanAddNudgeToThisEntry = nudgePointsMemberCanAssign > 0
				thingsUserCanDo = {}
				if entry.isStory():
					thingsUserCanDo["Tell another version of what happened"] = "/visit/retell?%s" % entry.key()
				if entry.isStory() or entry.isResource():
					thingsUserCanDo["Tell a story this %s reminds you of" % entry.type] = "/visit/remind?%s" % entry.key()
				if rakontuHasQuestionsForThisEntryType and memberCanAnswerQuestionsAboutThisEntry:
					thingsUserCanDo["Answer questions about this %s" % entry.type] = "/visit/answers?%s" % entry.key()
				if rakontuHasQuestionsForThisEntryType and member.isLiaison():
					thingsUserCanDo["Enter answers about this %s for an off-line member" % entry.type] = "/visit/answers?%s" % entry.key()
				if entry.isInvitation():
					thingsUserCanDo["Respond to this invitation with a story"] = "/visit/respond?%s" % entry.key()
				thingsUserCanDo["Comment on this %s" % entry.type] = "/visit/comment?%s" % entry.key()
				thingsUserCanDo["Tag this %s" % entry.type] = "/visit/tagset?%s" % entry.key()
				if memberCanAddNudgeToThisEntry:
					thingsUserCanDo["Nudge this %s up or down" % entry.type] = "/visit/nudge?%s" % entry.key()
				thingsUserCanDo["Request something about this %s" % entry.type] = "/visit/request?%s" % entry.key()
				thingsUserCanDo["Relate this %s to others" % entry.type] = "/visit/relate?%s" % entry.key()
				if member.isCurator():
					thingsUserCanDo["Curate this %s" % entry.type] = "/visit/curate?%s" % entry.key()
				if entry.creator.key() == member.key() and rakontu.allowsPostPublishEditOfEntryType(entry.type):
					thingsUserCanDo["Change this %s" % entry.type] = "/visit/%s?%s" % (entry.type, entry.key())
				if member.isLiaison():
					thingsUserCanDo["Print this %s with its answers and annotations" % entry.type] = '/liaise/printEntryAndAnnotations?%s' % entry.key()
				if entry.isCollage():
					includedLinksOutgoing = entry.getOutgoingLinksOfType("included")
				else:
					includedLinksOutgoing = None
				if entry.isPattern():
					referencedLinksOutgoing = entry.getOutgoingLinksOfType("referenced")
				else:
					referencedLinksOutgoing = None
				template_values = GetStandardTemplateDictionaryAndAddMore({
								   'title': entry.title, 
						   		   'title_extra': None,
								   'rakontu': rakontu, 
								   'current_member': member,
								   'current_member_key': member.key(),
								   'curating': curating,
								   'entry': entry,
								   # to show above grid
								   'attachments': entry.getAttachments(),
								   'included_links_outgoing': includedLinksOutgoing,
								   'referenced_links_outgoing': referencedLinksOutgoing,
								   # grid
								   'rows_cols': textsForGrid, 
								   'col_headers': colHeaders, 
								   'text_to_display_before_grid': "Annotations to this %s" % entry.type,
								   'row_colors': rowColors,
								   'grid_form_url': "/visit/read",
								   # actions
								   'things_member_can_do': thingsUserCanDo,
								   })
				member.lastReadAnything = datetime.now(tz=pytz.utc)
				member.nudgePoints += rakontu.getMemberNudgePointsForEvent("reading")
				member.put()
				path = os.path.join(os.path.dirname(__file__), 'templates/visit/read.html')
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect('/result?entryNotFound')
		else:
			self.redirect('/')
			
	@RequireLogin 
	def post(self):
		rakontu, member, access = GetCurrentRakontuAndMemberFromSession()
		if access:
			if "changeNudgeCategoriesShowing" in self.request.arguments():
				member.viewNudgeCategories = []
				for i in range(NUM_NUDGE_CATEGORIES):
					member.viewNudgeCategories.append(self.request.get("showCategory|%s" % i) == "yes")
				member.put()
				self.redirect(self.request.headers["Referer"])
			elif "toggleShowDetails" in self.request.arguments():
				member.viewDetails = not member.viewDetails
				member.put()
				self.redirect(self.request.headers["Referer"])
			else:
				self.redirect(self.request.get("nextAction"))
		else:
			self.redirect("/visit/home")
			
class ReadAnnotationPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		rakontu, member, access = GetCurrentRakontuAndMemberFromSession()
		if access:
			annotation = db.get(self.request.query_string)
			if annotation:
				template_values = GetStandardTemplateDictionaryAndAddMore({
								   'title': annotation.displayString(includeType=False), 
						   		   'title_extra': None,
								   'rakontu': rakontu, 
								   'current_member': member,
								   'current_member_key': member.key(),
								   'annotation': annotation,
								   'included_links_outgoing': annotation.entry.getOutgoingLinksOfType("included"),
								   })
				member.lastReadAnything = datetime.now(tz=pytz.utc)
				member.nudgePoints += rakontu.getMemberNudgePointsForEvent("reading")
				member.put()
				path = os.path.join(os.path.dirname(__file__), 'templates/visit/readAnnotation.html')
				self.response.out.write(template.render(path, template_values))
		else:
			self.redirect('/')
			
			
	@RequireLogin 
	def post(self):
		rakontu, member, access = GetCurrentRakontuAndMemberFromSession()
		if access:
			if "toggleRequestCompleted" in self.request.arguments():
				annotation = db.get(self.request.query_string)
			if annotation:
				annotation.completedIfRequest = not annotation.completedIfRequest
				annotation.put()
				self.redirect(self.request.headers["Referer"])
		else:
			self.redirect("/visit/home")

class SeeRakontuPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		rakontu, member, access = GetCurrentRakontuAndMemberFromSession()
		if access:
				template_values = GetStandardTemplateDictionaryAndAddMore({
								   'title': "About", 
						   		   'title_extra': rakontu.name, 
								   'rakontu': rakontu, 
								   'current_member': member,
								   'rakontu_members': rakontu.getActiveMembers(),
								   'characters': rakontu.getActiveCharacters(),
								   })
				path = os.path.join(os.path.dirname(__file__), 'templates/visit/rakontu.html')
				self.response.out.write(template.render(path, template_values))
		else:
			self.redirect('/')
			
class SeeRakontuMembersPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		rakontu, member, access = GetCurrentRakontuAndMemberFromSession()
		if access:
				template_values = GetStandardTemplateDictionaryAndAddMore({
								   'title': "Members of", 
						   		   'title_extra': rakontu.name, 
								   'rakontu': rakontu, 
								   'current_member': member,
								   'rakontu_members': rakontu.getActiveMembers(),
								   })
				path = os.path.join(os.path.dirname(__file__), 'templates/visit/members.html')
				self.response.out.write(template.render(path, template_values))
		else:
			self.redirect('/')
   
class SeeMemberPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		rakontu, member, access = GetCurrentRakontuAndMemberFromSession()
		if access:
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
					numCols = BROWSE_NUM_COLS
					timeStep = (maxTime - minTime) // numCols
					textsForGrid = []
					colHeaders = []
					for row in range(numRows):
						textsInThisRow = []
						for col in range(numCols):
							textsInThisCell = []
							startTime = minTime + timeStep * col
							endTime = minTime + timeStep * (col+1)
							if row == numRows - 1:
								colHeaders.append(RelativeTimeDisplayString(startTime, member))
							for item in allItems:
								shouldBeInRow = True
								shouldBeInCol = item.published >= startTime and item.published < endTime
								if shouldBeInRow and shouldBeInCol:
									text = ItemDisplayStringForGrid(item, curating, showingMember=not memberToSee.isLiaison(), showDetails=member.viewDetails)
									textsInThisCell.append(text)
							textsInThisRow.append(textsInThisCell)
						textsForGrid.append(textsInThisRow)
					textsForGrid.reverse()
				else:
					textsForGrid = None
					colHeaders = None
				template_values = GetStandardTemplateDictionaryAndAddMore({
							   'title': "Member", 
					   		   'title_extra': member.nickname, 
					   		   'rakontu': rakontu, 
					   		   'current_member': member,
					   		   'member': memberToSee,
					   		   'answers': memberToSee.getAnswers(),
					   		   'rows_cols': textsForGrid,
					   		   'col_headers': colHeaders,
					   		   'text_to_display_before_grid': "%s's entries" % memberToSee.nickname,
					   		   'grid_form_url': "/visit/member?%s" % memberToSee.key(),
					   		   'no_profile_text': NO_PROFILE_TEXT,
					   		   })
				path = os.path.join(os.path.dirname(__file__), 'templates/visit/member.html')
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect('/visit/home')
		else:
			self.redirect('/')

	@RequireLogin 
	def post(self):
		rakontu, member, access = GetCurrentRakontuAndMemberFromSession()
		if access:
			messageMember = None
			goAhead = True
			if "toggleShowDetails" in self.request.arguments():
				member.viewDetails = not member.viewDetails
				member.put()
				self.redirect(self.request.headers["Referer"])
			else:
				for argument in self.request.arguments():
					if argument.find("|") >= 0:
						for aMember in rakontu.getActiveMembers():
							if argument == "message|%s" % aMember.key():
								try:
									messageMember = aMember
								except: 
									messageMember = None
									goAhead = False
								break
				if goAhead and messageMember:
					message = mail.EmailMessage()
					message.sender = rakontu.contactEmail
					message.subject = htmlEscape(self.request.get("subject"))
					message.to = messageMember.googleAccountEmail
					message.body = htmlEscape(self.request.get("message"))
					message.send()
					self.redirect('/result?messagesent')
				else:
					self.redirect('/result?memberNotFound')
		else:
			self.redirect('/')
   
class SeeCharacterPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		rakontu, member, access = GetCurrentRakontuAndMemberFromSession()
		if access:
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
						colHeaders = []
						for row in range(numRows):
							textsInThisRow = []
							for col in range(numCols):
								textsInThisCell = []
								startTime = minTime + timeStep * col
								endTime = minTime + timeStep * (col+1)
								if row == numRows - 1:
									colHeaders.append(RelativeTimeDisplayString(startTime, member))
								for item in allItems:
									shouldBeInRow = True
									shouldBeInCol = item.published >= startTime and item.published < endTime
									if shouldBeInRow and shouldBeInCol:
										text = ItemDisplayStringForGrid(item, curating, showingMember=True, showDetails=member.viewDetails)
										textsInThisCell.append(text)
								textsInThisRow.append(textsInThisCell)
							textsForGrid.append(textsInThisRow)
						textsForGrid.reverse()
					else:
						textsForGrid = None
						colHeaders = None
					template_values = GetStandardTemplateDictionaryAndAddMore({
								   	   'title': "Character", 
						   		   	   'title_extra': character.name, 
									   'rakontu': rakontu, 
									   'current_member': member,
									   'character': character,
									   'answers': character.getAnswers(),
						   		   	   'rows_cols': textsForGrid,
						   		   	   'text_to_display_before_grid': "%s's entries" % character.name,
						   		   	   'grid_form_url': "/visit/character?%s" % character.key(),
						   		   	   'col_headers': colHeaders,
									   })
					path = os.path.join(os.path.dirname(__file__), 'templates/visit/character.html')
					self.response.out.write(template.render(path, template_values))
				else:
					self.redirect('/visit/home')
		else:
			self.redirect('/')

	@RequireLogin 
	def post(self):
		rakontu, member, access = GetCurrentRakontuAndMemberFromSession()
		if access:
			if "toggleShowDetails" in self.request.arguments():
				member.viewDetails = not member.viewDetails
				member.put()
			self.redirect(self.request.headers["Referer"])
		else:
			self.redirect('/')
   
class ChangeMemberProfilePage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		rakontu, member, access = GetCurrentRakontuAndMemberFromSession()
		if access:
			try:
				offlineMember = db.get(self.request.query_string)
			except:
				offlineMember = None
			if offlineMember:
				memberToEdit = offlineMember
			else:
				memberToEdit = member
			template_values = GetStandardTemplateDictionaryAndAddMore({
							   'title': "Profile of", 
						   	   'title_extra': memberToEdit.nickname, 
							   'rakontu': rakontu, 
							   'member': memberToEdit,
							   'current_member': member,
							   'questions': rakontu.getActiveMemberQuestions(),
							   'answers': memberToEdit.getAnswers(),
							   'refer_type': "member",
							   'show_leave_link': not rakontu.memberIsOnlyOwner(member),
							   'search_locations': SEARCH_LOCATIONS,
							   })
			path = os.path.join(os.path.dirname(__file__), 'templates/visit/profile.html')
			self.response.out.write(template.render(path, template_values))
		else:
			self.redirect('/')
							 
	@RequireLogin 
	def post(self):
		rakontu, member, access = GetCurrentRakontuAndMemberFromSession()
		if access:
			goAhead = True
			offlineMember = None
			for argument in self.request.arguments():
				if argument.find("|") >= 0:
					for aMember in rakontu.getActiveOfflineMembers():
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
				nicknameTheyWantToUse = htmlEscape(self.request.get("nickname")).strip()
				memberUsingNickname = rakontu.memberWithNickname(nicknameTheyWantToUse)
				if memberUsingNickname and memberUsingNickname.key() != member.key():
					self.redirect('/result?nicknameAlreadyInUse') 
					return
				memberToEdit.nickname = nicknameTheyWantToUse
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
					memberToEdit.preferredTextFormat = self.request.get("preferredTextFormat")
				memberToEdit.put()
				questions = Question.all().filter("rakontu = ", rakontu).filter("refersTo = ", "member").fetch(FETCH_NUMBER)
				for question in questions:
					foundAnswers = Answer.all().filter("question = ", question.key()).filter("referent =", memberToEdit.key()).fetch(FETCH_NUMBER)
					if foundAnswers:
						answerToEdit = foundAnswers[0]
					else:
						answerToEdit = Answer(question=question, rakontu=rakontu, referent=memberToEdit, referentType="member")
					keepAnswer = False
					queryText = "%s" % question.key()
					if question.type == "text":
						keepAnswer = len(self.request.get(queryText)) > 0 and self.request.get(queryText) != "None"
						if keepAnswer:
							answerToEdit.answerIfText = htmlEscape(self.request.get(queryText))
					elif question.type == "value":
						keepAnswer = len(self.request.get(queryText)) > 0 and self.request.get(queryText) != "None"
						if keepAnswer:
							oldValue = answerToEdit.answerIfValue
							try:
								answerToEdit.answerIfValue = int(self.request.get(queryText))
							except:
								answerToEdit.answerIfValue = oldValue
					elif question.type == "boolean":
						keepAnswer = queryText in self.request.params.keys()
						if keepAnswer:
							answerToEdit.answerIfBoolean = self.request.get(queryText) == "yes"
					elif question.type == "nominal" or question.type == "ordinal":
						if question.multiple:
							answerToEdit.answerIfMultiple = []
							for choice in question.choices:
								if self.request.get("%s|%s" % (question.key(), choice)) == "yes":
									answerToEdit.answerIfMultiple.append(choice)
									keepAnswer = True
						else:
							keepAnswer = len(self.request.get(queryText)) > 0 and self.request.get(queryText) != "None"
							if keepAnswer:
								answerToEdit.answerIfText = self.request.get(queryText)
					answerToEdit.creator = memberToEdit
					if keepAnswer:
						answerToEdit.put()
				if offlineMember:
					self.redirect('/liaise/members')
				else:
					self.redirect('/visit/member?%s' % memberToEdit.key())
			else:
				self.redirect("/visit/home")
		else:
			self.redirect("/")
			
class ChangeMemberDraftsPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		rakontu, member, access = GetCurrentRakontuAndMemberFromSession()
		if access:
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
							   'title': "Drafts by", 
						   	   'title_extra': memberToEdit.nickname, 
							   'rakontu': rakontu, 
							   'member': memberToEdit,
							   'current_member': member,
							   'searches': member.getSavedSearches(),
							   'draft_entries': memberToEdit.getDraftEntries(),
							   'draft_annotations': memberToEdit.getDraftAnnotations(),
							   'first_draft_answer_per_entry': firstDraftAnswerForEachEntry,
							   'refer_type': "member",
							   'search_locations': SEARCH_LOCATIONS,
							   })
			path = os.path.join(os.path.dirname(__file__), 'templates/visit/drafts.html')
			self.response.out.write(template.render(path, template_values))
		else:
			self.redirect('/')
							 
	@RequireLogin 
	def post(self):
		rakontu, member, access = GetCurrentRakontuAndMemberFromSession()
		if access:
			goAhead = True
			offlineMember = None
			for argument in self.request.arguments():
				if argument.find("|") >= 0:
					for aMember in rakontu.getActiveOfflineMembers():
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
				for search in memberToEdit.getSavedSearches():
					if self.request.get("remove|%s" % search.key()) == "yes":
						search.deleteAllDependents()
						db.delete(search)
				if offlineMember:
					self.redirect('/liaise/members')
				else:
					self.redirect('/visit/drafts?%s' % memberToEdit.key())
			else:
				self.redirect("/visit/home")
		else:
			self.redirect("/")
			
class LeaveRakontuPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		rakontu, member, access = GetCurrentRakontuAndMemberFromSession()
		if access:
			template_values = GetStandardTemplateDictionaryAndAddMore({
						   	   'title': "Leave rakontu", 
					   	   	   'title_extra': None, 
							   'rakontu': rakontu, 
							   'message': self.request.query_string,
							   "linkback": self.request.headers["Referer"],
							   'current_member': member,
							   })
			path = os.path.join(os.path.dirname(__file__), 'templates/visit/leave.html')
			self.response.out.write(template.render(path, template_values))
		else:
			self.redirect("/")
			
	@RequireLogin 
	def post(self):
		rakontu, member, access = GetCurrentRakontuAndMemberFromSession()
		if access:
			if "leave|%s" % member.key() in self.request.arguments():
				if rakontu.memberIsOnlyOwner(member):
					self.redirect("/result?ownerCannotLeave")
					return
				else:
					member.active = False
					member.put()
					self.redirect("/")
			else:
				self.redirect('/visit/profile?%s' % member.key())
		else:
			self.redirect("/")
		
class SavedSearchEntryPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		rakontu, member, access = GetCurrentRakontuAndMemberFromSession()
		if access:
			currentSearch = GetCurrentSearchForMember(member)
			questionsAndRefsDictList = []
			entryQuestions = rakontu.getActiveNonMemberQuestions()
			if entryQuestions:
				entryQuestionsAndRefsDictionary = {
					"result_preface": "entry", "afterAnyText":"of these answers to questions:",
					"questions": entryQuestions}
				if currentSearch:
					entryQuestionsAndRefsDictionary["references"] = currentSearch.getQuestionReferencesOfType("entry") 
					entryQuestionsAndRefsDictionary["anyOrAll"] = currentSearch.answers_anyOrAll
				else:
					entryQuestionsAndRefsDictionary["references"] = []
					entryQuestionsAndRefsDictionary["anyOrAll"] = None
				questionsAndRefsDictList.append(entryQuestionsAndRefsDictionary)
			creatorQuestions = rakontu.getActiveMemberAndCharacterQuestions()
			if creatorQuestions:
				if rakontu.hasActiveCharacters() and rakontu.hasActiveQuestionsOfType("character"):
					afterAnyText = "of these answers to questions about their creators (members or characters):"
				else:
					afterAnyText = "of these answers to questions about their creators:"
				creatorQuestionsAndRefsDictionary = {
					"result_preface": "creator", "afterAnyText": afterAnyText,
					"questions": creatorQuestions}
				if currentSearch:
					creatorQuestionsAndRefsDictionary["references"] = currentSearch.getQuestionReferencesOfType("creator") 
					creatorQuestionsAndRefsDictionary["anyOrAll"] = currentSearch.creatorAnswers_anyOrAll
				else:
					creatorQuestionsAndRefsDictionary["references"] = []
					creatorQuestionsAndRefsDictionary["anyOrAll"] = None
				questionsAndRefsDictList.append(creatorQuestionsAndRefsDictionary)
			template_values = GetStandardTemplateDictionaryAndAddMore({
							'title': "Filter",
						   	'title_extra': None,
							'rakontu': rakontu, 
							'current_member': member, 
							'num_search_fields': NUM_SEARCH_FIELDS,
							'search_locations': SEARCH_LOCATIONS,
							'any_or_all_choices': ANY_ALL,
							'answer_comparison_types': ANSWER_COMPARISON_TYPES,
							'current_search': currentSearch,
							'questions_and_refs_dict_list': questionsAndRefsDictList,
							})
			path = os.path.join(os.path.dirname(__file__), 'templates/visit/filter.html')
			self.response.out.write(template.render(path, template_values))
		else:
			self.redirect('/')
			
	@RequireLogin 
	def post(self):
		rakontu, member, access = GetCurrentRakontuAndMemberFromSession()
		if access:
			search = GetCurrentSearchForMember(member)
			if "deleteSearchByCreator" in self.request.arguments():
				if search:
					db.delete(search)
					member.viewSearch = None
					member.viewSearchResultList = []
					member.put()
				self.redirect("/visit/home")
			elif "flagSearchByCurator" in self.request.arguments():
				if search:
					search.flaggedForRemoval = not search.flaggedForRemoval
					search.put()
					self.redirect("/visit/filter")
				else:
					self.redirect("/visit/home")
			elif "removeSearchByManager" in self.request.arguments():
				if search:
					db.delete(search)
					member.viewSearch = None
					member.viewSearchResultList = []
					member.put()
				self.redirect("/visit/home")
			elif "cancel" in self.request.arguments():
				self.redirect("/visit/home")
			elif "saveAs" in self.request.arguments() or "save" in self.request.arguments():
				if not search or "saveAs" in self.request.arguments():
					search = SavedSearch(rakontu=rakontu, creator=member)
				search.private = self.request.get("privateOrSharedSearch") == "private"
				search.name = htmlEscape(self.request.get("searchName", default_value="Untitled"))
				text = self.request.get("comment")
				format = self.request.get("comment_format").strip()
				search.comment = text
				search.comment_formatted = db.Text(InterpretEnteredText(text, format))
				search.comment_format = format
				search.entryTypes = []
				for i in range(len(ENTRY_TYPES)):
					search.entryTypes.append(self.request.get(ENTRY_TYPES[i]) == "yes")
				search.overall_anyOrAll = self.request.get("overall_anyOrAll")
				# words
				search.words_anyOrAll = self.request.get("words_anyOrAll")
				search.words_locations = []
				for i in range(len(SEARCH_LOCATIONS)):
					search.words_locations.append(self.request.get("location|%s" % i) == "yes")
				if not search.words_locations:
					search.words_locations = SEARCH_LOCATIONS[0]
				search.words = []
				for i in range(NUM_SEARCH_FIELDS):
					response = self.request.get("words|%s" % i).strip()
					if response and response != "None" :
						search.words.append(response)
				# tags
				search.tags_anyOrAll = self.request.get("tags_anyOrAll")
				search.tags = []
				for i in range(NUM_SEARCH_FIELDS):
					if self.request.get("tags|%s" % i) and self.request.get("tags|%s" % i) != "None":
						search.tags.append(self.request.get("tags|%s" % i))
				search.put()
				# questions
				for preface in ["entry", "creator"]:
					if preface == "entry":
						search.answers_anyOrAll = self.request.get("entry|anyOrAll")
						questions = rakontu.getActiveNonMemberQuestions()
					else:
						search.creatornswers_anyOrAll = self.request.get("creator|anyOrAll")
						questions = rakontu.getActiveMemberAndCharacterQuestions()
					for i in range(NUM_SEARCH_FIELDS):
						response = self.request.get("%s|question|%s" % (preface, i))
						for question in questions:
							foundQuestion = False
							comparison = ""
							answer = ""
							if question.isTextOrValue():
								if response == "%s" % question.key():
									foundQuestion = True
									answer = self.request.get("%s|answer|%s" % (preface, i)).strip()
									comparison = self.request.get("%s|comparison|%s" % (preface, i))
							elif question.type == "boolean":
								if response == "yes|%s" % question.key():
									foundQuestion = True
									answer = "yes"
								elif response == "no|%s" % question.key():
									foundQuestion = True
									answer = "no"
							elif question.isOrdinalOrNominal():
								for choice in question.choices:
									if response == "%s|%s" % (choice, question.key()):
										foundQuestion = True
										answer = choice
							if foundQuestion and answer:
								ref = SavedSearchQuestionReference.all().filter("search = ", search).\
									filter("question = ", question).filter("order = ", i).get()
								if not ref:
									ref = SavedSearchQuestionReference(rakontu=rakontu, search=search, question=question)
								ref.answer = answer
								ref.comparison = comparison
								ref.order = i
								ref.type = preface
								ref.put()
				member.viewSearch = search
				member.viewSearchResultList = []
				member.put()
				self.redirect("/visit/home")
			else:
				self.redirect("/visit/home")
		else:
			self.redirect("/")
			
class ResultFeedbackPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		rakontu, member, access = GetCurrentRakontuAndMemberFromSession()
		if access:
			template_values = GetStandardTemplateDictionaryAndAddMore({
						   	   'title': "Message", 
					   	   	   'title_extra': None, 
							   'rakontu': rakontu, 
							   'message': self.request.query_string,
							   "linkback": self.request.headers["Referer"],
							   'current_member': member,
							   })
			path = os.path.join(os.path.dirname(__file__), 'templates/result.html')
			self.response.out.write(template.render(path, template_values))
		else:
			self.redirect("/")
				
class ContextualHelpPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		rakontu, member, access = GetCurrentRakontuAndMemberFromSession()
		if access:
			lookup = self.request.query_string.strip()
			help = Help.all().filter('name = ', lookup).get()
			if help:
				template_values = GetStandardTemplateDictionaryAndAddMore({
							   	   'title': "Help on item", 
						   	   	   'title_extra': None, 
								   'rakontu': rakontu, 
								   'help': help,
								   "linkback": self.request.headers["Referer"],
								   'current_member': member,
								   })
				path = os.path.join(os.path.dirname(__file__), 'templates/help.html')
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect("/result?helpNotFound")
		else:
			self.redirect("/")
