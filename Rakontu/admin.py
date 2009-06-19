# --------------------------------------------------------------------------------------------
# RAKONTU
# Description: Rakontu is open source story sharing software.
# Version: pre-0.1
# License: GPL 3.0
# Google Code Project: http://code.google.com/p/rakontu/
# --------------------------------------------------------------------------------------------

from utils import *

class AdministerCommunitiesPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		# this one method does not require a community and member, since the admin has to look at multiple communities.
		if users.is_current_user_admin():
			template_values = GetStandardTemplateDictionaryAndAddMore({
						   	   'title': "All communities", 
					   	   	   'title_extra': None, 
							   'communities': Community.all().fetch(FETCH_NUMBER), 
							   # here we do NOT give the current_member or community
							   })
			path = os.path.join(os.path.dirname(__file__), 'templates/admin/showAllCommunities.html')
			self.response.out.write(template.render(path, template_values))
		else:
			self.redirect('/')
			
	@RequireLogin 
	def post(self):
		# this one method does not require a community and member, since the admin has to look at multiple communities.
		DebugPrint("AdministerCommunitiesPage POST")
		if users.is_current_user_admin():
			communities = Community.all().fetch(FETCH_NUMBER)
			for aCommunity in communities:
				if "toggleActiveState|%s" % aCommunity.key() in self.request.arguments():
					aCommunity.active = not aCommunity.active
					aCommunity.put()
					self.redirect('/admin/communities')
				elif "remove|%s" % aCommunity.key() in self.request.arguments():
					aCommunity.removeAllDependents()
					db.delete(aCommunity)
					self.redirect('/admin/communities')
				elif "export|%s" % aCommunity.key() in self.request.arguments():
					DebugPrint("export")
					self.redirect("/manage/export?community_id=%s" % aCommunity.key())
		else:
			self.redirect("/")

class GenerateSystemQuestionsPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		community, member, access = GetCurrentCommunityAndMemberFromSession()
		if access:
			if users.is_current_user_admin():
				GenerateSystemQuestions()
				self.redirect('/result?systemQuestionsGenerated')
			else:
				self.redirect('/')
		else:
			self.redirect('/')
				
class GenerateHelpsPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		community, member, access = GetCurrentCommunityAndMemberFromSession()
		if access:
			if users.is_current_user_admin():
				GenerateHelps()
				self.redirect('/result?helpsGenerated')
			else:
				self.redirect('/')
		else:
			self.redirect('/')
				
