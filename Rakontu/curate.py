# --------------------------------------------------------------------------------------------
# RAKONTU
# Description: Rakontu is open source story sharing software.
# Version: pre-0.1
# License: GPL 3.0
# Google Code Project: http://code.google.com/p/rakontu/
# --------------------------------------------------------------------------------------------

from utils import *

class FlagOrUnflagItemPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		rakontu, member, access = GetCurrentRakontuAndMemberFromSession()
		if access:
			item = None
			if self.request.query_string:
				try:
					item = db.get(self.request.query_string)
				except:
					item = None
			if item:
				item.flaggedForRemoval = not item.flaggedForRemoval
				item.put()
				self.redirect(self.request.headers["Referer"])
			else:
				self.redirect(HOME)
		else:
			self.redirect(START)
	
class CurateFlagsPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		rakontu, member, access = GetCurrentRakontuAndMemberFromSession()
		if access:
			if member.isCuratorOrManagerOrOwner():
				(entries, annotations, answers, links, searches) = rakontu.getAllFlaggedItems()
				template_values = GetStandardTemplateDictionaryAndAddMore({
							   	   'title': TITLES["REVIEW_FLAGS"], 
						   	   	   'rakontu': rakontu, 
						   	   	   'current_member': member,
								   'entries': entries,
								   'annotations': annotations,
								   'answers': answers,
								   'links': links,
								   'searches': searches,
								   'search_locations': SEARCH_LOCATIONS,
								   'search_locations_display': SEARCH_LOCATIONS_DISPLAY,
								   })
				path = os.path.join(os.path.dirname(__file__), FindTemplate('curate/flags.html'))
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect(HOME)
		else:
			self.redirect(START)
				
	@RequireLogin 
	def post(self):
		rakontu, member, access = GetCurrentRakontuAndMemberFromSession()
		if access:
			if "cancel" in self.request.arguments():
				self.redirect(HOME)
				return
			items = rakontu.getAllFlaggedItemsAsOneList()
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
				self.redirect(BuildResultURL("changessaved"))
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
						# CFK FIX
						# not putting this last line in until I can start testing it, either locally or on the real server
						#message.send()
					self.redirect(BuildResultURL("messagesent"))
			else:
				self.redirect(HOME)
		else:
			self.redirect(START)
			
class CurateGapsPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		rakontu, member, access = GetCurrentRakontuAndMemberFromSession()
		if access:
			if member.isCurator():
				sortBy = self.request.query_string
				if not sortBy:
					sortBy = "date"
				(entriesWithoutTags, \
				entriesWithoutLinks, \
				entriesWithoutAnswers, \
				entriesWithoutComments, \
				invitationsWithoutResponses,
				collagesWithoutInclusions) = rakontu.getNonDraftEntriesWithMissingMetadata(sortBy)
				template_values = GetStandardTemplateDictionaryAndAddMore({
							   	   'title': TITLES["REVIEW_GAPS"], 
								   'rakontu': rakontu, 
								   'sort_by': sortBy,
								   'entries_without_tags': entriesWithoutTags,
								   'entries_without_links': entriesWithoutLinks,
								   'entries_without_answers': entriesWithoutAnswers,
								   'entries_without_comments': entriesWithoutComments,
								   'invitations_without_responses': invitationsWithoutResponses,
								   'collages_without_inclusions': collagesWithoutInclusions,
								   'current_member': member,
								   })
				path = os.path.join(os.path.dirname(__file__), FindTemplate('curate/gaps.html'))
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect(HOME)
		else:
			self.redirect(START)
			
	@RequireLogin 
	def post(self):
		rakontu, member, access = GetCurrentRakontuAndMemberFromSession()
		if access:
			if member.isCurator():
				if "sortBy" in self.request.arguments():
					self.redirect(BuildURL("dir_curate", "url_gaps", self.request.get("sortBy")))
			else:
				self.redirect(HOME)
		else:
			self.redirect(START)
			
class CurateAttachmentsPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		rakontu, member, access = GetCurrentRakontuAndMemberFromSession()
		if access:
			if member.isCurator():
				template_values = GetStandardTemplateDictionaryAndAddMore({
							   	   'title': TITLES["REVIEW_ATTACHMENTS"], 
								   'rakontu': rakontu, 
								   'attachments': rakontu.getAttachmentsForAllNonDraftEntries(),
								   'current_member': member,
								   })
				path = os.path.join(os.path.dirname(__file__), FindTemplate('curate/attachments.html'))
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect(HOME)
		else:
			self.redirect(START)
			
class CurateTagsPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		rakontu, member, access = GetCurrentRakontuAndMemberFromSession()
		if access:
			if member.isCurator():
				template_values = GetStandardTemplateDictionaryAndAddMore({
							   	   'title': TITLES["REVIEW_TAGS"], 
								   'rakontu': rakontu, 
								   'tag_sets': rakontu.getNonDraftTagSets(),
								   'current_member': member,
								   })
				path = os.path.join(os.path.dirname(__file__), FindTemplate('curate/tags.html'))
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect(HOME)
		else:
			self.redirect(START)
			
	@RequireLogin 
	def post(self):
		rakontu, member, access = GetCurrentRakontuAndMemberFromSession()
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
				db.put(tagsets)
				self.redirect(BuildURL("dir_curate", "url_tags"))

