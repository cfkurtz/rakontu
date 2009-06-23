# --------------------------------------------------------------------------------------------
# RAKONTU
# Description: Rakontu is open source story sharing software.
# Version: pre-0.1
# License: GPL 3.0
# Google Code Project: http://code.google.com/p/rakontu/
# --------------------------------------------------------------------------------------------

from utils import *

def ItemDisplayStringForGrid(item, curating=False, showingMember=False, showDetails=False):
	if not showingMember:
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
	if showDetails:
		if item.__class__.__name__ == "Annotation":
			if item.type == "comment" or item.type == "request":
				if item.longString_formatted:
					textString = ": %s" % upToWithLink(stripTags(item.longString_formatted), DEFAULT_DETAILS_TEXT_LENGTH, '/visit/readAnnotation?%s' % item.key())
				else:
					textString = ""
			else:
				textString = ""
		elif item.__class__.__name__ == "Entry":
			textString = ": %s" % upToWithLink(stripTags(item.text_formatted), DEFAULT_DETAILS_TEXT_LENGTH, '/visit/read?%s' % item.key())
		else:
			textString = ""
	else:
		textString = ""
	if item.__class__.__name__ == "Answer":
		if showDetails:
			if not showingMember:
				linkString = item.linkStringWithQuestionText()
			else:
				linkString = item.linkStringWithQuestionTextAndReferentLink()
		else:
			if not showingMember:
				linkString = item.linkStringWithQuestionName()
			else:
				linkString = item.linkStringWithQuestionNameAndReferentLink()
	elif item.__class__.__name__ == "Annotation":
		linkString = item.linkStringWithEntryLink()
	else:
		linkString = item.linkString()
	return '<p>%s %s %s%s%s</p>' % (item.getImageLinkForType(), curateString, linkString, nameString, textString)

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
					matchingMember = Member.all().filter("community = ", community).filter("googleAccountID = ", user.user_id()).get()
					if matchingMember:
						session['member_key'] = matchingMember.key()
						matchingMember.viewSearchResultList = []
						matchingMember.put()
						if matchingMember.active:
							self.redirect('/visit/look')
						else:
							matchingMember.active = True
							matchingMember.put()
							pendingMember = PendingMember.all().filter("community = ", community.key()).filter("email = ", user.email()).get()
							if pendingMember:
								db.delete(pendingMember)
							self.redirect("/visit/new")
					else:
						pendingMember = PendingMember.all().filter("community = ", community.key()).filter("email = ", user.email()).get()
						if pendingMember:
							newMember = Member(
								nickname=user.email(),
								googleAccountID=user.user_id(),
								googleAccountEmail=user.email(),
								community=community,
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
		elif "createCommunity" in self.request.arguments():
			self.redirect("/createCommunity")
		elif "reviewAllCommunities" in self.request.arguments():
			self.redirect("/admin/communities")
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
		community, member, access = GetCurrentCommunityAndMemberFromSession()
		if access:
			template_values = GetStandardTemplateDictionaryAndAddMore({
							'title': "Welcome",
							'title_extra': member.nickname,
							'community': community, 
							'current_member': member,
							'resources': community.getNonDraftNewMemberResources(),
							})
			path = os.path.join(os.path.dirname(__file__), 'templates/visit/new.html')
			self.response.out.write(template.render(path, template_values))
		else:
			self.redirect('/')
			
class GetHelpPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		community, member, access = GetCurrentCommunityAndMemberFromSession()
		if access:
			if member.isManagerOrOwner():
				managerResources = community.getNonDraftManagerOnlyHelpResources()
			else:
				managerResources = None
			template_values = GetStandardTemplateDictionaryAndAddMore({
							'title': "Help",
							'community': community, 
							'current_member': member,
							'resources': community.getNonDraftHelpResources(),
							'manager_resources': managerResources,
							'guides': community.getGuides(),
							})
			path = os.path.join(os.path.dirname(__file__), 'templates/visit/help.html')
			self.response.out.write(template.render(path, template_values))
		else:
			self.redirect('/')
			
class BrowseEntriesPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		community, member, access = GetCurrentCommunityAndMemberFromSession()
		if access:
			currentSearch = GetCurrentSearchForMember(member)
			textsForGrid = []
			colHeaders = []
			rowColors = []
			entries = community.getNonDraftEntriesInReverseTimeOrder()
			if entries:
				(textsForGrid, colHeaders, rowColors) = self.buildGrid(community, member, entries, currentSearch)
			template_values = GetStandardTemplateDictionaryAndAddMore({
							'title': "Main page",
						   	'title_extra': None,
							'community': community, 
							'current_member': member, 
							'rows_cols': textsForGrid, 
							'col_headers': colHeaders, 
							'row_colors': rowColors,
							'num_search_fields': NUM_SEARCH_FIELDS,
							'search_locations': SEARCH_LOCATIONS,
							'any_or_all_choices': ANY_ALL,
							'answer_comparison_types': ANSWER_COMPARISON_TYPES,
							'community_searches': community.getNonPrivateSavedSearches(),
							'member_searches': member.getPrivateSavedSearches(),
							'current_search': currentSearch,
							'member_time_frame_string': member.getFrameStringForViewTimeFrame(),
							})
			path = os.path.join(os.path.dirname(__file__), 'templates/visit/look.html')
			self.response.out.write(template.render(path, template_values))
		else:
			self.redirect('/')
			
	def buildGrid(self, community, member, entries, currentSearch):
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
							downdrift = community.getEntryActivityPointsForEvent("downdrift")
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
		community, member, access = GetCurrentCommunityAndMemberFromSession()
		if access:
			search = GetCurrentSearchForMember(member)
			if "changeNudgeCategoriesShowing" in self.request.arguments():
				member.viewNudgeCategories = []
				for i in range(NUM_NUDGE_CATEGORIES):
					member.viewNudgeCategories.append(self.request.get("showCategory|%s" % i) == "yes")
				member.put()
				self.redirect("/visit/look")
			elif "changeTimeFrame" in self.request.arguments():
				member.setViewTimeFrameFromTimeFrameString(self.request.get("timeFrame"))
				member.put()
				self.redirect("/visit/look")
			elif "refreshView" in self.request.arguments():
				if community.lastPublish:
					member.viewTimeEnd = community.lastPublish + timedelta(seconds=10)
				else:
					member.viewTimeEnd = datetime.now(tz=pytz.utc)
				member.put()
				self.redirect("/visit/look")
			elif "loadAndApplySavedSearch" in self.request.arguments():
				searchKey = self.request.get("savedSearch")
				if searchKey:
					search = SavedSearch.get(searchKey)
					if search:
						member.viewSearch = search
						member.viewSearchResultList = []
						member.put()
						self.redirect("/visit/look")
						return
				else:
					self.redirect("/visit/look")
			elif "clearSearch" in self.request.arguments():
				member.viewSearch = None
				member.viewSearchResultList = []
				member.put()
				self.redirect("/visit/look")
			elif "toggleShowDetails" in self.request.arguments():
				member.viewDetails = not member.viewDetails
				member.put()
				self.redirect("/visit/look")
			elif "copySearchAs" in self.request.arguments():
				newSearch = SavedSearch(community=community, creator=member)
				newSearch.copyDataFromOtherSearchAndPut(search)
				member.viewSearch = newSearch
				member.viewSearchResultList = []
				member.put()
				self.redirect('/visit/filter')
			elif "printSearchResults" in self.request.arguments():
				self.redirect('/liaise/printSearch')
			elif "makeNewSavedSearch" in self.request.arguments() or "changeSearch" in self.request.arguments():
				if "makeNewSavedSearch" in self.request.arguments():
					self.redirect('/visit/filter')
				else:
					if search:
						self.redirect("/visit/filter")
					else:
						member.viewSearch = None
						member.viewSearchResultList = []
						member.put()
						self.redirect('/visit/filter')
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
					if "moveTimeBack" in self.request.arguments():
						member.viewTimeEnd = member.viewTimeEnd - timedelta(seconds=member.viewTimeFrameInSeconds)
					else:
						member.viewTimeEnd = member.viewTimeEnd + timedelta(seconds=member.viewTimeFrameInSeconds)
				if community.firstPublish and member.getViewStartTime() < community.firstPublish:
				 	member.setTimeFrameToStartAtFirstPublish()
				if member.viewTimeEnd > datetime.now(tz=pytz.utc):
					member.viewTimeEnd = datetime.now(tz=pytz.utc)
				member.put()
				self.redirect("/visit/look")
		else:
			self.redirect("/")
			
class SavedSearchEntryPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		community, member, access = GetCurrentCommunityAndMemberFromSession()
		if access:
			currentSearch = GetCurrentSearchForMember(member)
			questionsAndRefsDictList = []
			entryQuestions = community.getActiveNonMemberQuestions()
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
			creatorQuestions = community.getActiveMemberAndCharacterQuestions()
			if creatorQuestions:
				if community.hasActiveCharacters() and community.hasActiveQuestionsOfType("character"):
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
							'community': community, 
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
		community, member, access = GetCurrentCommunityAndMemberFromSession()
		if access:
			search = GetCurrentSearchForMember(member)
			if "deleteSearchByCreator" in self.request.arguments():
				if search:
					db.delete(search)
					member.viewSearch = None
					member.viewSearchResultList = []
					member.put()
				self.redirect("/visit/look")
			elif "flagSearchByCurator" in self.request.arguments():
				if search:
					search.flaggedForRemoval = not search.flaggedForRemoval
					search.put()
					self.redirect("/visit/filter")
				else:
					self.redirect("/visit/look")
			elif "removeSearchByManager" in self.request.arguments():
				if search:
					db.delete(search)
					member.viewSearch = None
					member.viewSearchResultList = []
					member.put()
				self.redirect("/visit/look")
			elif "cancel" in self.request.arguments():
				self.redirect("/visit/look")
			elif "saveAs" in self.request.arguments() or "save" in self.request.arguments():
				if not search or "saveAs" in self.request.arguments():
					search = SavedSearch(community=community, creator=member)
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
						questions = community.getActiveNonMemberQuestions()
					else:
						search.creatornswers_anyOrAll = self.request.get("creator|anyOrAll")
						questions = community.getActiveMemberAndCharacterQuestions()
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
									ref = SavedSearchQuestionReference(community=community, search=search, question=question)
								ref.answer = answer
								ref.comparison = comparison
								ref.order = i
								ref.type = preface
								ref.put()
				member.viewSearch = search
				member.viewSearchResultList = []
				member.put()
				self.redirect("/visit/look")
			else:
				self.redirect("/visit/look")
		else:
			self.redirect("/")
			
class ReadEntryPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		community, member, access = GetCurrentCommunityAndMemberFromSession()
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
					nudgePointsMemberCanAssign = max(0, community.maxNudgePointsPerEntry - entry.getTotalNudgePointsForMember(member))
				communityHasQuestionsForThisEntryType = len(community.getActiveQuestionsOfType(entry.type)) > 0
				memberCanAnswerQuestionsAboutThisEntry = len(entry.getAnswersForMember(member)) == 0
				memberCanAddNudgeToThisEntry = nudgePointsMemberCanAssign > 0
				thingsUserCanDo = {}
				if entry.isStory():
					thingsUserCanDo["Tell another version of what happened"] = "/visit/retell?%s" % entry.key()
				if entry.isStory() or entry.isResource():
					thingsUserCanDo["Tell a story this %s reminds you of" % entry.type] = "/visit/remind?%s" % entry.key()
				if communityHasQuestionsForThisEntryType and memberCanAnswerQuestionsAboutThisEntry:
					thingsUserCanDo["Answer questions about this %s" % entry.type] = "/visit/answers?%s" % entry.key()
				if communityHasQuestionsForThisEntryType and member.isLiaison():
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
				if entry.creator.key() == member.key() and community.allowsPostPublishEditOfEntryType(entry.type):
					thingsUserCanDo["Change this %s" % entry.type] = "/visit/%s?%s" % (entry.type, entry.key())
				if member.isLiaison():
					thingsUserCanDo["Print this %s with its answers and annotations" % entry.type] = '/liaise/printEntryAndAnnotations?%s' % entry.key()
				template_values = GetStandardTemplateDictionaryAndAddMore({
								   'title': entry.title, 
						   		   'title_extra': None,
								   'community': community, 
								   'current_member': member,
								   'current_member_key': member.key(),
								   'curating': curating,
								   'entry': entry,
								   'rows_cols': textsForGrid, 
								   'col_headers': colHeaders, 
								   'text_to_display_before_grid': "Annotations to this %s" % entry.type,
								   'things_member_can_do': thingsUserCanDo,
								   'member_can_answer_questions': memberCanAnswerQuestionsAboutThisEntry,
								   'member_can_add_nudge': memberCanAddNudgeToThisEntry,
								   'community_has_questions_for_this_entry_type': communityHasQuestionsForThisEntryType,
								   'answers': entry.getNonDraftAnswers(),
								   'questions': community.getActiveQuestionsOfType(entry.type),
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
								   'row_colors': rowColors,
								   'grid_form_url': "/visit/read"
								   })
				member.lastReadAnything = datetime.now(tz=pytz.utc)
				member.nudgePoints += community.getMemberNudgePointsForEvent("reading")
				member.put()
				path = os.path.join(os.path.dirname(__file__), 'templates/visit/read.html')
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect('/result?entryNotFound')
		else:
			self.redirect('/')
			
	@RequireLogin 
	def post(self):
		community, member, access = GetCurrentCommunityAndMemberFromSession()
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
			self.redirect("/visit/look")
			
class ReadAnnotationPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		community, member, access = GetCurrentCommunityAndMemberFromSession()
		if access:
			annotation = db.get(self.request.query_string)
			if annotation:
				template_values = GetStandardTemplateDictionaryAndAddMore({
								   'title': annotation.displayString(includeType=False), 
						   		   'title_extra': None,
								   'community': community, 
								   'current_member': member,
								   'current_member_key': member.key(),
								   'annotation': annotation,
								   'included_links_outgoing': annotation.entry.getOutgoingLinksOfType("included"),
								   })
				member.lastReadAnything = datetime.now(tz=pytz.utc)
				member.nudgePoints += community.getMemberNudgePointsForEvent("reading")
				member.put()
				path = os.path.join(os.path.dirname(__file__), 'templates/visit/readAnnotation.html')
				self.response.out.write(template.render(path, template_values))
		else:
			self.redirect('/')

class SeeCommunityPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		community, member, access = GetCurrentCommunityAndMemberFromSession()
		if access:
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
		community, member, access = GetCurrentCommunityAndMemberFromSession()
		if access:
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
		community, member, access = GetCurrentCommunityAndMemberFromSession()
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
					   		   'community': community, 
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
				self.redirect('/visit/look')
		else:
			self.redirect('/')

	@RequireLogin 
	def post(self):
		community, member, access = GetCurrentCommunityAndMemberFromSession()
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
						for aMember in community.getActiveMembers():
							if argument == "message|%s" % aMember.key():
								try:
									messageMember = aMember
								except: 
									messageMember = None
									goAhead = False
								break
				if goAhead and messageMember:
					message = mail.EmailMessage()
					message.sender = community.contactEmail
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
		community, member, access = GetCurrentCommunityAndMemberFromSession()
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
									   'community': community, 
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
					self.redirect('/visit/look')
		else:
			self.redirect('/')

	@RequireLogin 
	def post(self):
		community, member, access = GetCurrentCommunityAndMemberFromSession()
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
		community, member, access = GetCurrentCommunityAndMemberFromSession()
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
							   'community': community, 
							   'member': memberToEdit,
							   'current_member': member,
							   'questions': community.getActiveMemberQuestions(),
							   'answers': memberToEdit.getAnswers(),
							   'refer_type': "member",
							   'show_leave_link': not community.memberIsOnlyOwner(member),
							   'search_locations': SEARCH_LOCATIONS,
							   })
			path = os.path.join(os.path.dirname(__file__), 'templates/visit/profile.html')
			self.response.out.write(template.render(path, template_values))
		else:
			self.redirect('/')
							 
	@RequireLogin 
	def post(self):
		community, member, access = GetCurrentCommunityAndMemberFromSession()
		if access:
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
				nicknameTheyWantToUse = htmlEscape(self.request.get("nickname")).strip()
				memberUsingNickname = community.memberWithNickname(nicknameTheyWantToUse)
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
				questions = Question.all().filter("community = ", community).filter("refersTo = ", "member").fetch(FETCH_NUMBER)
				for question in questions:
					foundAnswers = Answer.all().filter("question = ", question.key()).filter("referent =", memberToEdit.key()).fetch(FETCH_NUMBER)
					if foundAnswers:
						answerToEdit = foundAnswers[0]
					else:
						answerToEdit = Answer(question=question, community=community, referent=memberToEdit, referentType="member")
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
				self.redirect("/visit/look")
		else:
			self.redirect("/")
			
class ChangeMemberDraftsPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		community, member, access = GetCurrentCommunityAndMemberFromSession()
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
							   'community': community, 
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
		community, member, access = GetCurrentCommunityAndMemberFromSession()
		if access:
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
				self.redirect("/visit/look")
		else:
			self.redirect("/")
			
class LeaveCommunityPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		community, member, access = GetCurrentCommunityAndMemberFromSession()
		if access:
			template_values = GetStandardTemplateDictionaryAndAddMore({
						   	   'title': "Leave community", 
					   	   	   'title_extra': None, 
							   'community': community, 
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
		community, member, access = GetCurrentCommunityAndMemberFromSession()
		if access:
			if "leave|%s" % member.key() in self.request.arguments():
				if community.memberIsOnlyOwner(member):
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
		
class ResultFeedbackPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		community, member, access = GetCurrentCommunityAndMemberFromSession()
		if access:
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
				
				
