# --------------------------------------------------------------------------------------------
# RAKONTU
# Description: Rakontu is open source story sharing software.

# License: GPL 3.0
# Google Code Project: http://code.google.com/p/rakontu/
# --------------------------------------------------------------------------------------------

from utils import *

class CurateFlagsPage(ErrorHandlingRequestHander):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isCuratorOrManagerOrOwner():
				(entries, annotations, answers, links, filters) = rakontu.getAllFlaggedItems()
				template_values = GetStandardTemplateDictionaryAndAddMore({
							   	   'title': TITLES["REVIEW_FLAGS"], 
						   	   	   'rakontu': rakontu, 
						   	   	   'skin': rakontu.getSkinDictionary(),
						   	   	   'current_member': member,
								   'entries': entries,
								   'annotations': annotations,
								   'answers': answers,
								   'links': links,
								   'filters': filters,
								   'filter_locations': FILTER_LOCATIONS,
								   'filter_locations_display': FILTER_LOCATIONS_DISPLAY,
								   'changes_saved': GetChangesSavedState(member),
								   })
				path = os.path.join(os.path.dirname(__file__), FindTemplate('curate/flags.html'))
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect(RoleNotFoundURL("curator", rakontu))
		else:
			self.redirect(NoAccessURL(rakontu, member, users.is_current_user_admin()))
				
	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			user = users.get_current_user()
			items = rakontu.getAllFlaggedItemsAsOneList()
			def txn(items):
				itemsToPut = []
				for item in items:
					if self.request.get("flagComment|%s" % item.key()):
						item.flagComment = self.request.get("flagComment|%s" % item.key())
						itemsToPut.append(item)
					if self.request.get("unflag|%s" % item.key()) == "yes":
					 	item.flaggedForRemoval = False
					 	itemsToPut.append(item)
				db.put(itemsToPut)
			db.run_in_transaction(txn, items)
			if member.isManagerOrOwner():
				itemsToPut = []
				itemsToDelete = []
				# the reason you can't do this stuff inside the transaction is that
				# entries being deleted have to look up links whose ancestors are other entries
				# hence you can't use an ancestor query, hence you can't do it inside the transaction
				for item in items:
					if self.request.get("removeComment|%s" % item.key()) == "yes":
						if item.__class__.__name__ == "Annotation": 
							if item.isNudge():	
								item.shortString = ""
							elif item.isRequest():
								item.completionCommentIfRequest = ""
						elif item.__class__.__name__ == "Link":
							item.comment = ""
						itemsToPut.append(item)
					elif self.request.get("remove|%s" % item.key()) == "yes":
						if item.__class__.__name__ == "Entry":
							itemsToDelete.extend(item.listAllDependents())
						elif item.__class__.__name__ == "SavedFilter":
							itemsToDelete.extend(item.getQuestionReferences())
						itemsToDelete.append(item)
				def txn(itemsToPut, itemsToDelete):
					db.put(itemsToPut)
					db.delete(itemsToDelete)
				db.run_in_transaction(txn, itemsToPut, itemsToDelete)
				SetChangesSaved(member)
				self.redirect(BuildURL("dir_curate", "url_flags", rakontu=rakontu))
			elif member.isCurator():
				# make sure we have the correct email for them
				if member.googleAccountID == user.user_id() and member.googleAccountEmail != user.email():
					member.googleAccountEmail = user.email()
					member.put()
				itemsToSendMessageAbout = []
				for item in items:
					if self.request.get("notify|%s" % item.key()) == "yes":
						itemsToSendMessageAbout.append(item)
				if itemsToSendMessageAbout:
					subject = "%s %s" % (TERMS["term_reminder"], member.nickname)
					URL = self.request.headers["Host"]
					messageLines = []
					messageLines.append("%s\n" % TERMS["term_wanted_you_to_know"])
					itemsToSendMessageAbout.reverse()
					for item in itemsToSendMessageAbout:
						if item.__class__.__name__ == "Entry":
							linkKey = item.key()
							displayString = '%s (%s)' % (item.title, item.typeForDisplay())
						elif item.__class__.__name__ == "Annotation":
							linkKey = item.entry.key()
							if item.shortString:
								shortString = " (%s)" % item.shortString
							else:
								shortString = ""
							displayString = '%s (%s) - "%s" (%s)' % (item.typeForDisplay(), shortString, item.entry.title, item.entry.typeForDisplay())
 						elif item.__class__.__name__ == "Answer":
							linkKey = item.referent.key()
							displayString = '%s %s - "%s" (%s)' % (item.question.text, item.displayString(), item.referent.title, item.referent.typeForDisplay())
						elif item.__class__.__name__ == "Link":
							linkKey = item.itemFrom.key()
							if item.comment:
								commentString = " (%s)" % item.comment
							else:
								commentString = ""
							displayString = '%s %s%s "%s" (%s) --> "%s" (%s)' % \
								(item.itemFrom.type, TERMS["term_link"], commentString, item.itemFrom.displayString(), \
								item.itemTo.typeForDisplay(), item.itemTo.displayString(), item.itemTo.typeForDisplay())
						elif item.__class__.__name__ == "SavedFilter":
							linkKey = item.key()
							displayString = item.name
						if item.__class__.__name__ == "SavedFilter":
							messageLines.append('* %s\n\n	http://%s/%s/%s?%s (%s)\n' % (displayString, URL, DIRS["dir_visit"], URLS["url_home"], linkKey, item.flagComment))
						else:
							messageLines.append('* %s\n\n	http://%s/%s/%s?%s (%s)\n' % (displayString, URL, DIRS["dir_visit"], URLS["url_curate"], linkKey, item.flagComment))
					messageLines.append("%s\n" % TERMS["term_thank_you"])
					messageLines.append("%s," % TERMS["term_sincerely"])
					messageLines.append("	%s" % TERMS["term_your_site"])
					message = "\n".join(messageLines)
					ownersAndManagers = rakontu.getManagersAndOwners()
					for ownerOrManager in ownersAndManagers:
						if mail.is_email_valid(ownerOrManager.googleAccountEmail):
							messageLines.insert(0, "% %s:\n" % TERMS["term_dear_manager"], ownerOrManager.nickname)
							messageBody = "\n".join(messageLines)
							message = mail.EmailMessage()
							message.sender = member.googleAccountEmail 
							message.reply_to = member.googleAccountEmail
							message.subject = subject
							message.to = ownerOrManager.googleAccountEmail
							message.body = messageBody
							try:
								message.send()
							except Exception, e:
								logging.error(e)
								self.redirect(BuildResultURL("couldNotSendMessage", rakontu=rakontu))
								return
					self.redirect(BuildResultURL("messagesent", rakontu=rakontu))
				else:
					SetChangesSaved(member)
					self.redirect(BuildURL("dir_curate", "url_flags", rakontu=rakontu))
			else:
				self.redirect(RoleNotFoundURL("curator", rakontu))
		else:
			self.redirect(NoAccessURL(rakontu, member, users.is_current_user_admin()))
			
