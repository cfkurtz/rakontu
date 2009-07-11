# --------------------------------------------------------------------------------------------
# RAKONTU
# Description: Rakontu is open source story sharing software.
# Version: pre-0.1
# License: GPL 3.0
# Google Code Project: http://code.google.com/p/rakontu/
# --------------------------------------------------------------------------------------------

from utils import *

class AdministerRakontusPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		# this one method does not require a rakontu and member, since the admin has to look at multiple rakontus.
		if users.is_current_user_admin():
			template_values = GetStandardTemplateDictionaryAndAddMore({
						   	   'title': TITLES["REVIEW_RAKONTUS"], 
							   'rakontus': Rakontu.all().fetch(FETCH_NUMBER), 
							   # here we do NOT give the current_member or rakontu
							   })
			path = os.path.join(os.path.dirname(__file__), FindTemplate('admin/review.html'))
			self.response.out.write(template.render(path, template_values))
		else:
			self.redirect(START)
			
	@RequireLogin 
	def post(self):
		# this one method does not require a rakontu and member, since the admin has to look at multiple rakontus.
		if users.is_current_user_admin():
			rakontus = Rakontu.all().fetch(FETCH_NUMBER)
			for aRakontu in rakontus:
				if "toggleActiveState|%s" % aRakontu.key() in self.request.arguments():
					aRakontu.active = not aRakontu.active
					aRakontu.put()
					self.redirect(BuildURL("dir_admin", "url_review"))
				elif "remove|%s" % aRakontu.key() in self.request.arguments():
					aRakontu.removeAllDependents()
					db.delete(aRakontu)
					self.redirect(BuildURL("dir_admin", "url_review"))
				elif "export|%s" % aRakontu.key() in self.request.arguments():
					self.redirect(BuildURL("dir_manage", "url_export", "rakontu_id=%s" % aRakontu.key()))
		else:
			self.redirect(START)
			
class GenerateSampleQuestionsPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		rakontu, member, access = GetCurrentRakontuAndMemberFromSession()
		if access:
			if users.is_current_user_admin():
				GenerateSampleQuestions()
				self.redirect(BuildResultURL("sampleQuestionsGenerated"))
			else:
				self.redirect(START)
		else:
			self.redirect(START)
			
class GenerateSystemResourcesPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		rakontu, member, access = GetCurrentRakontuAndMemberFromSession()
		if access:
			if users.is_current_user_admin():
				GenerateSystemResources()
				self.redirect(BuildResultURL("systemResourcesGenerated"))
			else:
				self.redirect(START)
		else:
			self.redirect(START)
				
class GenerateHelpsPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		rakontu, member, access = GetCurrentRakontuAndMemberFromSession()
		if access:
			if users.is_current_user_admin():
				GenerateHelps()
				self.redirect(BuildResultURL("helpsGenerated"))
			else:
				self.redirect(START)
		else:
			self.redirect(START)
				
