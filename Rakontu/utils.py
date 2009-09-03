# --------------------------------------------------------------------------------------------
# RAKONTU
# Description: Rakontu is open source story sharing software.
# Version: pre-0.1
# License: GPL 3.0 
# Google Code Project: http://code.google.com/p/rakontu/
# -------------------------------------------------------------------------- -------- ----------
       
import os     
import string             
import cgi        
import htmllib          
       
from models import *        
    
from google.appengine.api import users    
from google.appengine.ext.webapp import template      
from google.appengine.ext import webapp   
from google.appengine.ext.webapp.util import run_wsgi_app   
from google.appengine.api import images 
from google.appengine.api import mail
from google.appengine.api import memcache
  
webapp.template.register_template_library('djangoTemplateExtras')
import csv 
import pytz
  
# ============================================================================================
# ============================================================================================
# PREPARING INFO FOR TEMPLATES
# ============================================================================================
# ============================================================================================

def FindTemplate(template): 
	return "templates/%s" % template  
	
def RequireLogin(func):
	def check_login(request):  
		if not users.get_current_user():  
			loginURL = users.create_login_url("/") 
			request.redirect(loginURL)
			return
		func(request)
	return check_login 

def getTimeZone(timeZoneName):
	try:
		timeZone = memcache.get("tz:%s" % timeZoneName)
	except:
		timeZone = None
	if timeZone is None:
		timeZone = timezone(timeZoneName)
		memcache.add("tz:%s" % timeZoneName, timeZone, DAY_SECONDS)
	return timeZone

def GetCurrentRakontuAndMemberFromRequest(request):
	rakontu = GetRakontuFromURLQuery(request.query_string)
	member = GetCurrentMemberFromRakontuAndUser(rakontu, users.get_current_user())
	okayToAccess = rakontu and rakontu.active and member and member.active
	if okayToAccess:
		isFirstVisit = SetFirstThingsAndReturnWhetherMemberIsNew(rakontu, member)
	else: 
		isFirstVisit = False
	return rakontu, member, okayToAccess, isFirstVisit

def GetCurrentMemberFromRakontuAndUser(rakontu, user):
	member = None
	if rakontu:
		if user:
			member = activeMemberForUserIDAndRakontu(user.user_id(), rakontu)
			if not member:
				pendingMember = pendingMemberForEmailAndRakontu(user.email(), rakontu)
				if pendingMember:
					member = Member(
						key_name=KeyName("member"), 
						nickname=user.email(),
						googleAccountID=user.user_id(),
						googleAccountEmail=user.email(),
						rakontu=rakontu,
						active=True,
						governanceType=pendingMember.governanceType) 
					member.initialize()
					member.put()
					member.createViewOptions()
					db.delete(pendingMember) 
	return member
 
def SetFirstThingsAndReturnWhetherMemberIsNew(rakontu, member):
	isFirstVisit = False
	if rakontu and member:
		isFirstVisit = not member.firstVisited
		if not rakontu.firstVisit:
			rakontu.firstVisit = datetime.now(tz=pytz.utc)
			rakontu.put()
			if member.governanceType == "owner":
				CopyDefaultResourcesForNewRakontu(rakontu, member)
		if not member.firstVisited:
			member.firstVisited = datetime.now(tz=pytz.utc)
			member.put()
	return isFirstVisit

def GetDictionaryFromURLQuery(query):
	result = {}
	pairs = query.split("&")
	for pair in pairs: 
		try: 
			key, value = pair.split("=")  
			result[key] = value 
		except:  
			pass 
	return result 
  
def GetRakontuFromURLQuery(query):  
	queryAsDictionary = GetDictionaryFromURLQuery(query)  
	rakontuLookupKey = URL_IDS["url_query_rakontu"]
	if queryAsDictionary.has_key(rakontuLookupKey):
		rakontuKey = queryAsDictionary[rakontuLookupKey]
		return Rakontu.get_by_key_name(rakontuKey) 
	else:
		for lookup, url in URL_IDS.items():
			if queryAsDictionary.has_key(url):
				entityKeyName = queryAsDictionary[url] 
				if lookup == "url_query_entry": 
					entity = Entry.get_by_key_name(entityKeyName) 
				elif lookup == "url_query_attachment": 
					entity = Attachment.get_by_key_name(entityKeyName)  
				elif lookup == "url_query_annotation":
					entity = Annotation.get_by_key_name(entityKeyName)   
				elif lookup == "url_query_answer": 
					entity = Answer.get_by_key_name(entityKeyName)
				elif lookup == "url_query_version": 
					entity = TextVersion.get_by_key_name(entityKeyName)
				elif lookup == "url_query_member":
					entity = Member.get_by_key_name(entityKeyName)
				elif lookup == "url_query_character":
					entity = Character.get_by_key_name(entityKeyName) 
				elif lookup == "url_query_search_filter":
					entity = SavedSearch.get_by_key_name(entityKeyName)
				elif lookup == "url_query_attachment":
					entity = Attachment.get_by_key_name(entityKeyName)
				elif lookup == "url_query_link":
					entity = Link.get_by_key_name(entityKeyName)
				elif lookup in ["url_query_export_csv", "url_query_export_txt", "url_query_export_xml"]:
					entity = Export.get_by_key_name(entityKeyName)
				if entity and entity.rakontu: 
					return entity.rakontu 
				else: 
					return None 
				 
def GetStringOfTypeFromURLQuery(query, type):
	dictionary = GetDictionaryFromURLQuery(query) 
	lookupKey = URL_OPTIONS[type]
	if dictionary.has_key(lookupKey):
		return dictionary[lookupKey]
	else:
		return None

def GetObjectOfTypeFromURLQuery(query, type): 
	dictionary = GetDictionaryFromURLQuery(query)
	lookupKey = URL_IDS[type]
	if dictionary.has_key(lookupKey):
		keyName = dictionary[lookupKey]
		if type == "url_query_rakontu":
			return Rakontu.get_by_key_name(keyName)
		elif type == "url_query_entry":
			return Entry.get_by_key_name(keyName)
		elif type == "url_query_attachment":
			return Attachment.get_by_key_name(keyName)
		elif type == "url_query_annotation":
			return Annotation.get_by_key_name(keyName)
		elif type == "url_query_answer":
			return Answer.get_by_key_name(keyName)
		elif type == "url_query_version": 
			return TextVersion.get_by_key_name(keyName)
		elif type == "url_query_member":
			return Member.get_by_key_name(keyName)
		elif type == "url_query_character": 
			return Character.get_by_key_name(keyName) 
		elif type == "url_query_link": 
			return Link.get_by_key_name(keyName)
		elif type == "url_query_search_filter":
			return SavedSearch.get_by_key_name(keyName)  
		elif type == "url_query_attachment":
			return Attachment.get_by_key_name(keyName)
		elif type == "url_query_export": 
			return Export.get_by_key_name(keyName)
	else:
		return None
	