class CurateGapsPage(ErrorHandlingRequestHander):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isCurator():
				show = GetStringOfTypeFromURLQuery(self.request.query_string, "url_query_show")
				if not show:
					show = GAPS_SHOW_CHOICES_URLS[0] # no tags
				type = GetStringOfTypeFromURLQuery(self.request.query_string, "url_query_type")
				if not type:
					type = ENTRY_TYPES_URLS[0] # story
				sortBy = GetStringOfTypeFromURLQuery(self.request.query_string, "url_query_sort_by")
				if not sortBy:
					sortBy = GAPS_SORT_BY_CHOICES_URLS[0] # date
				bookmark = GetBookmarkQueryWithCleanup(self.request.query_string)
				prev, entries, next = rakontu.getNonDraftEntriesLackingMetadata_WithPaging(show, type, sortBy, bookmark)
				template_values = GetStandardTemplateDictionaryAndAddMore({
							   	   'title': TITLES["REVIEW_GAPS"], 
								   'rakontu': rakontu, 
								   'skin': rakontu.getSkinDictionary(),
								   'show': show,
								   'sort_by': sortBy,
								   'type': type,
								   'entries': entries,
								   'current_member': member,
								   'bookmark': bookmark,
								   'previous': prev,
								   'next': next,
								   'entry_types_urls': ENTRY_TYPES_URLS,
								   'sort_by_choices_urls': GAPS_SORT_BY_CHOICES_URLS,
								   'sort_by_choices_display': GAPS_SORT_BY_CHOICES_DISPLAY,
								   'show_choices_urls': GAPS_SHOW_CHOICES_URLS,
								   'show_choices_display': GAPS_SHOW_CHOICES_DISPLAY,
								   })
				path = os.path.join(os.path.dirname(__file__), FindTemplate('curate/gaps.html'))
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect(RoleNotFoundURL("curator", rakontu))
		else:
			self.redirect(NoAccessURL(rakontu, member, users.is_current_user_admin()))
			
	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isCurator():
				bookmark = GetBookmarkQueryWithCleanup(self.request.query_string)
				if "changeSelections" in self.request.arguments():
					query = "%s=%s&%s=%s&%s=%s&%s" % (
							URL_OPTIONS["url_query_sort_by"], self.request.get("sortBy"), 
							URL_OPTIONS["url_query_type"], self.request.get("show_type"),
							URL_OPTIONS["url_query_show"], self.request.get("show"),
							rakontu.urlQuery())
					if bookmark:
						query += "&%s=%s" % (URL_OPTIONS["url_query_bookmark"], bookmark)
					url = BuildURL("dir_curate", "url_gaps", query)
					self.redirect(url)
				else:
					url = BuildURL("dir_curate", "url_gaps", rakontu=rakontu)
					self.redirect(url)
			else:
				self.redirect(RoleNotFoundURL("curator", rakontu))
		else:
			self.redirect(NoAccessURL(rakontu, member, users.is_current_user_admin()))
			
