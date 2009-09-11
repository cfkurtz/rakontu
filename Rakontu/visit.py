# --------------------------------------------------------------------------------------------
# RAKONTU
# Description: Rakontu is open source story sharing software.
# License: GPL 3.0
# Google Code Project: http://code.google.com/p/rakontu/
# --------------------------------------------------------------------------------------------

from utils import *

class StartPage(ErrorHandlingRequestHander):
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
						self.redirect(NoRakontuAndMemberURL())
				else:
					self.redirect(NoRakontuAndMemberURL())
			else:
				self.redirect(START)
		else:
			self.redirect(START)
			
class NewMemberPage(ErrorHandlingRequestHander):
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
							'have_helps': HaveHelps(),
							})
			path = os.path.join(os.path.dirname(__file__), FindTemplate('visit/new.html'))
			self.response.out.write(template.render(path, template_values))
		else:
			self.redirect(NoRakontuAndMemberURL())
			
class BrowseEntriesPage(ErrorHandlingRequestHander):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if isFirstVisit: self.redirect(member.firstVisitURL())
			curating = member.isCurator() and GetStringOfTypeFromURLQuery(self.request.query_string, "url_query_curate") == URL_OPTIONS["url_query_curate"]
			viewOptions = member.getViewOptionsForLocation("home")
			currentSearch = viewOptions.search
			querySearch = GetObjectOfTypeFromURLQuery(self.request.query_string, "url_query_search_filter")
			if querySearch:
				currentSearch = querySearch
				member.setSearchForLocation("home", currentSearch)
			skinDict = rakontu.getSkinDictionary()
			(entries, overLimitWarning, numItemsBeforeLimitTruncation) = ItemsMatchingViewOptionsForMemberAndLocation(member, "home")
			textsForGrid, rowColors = self.buildGrid(entries, member, skinDict, viewOptions.showDetails, curating)
			template_values = GetStandardTemplateDictionaryAndAddMore({
							'title': TITLES["HOME"],
							'rakontu': rakontu, 
							'skin': skinDict,
							'current_member': member, 
							# grid
							'rows_cols': textsForGrid, 
							'row_colors': rowColors,
							'num_items_before_truncation': numItemsBeforeLimitTruncation,
							'max_num_items': MAX_ITEMS_PER_GRID_PAGE,
							'too_many_items_warning': overLimitWarning,
							'show_details': viewOptions.showDetails,
							'grid_options_on_top': viewOptions.showOptionsOnTop,
							'curating': curating,
							# grid options
							'location': "home",
							'include_time_range': True,
									'member_time_frame_string': viewOptions.getFrameStringForViewTimeFrame(),
									'min_time': TimeDisplay(viewOptions.getStartTime(), member),
									'max_time': TimeDisplay(viewOptions.endTime, member),
								'include_entry_types': True,
											'entry_types_to_show': viewOptions.entryTypes,

							'include_annotation_types': False,
							
							'include_nudges': True,
							'include_nudge_floor': True,
							'nudge_categories_to_show': viewOptions.nudgeCategories,
							'nudge_floor': viewOptions.nudgeFloor,
							
							'include_search': True,
							'shared_searches': rakontu.getNonPrivateSavedSearches(),
							'member_searches': member.getPrivateSavedSearches(),
							'current_search': currentSearch,
							
							'include_curate': member.isCurator(),
							'include_print': True,
							'include_export': True,
							})
			path = os.path.join(os.path.dirname(__file__), FindTemplate('visit/home.html'))
			self.response.out.write(template.render(path, template_values))
		else:
			self.redirect(NoRakontuAndMemberURL())
			
	def buildGrid(self, entries, member, skinDict, showDetails, curating):
		haveContent = False
		textsForGrid = []
		rowColors = []
		minNudgePoints, maxNudgePoints, minActivityPoints, maxActivityPoints = GetMinMaxNudgeAndActivityPointsFromListOfItems(entries, member, "home")
		numRows = BROWSE_NUM_ROWS
		numCols = BROWSE_NUM_COLS
		rowColEntries = {}
		nudgePointRange = maxNudgePoints - minNudgePoints
		minTime = member.getViewStartTime("home")
		maxTime = member.getViewEndTime("home")
		timeRangeInSeconds = (maxTime - minTime).seconds + (maxTime - minTime).days * DAY_SECONDS
		exist, show = NudgeCategoriesExistAndShouldBeShownInContext(member, "home")
		for entry in entries:
			nudgePoints = entry.nudgePointsForExistAndShowOptions(exist, show)
			timeToCheck = entry.lastPublishedOrAnnotated()
			if nudgePointRange != 0:
				rowEntryShouldBeIn = max(0, min(numRows-1, int(1.0 * numRows * (nudgePoints - minNudgePoints) / nudgePointRange) - 1))
			else:
				rowEntryShouldBeIn = 0
			entryTimeInSeconds = (timeToCheck - minTime).seconds + (timeToCheck - minTime).days * DAY_SECONDS
			if timeRangeInSeconds > 0:
				colEntryShouldBeIn = max(0, min(numCols-1, int(1.0 * numCols * entryTimeInSeconds / timeRangeInSeconds) - 1))
			else:
				colEntryShouldBeIn = 0
			if not rowColEntries.has_key((rowEntryShouldBeIn, colEntryShouldBeIn)):
				rowColEntries[(rowEntryShouldBeIn, colEntryShouldBeIn)] = []
			rowColEntries[(rowEntryShouldBeIn, colEntryShouldBeIn)].append(entry)
		for row in range(numRows):
			rowColors.append(HexColorStringForRowIndex(row, skinDict))
			textsInThisRow = []
			for col in range(numCols): 
				textsInThisCell = []
				if rowColEntries.has_key((row, col)):
					entries = rowColEntries[(row, col)]
					for entry in entries:
						text =  ItemDisplayStringForGrid(entry, member, "home", curating=curating, showDetails=showDetails, adjustFontSize=True, minActivityPoints=minActivityPoints)
						textsInThisCell.append(text)
				haveContent = haveContent or len(textsInThisCell) > 0
				textsInThisRow.append(textsInThisCell)
			textsForGrid.append(textsInThisRow)
		textsForGrid.reverse()
		if not haveContent:
			textsForGrid = None
		return textsForGrid, rowColors
	
	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		curating = member.isCurator() and GetStringOfTypeFromURLQuery(self.request.query_string, "url_query_curate") == URL_OPTIONS["url_query_curate"]
		if access:
			if curating and not "stopCurating" in self.request.arguments():
				(entries, overLimitWarning, numItemsBeforeLimitTruncation) = ItemsMatchingViewOptionsForMemberAndLocation(member, "home")
				ProcessFlagOrUnFlagCommand(self.request, entries)
				self.redirect(self.request.uri)
			else:
				url = ProcessGridOptionsCommand(rakontu, member, self.request, location="home")
				self.redirect(url)
		else:
			self.redirect(NoRakontuAndMemberURL())
			
