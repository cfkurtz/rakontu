# --------------------------------------------------------------------------------------------
# RAKONTU
# Description: Rakontu is open source story sharing software.

# License: GPL 3.0
# Google Code Project: http://code.google.com/p/rakontu/
# --------------------------------------------------------------------------------------------

from utils import *

class ReviewResourcesPage(ErrorHandlingRequestHander):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isGuideOrManagerOrOwner():
				managersOnlyType = GetStringOfTypeFromURLQuery(self.request.query_string, "url_query_managers_only") 
				if not managersOnlyType:
					managersOnlyType = URL_OPTION_NAMES["url_option_all"]
				type = GetStringOfTypeFromURLQuery(self.request.query_string, "url_query_resource_type")
				if not type:
					type = URL_OPTION_NAMES["url_option_all"]
				resources = rakontu.getNonDraftEntriesOfType("resource")
				resourcesToShowNotConsideringManagers = []
				for resource in resources:
					if type == URL_OPTION_NAMES["url_option_all"]:
						resourcesToShowNotConsideringManagers.append(resource)
					elif type == URL_OPTION_NAMES["url_option_help"]:
						if resource.resourceForHelpPage:
							resourcesToShowNotConsideringManagers.append(resource)
					elif type == URL_OPTION_NAMES["url_option_new"]:
						if resource.resourceForNewMemberPage:
							resourcesToShowNotConsideringManagers.append(resource)
					elif type == URL_OPTION_NAMES["url_option_remind"]:
						if not resource.resourceForHelpPage and not resource.resourceForNewMemberPage:
							resourcesToShowNotConsideringManagers.append(resource)
				resourcesToShow = []
				if managersOnlyType == URL_OPTION_NAMES["url_option_managers_only"]:
					for resource in resourcesToShowNotConsideringManagers:
						if resource.resourceForManagersAndOwnersOnly:
							resourcesToShow.append(resource)
				elif managersOnlyType == URL_OPTION_NAMES["url_option_not_managers_only"]:
					for resource in resourcesToShowNotConsideringManagers:
						if not resource.resourceForManagersAndOwnersOnly:
							resourcesToShow.append(resource)
				elif managersOnlyType == URL_OPTION_NAMES["url_option_all"]:
					resourcesToShow.extend(resourcesToShowNotConsideringManagers)
				resourcesToShow.sort(lambda a,b: cmp(a.orderIfResource, b.orderIfResource))
				resourcesToShow.sort(lambda a,b: cmp(a.categoryIfResource, b.categoryIfResource))
				template_values = GetStandardTemplateDictionaryAndAddMore({
							   	   'title': TITLES["REVIEW_RESOURCES"], 
								   'rakontu': rakontu, 
								   'skin': rakontu.getSkinDictionary(),
								   'resources': resourcesToShow,
								   'current_member': member,
								   'url_resource': URLForEntryType("resource"),
								   'resource_group': type,
								   'managers_only': managersOnlyType,
								   'max_resources_per_category': MAX_RESOURCES_PER_CATEGORY,
								   'changes_saved': GetChangesSavedState(member),
								   })
				path = os.path.join(os.path.dirname(__file__), FindTemplate('guide/resources.html'))
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect(RoleNotFoundURL("guide", rakontu))
		else:
			self.redirect(NoAccessURL(rakontu, member, users.is_current_user_admin()))
			
	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isGuideOrManagerOrOwner():
				managersOnlyType = GetStringOfTypeFromURLQuery(self.request.query_string, "url_query_managers_only") 
				if not managersOnlyType:
					managersOnlyType = URL_OPTION_NAMES["url_option_all"]
				type = GetStringOfTypeFromURLQuery(self.request.query_string, "url_query_resource_type")
				if not type:
					type = URL_OPTION_NAMES["url_option_all"]
				if "changeSelections" in self.request.arguments():
					resourceGroupChoice = self.request.get("show_resource_group")
					managersOnlyChoice = self.request.get("show_managers_only")
					query = "%s&%s=%s&%s=%s" % (rakontu.urlQuery(), URL_OPTIONS["url_query_resource_type"], resourceGroupChoice, 
									URL_OPTIONS["url_query_managers_only"], managersOnlyChoice)
					self.redirect(BuildURL("dir_guide", "url_resources", query))
				else:
					resources = rakontu.getNonDraftEntriesOfType("resource")
					def txn(resources):
						resourcesToPut = []
						for resource in resources:
						 	if "submitChangesToOrders" in self.request.arguments():
								if self.request.get("order|%s" % resource.key()):
									oldValue = resource.orderIfResource
									try:
										resource.orderIfResource = int(self.request.get("order|%s" % resource.key()))
									except:
										resource.orderIfResource = oldValue
									resourcesToPut.append(resource)
							elif "flag|%s" % resource.key() in self.request.arguments():
								resource.flaggedForRemoval = True
								resourcesToPut.append(resource)
							elif "unflag|%s" % resource.key() in self.request.arguments():
								resource.flaggedForRemoval = False
								resourcesToPut.append(resource)
						db.put(resourcesToPut)
					db.run_in_transaction(txn, resources)
					query = "%s&%s=%s&%s=%s" % (rakontu.urlQuery(), URL_OPTIONS["url_query_resource_type"], type, 
									URL_OPTIONS["url_query_managers_only"], managersOnlyType)
					SetChangesSaved(member)
					self.redirect(BuildURL("dir_guide", "url_resources", query))
			else:
				self.redirect(RoleNotFoundURL("guide", rakontu))
		else:
			self.redirect(NoAccessURL(rakontu, member, users.is_current_user_admin()))
			