def GetObjectOfUnknownTypeFromURLQuery(query):
	dictionary = GetDictionaryFromURLQuery(query) 
	for lookupKey in URL_IDS.keys(): 
		if dictionary.has_key(URL_IDS[lookupKey]): 
			return GetObjectOfTypeFromURLQuery(query, lookupKey)
	
def GetEntryAndAnnotationFromURLQuery(query):
	annotation = None
	entry = GetObjectOfTypeFromURLQuery(query, "url_query_entry")
	if not entry:
		annotation = GetObjectOfTypeFromURLQuery(query, "url_query_annotation")
		if annotation:  
			entry = annotation.entry    
	return entry, annotation       
    
def GetStandardTemplateDictionaryAndAddMore(newItems):      
	user = users.get_current_user()  
	if user != None:  
		email = user.email()   
	else: 
		email = None  
	items = { 
	   'version_number': VERSION_NUMBER, 
	   'text_formats': TEXT_FORMATS,   
	   'text_formats_display': TEXT_FORMATS_DISPLAY,  
	   'governance_roles_display': GOVERNANCE_ROLE_TYPES_DISPLAY, 
	   'no_access': NO_ACCESS,
	   'num_nudge_categories': NUM_NUDGE_CATEGORIES, 
	   'num_tags_in_tag_set': NUM_TAGS_IN_TAG_SET,  
	   'time_zone_names': pytz.all_timezones,    
	   'date_formats': DateFormatStrings(), 
	   'time_formats': TimeFormatStrings(),  
	   'time_frames': TIME_FRAMES,  
	   'entry_types': ENTRY_TYPES,
	   'entry_types_display': ENTRY_TYPES_DISPLAY,
	   'entry_types_plural': ENTRY_TYPES_PLURAL,  
	   'entry_types_plural_display': ENTRY_TYPES_PLURAL_DISPLAY,
	   'annotation_types': ANNOTATION_TYPES,
	   'annotation_answer_link_types': ANNOTATION_ANSWER_LINK_TYPES,
	   'annotation_answer_link_types_plural_display': ANNOTATION_ANSWER_LINK_TYPES_PLURAL_DISPLAY,
	   'request_types': REQUEST_TYPES,
	   'helping_role_names': HELPING_ROLE_TYPES_DISPLAY,
	   'maxlength_subject_or_comment': MAXLENGTH_SUBJECT_OR_COMMENT, 
	   'maxlength_name': MAXLENGTH_NAME,
	   'maxlength_tag_or_choice': MAXLENGTH_TAG_OR_CHOICE, 
	   'maxlength_number': MAXLENGTH_NUMBER,
	   'home': HOME,
	   'current_user': user, 
	   'user_is_admin': users.is_current_user_admin(),
	   'user_email': email,
	   'logout_url': users.create_logout_url("/"),
	   'site_language': SITE_LANGUAGE,
	   'site_support_email': SITE_SUPPORT_EMAIL,
	   'max_possible_attachments': MAX_POSSIBLE_ATTACHMENTS,
	   'development': DEVELOPMENT,
	   }
	for key in DIRS.keys():				items[key] = DIRS[key]
	for key in URLS.keys():				items[key] = URLS[key] 
	for key in URL_IDS.keys():			items[key] = URL_IDS[key] 
	for key in URL_OPTIONS.keys():		items[key] = URL_OPTIONS[key] 
	for key in TERMS.keys():			items[key] = TERMS[key]
	for key in TEMPLATE_TERMS.keys(): 	items[key] = TEMPLATE_TERMS[key]
	for key in TEMPLATE_BUTTONS.keys(): items[key] = TEMPLATE_BUTTONS[key] 
	for key in TEMPLATE_MENUS.keys():	items[key] = TEMPLATE_MENUS[key]
	items["url_story"] = URLForEntryType("story")
	items["url_invitation"] = URLForEntryType("invitation")
	items["url_collage"] = URLForEntryType("collage")
	items["url_pattern"] = URLForEntryType("pattern")
	items["url_resource"] = URLForEntryType("resource")
	for key in newItems.keys():
		items[key] = newItems[key]
	return items
 
def GetKeyFromQueryString(queryString, keyname):
	if queryString:
		nameAndKey = queryString.split("=")
		if len(nameAndKey) > 1:
			return nameAndKey[1]
		else:  
			return None 
	else:  
		return None
 