class ReadEntryPage(ErrorHandlingRequestHander):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if isFirstVisit: self.redirect(member.firstVisitURL())
			entry = GetObjectOfTypeFromURLQuery(self.request.query_string, "url_query_entry")
			if entry:
				curating = member.isCurator() and GetStringOfTypeFromURLQuery(self.request.query_string, "url_query_curate") == URL_OPTIONS["url_query_curate"]
				showVersions = GetStringOfTypeFromURLQuery(self.request.query_string, "url_query_versions") == URL_OPTIONS["url_query_versions"]
				(items, overLimitWarning, numItemsBeforeLimitTruncation) = ItemsMatchingViewOptionsForMemberAndLocation(member, "entry", entry=entry)
				textsForGrid, rowColors = self.buildGrid(items, entry, member, rakontu, curating)
				thingsUserCanDo = self.buildThingsUserCanDo(entry, member, rakontu, curating)
				viewOptions = member.getViewOptionsForLocation("entry")
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
								   'row_colors': rowColors,
								   'text_to_display_before_grid': TEMPLATE_TERMS["template_annotations"],
								   'grid_form_url': self.request.uri, 
									'num_items_before_truncation': numItemsBeforeLimitTruncation,
									'max_num_items': MAX_ITEMS_PER_GRID_PAGE,
									'too_many_items_warning': overLimitWarning,
									'show_details': viewOptions.showDetails,
									'grid_options_on_top': viewOptions.showOptionsOnTop,
								   # grid options
									'location': "entry",
									'include_time_range': False,
									'include_entry_types': False,
									'include_annotation_types': True,
												'annotation_types_to_show': viewOptions.annotationAnswerLinkTypes,
									'include_nudges': True,
										'nudge_categories_to_show': viewOptions.nudgeCategories,
										'include_nudge_floor': False,
									'include_search': False,
									'include_curate': member.isCurator(),
									'include_print': True,
									'include_export': False,
								   # actions
								   'things_member_can_do': thingsUserCanDo,
								   # versions
								   'show_versions': showVersions,
								   'versions': entry.getTextVersionsInReverseTimeOrder(),
								   })
				def txn(member):
					member.lastReadAnything = datetime.now(tz=pytz.utc)
					member.nudgePoints += rakontu.getMemberNudgePointsForEvent("reading")
					member.put()
				db.run_in_transaction(txn, member)
				entry.recordAction("read", entry, "Entry")
				entry.put()
				path = os.path.join(os.path.dirname(__file__), FindTemplate('visit/read.html'))
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect(NotFoundURL(rakontu))
		else:
			self.redirect(NoRakontuAndMemberURL())
			
	def buildGrid(self, allItems, entry, member, rakontu, curating):
		haveContent = False
		if allItems:
			minNudgePoints, maxNudgePoints, minActivityPoints, maxActivityPoints = GetMinMaxNudgeAndActivityPointsFromListOfItems(allItems, member, "entry")
			numRows = BROWSE_NUM_ROWS
			numCols = BROWSE_NUM_COLS
			showDetails = member.getViewDetailsForLocation("entry")
			skinDict = rakontu.getSkinDictionary()
			textsForGrid = []
			rowColors = []
			rowColItems = {}
			nudgePointRange = maxNudgePoints - minNudgePoints
			minTime = entry.published
			maxTime = entry.lastPublishedOrAnnotated()
			timeRangeInSeconds = (maxTime - minTime).seconds + (maxTime - minTime).days * DAY_SECONDS
			exist, show = NudgeCategoriesExistAndShouldBeShownInContext(member, "entry")
			for item in allItems:
				nudgePoints = item.getEntryNudgePointsWhenPublishedForExistAndShowOptions(exist, show)
				timeToCheck = item.published
				if nudgePointRange > 0:
					rowItemShouldBeIn = max(0, min(numRows-1, int(1.0 * numRows * (nudgePoints - minNudgePoints) / nudgePointRange) - 1))
				else:
					rowItemShouldBeIn = 0
				itemTimeInSeconds = (timeToCheck - minTime).seconds + (timeToCheck - minTime).days * DAY_SECONDS
				if timeRangeInSeconds > 0:
					colItemShouldBeIn = max(0, min(numCols-1, int(1.0 * numCols * itemTimeInSeconds / timeRangeInSeconds) - 1))
				else:
					colItemShouldBeIn = 0
				if not rowColItems.has_key((rowItemShouldBeIn, colItemShouldBeIn)):
					rowColItems[(rowItemShouldBeIn, colItemShouldBeIn)] = []
				rowColItems[(rowItemShouldBeIn, colItemShouldBeIn)].append(item)
			for row in range(numRows):
				rowColors.append(HexColorStringForRowIndex(row, skinDict))
				textsInThisRow = []
				for col in range(numCols): 
					textsInThisCell = []
					if rowColItems.has_key((row, col)):
						items = rowColItems[(row, col)]
						for item in items:
							text = ItemDisplayStringForGrid(item, member, "entry", curating, showDetails=showDetails)
							textsInThisCell.append(text)
					haveContent = haveContent or len(textsInThisCell) > 0
					textsInThisRow.append(textsInThisCell)
				textsForGrid.append(textsInThisRow)
			textsForGrid.reverse()
		else:
			textsForGrid = None
			rowColors = []
		if not haveContent:
			textsForGrid = None
		return textsForGrid, rowColors
			
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
		# nudging
		if memberCanAddNudgeToThisEntry:
			key = "%s %s" % (TERMS["term_nudge_this"], displayType)
			thingsUserCanDo[key] = BuildURL("dir_visit", URLForAnnotationType("nudge"), entry.urlQuery())
		# answering questions
		if rakontuHasQuestionsForThisEntryType and memberCanAnswerQuestionsAboutThisEntry:
			key = "%s %s" % (TERMS["term_answer_questions_about_this"], displayType)
			thingsUserCanDo[key] = BuildURL("dir_visit", "url_answers", entry.urlQuery())
		# commenting
		key = "%s %s" % (TERMS["term_make_a_comment"], displayType)
		thingsUserCanDo[key] = BuildURL("dir_visit", URLForAnnotationType("comment"), entry.urlQuery())
		# tagging
		key = "%s %s" % (TERMS["term_tag_this"], displayType)
		thingsUserCanDo[key] = BuildURL("dir_visit", URLForAnnotationType("tag set"), entry.urlQuery())
		# requesting
		key = "%s %s" % (TERMS["term_request_something_about_this"], displayType)
		thingsUserCanDo[key] = BuildURL("dir_visit", URLForAnnotationType("request"), entry.urlQuery())
		# relating
		key = TERMS["term_relate_entry_to_others"]
		thingsUserCanDo[key] = BuildURL("dir_visit", "url_relate", entry.urlQuery())
		return thingsUserCanDo
			
	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			entry = GetObjectOfTypeFromURLQuery(self.request.query_string, "url_query_entry")
			curating = member.isCurator() and GetStringOfTypeFromURLQuery(self.request.query_string, "url_query_curate") == URL_OPTIONS["url_query_curate"]
			if "doSomething" in self.request.arguments():
				self.redirect(self.request.get("nextAction"))
			elif "showVersions" in self.request.arguments():
				url = BuildURL("dir_visit", "url_read", "%s&%s=%s" % (entry.urlQuery(), URL_OPTIONS["url_query_versions"], URL_OPTIONS["url_query_versions"]))
				self.redirect(url)
			elif "hideVersions" in self.request.arguments():
				url = BuildURL("dir_visit", "url_read", "%s" % (entry.urlQuery()))
				self.redirect(url)
			elif curating and not "stopCurating" in self.request.arguments():
				itemsThatCanBeCurated = [entry]
				for item in entry.getAllNonDraftDependents():
					 itemsThatCanBeCurated.append(item)
				ProcessFlagOrUnFlagCommand(self.request, itemsThatCanBeCurated)
				self.redirect(self.request.uri)
			else:
				url = ProcessGridOptionsCommand(rakontu, member, self.request, location="entry", entry=entry)
				self.redirect(url)
		else:
			self.redirect(NoRakontuAndMemberURL())
			
