# --------------------------------------------------------------------------------------------
# RAKONTU
# Description: Rakontu is open source story sharing software.
# Version: pre-0.1
# License: GPL 3.0
# Google Code Project: http://code.google.com/p/rakontu/
# --------------------------------------------------------------------------------------------

from utils import *

class ShowAllCommunities(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		community, member = GetCurrentCommunityAndMemberFromSession()
		if community and member:
			if users.is_current_user_admin():
				template_values = GetStandardTemplateDictionaryAndAddMore({
							   	   'title': "All communities", 
						   	   	   'title_extra': None, 
								   'communities': Community.all().fetch(FETCH_NUMBER), 
								   'members': Member.all().fetch(FETCH_NUMBER),
								   })
				path = os.path.join(os.path.dirname(__file__), 'templates/admin/showAllCommunities.html')
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect('/')

class ShowAllMembers(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		community, member = GetCurrentCommunityAndMemberFromSession()
		if community and member:
			if users.is_current_user_admin():
				template_values = GetStandardTemplateDictionaryAndAddMore({
							   	   'title': "All members", 
						   	   	   'title_extra': None, 
								   'members': Member.all().fetch(FETCH_NUMBER),
								   })
				path = os.path.join(os.path.dirname(__file__), 'templates/admin/showAllMembers.html')
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect('/')
				
class GenerateSystemQuestionsPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		community, member = GetCurrentCommunityAndMemberFromSession()
		if community and member:
			if users.is_current_user_admin():
				GenerateSystemQuestions()
				self.redirect(self.request.headers["Referer"])
			else:
				self.redirect('/')
				
class GenerateHelpsPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		community, member = GetCurrentCommunityAndMemberFromSession()
		if community and member:
			if users.is_current_user_admin():
				GenerateHelps()
				self.redirect(self.request.headers["Referer"])
			else:
				self.redirect('/')
				
class GenerateSystemResourcesPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		community, member = GetCurrentCommunityAndMemberFromSession()
		if community and member:
			if users.is_current_user_admin():
				GenerateSystemResources(community, member)
				self.redirect(self.request.headers["Referer"])
			else:
				self.redirect('/')
				
