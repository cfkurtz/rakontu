# --------------------------------------------------------------------------------------------
# RAKONTU
# Description: Rakontu is open source story sharing software.
# Version: pre-0.1
# License: GPL 3.0
# Google Code Project: http://code.google.com/p/rakontu/
# --------------------------------------------------------------------------------------------

from utils import *

class CreateRakontuPage_PartOne(ErrorHandlingRequestHander):
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
			self.redirect(AdminOnlyURL())
			
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
			self.redirect(AdminOnlyURL())

class CreateRakontuPage_PartTwo(ErrorHandlingRequestHander):
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
			self.redirect(AdminOnlyURL())
			
	@RequireLogin 
	def post(self):
		user = users.get_current_user()
		if users.is_current_user_admin():
			ownerEmail = self.request.get('ownerEmail').strip()
			if ownerEmail: # if this is not a valid email, the admin has to fix it
				url = self.request.get('url')
				name = htmlEscape(self.request.get('name'))
				type = self.request.get("type")
				rakontu = Rakontu(key_name=url, name=name, type=type)
				rakontu.initializeFormattedTexts()
				rakontu.initializeCustomSkinText()
				rakontu.put()
				if rakontu.type != RAKONTU_TYPES[-1]: # last type means no default questions
					GenerateDefaultQuestionsForRakontu(rakontu, rakontu.type)
				GenerateDefaultCharactersForRakontu(rakontu)
				keyName = GenerateSequentialKeyName("pendingmember")
				newPendingMember = PendingMember(
					key_name=keyName, 
					rakontu=rakontu, 
					email=ownerEmail,
					governanceType="owner")
				newPendingMember.put()
				self.redirect(BuildURL("dir_admin", "url_admin"))
		else:
			self.redirect(AdminOnlyURL())

class AdministerSitePage(ErrorHandlingRequestHander):
	@RequireLogin 
	def get(self):
		# this method does not require a rakontu and member, since the admin has to look at multiple rakontus.
		if users.is_current_user_admin():
			user = users.get_current_user()
			rakontus = AllRakontus()
			memberOfRakontus = {}
			for rakontu in rakontus:
				member = rakontu.memberWithGoogleUserID(user.user_id())
				if member and member.active:
					memberOfRakontus[rakontu.key()] = member.governanceTypeForDisplay()
				else:
					memberOfRakontus[rakontu.key()] = None
			onlyOwnerOfRakontus = {}
			for rakontu in rakontus:
				member = rakontu.memberWithGoogleUserID(user.user_id())
				if member and member.active:
					onlyOwnerOfRakontus[rakontu.key()] = rakontu.memberIsOnlyOwner(member)
				else:
					onlyOwnerOfRakontus[rakontu.key()] = False
			pendingMemberOfRakontus = {}
			for rakontu in rakontus:
				pendingMember = rakontu.pendingMemberWithGoogleEmail(user.email())
				if pendingMember:
					pendingMemberOfRakontus[rakontu.key()] = pendingMember.governanceTypeForDisplay()
				else:
					pendingMemberOfRakontus[rakontu.key()] = None
			siteResourceNames = []
			resources = SystemEntriesOfType("resource")
			numDefaultResources = len(resources)
			for resource in resources:
				siteResourceNames.append(resource.title)
			siteResourceNamesString = ", ".join(siteResourceNames)
			skinNames = []
			skins = AllSkins()
			numSkins = len(skins)
			for skin in skins:
				skinNames.append(skin.name)
			skinNamesString = ", ".join(skinNames)
			template_values = GetStandardTemplateDictionaryAndAddMore({
						   	   'title': TITLES["REVIEW_RAKONTUS"], 
							   'rakontus': rakontus, 
							   'member_of': memberOfRakontus,
							   'only_owner_of': onlyOwnerOfRakontus,
							   'pending_member_of': pendingMemberOfRakontus,
						   	   'num_sample_questions': NumSystemQuestions(),
						   	   'site_resource_names': siteResourceNamesString,
						   	   'num_default_resources': numDefaultResources,
						   	   "num_helps": NumHelps(),
						   	   'skin_names': skinNamesString,
						   	   "num_skins": numSkins,
						   	   'host': self.request.headers["Host"],
							   # here we do NOT give the current_member or rakontu
							   })
			path = os.path.join(os.path.dirname(__file__), FindTemplate('admin/admin.html'))
			self.response.out.write(template.render(path, template_values))
		else:
			self.redirect(AdminOnlyURL())
			
	@RequireLogin 
	def post(self):
		# this method does not require a rakontu and member, since the admin has to look at multiple rakontus.
		if users.is_current_user_admin():
			rakontus = AllRakontus()
			user = users.get_current_user()
			for aRakontu in rakontus:
				if "joinOrLeave|%s" % aRakontu.key() in self.request.arguments():
					pendingMember = aRakontu.pendingMemberWithGoogleEmail(user.email())
					if pendingMember:
						member = CreateMemberFromPendingMember(aRakontu, pendingMember, user.user_id(), user.email())
					else:
						member = aRakontu.memberWithGoogleUserID(user.user_id())
						joinAs = self.request.get("joinAs|%s" % aRakontu.key())
						if member and not aRakontu.memberIsOnlyOwner(member):
							def txn(member, joinAs):
								member.active = not member.active
								if member.active:
									member.governanceType = joinAs
								member.put()
							db.run_in_transaction(txn, member, joinAs)
						else:
							member = CreateMemberFromInfo(aRakontu, user.user_id(), user.email(), "administrator", joinAs)
					self.redirect(BuildURL("dir_admin", "url_admin"))
				elif "toggleActiveState|%s" % aRakontu.key() in self.request.arguments():
					aRakontu.active = not aRakontu.active
					aRakontu.put()
					self.redirect(BuildURL("dir_admin", "url_admin"))
				elif "addFakeDataTo|%s" % aRakontu.key() in self.request.arguments():
					# no error checking here
					numItems = int(self.request.get('numItems|%s' % aRakontu.key()))
					createWhat = self.request.get('createWhat|%s' % aRakontu.key())
					AddFakeDataToRakontu(aRakontu, numItems, createWhat)
					self.redirect(BuildURL("dir_admin", "url_admin"))
				elif "remove|%s" % aRakontu.key() in self.request.arguments():
					aRakontu.removeAllDependents()
					db.delete(aRakontu)
					self.redirect(BuildURL("dir_admin", "url_admin"))
				elif "export|%s" % aRakontu.key() in self.request.arguments():
					self.redirect(BuildURL("dir_manage", "url_export", aRakontu.urlQuery()))
		else:
			self.redirect(AdminOnlyURL())
			