class ReadAnnotationPage(ErrorHandlingRequestHander):
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
				def txn(member):
					member.lastReadAnything = datetime.now(tz=pytz.utc)
					member.nudgePoints += rakontu.getMemberNudgePointsForEvent("reading")
					member.put()
				db.run_in_transaction(txn, member)
				path = os.path.join(os.path.dirname(__file__), FindTemplate('visit/readAnnotation.html'))
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect(NotFoundURL(rakontu))
		else:
			self.redirect(NoRakontuAndMemberURL())
			
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
			self.redirect(NoRakontuAndMemberURL())

class SeeRakontuPage(ErrorHandlingRequestHander):
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
			self.redirect(NoRakontuAndMemberURL())
			
class SeeRakontuMembersPage(ErrorHandlingRequestHander):
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
			self.redirect(NoRakontuAndMemberURL())
			
	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if "sendMessage" in self.request.arguments():
				membersToSendMessagesTo = []
				for aMember in rakontu.getActiveMembers():
					for name, value in self.request.params.items():
						if name == "sendMessage|%s" % aMember.key() and value == "yes":
							membersToSendMessagesTo.append(aMember)
				if membersToSendMessagesTo:
					memcache.add("sendMessage:%s" % member.key(), membersToSendMessagesTo, HOUR_SECONDS)
					self.redirect(BuildURL("dir_visit", "url_message", member.urlQuery()))
				else:
					self.redirect(BuildURL("dir_visit", "url_members", rakontu=rakontu))
		else:
			self.redirect(NoRakontuAndMemberURL())
			
class SendMessagePage(ErrorHandlingRequestHander):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if isFirstVisit: self.redirect(member.firstVisitURL())
			try:
				membersToSendMessagesTo = memcache.get("sendMessage:%s" % member.key())
			except:
				membersToSendMessagesTo = None
			if membersToSendMessagesTo:
				template_values = GetStandardTemplateDictionaryAndAddMore({
							   'title': TITLES["SEND_MESSAGE"], 
					   		   'rakontu': rakontu, 
					   		   'skin': rakontu.getSkinDictionary(),
					   		   'current_member': member,
					   		   'members_to_send_message_to': membersToSendMessagesTo,
					   		   })
				path = os.path.join(os.path.dirname(__file__), FindTemplate('visit/message.html'))
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect(NotFoundURL(rakontu))
		else:
			self.redirect(NoRakontuAndMemberURL())
			
	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			try:
				membersToSendMessagesTo = memcache.get("sendMessage:%s" % member.key())
			except:
				membersToSendMessagesTo = None
			if membersToSendMessagesTo:
				emailAddresses = []
				for aMember in membersToSendMessagesTo:
					if aMember.isOnlineMember:
						if aMember.googleAccountEmail:
							emailAddresses.append(aMember.googleAccountEmail)
					else:
						if aMember.liaison and  aMember.liaison.active:
							if aMember.liaison.aMember.googleAccountEmail:
								emailAddresses.append(aMember.liaison.googleAccountEmail)
				if self.request.get("messageReplyToEmail") != None and self.request.get("messageReplyToEmail") != "":
					replyTo = self.request.get("messageReplyToEmail")
				else:
					replyTo = rakontu.contactEmail
				if emailAddresses:
					message = mail.EmailMessage()
					message.sender = rakontu.contactEmail
					message.reply_to = replyTo
					message.subject = htmlEscape(self.request.get("subject"))
					message.to = emailAddresses 
					message.body = htmlEscape(self.request.get("message"))
					message.send()
					self.redirect(BuildResultURL("messagesent", rakontu=rakontu))
				else:
					self.redirect(BuildResultURL("membersNotFound", rakontu=rakontu))
			else:
				self.redirect(BuildResultURL("membersNotFound", rakontu=rakontu))
		else:
			self.redirect(NoRakontuAndMemberURL())
	
