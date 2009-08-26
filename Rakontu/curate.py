# --------------------------------------------------------------------------------------------
# RAKONTU
# Description: Rakontu is open source story sharing software.
# Version: pre-0.1
# License: GPL 3.0
# Google Code Project: http://code.google.com/p/rakontu/
# --------------------------------------------------------------------------------------------

from utils import *

class CurateFlagsPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isCuratorOrManagerOrOwner():
				type = GetStringOfTypeFromURLQuery(self.request.query_string, "url_query_type")
				if not type:
					type = "story"
				items = rakontu.getAllFlaggedItemsOfType(type)
				template_values = GetStandardTemplateDictionaryAndAddMore({
							   	   'title': TITLES["REVIEW_FLAGS"], 
						   	   	   'rakontu': rakontu, 
						   	   	   'skin': rakontu.getSkinDictionary(),
						   	   	   'type': type,
						   	   	   'current_member': member,
						   	   	   'items': items,
								   'search_locations': SEARCH_LOCATIONS,
								   'search_locations_display': SEARCH_LOCATIONS_DISPLAY,
								   'flagged_item_types': FLAGGED_ITEM_TYPES,
								   'flagged_item_types_plural_display': FLAGGED_ITEM_TYPES_PLURAL_DISPLAY,
								   })
				path = os.path.join(os.path.dirname(__file__), FindTemplate('curate/flags.html'))
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect(rakontu.linkURL())
		else:
			self.redirect(START)
				
	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if "changeSelections" in self.request.arguments():
				query = "%s=%s" % (URL_OPTIONS["url_query_type"], self.request.get("type"))
				url = BuildURL("dir_curate", "url_flags", query, rakontu=rakontu)
				self.redirect(url)
			else:
				items = rakontu.getAllFlaggedItemsOfType(self.request.get("type"))
				for item in items:
					if self.request.get("flagComment|%s" % item.key()):
						item.flagComment = self.request.get("flagComment|%s" % item.key())
						item.put()
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
							if item.__class__.__name__ == "Entry":
								item.removeAllDependents()
							elif item.__class__.__name__ == "SavedSearch":
								item.deleteAllDependents()
							db.delete(item)
					self.redirect(BuildURL("dir_curate", "url_flags", rakontu=rakontu))
				elif member.isCurator():
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
							elif item.__class__.__name__ == "SavedSearch":
								linkKey = item.key()
								displayString = item.name
							if item.__class__.__name__ == "SavedSearch":
								messageLines.append('* %s\n\n	http://%s/%s/%s?%s (%s)\n' % (displayString, URL, DIRS["dir_visit"], URLS["url_home"], linkKey, item.flagComment))
							else:
								messageLines.append('* %s\n\n	http://%s/%s/%s?%s (%s)\n' % (displayString, URL, DIRS["dir_visit"], URLS["url_curate"], linkKey, item.flagComment))
						messageLines.append("%s\n" % TERMS["term_thank_you"])
						messageLines.append("%s," % TERMS["term_sincerely"])
						messageLines.append("	%s" % TERMS["term_your_site"])
						message = "\n".join(messageLines)
						ownersAndManagers = rakontu.getManagersAndOwners()
						for ownerOrManager in ownersAndManagers:
							messageLines.insert(0, "% %s:\n" % TERMS["term_dear_manager"], ownerOrManager.nickname)
							messageBody = "\n".join(messageLines)
							message = mail.EmailMessage()
							message.sender = rakontu.contactEmail
							message.subject = subject
							message.to = ownerOrManager.googleAccountEmail
							message.body = messageBody
							DebugPrint(messageBody)
							message.send()
						self.redirect(BuildResultURL("messagesent", rakontu=rakontu))
				else:
					self.redirect(rakontu.linkURL())
		else:
			self.redirect(START)
			
class CurateGapsPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isCurator():
				show = GetStringOfTypeFromURLQuery(self.request.query_string, "url_query_show")
				if not show:
					show = "entries_no_tags"
				type = GetStringOfTypeFromURLQuery(self.request.query_string, "url_query_type")
				if not type:
					type = "story"
				sortBy = GetStringOfTypeFromURLQuery(self.request.query_string, "url_query_sort_by")
				if not sortBy:
					sortBy = "date"
				entries = rakontu.getNonDraftEntriesLackingMetadata(show, type, sortBy)
				template_values = GetStandardTemplateDictionaryAndAddMore({
							   	   'title': TITLES["REVIEW_GAPS"], 
								   'rakontu': rakontu, 
								   'skin': rakontu.getSkinDictionary(),
								   'show': show,
								   'sort_by': sortBy,
								   'type': type,
								   'entries': entries,
								   'current_member': member,
								   })
				path = os.path.join(os.path.dirname(__file__), FindTemplate('curate/gaps.html'))
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect(rakontu.linkURL())
		else:
			self.redirect(START)
			
	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isCurator():
				if "changeSelections" in self.request.arguments():
					query = "%s=%s&%s=%s&%s=%s" % (
							URL_OPTIONS["url_query_sort_by"], self.request.get("sortBy"), 
							URL_OPTIONS["url_query_type"], self.request.get("type"),
							URL_OPTIONS["url_query_show"], self.request.get("show"))
					url = BuildURL("dir_curate", "url_gaps", query, rakontu=rakontu)
					self.redirect(url)
				else:
					url = BuildURL("dir_curate", "url_gaps", rakontu=rakontu)
					self.redirect(url)
			else:
				self.redirect(rakontu.linkURL())
		else:
			self.redirect(START)
			
class CurateAttachmentsPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isCurator():
				template_values = GetStandardTemplateDictionaryAndAddMore({
							   	   'title': TITLES["REVIEW_ATTACHMENTS"], 
								   'rakontu': rakontu, 
								   'skin': rakontu.getSkinDictionary(),
								   'attachments': rakontu.getAttachmentsForAllNonDraftEntries(),
								   'current_member': member,
								   })
				path = os.path.join(os.path.dirname(__file__), FindTemplate('curate/attachments.html'))
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect(rakontu.linkURL())
		else:
			self.redirect(START)
			
	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isCurator():
				for attachment in rakontu.getAttachmentsForAllNonDraftEntries():
					if "flag|%s" % attachment.entry.key() in self.request.arguments():
						attachment.entry.flaggedForRemoval = True
						attachment.entry.put()
					elif "unflag|%s" % attachment.entry.key() in self.request.arguments():
						attachment.entry.flaggedForRemoval = False
						attachment.entry.put()
				self.redirect(BuildURL("dir_curate", "url_attachments", rakontu=rakontu))
			else:
				self.redirect(rakontu.linkURL())
		else:
			self.redirect(START)

class CurateTagsPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isCurator():
				template_values = GetStandardTemplateDictionaryAndAddMore({
							   	   'title': TITLES["REVIEW_TAGS"], 
								   'rakontu': rakontu, 
								   'skin': rakontu.getSkinDictionary(),
								   'tag_sets': rakontu.getNonDraftTagSets(),
								   'current_member': member,
								   })
				path = os.path.join(os.path.dirname(__file__), FindTemplate('curate/tags.html'))
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect(rakontu.linkURL())
		else:
			self.redirect(START)
			
	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isCurator():
				tagsets = rakontu.getNonDraftTagSets()
				for tagset in tagsets:
					tagset.tagsIfTagSet = []
					for i in range(NUM_TAGS_IN_TAG_SET):
						if self.request.get("tag%s|%s" % (i, tagset.key())):
							tagset.tagsIfTagSet.append(self.request.get("tag%s|%s" % (i, tagset.key())))
						else:
							tagset.tagsIfTagSet.append("")
					if "flag|%s" % tagset.key() in self.request.arguments():
						tagset.flaggedForRemoval = True
					elif "unflag|%s" % tagset.key() in self.request.arguments():
						tagset.flaggedForRemoval = False
				db.put(tagsets)
				self.redirect(BuildURL("dir_curate", "url_tags", rakontu=rakontu))

