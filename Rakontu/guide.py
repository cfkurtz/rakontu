# --------------------------------------------------------------------------------------------
# RAKONTU
# Description: Rakontu is open source story sharing software.
# Version: pre-0.1
# License: GPL 3.0
# Google Code Project: http://code.google.com/p/rakontu/
# --------------------------------------------------------------------------------------------

from utils import *

class ReviewResourcesPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isGuideOrManagerOrOwner():
				template_values = GetStandardTemplateDictionaryAndAddMore({
							   	   'title': TITLES["REVIEW_RESOURCES"], 
								   'rakontu': rakontu, 
								   'skin': rakontu.getSkinDictionary(),
								   'resources': rakontu.getNonDraftEntriesOfType("resource"),
								   'current_member': member,
								   'url_resource': URLForEntryType("resource"),
								   })
				path = os.path.join(os.path.dirname(__file__), FindTemplate('guide/resources.html'))
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect(rakontu.linkURL())
		else:
			self.redirect(START)
			
	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isGuideOrManagerOrOwner():
				resources = rakontu.getNonDraftEntriesOfType("resource")
				for resource in resources:
					if "flag|%s" % resource.key() in self.request.arguments():
						resource.flaggedForRemoval = True
						resource.put()
					elif "unflag|%s" % resource.key() in self.request.arguments():
						resource.flaggedForRemoval = False
						resource.put()
				self.redirect(BuildURL("dir_guide", "url_resources", rakontu=rakontu))
			else:
				self.redirect(rakontu.linkURL())
		else:
			self.redirect(START)
			
class CopySystemResourcesPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isGuideOrManagerOrOwner():
				CopyDefaultResourcesForNewRakontu(rakontu, member)
				self.redirect(BuildURL("dir_visit", "url_help", rakontu=rakontu))
			else:
				self.redirect(START)
		else:
			self.redirect(START)
						
class ReviewRequestsPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isGuide():
				uncompletedOnly = GetStringOfTypeFromURLQuery(self.request.query_string, "url_query_uncompleted") == URL_OPTIONS["url_query_uncompleted"]
				requestsByType = []
				numRequests = 0
				for type in REQUEST_TYPES:
					if uncompletedOnly:
						requests = rakontu.getAllUncompletedNonDraftRequestsOfType(type)
					else:
						requests = rakontu.getAllNonDraftRequestsOfType(type)
					requestsByType.append(requests)
					numRequests += len(requests)
				template_values = GetStandardTemplateDictionaryAndAddMore({
							   	   'title': TITLES["REVIEW_REQUESTS"], 
								   'rakontu': rakontu, 
								   'skin': rakontu.getSkinDictionary(),
								   'current_member': member,
								   'requests': requestsByType,
								   'num_types': len(REQUEST_TYPES),
								   'request_types': REQUEST_TYPES,
								   'showing_all_requests': not uncompletedOnly,
								   'have_requests': numRequests > 0,
								   })
				path = os.path.join(os.path.dirname(__file__), FindTemplate('guide/requests.html'))
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect(rakontu.linkURL())
		else:
			self.redirect(START)
			
	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isGuide():
				if "showOnlyUncompletedRequests" in self.request.arguments():
					query = "%s=%s" % (URL_OPTIONS["url_query_uncompleted"], URL_OPTIONS["url_query_uncompleted"])
					self.redirect(BuildURL("dir_guide", "url_requests", query, rakontu=rakontu))
				elif "showAllRequests" in self.request.arguments():
					self.redirect(BuildURL("dir_guide", "url_requests", rakontu=rakontu))
				else:
					requests = rakontu.getAllNonDraftRequests()
					for request in requests:
						if "setCompleted|%s" % request.key() in self.request.arguments():
							request.completedIfRequest = True
							request.put()
							break
						elif "setUncompleted|%s" % request.key() in self.request.arguments():
							request.completedIfRequest = False
							request.put()
							break
					self.redirect(self.request.uri)
			else:
				self.redirect(rakontu.linkURL())
		else:
			self.redirect(START)
			
class ReviewInvitationsPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isGuide():
				noResponsesOnly = GetStringOfTypeFromURLQuery(self.request.query_string, "url_query_no_responses") == URL_OPTIONS["url_query_no_responses"]
				invitations = []
				allInvitations = rakontu.getNonDraftEntriesOfType("invitation")
				if noResponsesOnly:
					for invitation in allInvitations:
						if not invitation.hasOutgoingLinksOfType("responded"):
							invitations.append(invitation)
				else:
					invitations.extend(allInvitations)
				template_values = GetStandardTemplateDictionaryAndAddMore({
							   	   'title': TITLES["REVIEW_INVITATIONS"], 
								   'rakontu': rakontu, 
								   'skin': rakontu.getSkinDictionary(),
								   'current_member': member,
								   'invitations': invitations,
								   'showing_all_invitations': not noResponsesOnly,
								   })
				path = os.path.join(os.path.dirname(__file__), FindTemplate('guide/invitations.html'))
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect(rakontu.linkURL())
		else:
			self.redirect(START)
			
	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isGuide():
				if "showOnlyUnrespondedInvitations" in self.request.arguments():
					query = "%s=%s" % (URL_OPTIONS["url_query_no_responses"], URL_OPTIONS["url_query_no_responses"])
					self.redirect(BuildURL("dir_guide", "url_invitations", query, rakontu=rakontu))
				elif "showAllInvitations" in self.request.arguments():
					self.redirect(BuildURL("dir_guide", "url_invitations", rakontu=rakontu))
			else:
				self.redirect(rakontu.linkURL())
		else:
			self.redirect(START)
			