class SeeMemberPage(ErrorHandlingRequestHander):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if isFirstVisit: self.redirect(member.firstVisitURL())
			memberToSee = GetObjectOfTypeFromURLQuery(self.request.query_string, "url_query_member")
			curating = member.isCurator() and GetStringOfTypeFromURLQuery(self.request.query_string, "url_query_curate") == URL_OPTIONS["url_query_curate"]
			if memberToSee:
				(items, overLimitWarning, numItemsBeforeLimitTruncation) = ItemsMatchingViewOptionsForMemberAndLocation(member, "member", memberToSee=memberToSee)
				textsForGrid, rowColors = self.buildGrid(items, member, memberToSee, rakontu, curating)
				countNames, counts = memberToSee.getCounts()
				viewOptions = member.getViewOptionsForLocation("member")
				currentSearch = viewOptions.search
				template_values = GetStandardTemplateDictionaryAndAddMore({
							   'title': TITLES["MEMBER"], 
					   		   'title_extra': memberToSee.nickname, 
					   		   'rakontu': rakontu, 
					   		   'skin': rakontu.getSkinDictionary(),
					   		   'current_member': member,
					   		   'member': memberToSee,
					   		   'answers': memberToSee.getAnswers(),
					   		   # grid
					   		   'rows_cols': textsForGrid,
					   		   'row_colors': rowColors,
					   		   'text_to_display_before_grid': "%s %s" % (TERMS["term_entries_contributed_by"], memberToSee.nickname),
					   		   'grid_form_url': self.request.uri, 
								'num_items_before_truncation': numItemsBeforeLimitTruncation,
								'max_num_items': MAX_ITEMS_PER_GRID_PAGE,
								'too_many_items_warning': overLimitWarning,
					   		   'no_profile_text': NO_PROFILE_TEXT,
					   		   'count_names': countNames,
					   		   'counts': counts,
					   		   'curating': curating,
					   		   'show_details': viewOptions.showDetails,
								'grid_options_on_top': viewOptions.showOptionsOnTop,
							   # grid options
								'location': "member",
								'include_time_range': True,
									'member_time_frame_string': viewOptions.getFrameStringForViewTimeFrame(),
									'min_time': TimeDisplay(viewOptions.getStartTime(), member),
									'max_time': TimeDisplay(viewOptions.endTime, member),
								'include_entry_types': True,
											'entry_types_to_show': viewOptions.entryTypes,
								'include_annotation_types': True,
											'annotation_types_to_show': viewOptions.annotationAnswerLinkTypes,
								'include_nudges': False,
								'include_nudge_floor': False,
								'include_search': True,
												'shared_searches': rakontu.getNonPrivateSavedSearches(),
												'member_searches': member.getPrivateSavedSearches(),
												'current_search': currentSearch,
								'include_curate': member.isCurator(),
								'include_print': True,
								'include_export': False,
					   		   })
				path = os.path.join(os.path.dirname(__file__), FindTemplate('visit/member.html'))
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect(NotFoundURL(rakontu))
		else:
			self.redirect(NoRakontuAndMemberURL())
			
	def buildGrid(self, allItems, member, memberToSee, rakontu, curating):
		if allItems:
			minTime = member.getViewStartTime("member")
			maxTime = member.getViewEndTime("member")
			minNudgePoints, maxNudgePoints, minActivityPoints, maxActivityPoints = GetMinMaxNudgeAndActivityPointsFromListOfItems(allItems, member, "member")
			numRows = BROWSE_NUM_ROWS
			numCols = BROWSE_NUM_COLS
			showDetails = member.getViewDetailsForLocation("member")
			skinDict = rakontu.getSkinDictionary()
			textsForGrid = []
			rowColors = []
			rowColItems = {}
			nudgePointRange = maxNudgePoints - minNudgePoints
			timeRangeInSeconds = (maxTime - minTime).seconds + (maxTime - minTime).days * DAY_SECONDS
			exist, show = NudgeCategoriesExistAndShouldBeShownInContext(member, "member")
			for item in allItems:
				if item.__class__.__name__ == "Entry":
					nudgePoints = item.nudgePointsForExistAndShowOptions(exist, show)
				else:
					nudgePoints = item.getEntryNudgePointsWhenPublishedForExistAndShowOptions(exist, show)
				timeToCheck = item.published
				if nudgePointRange > 0:
					rowItemShouldBeIn = max(0, min(numRows-1, int(1.0 * numRows * (nudgePoints - minNudgePoints) / nudgePointRange) - 1))
				else:
					rowItemShouldBeIn = 0
				itemTimeInSeconds = (timeToCheck - minTime).seconds + (timeToCheck - minTime).days * DAY_SECONDS
				if timeRangeInSeconds > 0:
					colItemShouldBeIn = max(0, min(numCols-1, int(1.0 * numCols * itemTimeInSeconds / timeRangeInSeconds) - 1))
				else:
					colItemShouldBeIn = 0
				if not rowColItems.has_key((rowItemShouldBeIn, colItemShouldBeIn)):
					rowColItems[(rowItemShouldBeIn, colItemShouldBeIn)] = []
				rowColItems[(rowItemShouldBeIn, colItemShouldBeIn)].append(item)
			for row in range(numRows):
				rowColors.append(HexColorStringForRowIndex(row, skinDict))
				textsInThisRow = []
				for col in range(numCols): 
					textsInThisCell = []
					if rowColItems.has_key((row, col)):
						items = rowColItems[(row, col)]
						for item in items:
							text = ItemDisplayStringForGrid(item, member, "member", curating, showDetails=showDetails)
							textsInThisCell.append(text)
					textsInThisRow.append(textsInThisCell)
				textsForGrid.append(textsInThisRow)
			textsForGrid.reverse()
		else:
			textsForGrid = None
			rowColors = None
		return textsForGrid, rowColors
	
	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			memberToSee = GetObjectOfTypeFromURLQuery(self.request.query_string, "url_query_member")
			curating = member.isCurator() and GetStringOfTypeFromURLQuery(self.request.query_string, "url_query_curate") == URL_OPTIONS["url_query_curate"]
			if memberToSee:
				if curating and not "stopCurating" in self.request.arguments():
					ProcessFlagOrUnFlagCommand(self.request, memberToSee.getAllItemsAttributedToMember())
					self.redirect(self.request.uri)
				else:
					url = ProcessGridOptionsCommand(rakontu, member, self.request, location="member", memberToSee=memberToSee)
					self.redirect(url)
			else:
				self.redirect(NotFoundURL(rakontu))
		else:
			self.redirect(NoRakontuAndMemberURL())
   