def ItemsMatchingViewOptionsForMemberAndLocation(member, location, refresh=False, entry=None, memberToSee=None, character=None):
	if refresh:
		howLongToSetMemCache = 0
	else:
		howLongToSetMemCache = member.rakontu.howLongToSetMemCache * MINUTE_SECONDS
	howLongToSetMemCache = 0
	rakontu = member.rakontu
	viewOptions = member.getViewOptionsForLocation(location)
	startTime = viewOptions.getStartTime()
	endTime = viewOptions.endTime 
	entryTypeBooleans = viewOptions.entryTypes
	entryTypes = []
	for i in range(len(ENTRY_TYPES)):
		if entryTypeBooleans[i]:
			entryTypes.append(ENTRY_TYPES[i])
	annotationTypeBooleans = viewOptions.annotationAnswerLinkTypes
	annotationTypes = []
	for i in range(len(ANNOTATION_ANSWER_LINK_TYPES)):
		if annotationTypeBooleans[i]:
			annotationTypes.append(ANNOTATION_ANSWER_LINK_TYPES[i]) 
	if location == "home":
		if howLongToSetMemCache == 0:
			itemsToStart = member.rakontu.browseEntries(startTime, endTime, entryTypes)
		else:
			try:
				entries = memcache.get("entries:%s" % rakontu.key())
			except:
				entries = None
			if entries is None:
				entries = member.rakontu.getNonDraftEntries()
				memcache.add("entries:%s" % rakontu.key(), entries, howLongToSetMemCache)
				itemsToStart = member.rakontu.selectEntriesFromList(entries, startTime, endTime, entryTypes)
			else:
				itemsToStart = member.rakontu.selectEntriesFromList(entries, startTime, endTime, entryTypes)
		considerNudgeFloor = True
		considerSearch = True
	elif location == "entry":
		if howLongToSetMemCache == 0:
			itemsToStart = entry.browseItems(annotationTypes)
		else:
			try:
				items = memcache.get("entry_items:%s" % entry.key())
			except:
				items = None
			if items is None:
				items = entry.getNonDraftAnnotationsAnswersAndLinks() # assume never > 1000
				memcache.add("entry_items:%s" % entry.key(), items, howLongToSetMemCache)
				itemsToStart = entry.selectItemsFromList(items, annotationTypes)
			else:
				itemsToStart = entry.selectItemsFromList(items, annotationTypes)
		considerNudgeFloor = False
		considerSearch = False
	elif location == "member":
		if howLongToSetMemCache == 0:
			itemsToStart = memberToSee.browseItems(startTime, endTime, entryTypes, annotationTypes)
		else:
			try:
				items = memcache.get("member_items:%s" % member.key())
			except:
				items = None
			if items is None:
				items = member.getAllItemsAttributedToMember() # assume never > 1000 ??
				memcache.add("member_items:%s" % member.key(), items, howLongToSetMemCache)
				itemsToStart = member.selectItemsFromList(items, startTime, endTime, entryTypes, annotationTypes)
			else:
				itemsToStart = member.selectItemsFromList(items, startTime, endTime, entryTypes, annotationTypes)
		considerNudgeFloor = False
		considerSearch = True
	elif location == "character":
		if howLongToSetMemCache == 0:
			itemsToStart = character.browseItems(startTime, endTime, entryTypes, annotationTypes)
		else:
			try:
				items = memcache.get("character_items:%s" % character.key())
			except:
				items = None
			if items is None:
				items = character.getAllItemsAttributedToCharacter() # assume never > 1000 ??
				memcache.add("character_items:%s" % character.key(), items, howLongToSetMemCache)
				itemsToStart = character.selectItemsFromList(items, startTime, endTime, entryTypes, annotationTypes)
			else:
				itemsToStart = character.selectItemsFromList(items, startTime, endTime, entryTypes, annotationTypes)
		considerNudgeFloor = False
		considerSearch = True
	# nudge floor
	itemsWithNudgeFloor = []
	if considerNudgeFloor:
		for item in itemsToStart:
			if item.nudgePointsForMemberAndLocation(member, location) >= viewOptions.nudgeFloor:
				itemsWithNudgeFloor.append(item)
	else:
		itemsWithNudgeFloor.extend(itemsToStart)
	# search
	itemsWithSearch = []
	if considerSearch:
		search = member.getSearchForLocation(location)
		if search:
			entryRefs = search.getEntryQuestionRefs()
			creatorRefs = search.getCreatorQuestionRefs()
			for item in itemsWithNudgeFloor:
				if item.__class__.__name__ == "Entry":
					if item.satisfiesSearchCriteria(search, entryRefs, creatorRefs):
						itemsWithSearch.append(item)
				else: # if searching in member/character page, no annotations will show
					pass
		else:
			itemsWithSearch.extend(itemsWithNudgeFloor)
	else:
		itemsWithSearch.extend(itemsWithNudgeFloor)
	# limit
	itemsWithLimit = []
	overLimitWarning = None
	numItemsBeforeLimitTruncation = None
	considerLimit = True # in case of need later
	if considerLimit:
		limit = MAX_ITEMS_PER_GRID_PAGE # viewOptions.limit # in case of need later
		if len(itemsWithSearch) > limit:
			for i in range(limit):
				itemsWithLimit.append(itemsWithSearch[i])
			overLimitWarning = TERMS["term_too_many_items_warning"]
			numItemsBeforeLimitTruncation = len(itemsWithSearch)
		else:
			itemsWithLimit.extend(itemsWithSearch)
	else:
		itemsWithLimit.extend(itemsWithSearch)
	return (itemsWithLimit, overLimitWarning, numItemsBeforeLimitTruncation)

		
def GetBookmarkQueryWithCleanup(queryString):
	# for some reason PagerQuery SOMEtimes puts one or two equals signs on the end of the bookmark, which
	# messes up the url parsing since it separates on equals signs
	if queryString[-2:] == "==":
		queryStringToUse = queryString[:-2]
		equalsSigns = 2
	elif queryString[-1] == "=":
		queryStringToUse = queryString[:-1]
		equalsSigns = 1
	else:
		queryStringToUse = queryString
		equalsSigns = 0
	bookmark = GetStringOfTypeFromURLQuery(queryStringToUse, "url_query_bookmark") 
	# put them back on again for PagerQuery
	if bookmark:
		bookmark += "=" * equalsSigns
	return bookmark

# ============================================================================================
# ============================================================================================
# HANDLERS
# ============================================================================================
# ============================================================================================

class ImageHandler(webapp.RequestHandler):
	def get(self):
		memberKeyName = self.request.get(URL_IDS["url_query_member"])
		rakontuKeyName = self.request.get(URL_IDS["url_query_rakontu"])
		entryKeyName = self.request.get(URL_IDS["url_query_entry"])
		characterKeyName = self.request.get(URL_IDS["url_query_character"])
		attachmentKeyName = self.request.get(URL_IDS["url_query_attachment"])
		if memberKeyName:
			member = Member.get_by_key_name(memberKeyName)
			if member and member.profileImage:
				self.response.headers['Content-Type'] = "image/jpeg"
				self.response.out.write(member.profileImage)
			else:
				self.error(404)
		elif rakontuKeyName:
			rakontu = Rakontu.get_by_key_name(rakontuKeyName)
			if rakontu and rakontu.image:
				self.response.headers['Content-Type'] = "image/jpeg"
				self.response.out.write(rakontu.image)
			else:
				self.error(404)
		elif entryKeyName:
			entry = Entry.get_by_key_name(entryKeyName)
			if entry and entry.type == "pattern" and entry.screenshotIfPattern:
				self.response.headers['Content-Type'] = "image/jpeg"
				self.response.out.write(entry.screenshotIfPattern)
		elif characterKeyName:
			character = Character.get_by_key_name(characterKeyName)
			if character:
				self.response.headers['Content-Type'] = "image/jpeg"
				self.response.out.write(character.image)
		elif attachmentKeyName:
			attachment = Attachment.get_by_key_name(attachmentKeyName)
			if attachment:
				self.response.headers['Content-Type'] = attachment.mimeType
				self.response.out.write(attachment.data)
			   
