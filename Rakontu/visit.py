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
			for member in Member.all().filter("googleAccountID = ", user.user_id()):
				if member.rakontu and member.active:
					rakontusTheyAreAMemberOf.append(member.rakontu)
			for pendingMember in PendingMember.all().filter("email = ", user.email()):
				if pendingMember.rakontu:
					rakontusTheyAreInvitedTo.append(pendingMember.rakontu)
		template_values = GetStandardTemplateDictionaryAndAddMore({
						   'title': None,
						   'user': user, 
						   'rakontus_member_of': rakontusTheyAreAMemberOf,
						   'rakontus_invited_to': rakontusTheyAreInvitedTo,
						   'login_url': users.create_login_url("/"),
						   'logout_url': users.create_logout_url("/"),
						   "blurbs": BLURBS,
						   })
		path = os.path.join(os.path.dirname(__file__), FindTemplate('start.html'))
		self.response.out.write(template.render(path, template_values))

	def post(self):
		user = users.get_current_user()
		if user:
			if "visitRakontu" in self.request.arguments():
				rakontuKeyName = self.request.get('rakontu_key_name_visit')
			elif "joinRakontu" in self.request.arguments():
				rakontuKeyName = self.request.get('rakontu_key_name_join')
			if rakontuKeyName:
				rakontu = Rakontu.get_by_key_name(rakontuKeyName)
				if rakontu:
					member = GetCurrentMemberFromRakontuAndUser(rakontu, user)
					if rakontu and rakontu.active and member and member.active:
						if SetFirstThingsAndReturnWhetherMemberIsNew(rakontu, member): 
							self.redirect(member.firstVisitURL())
						else:
							self.redirect(rakontu.linkURL())
					else:
						self.redirect(START)
				else:
					self.redirect(START)
			else:
				self.redirect(START)
		else:
			self.redirect(START)
			
class NewMemberPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			template_values = GetStandardTemplateDictionaryAndAddMore({
							'title': TITLES["WELCOME"],
							'title_extra': member.nickname,
							'rakontu': rakontu, 
							'skin': rakontu.getSkinDictionary(),
							'current_member': member,
							'resources': rakontu.getNonDraftNewMemberResourcesAsDictionaryByCategory(),
							"blurbs": BLURBS,
							'have_helps': Help.all().count() > 0,
							})
			path = os.path.join(os.path.dirname(__file__), FindTemplate('visit/new.html'))
			self.response.out.write(template.render(path, template_values))
		else:
			self.redirect(START)
			
class BrowseEntriesPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if isFirstVisit: self.redirect(member.firstVisitURL())
			textsForGrid = []
			colHeaders = []
			rowColors = []
			currentSearch = GetCurrentSearchForMember(member)
			querySearch = None
			querySearch = GetObjectOfTypeFromURLQuery(self.request.query_string, "url_query_search_filter")
			if querySearch:
				currentSearch = querySearch
				member.viewSearch = querySearch
				member.viewEntriesList = []
				member.put()
			if currentSearch:
				entryRefs = currentSearch.getEntryQuestionRefs()
				creatorRefs = currentSearch.getCreatorQuestionRefs()
			else:
				entryRefs = None
				creatorRefs = None
			typeList = []
			i = 0
			for type in ENTRY_TYPES:
				if member.viewEntryTypes[i]:
					typeList.append(type)
				i += 1
			entries = rakontu.getNonDraftEntriesOfTypesInListBetweenDateTimesInReverseTimeOrder(typeList, member.getViewStartTime(), member.viewTimeEnd)
			skinDict = rakontu.getSkinDictionary()
			if entries:
				entriesThatMatchNewSearch = []
				entriesToShow = []
				for entry in entries:
					if currentSearch:
						if member.viewEntriesList:
							goAhead = entry.key() in member.viewEntriesList
							if goAhead:
								entriesToShow.append(entry)
						else:
							goAhead = entry.satisfiesSearchCriteria(currentSearch, entryRefs, creatorRefs)
							if goAhead:
								entriesThatMatchNewSearch.append(entry)
								entriesToShow.append(entry)
					else:
						entriesToShow.append(entry)
				entriesToShowConsideringNudgeFloor = []
				for entry in entriesToShow:
					if entry.nudgePointsForMemberViewOptions(member.viewNudgeCategories) >= member.viewNudgeFloor:
						entriesToShowConsideringNudgeFloor.append(entry)
				if entriesToShowConsideringNudgeFloor:
					member.viewEntriesList = []
					for entry in entriesToShow:
						member.viewEntriesList.append(entry.key())
					member.put()
					(textsForGrid, colHeaders, rowColors) = self.buildGrid(rakontu, member, entriesToShowConsideringNudgeFloor, currentSearch, skinDict)
			template_values = GetStandardTemplateDictionaryAndAddMore({
							'title': TITLES["HOME"],
							'rakontu': rakontu, 
							'skin': skinDict,
							'current_member': member, 
							'rows_cols': textsForGrid, 
							'col_headers': colHeaders, 
							'row_colors': rowColors,
							'has_entries': len(textsForGrid) > 0,
							'shared_searches': rakontu.getNonPrivateSavedSearches(),
							'member_searches': member.getPrivateSavedSearches(),
							'current_search': currentSearch,
							'member_time_frame_string': member.getFrameStringForViewTimeFrame(),
							'min_time': RelativeTimeDisplayString(member.getViewStartTime(), member),
							'max_time': RelativeTimeDisplayString(member.viewTimeEnd, member),
							})
			path = os.path.join(os.path.dirname(__file__), FindTemplate('visit/home.html'))
			self.response.out.write(template.render(path, template_values))
		else:
			self.redirect(START)
			
	def buildGrid(self, rakontu, member, entries, currentSearch, skinDict):
		textsForGrid = []
		colHeaders = []
		rowColors = []

		maxTime = member.viewTimeEnd
		minTime = member.getViewStartTime()
		maxNudgePoints = -9999999
		minNudgePoints = -9999999
		minActivityPoints = -9999999
		maxActivityPoints = -9999999
		for entry in entries:
			timeToCheck = entry.lastPublishedOrAnnotated()
			shouldBeCounted = timeToCheck >= minTime and timeToCheck < maxTime 
			if shouldBeCounted: 
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
		
		for row in range(numRows):
			rowColors.append(HexColorStringForRowIndex(row, skinDict))
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
				entryCount = 0
				for entry in entries:
					nudgePoints = entry.nudgePointsForMemberViewOptions(member.viewNudgeCategories)
					shouldBeInRow = nudgePoints >= startNudgePoints and nudgePoints < endNudgePoints
					timeToCheck = entry.lastPublishedOrAnnotated()
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
									nameString = ' (<a href="/%s/%s?%s">%s</a>, ' % (DIRS["dir_visit"], URLS["url_member"], entry.creator.urlQuery(), entry.creator.nickname)
								else:
									nameString = " (%s, " % entry.creator.nickname
							else:
								if entry.character.active:
									nameString = ' (<a href="/%s/%s?%s">%s</a>, ' % (DIRS["dir_visit"], URLS["url_character"], entry.character.urlQuery(), entry.character.name)
								else:
									nameString = " (%s, " % entry.character.name
							dateTimeString = " %s)" % RelativeTimeDisplayString(entry.published, member)
							if entry.text_formatted:
								textString = ": %s" % upToWithLink(stripTags(entry.text_formatted), DEFAULT_DETAILS_TEXT_LENGTH, entry.linkURL())
							else:
								textString = ""
						else:
							nameString = ""
							textString = ""
							dateTimeString = ""
						text = '<p>%s <span style="font-size:%s%%">%s</span>%s%s%s</p>' % \
							(entry.getImageLinkForType(), fontSizePercent, entry.linkString(), nameString, dateTimeString, textString)
						textsInThisCell.append(text)
					entryCount += 1
				textsInThisRow.append(textsInThisCell)
			textsForGrid.append(textsInThisRow)
		textsForGrid.reverse()
		return (textsForGrid, colHeaders, rowColors)
			
	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			search = GetCurrentSearchForMember(member)
			# time frame
			if "changeTimeFrame" in self.request.arguments():
				member.viewEntriesList = []
				member.setViewTimeFrameFromTimeFrameString(self.request.get("timeFrame"))
				member.put()
				self.redirect(rakontu.linkURL())
			elif "setToLast" in self.request.arguments():
				if rakontu.lastPublish:
					member.viewTimeEnd = rakontu.lastPublish + timedelta(seconds=10)
				else:
					member.viewTimeEnd = datetime.now(tz=pytz.utc)
				member.viewEntriesList = []
				member.put()
				self.redirect(rakontu.linkURL())
			elif "setToFirst" in self.request.arguments():
				if rakontu.firstPublish:
					member.setTimeFrameToStartAtFirstPublish()
				else:
					member.viewTimeEnd = datetime.now(tz=pytz.utc)
				member.viewEntriesList = []
				member.put()
				self.redirect(rakontu.linkURL())
			elif "moveTimeBack" in self.request.arguments() or "moveTimeForward" in self.request.arguments():
				if "moveTimeBack" in self.request.arguments():
					member.viewTimeEnd = member.viewTimeEnd - timedelta(seconds=member.viewTimeFrameInSeconds)
				else:
					member.viewTimeEnd = member.viewTimeEnd + timedelta(seconds=member.viewTimeFrameInSeconds)
				if rakontu.firstPublish and member.getViewStartTime() < rakontu.firstPublish:
				 	member.setTimeFrameToStartAtFirstPublish()
				if member.viewTimeEnd > datetime.now(tz=pytz.utc):
					member.viewTimeEnd = datetime.now(tz=pytz.utc)
				member.viewEntriesList = []
				member.put()
				self.redirect(rakontu.linkURL())
			elif "refreshView" in self.request.arguments():
				if rakontu.lastPublish:
					member.viewTimeEnd = rakontu.lastPublish + timedelta(seconds=10)
				else:
					member.viewTimeEnd = datetime.now(tz=pytz.utc)
				member.viewEntriesList = []
				member.put()
				self.redirect(rakontu.linkURL())
				
			# entry types
			elif "changeEntryTypesShowing" in self.request.arguments():
				member.viewEntryTypes = []
				for i in range(len(ENTRY_TYPES)):
					member.viewEntryTypes.append(self.request.get("showEntryType|%s" % i) == "yes")
				member.viewEntriesList = []
				member.put()
				self.redirect(rakontu.linkURL())

			# nudges
			elif "changeNudgeCategoriesShowing" in self.request.arguments():
				member.viewNudgeCategories = []
				for i in range(NUM_NUDGE_CATEGORIES):
					member.viewNudgeCategories.append(self.request.get("showCategory|%s" % i) == "yes")
				member.viewEntriesList = []
				oldValue = member.viewNudgeFloor
				try:
					member.viewNudgeFloor = int(self.request.get("nudgeFloor"))
				except:
					member.viewNudgeFloor = oldValue
				member.put()
				self.redirect(rakontu.linkURL())
				
			# search filter
			elif "loadAndApplySavedSearch" in self.request.arguments():
				if self.request.get("savedSearch") != "(%s)" % TERMS["term_choose"]:
					searchKey = self.request.get("savedSearch")
					if searchKey:
						search = SavedSearch.get(searchKey)
						if search:
							member.viewSearch = search
							member.viewEntriesList = []
							member.put()
							self.redirect(rakontu.linkURL())
							return
					else:
						self.redirect(rakontu.linkURL())
				else:
					self.redirect(rakontu.linkURL())
			elif "stopApplyingSearch" in self.request.arguments():
					member.viewSearch = None
					member.viewEntriesList = []
					member.put()
					self.redirect(rakontu.linkURL())
			elif "makeNewSavedSearch" in self.request.arguments():
					member.viewSearch = None
					member.viewEntriesList = []
					member.put()
					self.redirect(BuildURL("dir_visit", "url_search_filter", rakontu=rakontu))
			elif "changeSearch"  in self.request.arguments():
				if search:
					self.redirect(BuildURL("dir_visit", "url_search_filter", rakontu=rakontu))
				else:
					member.viewSearch = None
					member.viewEntriesList = []
					member.put()
					self.redirect(BuildURL("dir_visit", "url_search_filter", rakontu=rakontu))
			elif "copySearch"  in self.request.arguments():
				newSearch = SavedSearch(key_name=KeyName("filter"), rakontu=rakontu, creator=member)
				newSearch.copyDataFromOtherSearchAndPut(search)
				member.viewSearch = newSearch
				member.viewEntriesList = []
				member.put()
				self.redirect(BuildURL("dir_visit", "url_search_filter", rakontu=rakontu))

			# other options
			elif "toggleViewHomeOptionsOnTop" in self.request.arguments():
				member.viewHomeOptionsOnTop = not member.viewHomeOptionsOnTop
				member.put()
				self.redirect(rakontu.linkURL())
			elif "toggleShowDetails" in self.request.arguments():
				member.viewDetails = not member.viewDetails
				member.put()
				self.redirect(rakontu.linkURL())
			elif "printSearchResults"  in self.request.arguments():
				self.redirect(BuildURL("dir_liaise", "url_print_search", rakontu=rakontu))
			elif "exportSearchResults"  in self.request.arguments():
				self.redirect(BuildURL("dir_manage", "url_export_search", rakontu=rakontu))
		else:
			self.redirect(START)
			
class ReadEntryPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if isFirstVisit: self.redirect(member.firstVisitURL())
			entry = GetObjectOfTypeFromURLQuery(self.request.query_string, "url_query_entry")
			if entry:
				curating = GetStringOfTypeFromURLQuery(self.request.query_string, "url_query_curate") == URL_OPTIONS["url_query_curate"]
				showVersions = GetStringOfTypeFromURLQuery(self.request.query_string, "url_query_versions") == URL_OPTIONS["url_query_versions"]
				textsForGrid, colHeaders, rowColors = self.buildGrid(entry, member, rakontu, curating)
				thingsUserCanDo = self.buildThingsUserCanDo(entry, member, rakontu, curating)
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
								   'rakontu': rakontu, 
								   'skin': rakontu.getSkinDictionary(),
								   'current_member': member,
								   'current_member_key': member.key(),
								   'curating': curating,
								   'entry': entry,
								   # to show above grid
								   'attachments': entry.getAttachments(),
 								   'retold_links_incoming': entry.getIncomingLinksOfType("retold"),
 								   'reminded_links_incoming': entry.getIncomingLinksOfType("reminded"),
 								   'related_links_both_ways': entry.getLinksOfType("related"),
 								   'included_links_incoming_from_invitations': entry.getIncomingLinksOfType("responded"),
 								   'included_links_incoming_from_collages': entry.getIncomingLinksOfType("included"),
								   'included_links_outgoing': includedLinksOutgoing,
								   'referenced_links_outgoing': referencedLinksOutgoing,
								   # grid
								   'rows_cols': textsForGrid, 
								   'col_headers': colHeaders, 
								   'text_to_display_before_grid': TEMPLATE_TERMS["template_annotations"],
								   'row_colors': rowColors,
								   'grid_form_url': self.request.uri, 
								   # actions
								   'things_member_can_do': thingsUserCanDo,
								   # versions
								   'show_versions': showVersions,
								   'versions': entry.getTextVersionsInReverseTimeOrder(),
								   })
				member.lastReadAnything = datetime.now(tz=pytz.utc)
				member.nudgePoints += rakontu.getMemberNudgePointsForEvent("reading")
				member.put()
				path = os.path.join(os.path.dirname(__file__), FindTemplate('visit/read.html'))
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect(BuildResultURL("entryNotFound", rakontu=rakontu))
		else:
			self.redirect(START)
			
	def buildGrid(self, entry, member, rakontu, curating):
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
				rowColors.append(HexColorStringForRowIndex(rowIndex, rakontu.getSkinDictionary()))
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
							text = ItemDisplayStringForGrid(item, member, curating, showingMember=False, showDetails=member.viewDetails)
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
		return textsForGrid, colHeaders, rowColors
			
	def buildThingsUserCanDo(self, entry, member, rakontu, curating):
		thingsUserCanDo = {}
		if not entry.memberCanNudge(member):
			nudgePointsMemberCanAssign = 0
		else:
			nudgePointsMemberCanAssign = max(0, rakontu.maxNudgePointsPerEntry - entry.getTotalNudgePointsForMember(member))
		rakontuHasQuestionsForThisEntryType = len(rakontu.getActiveQuestionsOfType(entry.type)) > 0
		memberCanAnswerQuestionsAboutThisEntry = len(entry.getAnswersForMember(member)) == 0
		memberCanAddNudgeToThisEntry = nudgePointsMemberCanAssign > 0
		displayType = DisplayTypeForEntryType(entry.type)
		# retelling
		if entry.isStory():
			key = TERMS["term_tell_another_version_of_this_story"]
			thingsUserCanDo[key] = BuildURL("dir_visit","url_retell", entry.urlQuery())
		# reminding
		if entry.isStory() or entry.isResource():
			key = TERMS["term_tell_a_story_this_reminds_you_of"]
			thingsUserCanDo[key] = BuildURL("dir_visit", "url_remind", entry.urlQuery())
		# responding
		if entry.isInvitation():
			key = TERMS["term_respond_to_invitation"]
			thingsUserCanDo[key] = BuildURL("dir_visit", "url_respond", entry.urlQuery())
		# answering questions
		if rakontuHasQuestionsForThisEntryType and memberCanAnswerQuestionsAboutThisEntry:
			key = "%s %s" % (TERMS["term_answer_questions_about_this"], displayType)
			thingsUserCanDo[key] = BuildURL("dir_visit", "url_answers", entry.urlQuery())
		# comment
		key = "%s %s" % (TERMS["term_make_a_comment"], displayType)
		thingsUserCanDo[key] = BuildURL("dir_visit", URLForAnnotationType("comment"), entry.urlQuery())
		# tag
		key = "%s %s" % (TERMS["term_tag_this"], displayType)
		thingsUserCanDo[key] = BuildURL("dir_visit", URLForAnnotationType("tag set"), entry.urlQuery())
		# request
		key = "%s %s" % (TERMS["term_request_something_about_this"], displayType)
		thingsUserCanDo[key] = BuildURL("dir_visit", URLForAnnotationType("request"), entry.urlQuery())
		# relate
		key = TERMS["term_relate_entry_to_others"]
		thingsUserCanDo[key] = BuildURL("dir_visit", "url_relate", entry.urlQuery())
		# nudge
		if memberCanAddNudgeToThisEntry:
			key = "%s %s" % (TERMS["term_nudge_this"], displayType)
			thingsUserCanDo[key] = BuildURL("dir_visit", URLForAnnotationType("nudge"), entry.urlQuery())
		# curate
		if member.isCurator():
			if curating:
				key = "%s %s" % (TERMS["term_stop_curating_this"], displayType)
				thingsUserCanDo[key] = BuildURL("dir_visit", "url_read", "%s" % (entry.urlQuery()))
			else:
				key = "%s %s" % (TERMS["term_curate_this"], displayType)
				thingsUserCanDo[key] = BuildURL("dir_visit", "url_read", "%s&%s=%s" % (entry.urlQuery(), URL_OPTIONS["url_query_curate"], URL_OPTIONS["url_query_curate"]))
		# change
		if entry.creator.key() == member.key():
			key = "%s %s" % (TERMS["term_change_this"], displayType)
			thingsUserCanDo[key] = BuildURL("dir_visit", URLForEntryType(entry.type), entry.urlQuery())
		# print
		if member.isLiaison():
			key = "%s %s" % (TERMS["term_print_this"], displayType)
			thingsUserCanDo[key] = BuildURL("dir_liaise", "url_print_entry", entry.urlQuery())
		return thingsUserCanDo
			
	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			entry = GetObjectOfTypeFromURLQuery(self.request.query_string, "url_query_entry")
			if "doSomething" in self.request.arguments():
				self.redirect(self.request.get("nextAction"))
			elif "changeNudgeCategoriesShowing" in self.request.arguments():
				member.viewNudgeCategories = []
				for i in range(NUM_NUDGE_CATEGORIES):
					member.viewNudgeCategories.append(self.request.get("showCategory|%s" % i) == "yes")
				member.put()
				self.redirect(self.request.uri)
			elif "toggleShowDetails" in self.request.arguments():
				member.viewDetails = not member.viewDetails
				member.put()
				self.redirect(self.request.uri)
			elif "showVersions" in self.request.arguments():
				url = BuildURL("dir_visit", "url_read", "%s&%s=%s" % (entry.urlQuery(), URL_OPTIONS["url_query_versions"], URL_OPTIONS["url_query_versions"]))
				self.redirect(url)
			elif "hideVersions" in self.request.arguments():
				url = BuildURL("dir_visit", "url_read", "%s" % (entry.urlQuery()))
				self.redirect(url)
			elif "flag|%s" % entry.key() in self.request.arguments() or "unflag|%s" % entry.key() in self.request.arguments():
				curating = GetStringOfTypeFromURLQuery(self.request.query_string, "url_query_curate") == URL_OPTIONS["url_query_curate"]
				if entry and curating:
					if "flag|%s" % entry.key() in self.request.arguments():
						entry.flaggedForRemoval = True
						entry.put()
					elif "unflag|%s" % entry.key() in self.request.arguments():
						entry.flaggedForRemoval = False
						entry.put()
				self.redirect(self.request.uri)
			else:
				for item in entry.getAllNonDraftDependents():
					if "flag|%s" % item.key() in self.request.arguments():
						item.flaggedForRemoval = True
						item.put()
					elif "unflag|%s" % item.key() in self.request.arguments():
						item.flaggedForRemoval = False
						item.put()
				self.redirect(self.request.uri)
		else:
			self.redirect(START)
			
class ReadAnnotationPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if isFirstVisit: self.redirect(member.firstVisitURL())
			annotation = GetObjectOfTypeFromURLQuery(self.request.query_string, "url_query_annotation")
			if annotation:
				template_values = GetStandardTemplateDictionaryAndAddMore({
								   'title': annotation.displayString(includeType=False), 
								   'rakontu': rakontu, 
								   'skin': rakontu.getSkinDictionary(),
								   'current_member': member,
								   'current_member_key': member.key(),
								   'annotation': annotation,
								   'included_links_outgoing': annotation.entry.getOutgoingLinksOfType("included"),
								   })
				member.lastReadAnything = datetime.now(tz=pytz.utc)
				member.nudgePoints += rakontu.getMemberNudgePointsForEvent("reading")
				member.put()
				path = os.path.join(os.path.dirname(__file__), FindTemplate('visit/readAnnotation.html'))
				self.response.out.write(template.render(path, template_values))
		else:
			self.redirect(START)
			
	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			annotation = GetObjectOfTypeFromURLQuery(self.request.query_string, "url_query_annotation")
			if annotation:
				if "toggleRequestCompleted" in self.request.arguments():
					annotation.completedIfRequest = not annotation.completedIfRequest
					annotation.put()
			self.redirect(self.request.uri)
		else:
			self.redirect(rakontu.linkURL())

class SeeRakontuPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if isFirstVisit: self.redirect(member.firstVisitURL())
			nudgeCategoryAndQuestionStrings = []
			i = 0
			for category in rakontu.nudgeCategories:
				if category:
					nudgeCategoryAndQuestionStrings.append("%s (%s)" % (category, rakontu.nudgeCategoryQuestions[i]))
				i += 1
			nudgePointStrings = []
			i = 0
			for eventType in EVENT_TYPES:
				if i > 0: # skip zero for nudges
					nudgePointStrings.append("%s: %s %s" % (EVENT_TYPES_DISPLAY[i].capitalize(), rakontu.memberNudgePointsPerEvent[i], TERMS["term_points"]))
				i += 1
			nudgePointString = ", ".join(nudgePointStrings) + "."
			activityPointStrings = []
			i = 0
			for eventType in EVENT_TYPES:
				activityPointStrings.append("%s: %s %s" % (EVENT_TYPES_DISPLAY[i].capitalize(), rakontu.entryActivityPointsPerEvent[i], TERMS["term_points"]))
				i += 1
			activityPointString = ", ".join(activityPointStrings) + "."
			charactersAllowedFor = []
			i = 0
			for entryType in ENTRY_AND_ANNOTATION_TYPES:
				if rakontu.allowCharacter[i]:
					charactersAllowedFor.append(ENTRY_AND_ANNOTATION_TYPES_PLURAL_DISPLAY[i].capitalize())
				i += 1
			charactersAllowedForString = ", ".join(charactersAllowedFor) + "."
			template_values = GetStandardTemplateDictionaryAndAddMore({
							   'title': TITLES["ABOUT"], 
							   'rakontu': rakontu, 
							   'skin': rakontu.getSkinDictionary(),
							   'current_member': member,
							   'rakontu_members': rakontu.getActiveMembers(),
							   'characters': rakontu.getActiveCharacters(),
							   'nudge_category_and_question_strings': nudgeCategoryAndQuestionStrings,
							   'nudge_point_string': nudgePointString,
							   'activity_point_string': activityPointString,
							   'chars_allowed_string': charactersAllowedForString,
							   })
			path = os.path.join(os.path.dirname(__file__), FindTemplate('visit/rakontu.html'))
			self.response.out.write(template.render(path, template_values))
		else:
			self.redirect(START)
			
class SeeRakontuMembersPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if isFirstVisit: self.redirect(member.firstVisitURL())
			template_values = GetStandardTemplateDictionaryAndAddMore({
							   'title': TITLES["MEMBERS"], 
							   'rakontu': rakontu, 
							   'skin': rakontu.getSkinDictionary(),
							   'current_member': member,
							   'rakontu_members': rakontu.getActiveMembers(),
							   })
			path = os.path.join(os.path.dirname(__file__), FindTemplate('visit/members.html'))
			self.response.out.write(template.render(path, template_values))
		else:
			self.redirect(START)
   
class SeeMemberPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if isFirstVisit: self.redirect(member.firstVisitURL())
			memberToSee = GetObjectOfTypeFromURLQuery(self.request.query_string, "url_query_member")
			curating = member.isCurator() and GetStringOfTypeFromURLQuery(self.request.query_string, "url_query_curate") == URL_OPTIONS["url_query_curate"]
			if memberToSee:
				textsForGrid, colHeaders = self.buildGrid(member, memberToSee, rakontu, curating)
				statNames, stats = self.collectStats(memberToSee)
				template_values = GetStandardTemplateDictionaryAndAddMore({
							   'title': TITLES["MEMBER"], 
					   		   'title_extra': member.nickname, 
					   		   'rakontu': rakontu, 
					   		   'skin': rakontu.getSkinDictionary(),
					   		   'current_member': member,
					   		   'member': memberToSee,
					   		   'answers': memberToSee.getAnswers(),
					   		   'rows_cols': textsForGrid,
					   		   'col_headers': colHeaders,
					   		   'text_to_display_before_grid': "%s %s" % (TERMS["term_entries_contributed_by"], memberToSee.nickname),
					   		   'grid_form_url': self.request.uri, 
					   		   'no_profile_text': NO_PROFILE_TEXT,
					   		   'stat_names': statNames,
					   		   'stats': stats,
					   		   'curating': curating,
					   		   })
				path = os.path.join(os.path.dirname(__file__), FindTemplate('visit/member.html'))
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect(rakontu.linkURL())
		else:
			self.redirect(START)
			
	def buildGrid(self, member, memberToSee, rakontu, curating):
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
							text = ItemDisplayStringForGrid(item, member, curating, showingMember=not memberToSee.isLiaison(), showDetails=member.viewDetails)
							textsInThisCell.append(text)
					textsInThisRow.append(textsInThisCell)
				textsForGrid.append(textsInThisRow)
			textsForGrid.reverse()
		else:
			textsForGrid = None
			colHeaders = None
		return textsForGrid, colHeaders
	
	def collectStats(self, memberToSee):
		statNames = []
		stats = []
		for type in ENTRY_TYPES:
			stats.append(Entry.all().filter("creator = ", memberToSee.key()).filter("type = ", type).filter("draft = ", False).count())
		statNames.extend(ENTRY_TYPES_PLURAL_DISPLAY)
		for type in ANNOTATION_TYPES:
			stats.append(Annotation.all().filter("creator = ", memberToSee.key()).filter("type = ", type).filter("draft = ", False).count())
		statNames.extend(ANNOTATION_TYPES_PLURAL_DISPLAY)
		stats.append(Answer.all().filter("creator = ", memberToSee.key()).filter("draft = ", False).count())
		statNames.append(TERMS["term_answers"])
		return statNames, stats

	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			memberToSee = GetObjectOfTypeFromURLQuery(self.request.query_string, "url_query_member")
			if memberToSee:
				if "toggleShowDetails" in self.request.arguments():
					member.viewDetails = not member.viewDetails
					member.put()
					self.redirect(self.request.uri)
				elif "message|%s" % memberToSee.key() in self.request.arguments():
						if not memberToSee.isOnlineMember:
							if memberToSee.liaison and  memberToSee.liaison.active:
								memberToSendMessageTo = memberToSee.liaison
							else:
								memberToSendMessageTo = None
						else:
							memberToSendMessageTo = memberToSee
						if memberToSendMessageTo:
							message = mail.EmailMessage()
							message.sender = rakontu.contactEmail
							message.subject = htmlEscape(self.request.get("subject"))
							message.to = memberToSendMessageTo.googleAccountEmail
							message.body = htmlEscape(self.request.get("message"))
							message.send()
							self.redirect(BuildResultURL("messagesent", rakontu=rakontu))
						else:
							self.redirect(BuildResultURL("memberNotFound", rakontu=rakontu))
				else:
					allItems = memberToSee.getAllItemsAttributedToMember()
					allItems.extend(memberToSee.getNonDraftLiaisonedEntries())
					allItems.extend(memberToSee.getNonDraftLiaisonedAnnotations())
					allItems.extend(memberToSee.getNonDraftLiaisonedAnswers())
					for item in allItems:
						if "flag|%s" % item.key() in self.request.arguments():
							item.flaggedForRemoval = True
							item.put()
						elif "unflag|%s" % item.key() in self.request.arguments():
							item.flaggedForRemoval = False
							item.put()
					self.redirect(self.request.uri)
			else:
				self.redirect(BuildResultURL("memberNotFound", rakontu=rakontu))
		else:
			self.redirect(START)
   