class SeeCharacterPage(ErrorHandlingRequestHander):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if isFirstVisit: self.redirect(member.firstVisitURL())
			character = GetObjectOfTypeFromURLQuery(self.request.query_string, "url_query_character")
			curating = member.isCurator() and GetStringOfTypeFromURLQuery(self.request.query_string, "url_query_curate") == URL_OPTIONS["url_query_curate"]
			if character:
				(items, overLimitWarning, numItemsBeforeLimitTruncation) = ItemsMatchingViewOptionsForMemberAndLocation(member, "character", character=character)
				textsForGrid, rowColors = self.buildGrid(items, member, character, rakontu, curating)
				viewOptions = member.getViewOptionsForLocation("character")
				currentSearch = viewOptions.search
				countNames, counts = character.getCounts()
				template_values = GetStandardTemplateDictionaryAndAddMore({
							   	   'title': TITLES["CHARACTER"], 
					   		   	   'title_extra': character.name, 
								   'rakontu': rakontu, 
								   'skin': rakontu.getSkinDictionary(),
								   'current_member': member,
								   'character': character,
								   'answers': character.getAnswers(),
					   		   	   'rows_cols': textsForGrid,
					   		   	   'row_colors': rowColors,
					   		   	   'text_to_display_before_grid': "%s's entries" % character.name,
					   		   	   'grid_form_url': self.request.uri,
					   		   	   'curating': curating,
					   		   'count_names': countNames,
					   		   'counts': counts,
								'num_items_before_truncation': numItemsBeforeLimitTruncation,
								'max_num_items': MAX_ITEMS_PER_GRID_PAGE,
								'too_many_items_warning': overLimitWarning,
					   		   'show_details': viewOptions.showDetails,
								'grid_options_on_top': viewOptions.showOptionsOnTop,
							   # grid options
								'location': "member",
								'include_time_range': True,
									'member_time_frame_string': viewOptions.getFrameStringForViewTimeFrame(),
									'min_time': TimeDisplay(viewOptions.getStartTime(), member),
									'max_time': TimeDisplay(viewOptions.endTime, member),
								'include_entry_types': True,
											'entry_types_to_show': viewOptions.entryTypes,
								'include_annotation_types': True,
											'annotation_types_to_show': viewOptions.annotationAnswerLinkTypes,
								'include_nudges': False,
								'include_nudge_floor': False,
								'include_search': True,
												'shared_searches': rakontu.getNonPrivateSavedSearches(),
												'member_searches': member.getPrivateSavedSearches(),
												'current_search': currentSearch,
								'include_curate': member.isCurator(),
								'include_print': True,
								'include_export': False,
													 })
				path = os.path.join(os.path.dirname(__file__), FindTemplate('visit/character.html'))
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect(NotFoundURL(rakontu))
		else:
			self.redirect(NoRakontuAndMemberURL())
			
	def buildGrid(self, allItems, member, character, rakontu, curating):
		if allItems:
			minTime = member.getViewStartTime("character")
			maxTime = member.getViewEndTime("character")
			minNudgePoints, maxNudgePoints, minActivityPoints, maxActivityPoints = GetMinMaxNudgeAndActivityPointsFromListOfItems(allItems, member, "member")
			numRows = BROWSE_NUM_ROWS
			numCols = BROWSE_NUM_COLS
			showDetails = member.getViewDetailsForLocation("character")
			skinDict = rakontu.getSkinDictionary()
			textsForGrid = []
			rowColors = []
			rowColItems = {}
			nudgePointRange = maxNudgePoints - minNudgePoints
			timeRangeInSeconds = (maxTime - minTime).seconds + (maxTime - minTime).days * DAY_SECONDS
			exist, show = NudgeCategoriesExistAndShouldBeShownInContext(member, "character")
			for item in allItems:
				if item.__class__.__name__ == "Entry":
					nudgePoints = item.nudgePointsForExistAndShowOptions(exist, show)
				else:
					nudgePoints = item.getEntryNudgePointsWhenPublishedForExistAndShowOptions(exist, show)
				timeToCheck = item.published
				if nudgePointRange > 0:
					rowItemShouldBeIn = max(0, min(numRows-1, int(1.0 * numRows * (nudgePoints - minNudgePoints) / nudgePointRange) - 1))
				else:
					rowItemShouldBeIn = 0
				itemTimeInSeconds = (timeToCheck - minTime).seconds + (timeToCheck - minTime).days * DAY_SECONDS
				if timeRangeInSeconds > 0:
					colItemShouldBeIn = max(0, min(numCols-1, int(1.0 * numCols * itemTimeInSeconds / timeRangeInSeconds) - 1))
				else:
					colItemShouldBeIn = 0
				if not rowColItems.has_key((rowItemShouldBeIn, colItemShouldBeIn)):
					rowColItems[(rowItemShouldBeIn, colItemShouldBeIn)] = []
				rowColItems[(rowItemShouldBeIn, colItemShouldBeIn)].append(item)
			for row in range(numRows):
				rowColors.append(HexColorStringForRowIndex(row, skinDict))
				textsInThisRow = []
				for col in range(numCols): 
					textsInThisCell = []
					if rowColItems.has_key((row, col)):
						items = rowColItems[(row, col)]
						for item in items:
							text = ItemDisplayStringForGrid(item, member, "character", curating, showDetails=showDetails)
							textsInThisCell.append(text)
					textsInThisRow.append(textsInThisCell)
				textsForGrid.append(textsInThisRow)
			textsForGrid.reverse()
		else:
			textsForGrid = None
			rowColors = None
		return textsForGrid, rowColors

	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			character = GetObjectOfTypeFromURLQuery(self.request.query_string, "url_query_character")
			curating = member.isCurator() and GetStringOfTypeFromURLQuery(self.request.query_string, "url_query_curate") == URL_OPTIONS["url_query_curate"]
			if character:
				if curating and not "stopCurating" in self.request.arguments():
					ProcessFlagOrUnFlagCommand(self.request, character.getAllItemsAttributedToCharacter())
					self.redirect(self.request.uri)
				else:
					url = ProcessGridOptionsCommand(rakontu, member, self.request, location="character", character=character)
					self.redirect(url)
			else:
				self.redirect(NotFoundURL(rakontu))
		else:
			self.redirect(NoRakontuAndMemberURL())
   
class AskGuidePage(ErrorHandlingRequestHander):
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
				self.redirect(NotFoundURL(rakontu))
		else:
			self.redirect(NoRakontuAndMemberURL())

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
					self.redirect(NotFoundURL(rakontu))
		else:
			self.redirect(NoRakontuAndMemberURL())
   
class ChangeMemberProfilePage(ErrorHandlingRequestHander):
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
							   'title': TITLES["PROFILE_FOR"], 
						   	   'title_extra': memberToEdit.nickname, 
							   'rakontu': rakontu, 
							   'skin': rakontu.getSkinDictionary(),
							   'member': memberToEdit,
							   'accumulated_nudge_points': member.nudgePoints,
							   'current_member': member,
							   'questions': rakontu.getActiveMemberQuestions(),
							   'answers': memberToEdit.getAnswers(),
							   'refer_type': "member",
							   'refer_type_display': DisplayTypeForQuestionReferType("member"),
							   })
			path = os.path.join(os.path.dirname(__file__), FindTemplate('visit/profile.html'))
			self.response.out.write(template.render(path, template_values))
		else:
			self.redirect(NoRakontuAndMemberURL())
							 
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
				text = self.request.get("profileText")
				format = self.request.get("profileText_format").strip()
				memberToEdit.profileText = text
				memberToEdit.profileText_formatted = db.Text(InterpretEnteredText(text, format))
				memberToEdit.profileText_format = format
				if self.request.get("removeProfileImage") == "yes":
					memberToEdit.profileImage = None
				elif self.request.get("img"):
					memberToEdit.profileImage = db.Blob(images.resize(str(self.request.get("img")), THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT))
				memberToEdit.put()
				questions = rakontu.getActiveQuestionsOfType("member")
				answersToPut = []
				for question in questions:
					foundAnswer = memberToEdit.getAnswerForMemberQuestion(question)
					if foundAnswer:
						answerToEdit = foundAnswer
					else:
						keyName = GenerateSequentialKeyName("answer")
						answerToEdit = Answer(
											key_name=keyName, 
											parent=memberToEdit,
											rakontu=rakontu, 
											question=question, 
											referent=memberToEdit, 
											referentType="member")
					queryText = "%s" % question.key()
					response = self.request.get(queryText)
					keepAnswer = answerToEdit.shouldKeepMe(self.request, question)
					if keepAnswer:
						answerToEdit.setValueBasedOnResponse(question, self.request, response)
						answerToEdit.creator = memberToEdit
						answersToPut.append(answerToEdit)
				if answersToPut:
					db.put(answersToPut)
				if offlineMember:
					self.redirect(BuildURL("dir_liaise", "url_members", rakontu=rakontu))
				else:
					self.redirect(BuildURL("dir_visit", "url_member", memberToEdit.urlQuery()))
			else:
				self.redirect(NotFoundURL(rakontu))
		else:
			self.redirect(NoRakontuAndMemberURL())
			
