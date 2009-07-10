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
		rakontu, member, access = GetCurrentRakontuAndMemberFromSession()
		if access:
			if member.isGuide():
				template_values = GetStandardTemplateDictionaryAndAddMore({
							   	   'title': TITLE_REVIEW_RESOURCES, 
								   'rakontu': rakontu, 
								   'resources': rakontu.getNonDraftEntriesOfType("resource"),
								   'current_member': member,
								   'url_resource': URLForEntryType("resource"),
								   })
				path = os.path.join(os.path.dirname(__file__), 'templates/guide/resources.html')
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect(HOME)
		else:
			self.redirect(START)
			
	@RequireLogin 
	def post(self):
		rakontu, member, access = GetCurrentRakontuAndMemberFromSession()
		if access:
			if member.isGuide():
				resources = rakontu.getNonDraftEntriesOfType("resource")
				for resource in resources:
					 if self.request.get("flag|%s" % resource.key()) == "yes":
					 	resource.flaggedForRemoval = not resource.flaggedForRemoval
					 	resource.put()
				self.redirect(BuildResultURL(RESULT_changessaved))
			else:
				self.redirect(HOME)
		else:
			self.redirect(START)
			
class CopySystemResourcesPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		rakontu, member, access = GetCurrentRakontuAndMemberFromSession()
		if access:
			if member.isGuide():
				CopyDefaultResourcesForNewRakontu(rakontu, member)
				self.redirect(BuildURL("dir_guide", "url_resources"))
			else:
				self.redirect(START)
		else:
			self.redirect(START)
						
class ReviewRequestsPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		rakontu, member, access = GetCurrentRakontuAndMemberFromSession()
		if access:
			if member.isGuide():
				uncompletedOnly = self.request.query_string == "uncompleted"
				requestsByType = []
				numRequests = 0
				for type in REQUEST_TYPES:
					if uncompletedOnly:
						requests = Annotation.all().filter("rakontu = ", rakontu.key()).filter("draft = ", False).\
							filter("typeIfRequest = ", type).filter("completedIfRequest = ", False).fetch(FETCH_NUMBER)
					else:
						requests = Annotation.all().filter("rakontu = ", rakontu.key()).filter("draft = ", False).\
							filter("typeIfRequest = ", type).fetch(FETCH_NUMBER)
					requestsByType.append(requests)
					numRequests += len(requests)
				template_values = GetStandardTemplateDictionaryAndAddMore({
							   	   'title': TITLE_REVIEW_REQUESTS, 
								   'rakontu': rakontu, 
								   'current_member': member,
								   'requests': requestsByType,
								   'num_types': len(REQUEST_TYPES),
								   'request_types': REQUEST_TYPES,
								   'showing_all_requests': not uncompletedOnly,
								   'have_requests': numRequests > 0,
								   })
				path = os.path.join(os.path.dirname(__file__), 'templates/guide/requests.html')
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect(HOME)
		else:
			self.redirect(START)
			
	@RequireLogin 
	def post(self):
		rakontu, member, access = GetCurrentRakontuAndMemberFromSession()
		if access:
			if member.isGuide():
				if "submitChanges" in self.request.arguments():
					requests = Annotation.all().filter("rakontu = ", rakontu.key()).filter("draft = ", False).fetch(FETCH_NUMBER)
					for request in requests:
						if self.request.get("toggleComplete|%s" % request.key()):
							request.completedIfRequest = not request.completedIfRequest
							request.put()
					self.redirect(BuildResultURL(RESULT_changessaved))
				elif "showOnlyUncompletedRequests" in self.request.arguments():
					self.redirect(BuildURL("dir_guide", "url_requests", "uncompleted"))
				elif "showAllRequests" in self.request.arguments():
					self.redirect(BuildURL("dir_guide", "url_requests"))
			else:
				self.redirect(HOME)
		else:
			self.redirect(START)
			
class ReviewInvitationsPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		rakontu, member, access = GetCurrentRakontuAndMemberFromSession()
		if access:
			if member.isGuide():
				noResponsesOnly = self.request.query_string == "noresponses"
				invitations = []
				allInvitations = Entry.all().filter("rakontu = ", rakontu.key()).filter("draft = ", False).\
					filter("type = ", "invitation").fetch(FETCH_NUMBER)
				if noResponsesOnly:
					for invitation in allInvitations:
						if not invitation.hasOutgoingLinksOfType("responded"):
							invitations.append(invitation)
				else:
					invitations.extend(allInvitations)
				template_values = GetStandardTemplateDictionaryAndAddMore({
							   	   'title': TITLE_REVIEW_INVITATIONS, 
								   'rakontu': rakontu, 
								   'current_member': member,
								   'invitations': invitations,
								   'showing_all_invitations': not noResponsesOnly,
								   })
				path = os.path.join(os.path.dirname(__file__), 'templates/guide/invitations.html')
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect(HOME)
		else:
			self.redirect(START)
			
	@RequireLogin 
	def post(self):
		rakontu, member, access = GetCurrentRakontuAndMemberFromSession()
		if access:
			if member.isGuide():
				if "showOnlyUnrespondedInvitations" in self.request.arguments():
					self.redirect(BuildURL("dir_guide", "url_invitations", "noresponses"))
				elif "showAllInvitations" in self.request.arguments():
					self.redirect(BuildURL("dir_guide", "url_invitations"))
			else:
				self.redirect(HOME)
		else:
			self.redirect(START)
			