class AttachmentHandler(webapp.RequestHandler):
	def get(self):
		attachmentKeyName = self.request.get(URL_IDS["url_query_attachment"])
		if attachmentKeyName:
			attachment = Attachment.get_by_key_name(attachmentKeyName)
			if attachment and attachment.data:
				if attachment.mimeType in ["image/jpeg", "image/png", "text/html", "text/plain"]:
					self.response.headers['Content-Disposition'] = 'filename="%s"' % attachment.fileName
				else:
					self.response.headers['Content-Disposition'] ='attachment; filename="%s"' % attachment.fileName
				self.response.headers['Content-Type'] = attachment.mimeType
				self.response.out.write(attachment.data)
			else:
				self.error(404)
				
class ExportHandler(webapp.RequestHandler):
	def get(self): 
		csvKeyName = self.request.get(URL_IDS["url_query_export_csv"])
		txtKeyName = self.request.get(URL_IDS["url_query_export_txt"])
		xmlKeyName = self.request.get(URL_IDS["url_query_export_xml"])
		if csvKeyName:
			export = Export.get_by_key_name(csvKeyName)
			if export and export.data:
				self.response.headers['Content-Disposition'] ='export; filename="%s.%s"' % (TERMS["term_export"], "csv")
				self.response.headers['Content-Type'] ="text/csv"
				self.response.out.write(export.data)
			else:
				self.error(404)
		elif txtKeyName:
			export = Export.get_by_key_name(txtKeyName)
			if export and export.data:
				self.response.headers['Content-Disposition'] = 'export; filename="%s.%s"' % (TERMS["term_print"], "html")
				self.response.headers['Content-Type'] ="text/html"
				self.response.out.write(export.data)
			else:
				self.error(404)
		elif xmlKeyName:
			export = Export.get_by_key_name(xmlKeyName)
			if export and export.data:
				self.response.headers['Content-Disposition'] ='export; filename="%s.%s"' % (TERMS["term_export"], "xml")
				self.response.headers['Content-Type'] ="text/xml"
				self.response.out.write(export.data)
			else:
				self.error(404)
				
# ============================================================================================
# ============================================================================================
# SITE-LEVEL DEFAULTS AND SAMPLES
# ============================================================================================
# ============================================================================================

def GenerateHelps():
	db.delete(AllHelps()) 
	helps = [] 
	file = open(HELP_FILE_NAME)
	try:
		helpStrings = csv.reader(file)
		for row in helpStrings:
			if len(row[0]) > 0 and row[0][0] != ";":
				helps.append(Help(key_name=KeyName("help"), type=row[0].strip(), name=row[1].strip(), text=row[2].strip()))
		db.put(helps) 
	finally:
		file.close()  
		
def GenerateSkins():
	db.delete(AllSkins())
	skins = []
	file = open(SKINS_FILE_NAME)
	try: 
		rows = csv.reader(file)
		for row in rows:
			key = row[0].strip()
			if len(key) > 0 and key[0] != ";":
				if key == "ELEMENT":
					for cell in row[2:]: # 2 because 1 is explanation of element
						skins.append(Skin(name=cell.strip()))
				else:
					colIndex = 0
					for cell in row[2:]: # 2 because 1 is explanation of element
						textToUse = cell.strip()
						if textToUse == "":
							if key.find("color_text") >= 0:
								textToUse = "000000"
							elif key.find("_hover") >= 0: # put after text, so hover texts stay black
								textToUse = "CCCCCC"
							elif key.find("color_border") >= 0:
								textToUse = "666666"
							elif key.find("color_background") >= 0:
								textToUse = "FFFFFF"
						# this is because for numerical hex entries there needs to be quotes around it
						if textToUse and textToUse[0] == '"' and textToUse[-1] == '"': 
							textToUse = textToUse[1:]
							textToUse = textToUse[:-1]
						setattr(skins[colIndex], key, textToUse)
						colIndex += 1
		db.put(skins)
	finally:	
		file.close()
				
def GetSkinNames():  
	skins = AllSkins()
	result = []
	for skin in skins: 
		result.append(skin.name)
	result.sort()
	return result

def ReadQuestionsFromFile(fileName, rakontu=None, rakontuType="ALL"):
	if not rakontu:
		db.delete(AllSystemQuestions()) 
	file = open(fileName)
	questionStrings = csv.reader(file) 
	questionsToPut = []
	for row in questionStrings:
		if row[0] and row[1] and row[0][0] != ";":
			if rakontuType != "ALL":
				if row[8]: 
					typesOfRakontu = [x.strip() for x in row[8].split(",")]
				else:
					typesOfRakontu = RAKONTU_TYPES[:-1] # if no entry interpret as all except custom
			if rakontuType == "ALL" or rakontuType in typesOfRakontu:
				refersTo = [x.strip() for x in row[0].split(",")]
				for reference in refersTo:
					name = row[1]
					text = row[2]
					type = row[3]
					choices = []
					minValue = DEFAULT_QUESTION_VALUE_MIN
					maxValue = DEFAULT_QUESTION_VALUE_MAX
					responseIfBoolean = DEFAULT_QUESTION_BOOLEAN_RESPONSE
					if type == "ordinal" or type == "nominal":
						choices = [x.strip() for x in row[4].split(",")]
					elif type == "value":
						minAndMax = row[4].split("-")
						try:
							minValue = int(minAndMax[0])
						except:
							pass
						try:
							maxValue = int(minAndMax[1])
						except:
							pass
					elif type == "boolean":
						responseIfBoolean = row[4]
					multiple = row[5] == "yes"
					help = row[6]
					useHelp=row[7]
					typesOfRakontu = [x.strip() for x in row[8].split(",")]
					question = Question(
									key_name=KeyName("question"),
									rakontu=rakontu,
									refersTo=reference, 
									name=name, 
									text=text, 
									type=type, 
									choices=choices, 
									multiple=multiple,
									responseIfBoolean=responseIfBoolean, 
									minIfValue=minValue, 
									maxIfValue=maxValue, 
									help=help, 
									useHelp=useHelp)
					questionsToPut.append(question)
	db.put(questionsToPut)
	file.close()

def GenerateSampleQuestions():
	ReadQuestionsFromFile(SAMPLE_QUESTIONS_FILE_NAME)
	
def GenerateDefaultQuestionsForRakontu(rakontu, type):
	ReadQuestionsFromFile(DEFAULT_QUESTIONS_FILE_NAME, rakontu, type)
	