class ChangeMemberPreferencesPage(ErrorHandlingRequestHander):
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
							   'show_leave_link': not rakontu.memberIsOnlyOwner(member),
							   'my_offline_members': rakontu.getActiveOfflineMembersForLiaison(member),
							   'time_zone_names': pytz.all_timezones,    
							   })
			path = os.path.join(os.path.dirname(__file__), FindTemplate('visit/preferences.html'))
			self.response.out.write(template.render(path, template_values))
		else:
			self.redirect(NoRakontuAndMemberURL())
			
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
				memberToEdit.acceptsMessages = self.request.get("acceptsMessages") == "yes"
				memberToEdit.messageReplyToEmail = self.request.get("messageReplyToEmail")
				memberToEdit.timeZoneName = self.request.get("timeZoneName")
				memberToEdit.dateFormat = self.request.get("dateFormat")
				memberToEdit.timeFormat = self.request.get("timeFormat")
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
					memberToEdit.showAttachedImagesInline = self.request.get("showAttachedImagesInline") == "yes"
				memberToEdit.put()
				if offlineMember:
					self.redirect(BuildURL("dir_liaise", "url_members", rakontu=rakontu))
				else:
					self.redirect(BuildURL("dir_visit", "url_member", memberToEdit.urlQuery()))
			else:
				self.redirect(NotFoundURL(rakontu))
		else:
			self.redirect(NoRakontuAndMemberURL())
			
class ChangeMemberNicknamePage(ErrorHandlingRequestHander):
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
			nameTaken = GetStringOfTypeFromURLQuery(self.request.query_string, "url_query_name_taken") == URL_OPTIONS["url_query_name_taken"]
			try:
				nickname = memcache.get("nickname:%s" % memberToEdit.key())
			except:
				nickname = memberToEdit.nickname
			if not nickname:
				nickname = memberToEdit.nickname
			template_values = GetStandardTemplateDictionaryAndAddMore({
							   'title': TITLES["CHANGE_NICKNAME_FOR"], 
						   	   'title_extra': memberToEdit.nickname, 
							   'rakontu': rakontu, 
							   'skin': rakontu.getSkinDictionary(),
							   'member': memberToEdit,
							   'current_member': member,
							   'name_taken': nameTaken,
							   'nickname': nickname,
							   })
			path = os.path.join(os.path.dirname(__file__), FindTemplate('visit/nickname.html'))
			self.response.out.write(template.render(path, template_values))
		else:
			self.redirect(NoRakontuAndMemberURL())
							 
	@RequireLogin  
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			goAhead = True
			offlineMember = None
			for aMember in rakontu.getActiveOfflineMembers():
				if "%s" % aMember.key() in self.request.arguments():
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
				nickname = htmlEscape(self.request.get("nickname")).strip()
				memberUsingNickname = rakontu.memberWithNickname(nickname)
				if memberUsingNickname and memberUsingNickname.key() != memberToEdit.key():
					memcache.add("nickname:%s" % memberToEdit.key(), nickname, HOUR_SECONDS)
					query = "%s&%s=%s" % (memberToEdit.urlQuery(), URL_OPTIONS["url_query_name_taken"], URL_OPTIONS["url_query_name_taken"])
					self.redirect(BuildURL("dir_visit", "url_nickname", query))
				else:
					memberToEdit.nickname = nickname
					memberToEdit.put()
					memcache.delete("nickname:%s" % memberToEdit.key())
					self.redirect(BuildURL("dir_visit", "url_profile", memberToEdit.urlQuery()))
			else:
				self.redirect(NotFoundURL(rakontu))
		else:
			self.redirect(NoRakontuAndMemberURL())
			
class ChangeMemberDraftsPage(ErrorHandlingRequestHander):
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
			self.redirect(NoRakontuAndMemberURL())
							 
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
				self.redirect(NotFoundURL(rakontu))
		else:
			self.redirect(NoRakontuAndMemberURL())
			
class ChangeMemberFiltersPage(ErrorHandlingRequestHander):
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
			self.redirect(NoRakontuAndMemberURL())
							 
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
				self.redirect(NotFoundURL(rakontu))
		else:
			self.redirect(NoRakontuAndMemberURL())
			
class LeaveRakontuPage(ErrorHandlingRequestHander):
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
			self.redirect(NoRakontuAndMemberURL())
			
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
			self.redirect(NoRakontuAndMemberURL())
		
class SavedSearchEntryPage(ErrorHandlingRequestHander):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if isFirstVisit: self.redirect(member.firstVisitURL())
			location = GetStringOfTypeFromURLQuery(self.request.query_string, "url_query_location")
			currentSearch = GetObjectOfTypeFromURLQuery(self.request.query_string, "url_query_search_filter")
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
							'location': location,
							})
			path = os.path.join(os.path.dirname(__file__), FindTemplate('visit/filter.html'))
			self.response.out.write(template.render(path, template_values))
		else:
			self.redirect(NoRakontuAndMemberURL())
			
	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			location = GetStringOfTypeFromURLQuery(self.request.query_string, "url_query_location")
			if location == "home":
				defaultURL = rakontu.linkURL()
			elif location == "entry":
				defaultURL = entry.linkURL()
			elif location == "member": 
				defaultURL = memberToSee.linkURL()
			elif location == "character":
				defaultURL = character.linkURL()
			defaultURL += "&%s=%s" % (URL_OPTIONS["url_query_location"], location)
			search = member.getSearchForLocation(location)
			if "deleteSearchByCreator" in self.request.arguments():
				if search:
					db.delete(search)
					member.setSearchForLocation(location, None)
				self.redirect(defaultURL)
			elif "flagSearchByCurator" in self.request.arguments():
				if search:
					search.flaggedForRemoval = not search.flaggedForRemoval
					search.put()
					query = "%s=%s" % (URL_OPTIONS["url_query_location"], location)
					self.redirect(BuildURL("dir_visit", "url_search_filter", query, rakontu=rakontu))
				else:
					self.redirect(defaultURL)
			elif "removeSearchByManager" in self.request.arguments():
				if search:
					db.delete(search)
					member.setSearchForLocation(location, None)
				self.redirect(defaultURL)
			elif "saveAs" in self.request.arguments() or "save" in self.request.arguments():
				if not search or "saveAs" in self.request.arguments():
					keyName = GenerateSequentialKeyName("filter")
					search = SavedSearch(key_name=keyName, parent=member, id=keyName, rakontu=rakontu, creator=member)
				thingsToPut = []
				thingsToPut.append(search)
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
								ref = search.getQuestionReferenceForQuestionAndOrder(question, i)
								if not ref:
									keyName = GenerateSequentialKeyName("searchref")
									ref = SavedSearchQuestionReference(key_name=keyName, parent=search, rakontu=rakontu, search=search, question=question)
								ref.answer = answer
								ref.comparison = comparison
								ref.order = i
								ref.type = preface
								thingsToPut.append(ref)
				def txn(thingsToPut):
					if thingsToPut:
						db.put(thingsToPut)
				# SEQUENTIAL TRANSACTION PROBLEM
				db.run_in_transaction(txn, thingsToPut)
				member.setSearchForLocation(location, search)
				self.redirect(defaultURL)
			else:
				self.redirect(NotFoundURL(rakontu))
		else:
			self.redirect(NoRakontuAndMemberURL())
			
class ResultFeedbackPage(ErrorHandlingRequestHander):
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
			self.redirect(NoRakontuAndMemberURL())
				
