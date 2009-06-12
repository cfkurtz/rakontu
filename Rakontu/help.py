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
		community, member = GetCurrentCommunityAndMemberFromSession()
		if community and member:
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
				self.redirect("/visit/look")
		else:
			self.redirect("/")
	
class CurateFlagsPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		community, member = GetCurrentCommunityAndMemberFromSession()
		if community and member:
			if member.isCuratorOrManagerOrOwner():
				(articles, annotations, answers, links) = community.getAllFlaggedItems()
				template_values = {
							   	   'title': "Review flags", 
						   	   	   'title_extra': None, 
								   'community': community, 
								   'articles': articles,
								   'annotations': annotations,
								   'answers': answers,
								   'links': links,
								   'current_user': users.get_current_user(), 
								   'current_member': member,
								   'user_is_admin': users.is_current_user_admin(),
								   'logout_url': users.create_logout_url("/"),
								   }
				path = os.path.join(os.path.dirname(__file__), 'templates/curate/flags.html')
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect('/visit/look')
		else:
			self.redirect("/")
				
	@RequireLogin 
	def post(self):
		community, member = GetCurrentCommunityAndMemberFromSession()
		if community and member:
			items = community.getAllFlaggedItemsAsOneList()
			for item in items:
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
						if item.__class__.__name__ == "Article":
							item.removeAllDependents()
						db.delete(item)
				self.redirect('/result?changessaved')
			elif member.isCurator():
				itemsToSendMessageAbout = []
				for item in items:
					if self.request.get("notify|%s" % item.key()) == "yes":
						itemsToSendMessageAbout.append(item)
				if itemsToSendMessageAbout:
					subject = "Reminder about flagged items from %s" % member.nickname
					URL = self.request.headers["Host"]
					messageLines = []
					messageLines.append("The curator %s wanted you to know that these items require your attention.\n" % member.nickname)
					itemsToSendMessageAbout.reverse()
					for item in itemsToSendMessageAbout:
						if item.__class__.__name__ == "Article":
							linkKey = item.key()
							displayString = 'A %s called "%s"' % (item.type, item.title)
						elif item.__class__.__name__ == "Annotation":
							linkKey = item.article.key()
							if item.shortString:
								shortString = " (%s)" % item.shortString
							else:
								shortString = ""
							displayString = 'A %s%s for the %s called "%s"' % (item.type, shortString, item.article.type, item.article.title)
 						elif item.__class__.__name__ == "Answer":
							linkKey = item.referent.key()
							displayString = 'An answer (%s) for the %s called "%s"' % (item.displayString(), item.referent.type, item.referent.title)
						elif item.__class__.__name__ == "Link":
							linkKey = item.articleFrom.key()
							if item.comment:
								commentString = " (%s)" % item.comment
							else:
								commentString = ""
							displayString = 'A link%s from the %s called "%s" to the %s called "%s"' % \
								(commentString, item.articleFrom.type, item.articleFrom.title, item.articleTo.type, item.articleTo.title)
						messageLines.append('* %s\n\n    http://%s/visit/curate?%s\n' % (displayString, URL, linkKey))
					messageLines.append("Thank you for your attention.\n")
					messageLines.append("Sincerely,")
					messageLines.append("    Your Rakontu site")
					message = "\n".join(messageLines)
					ownersAndManagers = community.getManagersAndOwners()
					for ownerOrManager in ownersAndManagers:
						messageLines.insert(0, "Dear manager %s:\n" % ownerOrManager.nickname)
						messageBody = "\n".join(messageLines)
						message = mail.EmailMessage()
						message.sender = community.contactEmail
						message.subject = subject
						message.to = ownerOrManager.googleAccountEmail
						message.body = messageBody
						DebugPrint(messageBody)
						# CFK FIX
						# not putting this last line in until I can start testing it, either locally or on the real server
						#message.send()
					self.redirect('/result?messagesent')
			else:
				self.redirect("/visit/look")
		else:
			self.redirect("/")
			
class CurateGapsPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		community, member = GetCurrentCommunityAndMemberFromSession()
		if community and member:
			if member.isCuratorOrManagerOrOwner():
				(articlesWithoutTags, \
				articlesWithoutLinks, \
				articlesWithoutAnswers, \
				articlesWithoutComments, \
				invitationsWithoutResponses,
				collagesWithoutInclusions) = community.getNonDraftArticlesWithMissingMetadata()
				template_values = {
							   	   'title': "Review flags", 
						   	   	   'title_extra': None, 
								   'community': community, 
								   'articles_without_tags': articlesWithoutTags,
								   'articles_without_links': articlesWithoutLinks,
								   'articles_without_answers': articlesWithoutAnswers,
								   'articles_without_comments': articlesWithoutComments,
								   'invitations_without_responses': invitationsWithoutResponses,
								   'collages_without_inclusions': collagesWithoutInclusions,
								   'current_user': users.get_current_user(), 
								   'current_member': member,
								   'user_is_admin': users.is_current_user_admin(),
								   'logout_url': users.create_logout_url("/"),
								   }
				path = os.path.join(os.path.dirname(__file__), 'templates/curate/gaps.html')
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect('/visit/look')
		else:
			self.redirect("/")
			
class ReviewResourcesPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		community, member = GetCurrentCommunityAndMemberFromSession()
		if community and member:
			if member.isGuideOrManagerOrOwner():
				template_values = {
							   	   'title': "Resources", 
						   	   	   'title_extra': None, 
								   'community': community, 
								   'resources': community.getNonDraftArticlesOfType("resource"),
								   'current_user': users.get_current_user(), 
								   'current_member': member,
								   'user_is_admin': users.is_current_user_admin(),
								   'logout_url': users.create_logout_url("/"),
								   }
				path = os.path.join(os.path.dirname(__file__), 'templates/guide/resources.html')
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect("/visit/look")
		else:
			self.redirect("/")
			
	@RequireLogin 
	def post(self):
		community, member = GetCurrentCommunityAndMemberFromSession()
		if community and member:
			if member.isGuideOrManagerOrOwner():
				resources = community.getNonDraftArticlesOfType("resource")
				for resource in resources:
					 if self.request.get("flag|%s" % resource.key()) == "yes":
					 	resource.flaggedForRemoval = not resource.flaggedForRemoval
					 	resource.put()
				self.redirect('/result?changessaved')
						
class ReviewOfflineMembersPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		community, member = GetCurrentCommunityAndMemberFromSession()
		if community and member:
				template_values = {
								   'title': "Off-line members", 
						   		   'title_extra': community.name, 
								   'community': community, 
								   'current_member': member,
								   'active_members': community.getActiveOfflineMembers(),
								   'inactive_members': community.getInactiveOfflineMembers(),
								   'user_is_admin': users.is_current_user_admin(),
								   'logout_url': users.create_logout_url("/"),								   
								   }
				path = os.path.join(os.path.dirname(__file__), 'templates/liaise/members.html')
				self.response.out.write(template.render(path, template_values))
		else:
			self.redirect('/')
			
	@RequireLogin 
	def post(self):
		community, member = GetCurrentCommunityAndMemberFromSession()
		if community and member:
			if member.isLiaisonOrManagerOrOwner():
				offlineMembers = community.getActiveOfflineMembers()
				for aMember in offlineMembers:
					if self.request.get("remove|%s" % aMember.key()) == "yes":
						aMember.active = False
						aMember.put()
				memberNicknamesToAdd = cgi.escape(self.request.get("newMemberNicknames")).split('\n')
				for nickname in memberNicknamesToAdd:
					if nickname.strip():
						if not community.hasMemberWithNickname(nickname.strip()):
							newMember = Member(community=community, 
											nickname=nickname.strip(),
											isOnlineMember = False,
											liaisonIfOfflineMember = member,
											googleAccountID = None,
											googleAccountEmail = None)
							newMember.put()
			self.redirect('/liaise/members')

class ImportItemsPage(webapp.RequestHandler):
	@RequireLogin 
	def get(self):
		community, member = GetCurrentCommunityAndMemberFromSession()
		if community and member:
			if member.isLiaisonOrManagerOrOwner():
				template_values = {
							   	   'title': "Import", 
						   	   	   'title_extra': None, 
								   'community': community, 
								   'current_user': users.get_current_user(), 
								   'articles': community.getArticlesInImportBufferForLiaison(member),
								   'current_member': member,
								   'user_is_admin': users.is_current_user_admin(),
								   'logout_url': users.create_logout_url("/"),
								   }
				path = os.path.join(os.path.dirname(__file__), 'templates/liaise/import.html')
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect("/visit/look")
		else:
			self.redirect("/")
			
	@RequireLogin 
	def post(self):
		community, member = GetCurrentCommunityAndMemberFromSession()
		if community and member:
			if member.isLiaisonOrManagerOrOwner():
				if "finalizeImport" in self.request.arguments():
					itemsToFinalize = []
					items = community.getArticlesInImportBufferForLiaison(member)
					for item in items:
						if self.request.get("import|%s" % item.key()) == "yes":
							itemsToFinalize.append(item)
					if itemsToFinalize:
						community.moveImportedArticlesOutOfBuffer(itemsToFinalize)
				elif self.request.get("import"):
					community.addArticlesFromCSV(self.request.get("import"), member)
				self.redirect('/liaise/import')

