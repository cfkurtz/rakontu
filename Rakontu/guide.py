# --------------------------------------------------------------------------------------------
# RAKONTU
# Description: Rakontu is open source story sharing software.
# Version: pre-0.1
# License: GPL 3.0
# Google Code Project: http://code.google.com/p/rakontu/
# --------------------------------------------------------------------------------------------

from utils import *

class GuideOrphansPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		rakontu, member, access = GetCurrentRakontuAndMemberFromSession()
		if access:
			if member.isGuide():
				sortBy = self.request.query_string
				if not sortBy:
					sortBy = "activity"
				(entriesWithoutTags, \
				entriesWithoutLinks, \
				entriesWithoutAnswers, \
				entriesWithoutComments, \
				invitationsWithoutResponses,
				collagesWithoutInclusions) = rakontu.getNonDraftEntriesWithMissingMetadata(sortBy)
				template_values = GetStandardTemplateDictionaryAndAddMore({
							   	   'title': "Review orphans", 
						   	   	   'title_extra': None, 
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
				path = os.path.join(os.path.dirname(__file__), 'templates/guide/orphans.html')
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect('/visit/home')
		else:
			self.redirect("/")
			
	@RequireLogin 
	def post(self):
		rakontu, member, access = GetCurrentRakontuAndMemberFromSession()
		if access:
			if member.isCurator():
				if "sortBy" in self.request.arguments():
					self.redirect("/guide/orphans?%s" % self.request.get("sortBy"))
			else:
				self.redirect('/visit/home')
		else:
			self.redirect("/")
			
class ReviewResourcesPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		rakontu, member, access = GetCurrentRakontuAndMemberFromSession()
		if access:
			if member.isGuide():
				template_values = GetStandardTemplateDictionaryAndAddMore({
							   	   'title': "Review resources", 
						   	   	   'title_extra': None, 
								   'rakontu': rakontu, 
								   'resources': rakontu.getNonDraftEntriesOfType("resource"),
								   'current_member': member,
								   })
				path = os.path.join(os.path.dirname(__file__), 'templates/guide/resources.html')
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect("/visit/home")
		else:
			self.redirect("/")
			
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
				self.redirect('/result?changessaved')
			else:
				self.redirect("/visit/home")
		else:
			self.redirect("/")
						
class ReviewRequestsPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		rakontu, member, access = GetCurrentRakontuAndMemberFromSession()
		if access:
			if member.isGuide():
				uncompletedOnly = self.request.query_string == "uncompleted"
				requestsByType = []
				for type in REQUEST_TYPES:
					if uncompletedOnly:
						requests = Annotation.all().filter("rakontu = ", rakontu.key()).filter("draft = ", False).\
							filter("typeIfRequest = ", type).filter("completedIfRequest = ", False).fetch(FETCH_NUMBER)
					else:
						requests = Annotation.all().filter("rakontu = ", rakontu.key()).filter("draft = ", False).\
							filter("typeIfRequest = ", type).fetch(FETCH_NUMBER)
					requestsByType.append(requests)
				template_values = GetStandardTemplateDictionaryAndAddMore({
							   	   'title': "Review requests", 
						   	   	   'title_extra': None, 
								   'rakontu': rakontu, 
								   'current_member': member,
								   'requests': requestsByType,
								   'num_types': NUM_REQUEST_TYPES,
								   'request_types': REQUEST_TYPES,
								   })
				path = os.path.join(os.path.dirname(__file__), 'templates/guide/requests.html')
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect("/visit/home")
		else:
			self.redirect("/")
			
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
					self.redirect('/result?changessaved')
				elif "showOnlyUncompletedRequests" in self.request.arguments():
					self.redirect("/guide/requests?uncompleted")
				elif "showAllRequests" in self.request.arguments():
					self.redirect("/guide/requests")
			else:
				self.redirect("/visit/home")
		else:
			self.redirect("/")
			