class CurateAttachmentsPage(ErrorHandlingRequestHander):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isCurator():
				bookmark = GetBookmarkQueryWithCleanup(self.request.query_string)
				prev, attachments, next = rakontu.getAttachments_WithPaging(bookmark)
				template_values = GetStandardTemplateDictionaryAndAddMore({
							   	   'title': TITLES["REVIEW_ATTACHMENTS"], 
								   'rakontu': rakontu, 
								   'skin': rakontu.getSkinDictionary(),
								   'attachments': attachments,
								   'current_member': member,
								   'bookmark': bookmark,
								   'previous': prev,
								   'next': next,
								   })
				path = os.path.join(os.path.dirname(__file__), FindTemplate('curate/attachments.html'))
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect(RoleNotFoundURL("curator", rakontu))
		else:
			self.redirect(NoAccessURL(rakontu, member, users.is_current_user_admin()))
			
	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isCurator():
				bookmark = GetBookmarkQueryWithCleanup(self.request.query_string)
				prev, attachments, next = rakontu.getAttachments_WithPaging(bookmark)
				def txn(attachments):
					entriesToPut = []
					for attachment in attachments:
						if "flag|%s" % attachment.entry.key() in self.request.arguments():
							attachment.entry.flaggedForRemoval = True
							entriesToPut.append(attachment.entry)
						elif "unflag|%s" % attachment.entry.key() in self.request.arguments():
							attachment.entry.flaggedForRemoval = False
							entriesToPut.append(attachment.entry)
					db.put(entriesToPut)
				db.run_in_transaction(txn, attachments)
				if bookmark:
					# bookmark must be last, because of the extra == the PageQuery puts on it
					query = "%s=%s&%s=%s" % (URL_IDS["url_query_rakontu"], rakontu.getKeyName(), URL_OPTIONS["url_query_bookmark"], bookmark)
				else:
					query = "%s=%s" % (URL_IDS["url_query_rakontu"], rakontu.getKeyName())
				self.redirect(BuildURL("dir_curate", "url_attachments", query))
			else:
				self.redirect(RoleNotFoundURL("curator", rakontu))
		else:
			self.redirect(NoAccessURL(rakontu, member, users.is_current_user_admin()))