class AskGuidePage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if isFirstVisit: self.redirect(member.firstVisitURL())
			memberToSee = GetObjectOfTypeFromURLQuery(self.request.query_string, "url_query_member")
			if memberToSee:
				template_values = GetStandardTemplateDictionaryAndAddMore({
							   'title': TITLES["GUIDE"], 
					   		   'title_extra': member.nickname, 
					   		   'rakontu': rakontu, 
					   		   'skin': rakontu.getSkinDictionary(),
					   		   'current_member': member,
					   		   'member': memberToSee,
					   		   'grid_form_url': self.request.uri, 
					   		   })
				path = os.path.join(os.path.dirname(__file__), FindTemplate('visit/ask.html'))
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect(rakontu.linkURL())
		else:
			self.redirect(START)

	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			messageMember = None
			goAhead = True
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
					message.subject = "Rakontu %s - %s" % (TERMS["term_question"], htmlEscape(self.request.get("subject")))
					message.to = messageMember.googleAccountEmail
					message.body = htmlEscape(self.request.get("message"))
					message.send()
					self.redirect(BuildResultURL("messagesent", rakontu=rakontu))
				else:
					self.redirect(BuildResultURL("memberNotFound", rakontu=rakontu))
		else:
			self.redirect(START)
   
class SeeCharacterPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if isFirstVisit: self.redirect(member.firstVisitURL())
			character = GetObjectOfTypeFromURLQuery(self.request.query_string, "url_query_character")
			curating = member.isCurator() and GetStringOfTypeFromURLQuery(self.request.query_string, "url_query_curate") == URL_OPTIONS["url_query_curate"]
			if character:
				textsForGrid, colHeaders = self.buildGrid(member, character, rakontu, curating)
				template_values = GetStandardTemplateDictionaryAndAddMore({
							   	   'title': TITLES["CHARACTER"], 
					   		   	   'title_extra': character.name, 
								   'rakontu': rakontu, 
								   'skin': rakontu.getSkinDictionary(),
								   'current_member': member,
								   'character': character,
								   'answers': character.getAnswers(),
					   		   	   'rows_cols': textsForGrid,
					   		   	   'text_to_display_before_grid': "%s's entries" % character.name,
					   		   	   'grid_form_url': self.request.uri,
					   		   	   'col_headers': colHeaders,
					   		   	   'curating': curating,
								   })
				path = os.path.join(os.path.dirname(__file__), FindTemplate('visit/character.html'))
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect(rakontu.linkURL())
		else:
			self.redirect(START)
			
	def buildGrid(self, member, character, rakontu, curating):
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
							text = ItemDisplayStringForGrid(item, member, curating, showingMember=True, showDetails=member.viewDetails)
							textsInThisCell.append(text)
					textsInThisRow.append(textsInThisCell)
				textsForGrid.append(textsInThisRow)
			textsForGrid.reverse()
		else:
			textsForGrid = None
			colHeaders = None
		return textsForGrid, colHeaders

	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			character = GetObjectOfTypeFromURLQuery(self.request.query_string, "url_query_character")
			if character:
				if "toggleShowDetails" in self.request.arguments():
					member.viewDetails = not member.viewDetails
					member.put()
					self.redirect(self.request.uri)
				else:
					for item in character.getAllItemsAttributedToCharacter():
						if "flag|%s" % item.key() in self.request.arguments():
							item.flaggedForRemoval = True
							item.put()
						elif "unflag|%s" % item.key() in self.request.arguments():
							item.flaggedForRemoval = False
							item.put()
					self.redirect(self.request.uri)
			else:
				self.redirect(rakontu.linkURL())
		else:
			self.redirect(START)
   