class ContextualHelpPage(ErrorHandlingRequestHander):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		# don't require access to rakontu, since administrator may be calling this from the admin or create pages
		name = GetStringOfTypeFromURLQuery(self.request.query_string, "url_query_help")
		type = GetStringOfTypeFromURLQuery(self.request.query_string, "url_query_help_type")
		help = helpLookup(name, type)
		if type == "info":
			message = TERMS["term_help_info"]
		elif type == "tip": 
			message = TERMS["term_help_tip"]
		elif type == "caution": 
			message = TERMS["term_help_caution"]
		if help:
			helpShortName = help.name.replace("_", " ").capitalize()
			template_values = GetStandardTemplateDictionaryAndAddMore({
						   	   'title': TITLES["HELP_ON"], 
					   	   	   'title_extra': helpShortName,
					   	   	   'system_message': TERMS["term_help"], 
							   'top_message': message,
							   'help': help,
							   'type': type,
							   })
			path = os.path.join(os.path.dirname(__file__), FindTemplate('help.html'))
			self.response.out.write(template.render(path, template_values))
		else:
			self.redirect(BuildResultURL("helpNotFound", rakontu=rakontu))
			
class GeneralHelpPage(ErrorHandlingRequestHander):
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
			self.redirect(NoRakontuAndMemberURL())
			
def ProcessGridOptionsCommand(rakontu, member, request, location="home", entry=None, memberToSee=None, character=None):
	viewOptions = member.getViewOptionsForLocation(location)
	search = viewOptions.search
	if location == "home":
		defaultURL = rakontu.linkURL()
	elif location == "entry":
		defaultURL = entry.linkURL()
	elif location == "member": 
		defaultURL = memberToSee.linkURL()
	elif location == "character":
		defaultURL = character.linkURL()
	defaultURL += "&%s=%s" % (URL_OPTIONS["url_query_location"], location)
	delta = timedelta(seconds=viewOptions.timeFrameInSeconds)
	now = datetime.now(tz=pytz.utc)
	# turn on or off curating
	if "startCurating" in request.arguments():
		return defaultURL + "&%s=%s" % (URL_OPTIONS["url_query_curate"], URL_OPTIONS["url_query_curate"])
	elif "stopCurating" in request.arguments():
		return defaultURL
	# time frame - home, member, character
	elif "changeTimeFrame" in request.arguments():
		viewOptions.setViewTimeFrameFromTimeFrameString(request.get("timeFrame"))
		viewOptions.put()
		return defaultURL
	elif "setToLast" in request.arguments():
		viewOptions.endTime = datetime.now(tz=pytz.utc)
		viewOptions.put()
		return defaultURL 
	elif "setToFirst" in request.arguments():
		if location == "home":
			startTime = rakontu.created
		elif location == "member":
			startTime = member.joined
		elif location == "character":
			startTime = character.created
		endTime = startTime + delta
		viewOptions.endTime = endTime
		viewOptions.put()
		return defaultURL
	elif "moveTimeBack" in request.arguments() or "moveTimeForward" in request.arguments():
		if "moveTimeBack" in request.arguments():
			endTime = viewOptions.endTime - delta
		else:
			endTime = viewOptions.endTime + delta
		viewOptions.endTime = endTime
		viewOptions.put()
		return defaultURL
	# entry types - home, member, character 
	elif "changeEntryTypesShowing" in request.arguments():
		newEntryTypes = []
		for i in range(len(ENTRY_TYPES)):
			newEntryTypes.append(request.get("showEntryType|%s" % i) == "yes")
		viewOptions.entryTypes = []
		viewOptions.entryTypes.extend(newEntryTypes)
		viewOptions.put()
		return defaultURL
	# annotation types - entry, member, character 
	elif "changeAnnotationTypesShowing" in request.arguments():
		newAnnotationAnswerLinkTypes = []
		for i in range(len(ANNOTATION_ANSWER_LINK_TYPES)):
			newAnnotationAnswerLinkTypes.append(request.get("showAnnotationAnswerLinkType|%s" % i) == "yes")
		viewOptions.annotationAnswerLinkTypes = []
		viewOptions.annotationAnswerLinkTypes.extend(newAnnotationAnswerLinkTypes)
		viewOptions.put()
		return defaultURL
	# nudges - home, entry 
	elif "changeNudgeCategoriesShowing" in request.arguments():
		newNudgeCategories = []
		for i in range(NUM_NUDGE_CATEGORIES):
			if rakontu.nudgeCategoryIndexHasContent(i):
				newNudgeCategories.append(request.get("showCategory|%s" % i) == "yes")
		viewOptions.nudgeCategories = []
		viewOptions.nudgeCategories.extend(newNudgeCategories)
		oldValue = viewOptions.nudgeFloor
		try:
			viewOptions.nudgeFloor = int(request.get("nudgeFloor"))
		except:
			viewOptions.nudgeFloor = oldValue
		viewOptions.put()
		return defaultURL
	# search filter - home, member, character
	elif "loadAndApplySavedSearch" in request.arguments():
		if request.get("savedSearch") != "(%s)" % TERMS["term_choose"]:
			searchKey = request.get("savedSearch")
			if searchKey:
				search = SavedSearch.get(searchKey)
				if search:
					viewOptions.search = search
					viewOptions.put()
					return defaultURL
			else:
				return defaultURL
		else:
			return defaultURL
	elif "stopApplyingSearch" in request.arguments():
			viewOptions.search = None
			viewOptions.put()
			return defaultURL
	elif "makeNewSavedSearch" in request.arguments():
			viewOptions.search = None
			viewOptions.put()
			query ="%s=%s" % (URL_OPTIONS["url_query_location"], location)
			return BuildURL("dir_visit", "url_search_filter", query, rakontu=rakontu)
	elif "changeSearch"  in request.arguments():
		if search:
			query = "%s&%s=%s" % (search.urlQuery(), URL_OPTIONS["url_query_location"], location)
			return BuildURL("dir_visit", "url_search_filter", query, rakontu=rakontu)
		else:
			viewOptions.search = None
			viewOptions.put()
			query ="%s=%s" % (URL_OPTIONS["url_query_location"], location)
			return BuildURL("dir_visit", "url_search_filter", query, rakontu=rakontu)
	elif "copySearch"  in request.arguments():
		if search:
			keyName = GenerateSequentialKeyName("filter")
			refs = search.getQuestionReferences()
			def txn(keyName, member, rakontu, search, refs):
				newSearch = SavedSearch(key_name=keyName, parent=member, id=keyName, rakontu=rakontu, creator=member)
				newSearch.copyDataFromOtherSearchAndPut(search, refs)
				return newSearch
			# SEQUENTIAL TRANSACTION PROBLEM
			newSearch = db.run_in_transaction(txn, keyName, member, rakontu, search, refs)
			viewOptions.search = newSearch
			viewOptions.put()
			query = "%s&%s=%s" % (newSearch.urlQuery(), URL_OPTIONS["url_query_location"], location)
			return BuildURL("dir_visit", "url_search_filter", query, rakontu=rakontu)
		else:
			return defaultURL
	# other options - all
	elif "toggleViewHomeOptionsOnTop" in request.arguments():
		viewOptions.showOptionsOnTop = not viewOptions.showOptionsOnTop
		viewOptions.put()
		return defaultURL  
	elif "toggleShowDetails" in request.arguments():  
		viewOptions.showDetails = not viewOptions.showDetails
		viewOptions.put()
		return defaultURL   
	elif "printSearchResults"  in request.arguments(): 
		if location == "home": 
			return BuildURL("dir_liaise", "url_print_search", rakontu=rakontu)
		elif location == "entry": 
			return BuildURL("dir_liaise", "url_print_entry", entry.urlQuery())
		elif location == "member":
			return BuildURL("dir_liaise", "url_print_member", memberToSee.urlQuery())
		elif location == "character":
			return BuildURL("dir_liaise", "url_print_character", character.urlQuery())
	elif "exportSearchResults"  in request.arguments():
		if location == "home":
			return BuildURL("dir_manage", "url_export_search", rakontu=rakontu)
		else:
			# no reaction yet for entry or member or character - should add export for that?
			return defaultURL
	else:
			return None
		