class CurateTagsPage(ErrorHandlingRequestHander):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isCurator():
				bookmark = GetBookmarkQueryWithCleanup(self.request.query_string)
				prev, tagSets, next = rakontu.getTagSets_WithPaging(bookmark)
				entryDictionaryWithTagSets = {}
				# note, i'm trying to aggregate all tag sets per entry here, 
				# but for some reason it won't aggregate by the object itself. i have to use the index instead
				# so the object (entry) is the first in the series, the rest are tag sets
				for tagSet in tagSets:
					entry = tagSet.entry
					index = indexFromKeyName(entry.getKeyName())
					if not entryDictionaryWithTagSets.has_key(index):
						entryDictionaryWithTagSets[index] = [entry]
					entryDictionaryWithTagSets[index].append(tagSet)
				alreadyThereTags = rakontu.getTags()
				tagCounts = rakontu.getTagsWithCountsSorted()
				template_values = GetStandardTemplateDictionaryAndAddMore({
							   	   'title': TITLES["REVIEW_TAGS"], 
								   'rakontu': rakontu, 
								   'skin': rakontu.getSkinDictionary(),
								   'tag_sets': tagSets,
								   'entries_with_tag_sets_dict': entryDictionaryWithTagSets,
								   'already_there_tags': alreadyThereTags,
								   'tag_counts': tagCounts,
								   'current_member': member,
								   'bookmark': bookmark,
								   'previous': prev,
								   'next': next,
								   'changes_saved': GetChangesSavedState(member),
								   })
				path = os.path.join(os.path.dirname(__file__), FindTemplate('curate/tags.html'))
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect(RoleNotFoundURL("curator", rakontu))
		else:
			self.redirect(NoAccessURL(rakontu, member, users.is_current_user_admin()))
			
	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isCurator():
				bookmark = GetBookmarkQueryWithCleanup(self.request.query_string)
				prev, tagSets, next = rakontu.getTagSets_WithPaging(bookmark)
				def txn(tagSets):
					tagsetsToPut = []
					for tagset in tagSets:
						if "flag|%s" % tagset.key() in self.request.arguments():
							tagset.flaggedForRemoval = True
							tagsetsToPut.append(tagset)
							break
						elif "unflag|%s" % tagset.key() in self.request.arguments():
							tagset.flaggedForRemoval = False
							tagsetsToPut.append(tagset)
							break
						else:
							tags = []
							for i in range(NUM_TAGS_IN_TAG_SET):
								response = self.request.get("new_tag|%s|%s" % (i, tagset.key()))
								if not response:
									response = self.request.get("existing_tag|%s|%s" % (i, tagset.key()))
								if response.strip() and response != "none":
									tags.append(response)
							if tags:
								tagset.tagsIfTagSet = []
								tagset.tagsIfTagSet.extend(tags)
								tagset.edited = datetime.now(tz=pytz.utc)
								tagsetsToPut.append(tagset)
					if tagsetsToPut:
						db.put(tagsetsToPut)
				db.run_in_transaction(txn, tagSets)
				if bookmark:
					# bookmark must be last, because of the extra == the PageQuery puts on it
					query = "%s=%s&%s=%s" % (URL_IDS["url_query_rakontu"], rakontu.getKeyName(), URL_OPTIONS["url_query_bookmark"], bookmark)
				else:
					query = "%s=%s" % (URL_IDS["url_query_rakontu"], rakontu.getKeyName())
				SetChangesSaved(member)
				self.redirect(BuildURL("dir_curate", "url_tags", query))
			else:
				self.redirect(RoleNotFoundURL("curator", rakontu))
		else:
			self.redirect(NoAccessURL(rakontu, member, users.is_current_user_admin()))