def GenerateDefaultCharactersForRakontu(rakontu):
	file = open(DEFAULT_CHARACTERS_FILE_NAME)
	questionStrings = csv.reader(file)
	characters = []
	for row in questionStrings:
		if len(row) >= 4 and row[0][0] != ";":
			name = row[0]
			description = row[1] 
			etiquetteStatement = row[2] 
			imageFileName = row[3]  
			fullImageFileName = "config/images/%s" % imageFileName    
			imageData = open(fullImageFileName).read()  
			image = db.Blob(imageData) 
			character = Character( 
							   key_name=KeyName("character"),   
							   name=row[0], 
							   rakontu=rakontu,
							   )
			format = "plain text" 
			character.description = db.Text(description)
			character.description_formatted = db.Text(InterpretEnteredText(description, format))
			character.description_format = format
			character.etiquetteStatement = db.Text(etiquetteStatement)
			character.etiquetteStatement_formatted = db.Text(InterpretEnteredText(etiquetteStatement, format))
			character.etiquetteStatement_format = format
			character.image = image
			characters.append(character)
	db.put(characters)
	file.close()
	
def GenerateSystemResources(): 
	db.delete(SystemEntriesOfType("resource"))
	file = open(DEFAULT_RESOURCES_FILE_NAME) 
	lines = file.readlines()
	resources = []
	currentText = ""
	currentResource = None
	for line in lines:
		if line[0] == ";":
			continue
		elif line[0] == "[":
			name = stringBetween("[", "]", line)
			if currentResource:
				currentResource.text = currentText
				currentResource.text_formatted = db.Text(InterpretEnteredText(currentText, currentResource.text_format))
				resources.append(currentResource)
			currentResource = Entry(key_name=KeyName("entry"),
							rakontu=None, 
							type="resource",
							title=name,
							creator=None,
							draft=False,
							inBatchEntryBuffer=False,
							published=datetime.now(tz=pytz.utc),
							resourceForHelpPage=True,
							resourceForNewMemberPage=True,
							)
			currentText = ""
		elif stringUpTo(line, "=") == "Category":
			currentResource.categoryIfResource = stringBeyond(line, "=").strip()
		elif stringUpTo(line, "=") == "Interpret as":
			currentResource.text_format = stringBeyond(line, "=").strip()
		elif stringUpTo(line, "=") == "Managers only":
			currentResource.resourceForManagersAndOwnersOnly = stringBeyond(line, "=").strip().lower() == "yes"
		else:
			currentText += line
	resources.append(currentResource)	
	db.put(resources)
	
def CopyDefaultResourcesForNewRakontu(rakontu, member):
	systemResources = SystemEntriesOfType("resource")
	for resource in systemResources:
		newResource = Entry(key_name=KeyName("entry"), 
						rakontu=rakontu, 
						type="resource",
						title=resource.title,
						text=resource.text,
						text_format=resource.text_format,
						text_formatted=resource.text_formatted,
						creator=member,
						draft=False,
						inBatchEntryBuffer=False,
						published=datetime.now(tz=pytz.utc),
						resourceForHelpPage=resource.resourceForHelpPage,
						resourceForNewMemberPage=resource.resourceForNewMemberPage,
						resourceForManagersAndOwnersOnly=resource.resourceForManagersAndOwnersOnly,
						resourceForAllNewRakontus=False,
						categoryIfResource=resource.categoryIfResource,
						)
	 	newResource.put()

# ============================================================================================
# ============================================================================================
# COLORS
# ============================================================================================
# ============================================================================================
 
def HTMLColorToRGB(colorstring):     
    colorstring = colorstring.strip() 
    r, g, b = colorstring[:2], colorstring[2:4], colorstring[4:] 
    r, g, b = [int(n, 16) for n in (r, g, b)]    
    return (r, g, b)            
           
def RGBToHTMLColor(rgb_tuple):       
    return '%02x%02x%02x' % rgb_tuple 
           
def HexColorStringForRowIndex(index, colorDict):    
	if colorDict.has_key("color_background_grid_top"):
		topColor = colorDict["color_background_grid_top"]  
	else:
		topColor = "FFFFFF"
	if index == 0:   
		return topColor
	else:
		startR, startG, startB = HTMLColorToRGB(topColor)
		if colorDict.has_key("color_background_grid_bottom"):
			bottomColor = colorDict["color_background_grid_bottom"]  
		else:
			bottomColor = "333333"
		endR, endG, endB = HTMLColorToRGB(bottomColor)
		rDecrement = (startR - endR) // BROWSE_NUM_ROWS
		gDecrement = (startG - endG) // BROWSE_NUM_ROWS 
		bDecrement = (startB - endB) // BROWSE_NUM_ROWS 
		r = min(255, max(0, startR - index * rDecrement))
		g = min(255, max(0, startG - index * gDecrement))
		b = min(255, max(0, startB - index * bDecrement))
		return RGBToHTMLColor((r,g,b)) 
	   
# ============================================================================================
# ============================================================================================
# DATE AND TIME
# ============================================================================================
# ============================================================================================

def parseDate(yearString, monthString, dayString):
	if yearString and monthString and dayString:
		try:
			year = int(yearString)
			month = int(monthString) 
			day = int(dayString)
			date = datetime(year, month, day, tzinfo=pytz.utc)
			return date
		except:
			return datetime.now(tz=pytz.utc)
	return datetime.now(tz=pytz.utc)

def DjangoToPythonDateFormat(format):
	if DATE_FORMATS.has_key(format):
		return DATE_FORMATS[format]
	return "%B %d, %Y"

def DjangoToPythonTimeFormat(format):
	if TIME_FORMATS.has_key(format):
		return TIME_FORMATS[format]
	return "%I:%M %p"

def DateFormatStrings():
	result = {}
	for format in DATE_FORMATS.keys():
		result[format] = datetime.now().strftime(DATE_FORMATS[format])
	return result

def TimeFormatStrings():
	result = {}
	for format in TIME_FORMATS.keys():
		result[format] = datetime.now().strftime(TIME_FORMATS[format])
	return result

def RelativeTimeDisplayString(whenUTC, member):
	if member and member.timeZoneName:
		timeZone = getTimeZone(member.timeZoneName)
		when = whenUTC.astimezone(timeZone)
		return "%s %s" % (stripZeroOffStart(when.strftime(DjangoToPythonTimeFormat(member.timeFormat))),
						(when.strftime(DjangoToPythonDateFormat(member.dateFormat))))
	else:
		return None
	