def ProcessFlagOrUnFlagCommand(request, itemsThatCanBeCurated):
	for item in itemsThatCanBeCurated:
		if "flag|%s" % item.key() in request.arguments():
			item.flaggedForRemoval = True
			item.put()
			break # only one thing can be flagged or unflagged at a time
		elif "unflag|%s" % item.key() in request.arguments():
			item.flaggedForRemoval = False
			item.put()
			break # only one thing can be flagged or unflagged at a time
		
def ItemDisplayStringForGrid(item, member, location, curating=False, showDetails=False, adjustFontSize=False, minActivityPoints=0):
	# font size string (home grid only)
	fontSizeStartString = ""
	fontSizeEndString = ""
	if adjustFontSize and item.__class__.__name__ == "Entry":
		fontSizePercent = min(200, 90 + item.activityPoints - minActivityPoints)
		downdrift = member.rakontu.getEntryActivityPointsForEvent("downdrift")
		if downdrift:
			daysSinceTouched = 1.0 * (datetime.now(tz=pytz.utc) - item.lastTouched()).seconds / DAY_SECONDS
			timeLoss = daysSinceTouched * downdrift
			fontSizePercent += timeLoss
			fontSizePercent = int(max(MIN_BROWSE_FONT_SIZE_PERCENT, min(fontSizePercent, MAX_BROWSE_FONT_SIZE_PERCENT)))
		fontSizeStartString = '<span style="font-size:%s%%">' % fontSizePercent
		fontSizeEndString = "</span>"
	# link string
	if item.__class__.__name__ == "Answer":
		if showDetails: 
			if location != "entry":
				linkString = item.linkStringWithQuestionTextAndReferentLink()
			else:
				linkString = item.linkStringWithQuestionText()
		else:
			if location != "entry":
				linkString = item.linkStringWithQuestionNameAndReferentLink()
			else:
				linkString = item.linkStringWithQuestionName()
	elif item.__class__.__name__ == "Annotation":
		if location != "entry":
			linkString = item.linkStringWithEntryLink(showDetails=showDetails)
		else:
			linkString = item.linkString(showDetails=showDetails)
	else:
		linkString = item.linkString()
	# name 
	if showDetails and location != "member":
		if item.attributedToMember(): 
			if item.creator.active:
				nameString = ' (%s' % (item.creator.linkString())
			else: 
				nameString = ' (%s' % item.creator.nickname
		else:
			if item.character.active: 
				nameString = ' (%s' % (item.character.linkString())
			else: 
				nameString = ' (%s' % item.character.name
		nameString += ")"
	else:
		nameString = ""
	# curating flag 
	if curating: 
		if item.flaggedForRemoval:
			curateString = '<input type="submit" class="flag_red" value="" name="unflag|%s" title="%s">' % (item.key(), TEMPLATE_TERMS["template_click_here_to_unflag"])
		else:
			curateString = '<input type="submit" class="flag_green" value="" name="flag|%s" title="%s">' % (item.key(), TEMPLATE_TERMS["template_click_here_to_flag"])
	else:
		curateString = ""
	# date string if showing details
	if showDetails:
		dateTimeString = " %s" % TimeDisplay(item.published, member)
	else:
		dateTimeString = ""
	# annotations count string if entry and showing details
	annotationsCountString = ""
	if showDetails and item.__class__.__name__ == "Entry":
		annotationsCountString += " "
		i = 0
		for type in ANNOTATION_TYPES:
			if item.numAnnotations[i] > 0:
				annotationsCountString += "%s%s" % (ImageLinkForAnnotationType(type), item.numAnnotations[i]) 
			i += 1
		if item.numAnswers > 0:
			annotationsCountString += "%s%s" % (ImageLinkForAnswer(), item.numAnswers)
		if item.numLinks > 0:
			annotationsCountString += "%s%s" % (ImageLinkForLink(), item.numLinks)
	# longer text if showing details
	if showDetails:
		if item.__class__.__name__ == "Annotation":
			if item.type == "comment" or item.type == "request":
				if item.longString_formatted:
					textString = ": %s" % upToWithLink(stripTags(item.longString_formatted), SHORT_DISPLAY_LENGTH, item.linkURL())
				else:
					textString = ""
			else:
				textString = ""
		elif item.__class__.__name__ == "Entry":
			if item.text_formatted:
				textString = " %s" % upToWithLink(stripTags(item.text_formatted), SHORT_DISPLAY_LENGTH, item.linkURL())
			else:
				textString = ""
		else:
			textString = ""
	else:
		textString = ""
	return '<p>%s %s %s %s%s%s%s%s%s</p>' % (item.getImageLinkForType(), fontSizeStartString, curateString, linkString, fontSizeEndString, nameString, dateTimeString, annotationsCountString, textString)

def GetMinMaxNudgeAndActivityPointsFromListOfItems(items, member, location):
		maxNudgePoints = -9999999
		minNudgePoints = -9999999
		minActivityPoints = -9999999
		maxActivityPoints = -9999999
		exist, show = NudgeCategoriesExistAndShouldBeShownInContext(member, location)
		for item in items:
			if item.__class__.__name__ == "Entry":
				nudgePoints = item.nudgePointsForExistAndShowOptions(exist, show)
				activityPoints = item.activityPoints
			else:
				nudgePoints = item.getEntryNudgePointsWhenPublishedForExistAndShowOptions(exist, show)
				activityPoints = item.entryActivityPointsWhenPublished
			if minNudgePoints == -9999999:
				minNudgePoints = nudgePoints
			elif nudgePoints < minNudgePoints:
				minNudgePoints = nudgePoints
			if maxNudgePoints == -9999999:
				maxNudgePoints = nudgePoints
			elif nudgePoints > maxNudgePoints:
				maxNudgePoints = nudgePoints
			if minActivityPoints == -9999999:
				minActivityPoints = activityPoints
			elif activityPoints < minActivityPoints:
				minActivityPoints = activityPoints
			if maxActivityPoints == -9999999:
				maxActivityPoints = activityPoints
			elif activityPoints > maxActivityPoints:
				maxActivityPoints = activityPoints
		return minNudgePoints, maxNudgePoints, minActivityPoints, maxActivityPoints
	