class CopySystemResourcesPage(ErrorHandlingRequestHander):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isGuideOrManagerOrOwner():
				CopyDefaultResourcesForNewRakontu(rakontu, member)
				self.redirect(BuildURL("dir_visit", "url_help", rakontu=rakontu))
			else:
				self.redirect(RoleNotFoundURL("guide", rakontu))
		else:
			self.redirect(NoAccessURL(rakontu, member, users.is_current_user_admin()))
						
class ReviewRequestsPage(ErrorHandlingRequestHander):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isGuide():
				uncompletedOnly = GetStringOfTypeFromURLQuery(self.request.query_string, "url_query_uncompleted") == URL_OPTION_NAMES["url_option_yes"]
				type = GetStringOfTypeFromURLQuery(self.request.query_string, "url_query_request_type")
				if not type:
					type = REQUEST_TYPES_URLS[-1]
				typeForLookup = CorrespondingItemFromMatchedOrderList(type, REQUEST_TYPES_URLS, REQUEST_TYPES)
				if uncompletedOnly:
					requests = rakontu.getAllUncompletedRequestsOfType(typeForLookup)
				else:
					requests = rakontu.getAllRequestsOfType(typeForLookup)
				template_values = GetStandardTemplateDictionaryAndAddMore({
							   	   'title': TITLES["REVIEW_REQUESTS"], 
								   'rakontu': rakontu, 
								   'skin': rakontu.getSkinDictionary(),
								   'current_member': member,
								   'requests': requests,
								   'request_types': REQUEST_TYPES,
								   'request_types_urls': REQUEST_TYPES_URLS,
								   'showing_all_requests': not uncompletedOnly,
								   'request_type': type,
								   'changes_saved': GetChangesSavedState(member),
								   })
				path = os.path.join(os.path.dirname(__file__), FindTemplate('guide/requests.html'))
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect(RoleNotFoundURL("guide", rakontu))
		else:
			self.redirect(NoAccessURL(rakontu, member, users.is_current_user_admin()))
			
	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isGuide():
				if "changeSelections" in self.request.arguments():
					uncompletedOnly = self.request.get("all_or_uncompleted") == "showOnlyUncompledRequests"
					type = self.request.get("request_type_choice")
					if uncompletedOnly:
						query = "%s=%s&%s=%s" % (URL_OPTIONS["url_query_request_type"], type, URL_OPTIONS["url_query_uncompleted"], URL_OPTION_NAMES["url_option_yes"])
					else:
						query = "%s=%s" % (URL_OPTIONS["url_query_request_type"], type)
					self.redirect(BuildURL("dir_guide", "url_requests", query, rakontu=rakontu))
				else:
					requests = rakontu.getAllRequests()
					def txn(requests):
						requestsToPut = []
						for request in requests:
							if "setCompleted|%s" % request.key() in self.request.arguments():
								request.completedIfRequest = True
								request.completionCommentIfRequest = self.request.get("comment|%s" % request.key())
								requestsToPut.append(request)
								break
							elif "setUncompleted|%s" % request.key() in self.request.arguments():
								request.completedIfRequest = False
								request.completionCommentIfRequest = self.request.get("comment|%s" % request.key())
								requestsToPut.append(request)
								break
						db.put(requestsToPut)
					db.run_in_transaction(txn, requests)
					SetChangesSaved(member)
					self.redirect(self.request.uri)
			else:
				self.redirect(RoleNotFoundURL("guide", rakontu))
		else:
			self.redirect(NoAccessURL(rakontu, member, users.is_current_user_admin()))
			