def stripZeroOffStart(text):
	if text[0] == "0":
		return text[1:]
	else:
		return text
	
# ============================================================================================
# ============================================================================================
# TEXT PROCESSING
# ============================================================================================
# ============================================================================================

HTML_ESCAPES = {
 	"&": "&amp;",
 	'"': "&quot;",
 	"'": "&apos;",
 	">": "&gt;",
 	"<": "&lt;",  
 	 } 
  
def htmlEscape(text):  
	result = []  
	for character in text:  
		result.append(HTML_ESCAPES.get(character, character))  
	return "".join(result)
 
SIMPLE_HTML_REPLACEMENTS = [  
							("<p>", "{{startPar}}"), ("</p>", "{{stopPar}}"),
							("<b>", "{{startBold}}"), ("</b>", "{{stopBold}}"),
							("<i>", "{{startItalic}}"), ("</i>", "{{stopItalic}}"),
							("<del>", "{{startStrike}}"), ("</del>", "{{stopStrike}}"),
							("<code>", "{{startCode}}"), ("</code>", "{{stopCode}}"),
							("<ul>", "{{startUL}}"), ("</ul>", "{{stopUL}}"),
							("<ol>", "{{startOL}}"), ("</ol>", "{{stopOL}}"),
							("<li>", "{{startLI}}"), ("</li>", "{{stopLI}}"),
							("<h1>", "{{startH1}}"), ("</h1>", "{{stopH1}}"),
							("<h2>", "{{startH2}}"), ("</h2>", "{{stopH2}}"),
							("<h3>", "{{startH3}}"), ("</h3>", "{{stopH3}}"),
							("<br/>", "{{BR}}"),
							("<hr>", "{{HR}}"),
							("&nbsp;", "{{NBSP}}")  
							]
 
def InterpretEnteredText(text, mode="text"):
	result = text
	if mode == "plain text":
		""" Plain text format:
		Blank lines denote paragraphs; all others are merged.
		"""
		result = htmlEscape(result)
		lines = result.split("\n")
		changedLines = []
		changedLines.append("<p>")
		for line in lines:
			if len(line.strip()) == 0:
				changedLines.append("</p>\n<p>")
			changedLines.append(line)
		changedLines.append("</p>")
		result = "\n".join(changedLines)
	elif mode == "simple HTML":
		""" Simple HTML support:
			p, b, i, del, code, ul, ol, h1, h2, h3, br, hr, href, img
		"""
		# links
		linkExpression = re.compile(r'<a href="(.+?)">(.+?)</a>')
		links = linkExpression.findall(result)
		for url, label in links:
			result = result.replace('<a href="%s">' % url, '{{BEGINHREF}}%s{{ENDHREF}}' % url)
			result = result.replace('%s</a>' % label, '%s{{ENDLINK}}' % label)
		# image links
		imageLinkExpression = re.compile(r'<img src="(.+?)" alt="(.+?)"/>')
		imageLinks = imageLinkExpression.findall(result)
		for url, alt in imageLinks:
			result = result.replace('<img src="%s" alt="%s"/>' % (url, alt), '{{BEGINIMG}}%s|%s{{ENDIMG}}' % (url,alt))
		# bold, italic, etc
		for htmlVersion, longVersion in SIMPLE_HTML_REPLACEMENTS:
			result = result.replace(htmlVersion, longVersion)
		# now escape it
		result = htmlEscape(result)
		# bold, italic, etc
		for htmlVersion, longVersion in SIMPLE_HTML_REPLACEMENTS:
			result = result.replace(longVersion, htmlVersion)
		# links
		for url, label in links:
			result = result.replace('{{BEGINHREF}}%s{{ENDHREF}}' % url, '<a href="%s">' % url)
			result = result.replace('%s{{ENDLINK}}' % label, '%s</a>' % label)
		# image links
		for url, alt in imageLinks:
			result = result.replace('{{BEGINIMG}}%s|%s{{ENDIMG}}' % (url, alt), '<img src="%s" alt="%s"/>' % (url,alt))
	elif mode == "Wiki markup":
		result = htmlEscape(result)
		lines = result.split("\n")
		changedLines = []
		changedLines.append("<p>")
		bulletedListGoingOn = False
		numberedListGoingOn = False
		for line in lines:
			if len(line.strip()) == 0:
				changedLines.append("</p>\n<p>")
			if len(line) >= 3 and line[:3] == "===":
				if bulletedListGoingOn:
					bulletedListGoingOn = False
					changedLines.append("</ul>")
				if numberedListGoingOn:
					numberedListGoingOn = False
					changedLines.append("</ol>")
				changedLines.append("<h3>%s</h3>" % line[3:].strip())
			elif len(line) >= 2 and line[:2] == "==":
				if bulletedListGoingOn:
					bulletedListGoingOn = False
					changedLines.append("</ul>")
				if numberedListGoingOn:
					numberedListGoingOn = False
					changedLines.append("</ol>")
				changedLines.append("<h2>%s</h2>" % line[2:].strip())
			elif len(line) >= 1 and line[:1] == "=":
				if bulletedListGoingOn:
					bulletedListGoingOn = False
					changedLines.append("</ul>")
				if numberedListGoingOn:
					numberedListGoingOn = False
					changedLines.append("</ol>")
				changedLines.append("<h1>%s</h1>" % line[1:].strip())
			elif len(line) >= 3 and line[:3] == "  *":
				if not bulletedListGoingOn:
					bulletedListGoingOn = True
					changedLines.append("<ul>")
				changedLines.append("<li>%s</li>" % line[3:].strip())
			elif len(line) >= 3 and line[:3] == "  #":
				if not numberedListGoingOn:
					numberedListGoingOn = True
					changedLines.append("<ol>")
				changedLines.append("<li>%s</li>" % line[3:].strip())
			elif line.strip() == "----":
				if bulletedListGoingOn:
					bulletedListGoingOn = False
					changedLines.append("</ul>")
				if numberedListGoingOn:
					numberedListGoingOn = False
					changedLines.append("</ol>")
				changedLines.append("<hr>")
			else:
				if len(line) >= 2 and line[:2] != "  ":
					if bulletedListGoingOn:
						bulletedListGoingOn = False
						changedLines.append("</ul>")
					if numberedListGoingOn:
						numberedListGoingOn = False
						changedLines.append("</ol>")
				changedLines.append(line)
		if bulletedListGoingOn:
			changedLines.append("</ul>")
		if numberedListGoingOn:
			changedLines.append("</ol>")
		changedLines.append("</p>")
		result = "\n".join(changedLines)
		for bold in re.compile(r'\*(.+?)\*').findall(result):
			result = result.replace('*%s*' % bold, '<b>%s</b>' % bold)
		for italic in re.compile(r'\_(.+?)\_').findall(result):
			result = result.replace('_%s_' % italic, '<i>%s</i>' % italic)
		for code in re.compile(r'\^(.+?)\^').findall(result):
			result = result.replace('^%s^' % code, '<code>%s</code>' % code)
		for strike in re.compile(r'\~(.+?)\~').findall(result):
			result = result.replace('~%s~' % strike, '<span style="text-decoration: line-through">%s</span>' % strike)
		for link, name in re.compile(r'\[(.+?)\((.+?)\)\]').findall(result):
			result = result.replace('[%s(%s)]' % (link,name), '<a href="%s">%s</a>' % (link, name))
		for link in re.compile(r'\[(.+?)\]').findall(result):
			result = result.replace('[%s]' % link, '<a href="%s">%s</a>' % (link, link))
		for imageLink, alt in re.compile(r'\{(.+?)\((.+?)\)\}').findall(result):
			result = result.replace('{%s(%s)}' % (imageLink,alt), '<img src="%s" alt="%s"/>' % (imageLink, alt))
	return result