class GenerateSampleQuestionsPage(ErrorHandlingRequestHander):
	@RequireLogin 
	def get(self):
		if users.is_current_user_admin():
			GenerateSampleQuestions()
			self.redirect(BuildURL("dir_admin", "url_admin"))
		else:
			self.redirect(AdminOnlyURL())
				
class GenerateSystemResourcesPage(ErrorHandlingRequestHander):
	@RequireLogin 
	def get(self):
		if users.is_current_user_admin():
			GenerateSystemResources()
			self.redirect(BuildURL("dir_admin", "url_admin"))
		else:
			self.redirect(AdminOnlyURL())
				
class GenerateHelpsPage(ErrorHandlingRequestHander):
	@RequireLogin 
	def get(self):
		if users.is_current_user_admin():
			GenerateHelps()
			self.redirect(BuildURL("dir_admin", "url_admin"))
		else:
			self.redirect(AdminOnlyURL())
			
class GenerateSkinsPage(ErrorHandlingRequestHander):
	@RequireLogin 
	def get(self):
		if users.is_current_user_admin():
			GenerateSkins()
			self.redirect(BuildURL("dir_admin", "url_admin"))
		else:
			self.redirect(AdminOnlyURL())

class GenerateFakeDataPage(ErrorHandlingRequestHander):
	@RequireLogin 
	def get(self):
		# no transaction: not likely to conflict
		if users.is_current_user_admin():
			GenerateFakeTestingData()
			self.redirect(BuildURL("dir_admin", "url_admin"))
		else:
			self.redirect(AdminOnlyURL())
				
class GenerateStressTestPage(ErrorHandlingRequestHander):
	@RequireLogin 
	def get(self):
		# no transaction: not likely to conflict
		if users.is_current_user_admin():
			GenerateStressTestData()
			self.redirect(BuildURL("dir_admin", "url_admin"))
		else:
			self.redirect(AdminOnlyURL())
				