class ChangeMemberProfilePage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if isFirstVisit: self.redirect(member.firstVisitURL())
			offlineMember = GetObjectOfTypeFromURLQuery(self.request.query_string, "url_query_member")
			if offlineMember:
				memberToEdit = offlineMember
			else:
				memberToEdit = member
			template_values = GetStandardTemplateDictionaryAndAddMore({
							   'title': TITLES["PREFERENCES_FOR"], 
						   	   'title_extra': memberToEdit.nickname, 
							   'rakontu': rakontu, 
							   'skin': rakontu.getSkinDictionary(),
							   'member': memberToEdit,
							   'current_member': member,
							   'questions': rakontu.getActiveMemberQuestions(),
							   'answers': memberToEdit.getAnswers(),
							   'refer_type': "member",
							   'refer_type_display': DisplayTypeForQuestionReferType("member"),
							   'show_leave_link': not rakontu.memberIsOnlyOwner(member),
							   'search_locations': SEARCH_LOCATIONS,
							   'search_locations_display': SEARCH_LOCATIONS_DISPLAY,
							   'my_offline_members': rakontu.getActiveOfflineMembersForLiaison(member),
							   })
			path = os.path.join(os.path.dirname(__file__), FindTemplate('visit/profile.html'))
			self.response.out.write(template.render(path, template_values))
		else:
			self.redirect(START)
							 
	@RequireLogin  
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
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
				if memberUsingNickname and memberUsingNickname.key() != memberToEdit.key():
					self.redirect(BuildResultURL("nicknameAlreadyInUse", rakontu=rakontu))
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
				memberToEdit.showAttachedImagesInline = self.request.get("showAttachedImagesInline") == "yes"
				if memberToEdit.isOnlineMember:
					wasLiaison = memberToEdit.isLiaison()
					for i in range(3):
						memberToEdit.helpingRoles[i] = self.request.get("helpingRole%s" % i) == "helpingRole%s" % i
					if not memberToEdit.isLiaison() and wasLiaison:
						offlineMembers = rakontu.getActiveOfflineMembersForLiaison(memberToEdit)
						if len(offlineMembers):
							self.redirect(BuildResultURL("cannotGiveUpLiaisonWithMembers", rakontu=rakontu))
							return
					text = self.request.get("guideIntro")
					format = self.request.get("guideIntro_format").strip()
					memberToEdit.guideIntro = text
					memberToEdit.guideIntro_formatted = db.Text(InterpretEnteredText(text, format))
					memberToEdit.guideIntro_format = format
					memberToEdit.preferredTextFormat = self.request.get("preferredTextFormat")
				memberToEdit.put()
				questions = rakontu.getActiveQuestionsOfType("member")
				for question in questions:
					foundAnswer = memberToEdit.getAnswerForMemberQuestion(question)
					if foundAnswer:
						answerToEdit = foundAnswer
					else:
						answerToEdit = Answer(
											key_name=KeyName("answer"), 
											rakontu=rakontu, 
											question=question, 
											referent=memberToEdit, 
											referentType="member")
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
					self.redirect(BuildURL("dir_liaise", "url_members", rakontu=rakontu))
				else:
					self.redirect(BuildURL("dir_visit", "url_member", memberToEdit.urlQuery()))
			else:
				self.redirect(rakontu.linkURL())
		else:
			self.redirect(START)
			
class ChangeMemberDraftsPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if isFirstVisit: self.redirect(member.firstVisitURL())
			offlineMember = GetObjectOfTypeFromURLQuery(self.request.query_string, "url_query_member")
			if offlineMember:
				memberToEdit = offlineMember
			else:
				memberToEdit = member
			draftAnswerEntries = memberToEdit.getEntriesWithDraftAnswers()
			firstDraftAnswerForEachEntry = []
			for entry in draftAnswerEntries:
				answers = memberToEdit.getDraftAnswersForEntry(entry)
				if answers:
					firstDraftAnswerForEachEntry.append(answers[0])
			template_values = GetStandardTemplateDictionaryAndAddMore({
							   'title': TITLES["DRAFTS_FOR"], 
						   	   'title_extra': memberToEdit.nickname, 
							   'rakontu': rakontu, 
							   'skin': rakontu.getSkinDictionary(),
							   'member': memberToEdit,
							   'current_member': member,
							   'draft_entries': memberToEdit.getDraftEntries(),
							   'refer_type': "member",
							   'refer_type_display': DisplayTypeForQuestionReferType("member"),
							   })
			path = os.path.join(os.path.dirname(__file__), FindTemplate('visit/drafts.html'))
			self.response.out.write(template.render(path, template_values))
		else:
			self.redirect(START)
							 
	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
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
						entry.removeAllDependents()
						db.delete(entry)
				for annotation in memberToEdit.getDraftAnnotations():
					if self.request.get("remove|%s" % annotation.key()) == "yes":
						db.delete(annotation)
				for entry in memberToEdit.getEntriesWithDraftAnswers():
					if self.request.get("removeAnswers|%s" % entry.key()) == "yes":
						answers = memberToEdit.getDraftAnswersForEntry(entry)
						for answer in answers:
							db.delete(answer)
				if offlineMember:
					self.redirect(BuildURL("dir_liaise", "url_members", rakontu=rakontu))
				else:
					self.redirect(BuildURL("dir_visit", "url_drafts", memberToEdit.urlQuery()))
			else:
				self.redirect(rakontu.linkURL())
		else:
			self.redirect(START)
			
class ChangeMemberFiltersPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if isFirstVisit: self.redirect(member.firstVisitURL())
			offlineMember = GetObjectOfTypeFromURLQuery(self.request.query_string, "url_query_member")
			if offlineMember:
				memberToEdit = offlineMember
			else:
				memberToEdit = member
			template_values = GetStandardTemplateDictionaryAndAddMore({
							   'title': TITLES["DRAFTS_FOR"], 
						   	   'title_extra': memberToEdit.nickname, 
							   'rakontu': rakontu, 
							   'skin': rakontu.getSkinDictionary(),
							   'member': memberToEdit,
							   'current_member': member,
							   'searches': member.getSavedSearches(),
							   'refer_type': "member",
							   'refer_type_display': DisplayTypeForQuestionReferType("member"),
							   'search_locations': SEARCH_LOCATIONS,
							   'search_locations_display': SEARCH_LOCATIONS_DISPLAY,
							   })
			path = os.path.join(os.path.dirname(__file__), FindTemplate('visit/filters.html'))
			self.response.out.write(template.render(path, template_values))
		else:
			self.redirect(START)
							 
	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
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
				for search in memberToEdit.getSavedSearches():
					if self.request.get("remove|%s" % search.key()) == "yes":
						search.deleteAllDependents()
						db.delete(search)
				if offlineMember:
					self.redirect(BuildURL("dir_liaise", "url_members", rakontu=rakontu))
				else:
					self.redirect(BuildURL("dir_visit", "url_filters", memberToEdit.urlQuery()))
			else:
				self.redirect(rakontu.linkURL())
		else:
			self.redirect(START)
			
class LeaveRakontuPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if isFirstVisit: self.redirect(member.firstVisitURL())
			member = GetObjectOfTypeFromURLQuery(self.request.query_string, "url_query_member")
			template_values = GetStandardTemplateDictionaryAndAddMore({
						   	   'title': TITLES["LEAVE_RAKONTU"], 
							   'rakontu': rakontu, 
							   'skin': rakontu.getSkinDictionary(),
							   'message': member.getKeyName(),
							   'current_member': member,
							   })
			path = os.path.join(os.path.dirname(__file__), FindTemplate('visit/leave.html'))
			self.response.out.write(template.render(path, template_values))
		else:
			self.redirect(START)
			
	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if "leave|%s" % member.key() in self.request.arguments():
				if rakontu.memberIsOnlyOwner(member):
					self.redirect(BuildResultURL("ownerCannotLeave", rakontu=rakontu))
					return
				else:
					member.active = False
					member.put()
					self.redirect(START)
			else:
				self.redirect(BuildURL("dir_visit", "url_preferences", member.urlQuery()))
		else:
			self.redirect(START)
		
class SavedSearchEntryPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if isFirstVisit: self.redirect(member.firstVisitURL())
			currentSearch = GetCurrentSearchForMember(member)
			questionsAndRefsDictList = []
			entryQuestions = rakontu.getActiveNonMemberQuestions()
			if entryQuestions:
				entryQuestionsAndRefsDictionary = {
					"result_preface": "entry", "afterAnyText": "%s:" % TERMS["term_of_these_answers_to_questions"],
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
					afterAnyText = "%s:" % TERMS["term_of_these_answers_to_questions_about_members_or_characters"]
				else:
					afterAnyText = "%s:" % TERMS["term_of_these_answers_to_questions_about_creators"]
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
							'title': TITLES["SEARCH_FILTER"],
							'rakontu': rakontu, 
							'skin': rakontu.getSkinDictionary(),
							'current_member': member, 
							'num_search_fields': NUM_SEARCH_FIELDS,
							'search_locations': SEARCH_LOCATIONS,
							'search_locations_display': SEARCH_LOCATIONS_DISPLAY,
							'any_or_all_choices': ANY_ALL,
							'any_or_all_choices_display': ANY_ALL_DISPLAY,
							'answer_comparison_types': ANSWER_COMPARISON_TYPES,
							'answer_comparison_types_display': ANSWER_COMPARISON_TYPES_DISPLAY,
							'current_search': currentSearch,
							'questions_and_refs_dict_list': questionsAndRefsDictList,
							})
			path = os.path.join(os.path.dirname(__file__), FindTemplate('visit/filter.html'))
			self.response.out.write(template.render(path, template_values))
		else:
			self.redirect(START)
			
	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			search = GetCurrentSearchForMember(member)
			if "deleteSearchByCreator" in self.request.arguments():
				if search:
					db.delete(search)
					member.viewSearch = None
					member.viewEntriesList = []
					member.put()
				self.redirect(rakontu.linkURL())
			elif "flagSearchByCurator" in self.request.arguments():
				if search:
					search.flaggedForRemoval = not search.flaggedForRemoval
					search.put()
					self.redirect(BuildURL("dir_visit", "url_search_filter", rakontu=rakontu))
				else:
					self.redirect(rakontu.linkURL())
			elif "removeSearchByManager" in self.request.arguments():
				if search:
					db.delete(search)
					member.viewSearch = None
					member.viewEntriesList = []
					member.put()
				self.redirect(rakontu.linkURL())
			elif "cancel" in self.request.arguments():
				self.redirect(rakontu.linkURL())
			elif "saveAs" in self.request.arguments() or "save" in self.request.arguments():
				if not search or "saveAs" in self.request.arguments():
					search = SavedSearch(key_name=KeyName("filter"), rakontu=rakontu, creator=member)
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
									ref = SavedSearchQuestionReference(key_name=KeyName("searchref"), rakontu=rakontu, search=search, question=question)
								ref.answer = answer
								ref.comparison = comparison
								ref.order = i
								ref.type = preface
								ref.put()
				member.viewSearch = search
				member.viewEntriesList = []
				member.put()
				self.redirect(rakontu.linkURL())
			else:
				self.redirect(rakontu.linkURL())
		else:
			self.redirect(START)
			
class ResultFeedbackPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			message = GetStringOfTypeFromURLQuery(self.request.query_string, "url_query_result")
			template_values = GetStandardTemplateDictionaryAndAddMore({
						   	   'title': TITLES["MESSAGE_TO_USER"], 
							   'system_message': TERMS["term_result"],
							   'message': message,
							   'results': RESULTS,
							   })
			path = os.path.join(os.path.dirname(__file__), FindTemplate('result.html'))
			self.response.out.write(template.render(path, template_values))
		else:
			self.redirect(START)
				
class ContextualHelpPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		# don't require access to rakontu, since administrator may be calling this from the admin or create pages
		lookup = GetStringOfTypeFromURLQuery(self.request.query_string, "url_query_help")
		help = Help.all().filter('name = ', lookup).get()
		if help:
			helpShortName = help.name.replace("_", " ").capitalize()
			template_values = GetStandardTemplateDictionaryAndAddMore({
						   	   'title': TITLES["HELP_ON"], 
					   	   	   'title_extra': helpShortName, 
							   'system_message': TERMS["term_help"],
							   'help': help,
							   })
			path = os.path.join(os.path.dirname(__file__), FindTemplate('help.html'))
			self.response.out.write(template.render(path, template_values))
		else:
			self.redirect(BuildResultURL("helpNotFound", rakontu=rakontu))
			
class GeneralHelpPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if isFirstVisit: self.redirect(member.firstVisitURL())
			template_values = GetStandardTemplateDictionaryAndAddMore({
							'title': TITLES["HELP"],
							'rakontu': rakontu, 
							'skin': rakontu.getSkinDictionary(),
							'current_member': member,
							'non_manager_resources': rakontu.getNonDraftHelpResourcesAsDictionaryByCategory(),
							'manager_resources': rakontu.getNonDraftManagerOnlyHelpResourcesAsDictionaryByCategory(),
							'guides': rakontu.getGuides(),
							'have_system_resources': HaveSystemResources(),
							})
			path = os.path.join(os.path.dirname(__file__), FindTemplate('visit/help.html'))
			self.response.out.write(template.render(path, template_values))
		else:
			self.redirect(START)
			
