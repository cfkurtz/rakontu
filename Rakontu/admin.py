# --------------------------------------------------------------------------------------------
# RAKONTU
# Description: Rakontu is open source story sharing software.
# Version: pre-0.1
# License: GPL 3.0
# Google Code Project: http://code.google.com/p/rakontu/
# --------------------------------------------------------------------------------------------

from utils import *

class CreateRakontuPage_PartOne(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		user = users.get_current_user()
		if users.is_current_user_admin():
			template_values = GetStandardTemplateDictionaryAndAddMore({
							   'title': TITLES["CREATE_RAKONTU"],
							   'name_taken': self.request.query_string == "nameTaken",
							   'url': self.request.query_string,
							   })
			path = os.path.join(os.path.dirname(__file__), FindTemplate('admin/create_rakontu_part_one.html'))
			self.response.out.write(template.render(path, template_values))
		else:
			self.redirect(START)
			
	@RequireLogin 
	def post(self):
		user = users.get_current_user()
		if users.is_current_user_admin():
				url = self.request.get('url')
				url = url.strip()
				url = htmlEscape(url)
				url = url.replace(" ", "")
				url.encode("ascii", "ignore")
				foundRakontuWithSameURL = False
				for rakontu in Rakontu.all():
					if rakontu.getKeyName() == url:
						foundRakontuWithSameURL = True
						break
				if not foundRakontuWithSameURL:
					self.redirect(BuildURL("dir_admin", "url_create2", url))
				else:
					self.redirect(BuildURL("dir_admin", "url_create1", "nameTaken"))
		else:
			self.redirect(START)

class CreateRakontuPage_PartTwo(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		user = users.get_current_user()
		if users.is_current_user_admin():
			template_values = GetStandardTemplateDictionaryAndAddMore({
							   'title': TITLES["CREATE_RAKONTU"],
							   "title_extra": self.request.query_string,
							   'rakontu_types': RAKONTU_TYPES,
							   'url': self.request.query_string,
							   })
			path = os.path.join(os.path.dirname(__file__), FindTemplate('admin/create_rakontu_part_two.html'))
			self.response.out.write(template.render(path, template_values))
		else:
			self.redirect(START)
			
	@RequireLogin 
	def post(self):
		user = users.get_current_user()
		if users.is_current_user_admin():
			ownerEmail = self.request.get('ownerEmail').strip()
			if ownerEmail: # cfk fix - check if valid email?
				url = self.request.get('url')
				name = htmlEscape(self.request.get('name'))
				type = self.request.get("type")
				rakontu = Rakontu(key_name=url, name=name, type=type)
				rakontu.initializeFormattedTexts()
				rakontu.put()
				if rakontu.type != RAKONTU_TYPES[-1]:
					GenerateDefaultQuestionsForRakontu(rakontu, rakontu.type)
				GenerateDefaultCharactersForRakontu(rakontu)
				if self.request.get("becomeMember") == "yes" and ownerEmail != user.email():
					member = Member(
						key_name=KeyName("member"), 
						googleAccountEmail=user.email(),
						googleAccountID=user.user_id(),
						active=True,
						rakontu=rakontu,
						governanceType="member",
						nickname = "administrator")
					member.initialize()
					member.put()
				# add new owner as pending member
				newPendingMember = PendingMember(
					key_name=KeyName("pendingmember"), 
					rakontu=rakontu, 
					email=ownerEmail,
					governanceType="owner")
				newPendingMember.put()
				self.redirect(BuildURL("dir_admin", "url_admin"))
		else:
			self.redirect(START)

class AdministerSitePage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		# this one method does not require a rakontu and member, since the admin has to look at multiple rakontus.
		if users.is_current_user_admin():
			numSampleQuestions = Question.all().filter("rakontu = ", None).count()
			numDefaultResources = Entry.all().filter("rakontu = ", None).filter("type = ", "resource").count()
			numHelps = Help.all().count()
			template_values = GetStandardTemplateDictionaryAndAddMore({
						   	   'title': TITLES["REVIEW_RAKONTUS"], 
							   'rakontus': Rakontu.all().fetch(FETCH_NUMBER), 
						   	   'num_sample_questions': numSampleQuestions,
						   	   'num_default_resources': numDefaultResources,
						   	   "num_helps": numHelps,
						   	   'host': self.request.headers["Host"],
							   # here we do NOT give the current_member or rakontu
							   })
			path = os.path.join(os.path.dirname(__file__), FindTemplate('admin/admin.html'))
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
					self.redirect(BuildURL("dir_admin", "url_admin"))
				elif "remove|%s" % aRakontu.key() in self.request.arguments():
					aRakontu.removeAllDependents()
					db.delete(aRakontu)
					self.redirect(BuildURL("dir_admin", "url_admin"))
				elif "export|%s" % aRakontu.key() in self.request.arguments():
					self.redirect(BuildURL("dir_manage", "url_export", aRakontu.urlQuery()))
		else:
			self.redirect(START)
			
class GenerateSampleQuestionsPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		if users.is_current_user_admin():
			GenerateSampleQuestions()
			self.redirect(self.request.headers["Referer"])
		else:
			self.redirect(START)
				
class GenerateSystemResourcesPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		if users.is_current_user_admin():
			GenerateSystemResources()
			self.redirect(self.request.headers["Referer"])
		else:
			self.redirect(START)
				
class GenerateHelpsPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		if users.is_current_user_admin():
			GenerateHelps()
			self.redirect(self.request.headers["Referer"])
		else:
			self.redirect(START)

class GenerateFakeDataPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		if users.is_current_user_admin():
			GenerateFakeTestingData()
			self.redirect(self.request.headers["Referer"])
		else:
			self.redirect(START)
				
class GenerateStressTestPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		if users.is_current_user_admin():
			GenerateStressTestData()
			self.redirect(self.request.headers["Referer"])
		else:
			self.redirect(START)
				