class CurateBulkCreateTagsPage(ErrorHandlingRequestHander):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isCurator():
				show = GAPS_SHOW_CHOICES_URLS[0] # no tags
				sortBy = GAPS_SORT_BY_CHOICES_URLS[0] # date
				type = GetStringOfTypeFromURLQuery(self.request.query_string, "url_query_type")
				if not type:
					type = ENTRY_TYPES_URLS[0] # story
				bookmark = GetBookmarkQueryWithCleanup(self.request.query_string)
				prev, entries, next = rakontu.getNonDraftEntriesLackingMetadata_WithPaging(show, type, sortBy, bookmark)
				template_values = GetStandardTemplateDictionaryAndAddMore({
							   	   'title': TITLES["CREATE_BULK_TAGS"], 
								   'rakontu': rakontu, 
								   'skin': rakontu.getSkinDictionary(),
								   'current_member': member,
								   'bookmark': bookmark,
								   'previous': prev,
								   'next': next,
								   'changes_saved': GetChangesSavedState(member),
								   'entries': entries,
								   'entry_types_urls': ENTRY_TYPES_URLS,
								   'already_there_tags': rakontu.getTags(),
								   'type': type,
								   })
				path = os.path.join(os.path.dirname(__file__), FindTemplate('curate/bulkcreatetags.html'))
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect(RoleNotFoundURL("curator", rakontu))
		else:
			self.redirect(NoAccessURL(rakontu, member, users.is_current_user_admin()))
			
	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isCurator():
				bookmark = GetBookmarkQueryWithCleanup(self.request.query_string)
				if "changeSelections" in self.request.arguments():
					query = "%s=%s&%s" % (
							URL_OPTIONS["url_query_type"], self.request.get("show_type"),
							rakontu.urlQuery())
					if bookmark:
						query += "&%s=%s" % (URL_OPTIONS["url_query_bookmark"], bookmark)
					url = BuildURL("dir_curate", "url_bulkcreatetags", query)
					self.redirect(url)
				else:
					show = GAPS_SHOW_CHOICES_URLS[0] # no tags
					sortBy = GAPS_SORT_BY_CHOICES_URLS[0] # date
					type = GetStringOfTypeFromURLQuery(self.request.query_string, "url_query_type")
					if not type:
						type = ENTRY_TYPES_URLS[0] # story
					prev, entries, next = rakontu.getNonDraftEntriesLackingMetadata_WithPaging(show, type, sortBy, bookmark)
					thingsToPut = []
					tagsetsToPublish = []
					for entry in entries:
						tags = []
						for i in range(NUM_TAGS_IN_TAG_SET):
							response = self.request.get("new_tag|%s|%s" % (i, entry.key()))
							if not response:
								response = self.request.get("existing_tag|%s|%s" % (i, entry.key()))
							if response and response != "none":
								tags.append(response)
						if tags:
							keyName = GenerateSequentialKeyName("annotation", rakontu)
							tagset = Annotation(
											key_name=keyName, 
											parent=entry, 
											id=keyName, 
											rakontu=rakontu, type="tag set", 
											entry=entry)
							tagset.tagsIfTagSet = []
							tagset.tagsIfTagSet.extend(tags)
							tagset.edited = datetime.now(tz=pytz.utc)
							tagset.creator = member
							tagset.character = None
							tagset.liaison = None
							tagset.inBatchEntryBuffer = False
							tagset.collected = entry.collected
							tagsetsToPublish.append(tagset)
							thingsToPut.append(tagset)
							thingsToPut.append(entry)
					if len(thingsToPut):
						thingsToPut.append(member)
					# finally, commit all changes to the database
					def txn(thingsToPut, tagsetsToPublish):
						# publishing must be done inside the transaction 
						# because it updates counters which rely on a consistent state
						for tagset in tagsetsToPublish:
							tagset.publish()
						db.put(thingsToPut)
					db.run_in_transaction(txn, thingsToPut, tagsetsToPublish)
					if bookmark:
						# bookmark must be last, because of the extra == the PageQuery puts on it
						query = "%s=%s&%s=%s&%s=%s" % (URL_OPTIONS["url_query_type"], type, URL_IDS["url_query_rakontu"], rakontu.getKeyName(), URL_OPTIONS["url_query_bookmark"], bookmark)
					else:
						query = "%s=%s&%s=%s" % (URL_OPTIONS["url_query_type"], type, URL_IDS["url_query_rakontu"], rakontu.getKeyName())
					SetChangesSaved(member)
					self.redirect(BuildURL("dir_curate", "url_bulkcreatetags", query))
			else:
				self.redirect(RoleNotFoundURL("curator", rakontu))
		else:
			self.redirect(NoAccessURL(rakontu, member, users.is_current_user_admin()))