def upTo(value, number):
	if value:
		result = value[:number]
		if len(value) > number:
			result += "..."  
	else:
		result = value
	return result
 
def upToWithLink(value, number, link):
	if value: 
		result = value[:number]
		if len(value) > number:
			result += ' <a href="%s">...</a>' % link
	else:
		result = value
	return result

def checkedBlank(value):
	if value:
		return "checked"
	return "" 

# ============================================================================================
# ============================================================================================
# MAKING FAKE DATA FOR TESTING
# ============================================================================================
# ============================================================================================

def GenerateFakeTestingData():
	user = users.get_current_user()
	rakontu = Rakontu(key_name=KeyName("rakontu"), name="Test rakontu", description="Test description")
	rakontu.initializeFormattedTexts()
	rakontu.put()
	member = Member(key_name=KeyName("member"), googleAccountID=user.user_id(), googleAccountEmail=user.email(), nickname="Tester", rakontu=rakontu, governanceType="owner")
	member.initialize()
	member.put()
	member.createViewOptions()
	if user.email() != "test@example.com":
		PendingMember(key_name=KeyName("pendingmember"), rakontu=rakontu, email="test@example.com").put()
	else:
		PendingMember(key_name=KeyName("pendingmember"), rakontu=rakontu, email="cfkurtz@cfkurtz.com").put()
	PendingMember(key_name=KeyName("pendingmember"), rakontu=rakontu, email="admin@example.com").put()
	Character(key_name=KeyName("character"), name="Little Bird", rakontu=rakontu).put()
	Character(key_name=KeyName("character"), name="Old Coot", rakontu=rakontu).put()
	Character(key_name=KeyName("character"), name="Blooming Idiot", rakontu=rakontu).put()
	entry = Entry(key_name=KeyName("entry"), rakontu=rakontu, type="story", creator=member, title="The dog", text="The dog sat on a log.", draft=False)
	entry.put()
	entry.publish()
	annotation = Annotation(key_name=KeyName("annotation"), rakontu=rakontu, type="comment", creator=member, entry=entry, shortString="Great!", longString="Wonderful!", draft=False)
	annotation.put()
	annotation.publish()
	annotation = Annotation(key_name=KeyName("annotation"), rakontu=rakontu, type="comment", creator=member, entry=entry, shortString="Dumb", longString="Silly", draft=False)
	annotation.put()
	annotation.publish()
	entry = Entry(key_name=KeyName("entry"), rakontu=rakontu, type="story", creator=member, title="The circus", text="I went the the circus. It was great.", draft=False)
	entry.put()
	entry.publish()

LOREM_IPSUM = [
"Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla malesuada arcu a lorem interdum euismod aliquet dui vehicula. Integer posuere mollis massa, ac posuere diam vestibulum eget. Quisque gravida arcu non lorem placerat tempus eget in risus. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Aliquam velit nulla, tempus sit amet gravida vel, gravida sit amet libero. Maecenas bibendum nulla ac leo feugiat egestas. Suspendisse vel dui velit. Duis a velit eget augue pellentesque bibendum in non urna. Nunc vestibulum mi vitae neque pulvinar et feugiat urna auctor. Proin volutpat euismod nunc, adipiscing pharetra leo commodo a. Suspendisse potenti. Vestibulum luctus velit non purus laoreet elementum. Donec euismod, ipsum interdum facilisis porttitor, dui dui suscipit turpis, faucibus imperdiet ante metus tempus elit. Ut vulputate, leo quis tincidunt tincidunt, massa ante fringilla libero, iaculis varius tortor quam tempor ipsum. Praesent cursus consequat tellus, eget molestie dui aliquet vitae.",
"Cras sagittis nibh tempor orci pellentesque condimentum. Etiam vel ipsum tortor. Phasellus quam erat, aliquet sit amet egestas a, vehicula vitae risus. Nam ac quam sit amet risus imperdiet eleifend. Pellentesque nec arcu ut nunc rutrum posuere. Fusce at elit est, ac auctor sapien. Pellentesque semper enim et turpis euismod tincidunt. Donec nibh nunc, placerat vitae semper et, ullamcorper vel lectus. Praesent ut tellus eros. Ut sit amet odio vel risus auctor mollis. Duis luctus viverra diam, eu tincidunt ante sodales nec. Suspendisse potenti.",
"Fusce pharetra mauris eget neque adipiscing a suscipit ante laoreet. Sed nec risus risus, quis vulputate quam. Nam tristique fringilla tristique. Phasellus ultricies scelerisque feugiat. Etiam hendrerit elementum varius. Sed nibh massa, sollicitudin quis semper id, tempor nec nisl. Fusce sodales cursus nunc a elementum. Suspendisse potenti. Nulla facilisi. Maecenas mattis, nibh sed sodales congue, turpis nunc bibendum felis, ac malesuada erat mi id lorem. Fusce blandit venenatis gravida. In posuere diam at magna bibendum suscipit.",
"Fusce tincidunt iaculis justo, in viverra ipsum ullamcorper quis. Cras sed molestie libero. Praesent laoreet nisi volutpat enim bibendum porttitor. Duis rhoncus vestibulum justo nec adipiscing. Cras quam lorem, cursus ut gravida eget, porttitor ac nisl. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Curabitur eget mauris ante, sit amet convallis dui. Donec metus augue, condimentum ut tempus vel, ullamcorper et nisi. Integer vestibulum, risus eget accumsan malesuada, turpis ligula posuere eros, nec consectetur metus nisl nec ligula. Fusce non est sit amet mi pellentesque placerat eget ut magna. Nulla sit amet diam augue, quis gravida magna. Donec eleifend nunc sit amet lacus vehicula quis ornare sem sagittis. Duis sodales, lectus nec vestibulum lobortis, orci erat fermentum augue, interdum varius nulla ipsum ac mi. Sed at tellus quam, sed rhoncus enim. Pellentesque scelerisque consectetur turpis eu ullamcorper. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Mauris a sapien orci. Integer volutpat ornare urna non tristique. Nullam eget elit est, sed mollis ante. Sed eget risus tortor.",
"Nullam sapien ligula, suscipit adipiscing elementum et, faucibus quis metus. Aliquam ullamcorper libero et purus adipiscing ut feugiat ligula dictum. Duis ante est, volutpat vitae suscipit eu, ultricies sed orci. Fusce eleifend elit ullamcorper felis molestie vitae convallis mi vehicula. Nullam eu turpis non purus feugiat fringilla. Morbi egestas sem eget eros adipiscing a pharetra enim vestibulum. Ut eu nisl quis nisl elementum elementum. In feugiat sapien eu leo rhoncus aliquet. Cras porttitor adipiscing orci, nec tristique tellus adipiscing et. Nulla ut dui arcu, non tincidunt nulla. Nunc lacus turpis, adipiscing eget vestibulum vel, congue nec leo. Maecenas est arcu, pretium at congue sed, venenatis eget metus.",
]

