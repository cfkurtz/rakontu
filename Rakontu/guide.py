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
		community, member, access = GetCurrentCommunityAndMemberFromSession()
		if access:
			if member.isGuide():
				template_values = GetStandardTemplateDictionaryAndAddMore({
							   	   'title': "Resources", 
						   	   	   'title_extra': None, 
								   'community': community, 
								   'resources': community.getNonDraftEntriesOfType("resource"),
								   'current_member': member,
								   })
				path = os.path.join(os.path.dirname(__file__), 'templates/guide/resources.html')
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect("/visit/look")
		else:
			self.redirect("/")
			
	@RequireLogin 
	def post(self):
		community, member, access = GetCurrentCommunityAndMemberFromSession()
		if access:
			if member.isGuide():
				resources = community.getNonDraftEntriesOfType("resource")
				for resource in resources:
					 if self.request.get("flag|%s" % resource.key()) == "yes":
					 	resource.flaggedForRemoval = not resource.flaggedForRemoval
					 	resource.put()
				self.redirect('/result?changessaved')
						
class ReviewRequestsPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		community, member, access = GetCurrentCommunityAndMemberFromSession()
		if access:
			if member.isGuide():
				requestsByType = []
				for type in REQUEST_TYPES:
					requests = Annotation.all().filter("community = ", community.key()).filter("draft = ", False).filter("typeIfRequest = ", type).fetch(FETCH_NUMBER)
					requestsByType.append(requests)
				template_values = GetStandardTemplateDictionaryAndAddMore({
							   	   'title': "Resources", 
						   	   	   'title_extra': None, 
								   'community': community, 
								   'current_member': member,
								   'requests': requestsByType,
								   'num_types': NUM_REQUEST_TYPES,
								   'request_types': REQUEST_TYPES,
								   })
				path = os.path.join(os.path.dirname(__file__), 'templates/guide/requests.html')
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect("/visit/look")
		else:
			self.redirect("/")
			