class ReviewTopicsPage(ErrorHandlingRequestHander):
	@RequireLogin 
	def get(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isGuide():
				noResponsesOnly = GetStringOfTypeFromURLQuery(self.request.query_string, "url_query_no_responses") == URL_OPTION_NAMES["url_option_yes"]
				bookmark = GetBookmarkQueryWithCleanup(self.request.query_string)
				prev, topics, next = rakontu.getNonDraftEntriesOfType_WithPaging(ENTRY_TYPES_URLS[ENTRY_TYPE_INDEX_INVITATION], bookmark) 
				if noResponsesOnly:
					unrespondedTopics = self.reduceTopicsByOnlyUnresponded(topics)
					# if the list is reduced so far that there is nothing to show, make one attempt to add more entries
					if len(topics) > 0 and len(unrespondedTopics) == 0:
						prev, moreTopics, next = rakontu.getNonDraftEntriesOfType_WithPaging(ENTRY_TYPES_URLS[ENTRY_TYPE_INDEX_INVITATION], next)
						moreUnrespondedTopics = self.reduceTopicsByOnlyUnresponded(moreTopics)
						unrespondedTopics.extend(moreUnrespondedTopics)
					topics = unrespondedTopics
				template_values = GetStandardTemplateDictionaryAndAddMore({
							   	   'title': TITLES["REVIEW_TOPICS"], 
								   'rakontu': rakontu, 
								   'skin': rakontu.getSkinDictionary(),
								   'current_member': member,
								   'topics': topics,
								   'showing_all_topics': not noResponsesOnly,
								   'bookmark': bookmark,
								   'previous': prev,
								   'next': next,
								   })
				path = os.path.join(os.path.dirname(__file__), FindTemplate('guide/topics.html'))
				self.response.out.write(template.render(path, template_values))
			else:
				self.redirect(RoleNotFoundURL("guide", rakontu))
		else:
			self.redirect(NoAccessURL(rakontu, member, users.is_current_user_admin()))
			
	def reduceTopicsByOnlyUnresponded(self, topics):
		unrespondedTopics = []
		for topic in topics:
			if not topic.hasOutgoingLinksOfType("responded"):
				unrespondedTopics.append(topic)
		return unrespondedTopics
			
	@RequireLogin 
	def post(self):
		rakontu, member, access, isFirstVisit = GetCurrentRakontuAndMemberFromRequest(self.request)
		if access:
			if member.isGuide():
				bookmark = GetBookmarkQueryWithCleanup(self.request.query_string)
				if "changeSelections" in self.request.arguments():
					if self.request.get("all_or_unresponded") == "showOnlyUnrespondedTopics":
						if bookmark:
							query = "%s&%s=%s&%s=%s" % (rakontu.urlQuery(), 
													URL_OPTIONS["url_query_no_responses"], URL_OPTION_NAMES["url_option_yes"],
													URL_OPTIONS["url_query_bookmark"], bookmark)
						else:
							query = "%s&%s=%s" % (rakontu.urlQuery(), 
													URL_OPTIONS["url_query_no_responses"], URL_OPTION_NAMES["url_option_yes"])
						self.redirect(BuildURL("dir_guide", "url_topics", query))
					else:
						if bookmark:
							query = "%s&%s=%s" % (rakontu.urlQuery(), URL_OPTIONS["url_query_bookmark"], bookmark)
						else:
							query = rakontu.urlQuery()
						self.redirect(BuildURL("dir_guide", "url_topics", query))
			else:
				self.redirect(RoleNotFoundURL("guide", rakontu))
		else:
			self.redirect(NoAccessURL(rakontu, member, users.is_current_user_admin()))
			