def GenerateRandomDate(start, end):
    delta = end - start
    deltaSeconds = (delta.days * 24 * 60 * 60) + delta.seconds
    randomSeconds = random.randrange(deltaSeconds)
    return start + timedelta(seconds=randomSeconds)
	
def AddFakeDataToRakontu(rakontu, numItems, createWhat):
	user = users.get_current_user()
	startDate = rakontu.created
	startDate = startDate.replace(tzinfo=pytz.utc)
	endDate = datetime.now()
	endDate = endDate.replace(tzinfo=pytz.utc)
	
	if createWhat == "members":
		numMembersNow = rakontu.numActiveMembers()
		for i in range(numItems):
			member = Member(
						key_name=KeyName("member"), 
						nickname="Member %s" % (numMembersNow + i + 1), 
						rakontu=rakontu, 
						governanceType="member")  
			member.joined = startDate
			member.initialize()
			member.put() 
			member.createViewOptions()
		DebugPrint("%s members generated" % numItems)
	elif createWhat == "entries":
		memberKeyNames = []
		for member in rakontu.getActiveMembers():
			memberKeyNames.append(member.getKeyName())
		for i in range(numItems):
			type = random.choice(ENTRY_TYPES)
			member = Member.get_by_key_name(random.choice(memberKeyNames))
			text = random.choice(LOREM_IPSUM)
			entry = Entry( 
						key_name=KeyName("entry"), 
						rakontu=rakontu, 
						type=type, 
						creator=member, 
						title=text[:random.randrange(5,40)], 
						text=text, 
						draft=False)
			entry.text_formatted = db.Text(InterpretEnteredText(text, "plain text"))
			entry.put()
			entry.publish()
			entry.published = GenerateRandomDate(startDate, endDate)
			entry.created = entry.published
			entry.put()
		DebugPrint("%s entries generated" % numItems)
	elif createWhat == "annotations":
		entryKeyNames = [] 
		memberKeyNames = []
		for member in rakontu.getActiveMembers():
			memberKeyNames.append(member.getKeyName())  
		for entry in rakontu.getNonDraftEntries():
			entryKeyNames.append(entry.getKeyName())
		for i in range(numItems):
			type = random.choice(ANNOTATION_TYPES)
			member = Member.get_by_key_name(random.choice(memberKeyNames))
			entry = Entry.get_by_key_name(random.choice(entryKeyNames))
			text = random.choice(LOREM_IPSUM)
			annotation = Annotation(
								key_name=KeyName("annotation"), 
								rakontu=rakontu, 
								type=type, 
								creator=member, 
								entry=entry, 
								shortString=text[:random.randrange(5,40)], 
								longString=text, 
								draft=False)
			if type == "nudge":
				annotation.valuesIfNudge = []
				for j in range(NUM_NUDGE_CATEGORIES):
					annotation.valuesIfNudge.append(random.randint(-10, 10))
			elif type == "tag set":
				annotation.tagsIfTagSet = []
				for i in range(4):
					annotation.tagsIfTagSet.append(random.choice(LOREM_IPSUM)[:random.randrange(5,20)])
			annotation.longString_formatted = db.Text(InterpretEnteredText(annotation.longString, "plain text"))
			annotation.put()
			annotation.publish()
			annotation.published = GenerateRandomDate(entry.published, endDate)
			annotation.created = annotation.published
			annotation.put()
			entry.lastAnnotatedOrAnsweredOrLinked = annotation.published
			entry.put()
	elif createWhat == "nudges":
		entryKeyNames = []
		memberKeyNames = []
		for member in rakontu.getActiveMembers():
			memberKeyNames.append(member.getKeyName())
		for entry in rakontu.getNonDraftEntries():
			entryKeyNames.append(entry.getKeyName())
		for i in range(numItems):
			member = Member.get_by_key_name(random.choice(memberKeyNames))
			entry = Entry.get_by_key_name(random.choice(entryKeyNames))
			text = random.choice(LOREM_IPSUM)
			annotation = Annotation(
								key_name=KeyName("annotation"), 
								rakontu=rakontu, 
								type="nudge", 
								creator=member, 
								entry=entry, 
								shortString=text[:random.randrange(5,40)], 
								draft=False)
			annotation.valuesIfNudge = []
			for j in range(NUM_NUDGE_CATEGORIES):
				annotation.valuesIfNudge.append(random.randint(-10, 10))
			annotation.put()
			annotation.publish()
			annotation.published = GenerateRandomDate(entry.published, endDate)
			annotation.created = annotation.published
			annotation.put()
			entry.lastAnnotatedOrAnsweredOrLinked = annotation.published
			entry.put()
		DebugPrint("%s nudges generated" % numItems)

