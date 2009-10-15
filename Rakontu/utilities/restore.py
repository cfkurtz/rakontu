#!/usr/bin/python

# ============================================================================================ 
# RAKONTU
# Description: Rakontu is open source story sharing software.
# Version: beta (0.9+)
# License: GPL 3.0
# Google Code Project: http://code.google.com/p/rakontu/ 
# ============================================================================================ 
# This Python script uses the Google App Engine remote_api service to restore the data 
# for ONE Rakontu to any Rakontu site. 
#
# HEY! SET UP THE RESTORE_CONFIG.PY FILE TO MAKE THIS WORK CORRECTLY FOR YOUR SITUATION.
#
# This script can restore a backed-up Rakontu or transfer it to a new site.
# It can ONLY work with an XML file saved using the Rakontu backup.py program.
# 
# This is a CONSERVATIVE restore; it will NEVER overwrite an object with the same
# key_name as an existing one. If you want to write over an existing Rakontu (or any object) with a
# restored XML file, you must DELETE the Rakontu (or object) first.
# ============================================================================================ 

import os, code, getpass, sys, datetime, codecs, base64, pytz
from time import sleep

from restore_config import *

sys.path.append("/Applications/GoogleAppEngineLauncher.app/Contents/Resources/GoogleAppEngine-default.bundle/Contents/Resources/google_appengine")
sys.path.append("/Applications/GoogleAppEngineLauncher.app/Contents/Resources/GoogleAppEngine-default.bundle/Contents/Resources/google_appengine/lib/yaml/lib")
from google.appengine.ext.remote_api import remote_api_stub
from google.appengine.ext import db

sys.path.insert(0, "..") 
sys.path.insert(0, "../config")
sys.path.insert(0, CONFIG_LANGUAGE_DIR) 
from models import *

from xml.dom.minidom import parse

oldAndNewKeysDict = {}

# this maps the model class names to the names used in key_names
# it also stores counts for later
kind_type_maxindex = {
		"Member": ("member", 0),
		"PendingMember": ("pendingMember", 0),
		"Character": ("character", 0),
		"Question": ("question", 0),
		"ViewOptions": ("viewOptions", 0),
		"SavedFilter": ("filter", 0),
		"SavedFilterQuestionReference": ("filterref", 0),
		"Entry": ("entry", 0),
		"Annotation": ("annotation", 0),
		"Link": ("link", 0),
		"Attachment": ("attachment", 0),
		"TextVersion": ("version", 0),
		"Answer": ("answer", 0),
		}

spacer = "     "

# ============================================================================================ 
# COMMON XML IMPORT FUNCTIONS
# ============================================================================================ 

def getText(nodelist):
    rc = ""
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc = rc + node.data
    return rc
   
def getKey(propertyNode):
	text = getText(propertyNode.childNodes)
	keyStringWithCloseBracket = stringBeyond(text, "[")
	keyString = stringUpTo(keyStringWithCloseBracket, "]")
	return db.Key(keyString)

def getRequiredProperty(propertyNodes, propertyName):
	for propertyNode in propertyNodes:
		if propertyNode.attributes['name'].value == propertyName:
			type = propertyNode.attributes['type'].value
			if type == "key":
				return getKey(propertyNode)
			elif type == "string":
				return getText(propertyNode.childNodes)
			else:
				raise Exception("No required-property processor for type: %s" % type)
			break
	return None

def getModelIDAndPropertyNodes(node, rakontu):
	propertyNodes = node.getElementsByTagName('property')
	id = getRequiredProperty(propertyNodes, "id")
	if rakontu:
		id = addRakontuIDToObjectID(id, rakontu)
	return id, propertyNodes

def saveOldAndNewKeys(node, model):
	text = node.attributes['key'].value
	keyStringWithCloseBracket = stringBeyond(text, "[")
	keyString = stringUpTo(keyStringWithCloseBracket, "]")
	oldKey = db.Key(keyString)
	oldAndNewKeysDict[oldKey] = model.key()
   
def handleNonRequiredProperty(propertyNode, modelProperties):
 	name = propertyNode.attributes['name'].value
	type = propertyNode.attributes['type'].value
	if modelProperties:
		if modelProperties.has_key(name):
			propertyType = modelProperties[name].__class__.__name__
		else:
			propertyType = None
	else:
		propertyType = None
	text = getText(propertyNode.childNodes)
	if type == "bool":
		if text == "True":
			value = True
		elif text == "False":
			value = False
		else:
			value = None
	elif type == "int":
		value = int(text)
	elif type == "text":
		value = db.Text(text)
	elif type == "gd:when":
		if text.find(".") >= 0:
			partialText = stringUpTo(text, ".")
		elif text.find("+") >= 0:
			partialText = stringUpTo(text, "+")
		else:
			partialText = text
		value = datetime.strptime(partialText, "%Y-%m-%d %H:%M:%S")
		value.replace(tzinfo=pytz.utc)
	elif type == "string":
		value = text
	elif type == "null":
		value = None
	elif type == "blob":
		value = db.Blob(base64.urlsafe_b64decode(text.encode("ascii", "ignore")))
	elif type == "key":
		value = getKey(propertyNode)
	else:
		raise Exception("No non-required property processor for type: %s" % type)
	isListProperty = propertyType in ["ListProperty", "StringListProperty"]
	return name, value, type, isListProperty

def getNonListPropertyFromObjectNode(node, nameToLookFor):
	propertyNodes = node.getElementsByTagName('property')
	for propertyNode in propertyNodes:
		name = propertyNode.attributes['name'].value
		if name == nameToLookFor:
			return getText(propertyNode.childNodes)
	return None

def processModelProperties(object, propertyNodes):
	modelProperties = object.properties()
	lastName = None
	lastValueWasInList = False
	accumulatedValues = []
	for propertyNode in propertyNodes:
		name, value, type, isListProperty = handleNonRequiredProperty(propertyNode, modelProperties)
		if name != "id":
			if lastName and lastValueWasInList and lastName != name:
				setattr(object, lastName, accumulatedValues)
				accumulatedValues = []
			if isListProperty:
				accumulatedValues.append(value)
				lastValueWasInList = True
			else:
				setattr(object, name, value)
				lastValueWasInList = False
			lastName = name
	# this is in case a list was the last thing in the object
	if len(accumulatedValues):
		setattr(object, lastName, accumulatedValues)
		
def cleanUpReferenceProperties(object, node):
	propertyNodes = node.getElementsByTagName('property')
	modelProperties = object.properties()
	lastName = None
	lastValueWasInList = False
	accumulatedValues = []
	for propertyNode in propertyNodes:
		type = propertyNode.attributes['type'].value
		name = propertyNode.attributes['name'].value
		if type == "key":
			propertyType = modelProperties[name].__class__.__name__
			isListProperty = propertyType in ["ListProperty", "StringListProperty"]
			oldKey = getKey(propertyNode)
			if oldAndNewKeysDict.has_key(oldKey):
				newKey = oldAndNewKeysDict[oldKey]
			else:
				raise Exception("Could not find old-new key mapping for %s" % value)
			if lastName and lastValueWasInList and lastName != name:
				setattr(object, lastName, accumulatedValues)
				accumulatedValues = []
			if isListProperty:
				accumulatedValues.append(newKey)
				lastValueWasInList = True
			else:
				setattr(object, name, newKey)
				lastValueWasInList = False
			lastName = name
	# this is in case a list was the last thing in the object
	if len(accumulatedValues):
		setattr(object, lastName, accumulatedValues)
		
def addRakontuIDToObjectID(id, rakontu):
	if id.find("_") >= 0:
		idAfterUnderscore = stringBeyond(id, "_")
	else:
		idAfterUnderscore = id
	return rakontu.key().name() + "_" + idAfterUnderscore
	
# ============================================================================================ 
# SPECIAL FUNCTIONS FOR EACH MODEL CLASS
# ============================================================================================ 

def processRakontuNode(node, rakontuID):
	result = None
	id, propertyNodes = getModelIDAndPropertyNodes(node, None)
	if not rakontuID is None:
		id = rakontuID
	name = getRequiredProperty(propertyNodes, "name")
	if id and name:
		rakontu = Rakontu.get_by_key_name(id) # rakontu has no parent
		if rakontu is None:
			rakontu = Rakontu(key_name=id, id=id, name=name)
			processModelProperties(rakontu, propertyNodes) # only do this if created new
		if rakontu:
			saveOldAndNewKeys(node, rakontu) # save keys in either case
			print rakontu.getNameForExport()
			result = rakontu
		else:
			raise Exception("Could not find or create rakontu with id %s" % id)
	return result

def processQuestionNode(node, rakontu):
	result = None
	id, propertyNodes = getModelIDAndPropertyNodes(node, rakontu)
	refersTo = getRequiredProperty(propertyNodes, "refersTo")
	name = getRequiredProperty(propertyNodes, "name")
	text = getRequiredProperty(propertyNodes, "text")
	if id and refersTo and name and text:
		question = Question.get_by_key_name(id, parent=rakontu)
		if question is None:
			question = Question(key_name=id, parent=rakontu, id=id, refersTo=refersTo, name=name, text=text, rakontu=rakontu)
			processModelProperties(question, propertyNodes)
		if question:
			saveOldAndNewKeys(node, question)
			print spacer * 1, question.getNameForExport()
			result = question
		else:
			raise Exception("Could not find or create question with id %s" % id)
	return result

def processPendingMemberNode(node, rakontu):
	result = None
	id, propertyNodes = getModelIDAndPropertyNodes(node, rakontu)
	email = getRequiredProperty(propertyNodes, "email")
	if id and email:
		pendingMember = PendingMember.get_by_key_name(id, parent=rakontu)
		if pendingMember is None:
			pendingMember = PendingMember(key_name=id, parent=rakontu, id=id, email=email, rakontu=rakontu)
		if pendingMember:
			processModelProperties(pendingMember, propertyNodes)
			saveOldAndNewKeys(node, pendingMember)
			print spacer * 1, pendingMember.getNameForExport()
			result = pendingMember
		else:
			raise Exception("Could not find or create pending member with id %s" % id)
	return result
			
def processMemberNode(node, rakontu):
	result = None
	id, propertyNodes = getModelIDAndPropertyNodes(node, rakontu)
	if id:
		member = Member.get_by_key_name(id, parent=rakontu)
		if member is None:
			member = Member(key_name=id, parent=rakontu, id=id, rakontu=rakontu)
			processModelProperties(member, propertyNodes)
		if member:
			saveOldAndNewKeys(node, member)
			print spacer * 1, member.getNameForExport()
			result = member
		else:
			raise Exception("Could not find or create member with id %s" % id)
	return result

def processViewOptionsNode(node, rakontu, member):
	result = None
	id, propertyNodes = getModelIDAndPropertyNodes(node, rakontu)
	if id:
		options = ViewOptions.get_by_key_name(id, parent=member)
		if options is None:
			options = ViewOptions(key_name=id, parent=member, id=id, rakontu=rakontu, member=member)
			processModelProperties(options, propertyNodes)
		if options:
			saveOldAndNewKeys(node, options)
			print spacer * 2, options.getNameForExport()
			result = options
		else:
			raise Exception("Could not find or create view options with id %s" % id)
	return result

def processFilterNode(node, rakontu, member):
	result = None
	id, propertyNodes = getModelIDAndPropertyNodes(node, rakontu)
	if id:
		filter = SavedFilter.get_by_key_name(id, parent=member)
		if filter is None:
			filter = SavedFilter(key_name=id, parent=member, id=id, rakontu=rakontu, creator=member)
			processModelProperties(filter, propertyNodes)
		if filter:
			saveOldAndNewKeys(node, filter)
			print spacer * 2, filter.getNameForExport()
			result = filter
		else:
			raise Exception("Could not find or create filter with id %s" % id)
	return result

def processFilterQuestionRefNode(node, rakontu, member, filter):
	result = None
	id, propertyNodes = getModelIDAndPropertyNodes(node, rakontu)
	questionName = getRequiredProperty(propertyNodes, "questionName")
	questionType = getRequiredProperty(propertyNodes, "questionType")
	if id and questionName and questionType:
		ref = SavedFilterQuestionReference.get_by_key_name(id, parent=filter)
		if ref is None:
			ref = SavedFilterQuestionReference(key_name=id, parent=filter, id=id, questionName=questionName, questionType=questionType, rakontu=rakontu, filter=filter)
			processModelProperties(ref, propertyNodes)
		if ref:
			saveOldAndNewKeys(node, ref)
			print spacer * 3, ref.getNameForExport()
			result = ref
		else:
			raise Exception("Could not find or create filter-question reference with id %s" % id)
	return result

def processCharacterNode(node, rakontu):
	result = None
	id, propertyNodes = getModelIDAndPropertyNodes(node, rakontu)
	name = getRequiredProperty(propertyNodes, "name")
	if id and name:
		character = Character.get_by_key_name(id, parent=rakontu)
		if character is None:
			character = Character(key_name=id, parent=rakontu, id=id, name=name, rakontu=rakontu)
			processModelProperties(character, propertyNodes)
		if character:
			saveOldAndNewKeys(node, character)
			print spacer * 1, character.getNameForExport()
			result = character
		else:
			raise Exception("Could not find or create character with id %s" % id)
	return result

def processAnswerNode(node, rakontu, referent):
	result = None
	id, propertyNodes = getModelIDAndPropertyNodes(node, rakontu)
	if id:
		answer = Answer.get_by_key_name(id, parent=referent)
		if answer is None:
			answer = Answer(key_name=id, parent=referent, id=id, rakontu=rakontu, referent=referent)
			processModelProperties(answer, propertyNodes)
		if answer:
			processModelProperties(answer, propertyNodes)
			if referent.__class__.__name__ == "Entry":
				space = spacer * 3
			else:
				space = spacer * 2
			saveOldAndNewKeys(node, answer)
			print space, answer.getNameForExport()
			result = answer
		else:
			raise Exception("Could not find or create answer with id %s" % id)
	return result

def processEntryNode(node, rakontu, member):
	result = None
	id, propertyNodes = getModelIDAndPropertyNodes(node, rakontu)
	type = getRequiredProperty(propertyNodes, "type")
	title = getRequiredProperty(propertyNodes, "title")
	if id and type and title:
		entry = Entry.get_by_key_name(id, parent=member)
		if entry is None:
			entry = Entry(key_name=id, parent=member, id=id, type=type, title=title, rakontu=rakontu, creator=member)
			processModelProperties(entry, propertyNodes)
		if entry:
			saveOldAndNewKeys(node, entry)
			print spacer * 2, entry.getNameForExport()
			result = entry
		else:
			raise Exception("Could not find or create entry with id %s" % id)
	return result

def processAnnotationNode(node, rakontu, entry):
	result = None
	id, propertyNodes = getModelIDAndPropertyNodes(node, rakontu)
	type = getRequiredProperty(propertyNodes, "type")
	if id and type:
		annotation = Annotation.get_by_key_name(id, parent=entry)
		if annotation is None:
			annotation = Annotation(key_name=id, parent=entry, id=id, type=type, rakontu=rakontu, entry=entry)
			processModelProperties(annotation, propertyNodes)
		if annotation:
			saveOldAndNewKeys(node, annotation)
			print spacer * 3, annotation.getNameForExport()
			result = annotation
		else:
			raise Exception("Could not find or create annotation with id %s" % id)
	return result

def processLinkNode(node, rakontu, entry):
	result = None
	id, propertyNodes = getModelIDAndPropertyNodes(node, rakontu)
	type = getRequiredProperty(propertyNodes, "type")
	itemTo = getRequiredProperty(propertyNodes, "itemTo")
	if id and type and itemTo:
		link = Link.get_by_key_name(id, parent=entry)
		if link is None:
			link = Link(key_name=id, parent=entry, id=id, type=type, rakontu=rakontu, itemFrom=entry, itemTo=itemTo)
			processModelProperties(link, propertyNodes)
		if link:
			saveOldAndNewKeys(node, link)
			print spacer * 3, link.getNameForExport()
			result = link
		else:
			raise Exception("Could not find or create link with id %s" % id)
	return result

def processAttachmentNode(node, rakontu, entry):
	result = None
	id, propertyNodes = getModelIDAndPropertyNodes(node, rakontu)
	if id:
		attachment = Attachment.get_by_key_name(id, parent=entry)
		if attachment is None:
			attachment = Attachment(key_name=id, parent=entry, id=id, rakontu=rakontu, entry=entry)
			processModelProperties(attachment, propertyNodes)
		if attachment:
			saveOldAndNewKeys(node, attachment)
			print spacer * 3, attachment.getNameForExport()
			result = attachment
		else:
			raise Exception("Could not find or create attachment with id %s" % id)
	return result

def processTextVersionNode(node, rakontu, entry):
	result = None
	id, propertyNodes = getModelIDAndPropertyNodes(node, rakontu)
	if id:
		version = TextVersion.get_by_key_name(id, parent=entry)
		if version is None:
			version = TextVersion(key_name=id, parent=entry, id=id, rakontu=rakontu, entry=entry)
			processModelProperties(version, propertyNodes)
		if version:
			saveOldAndNewKeys(node, version)
			print spacer * 3, version.getNameForExport()
			result = version
		else:
			raise Exception("Could not find or create text version with id %s" % id)
	return result

# ============================================================================================ 
# MAIN RESTORE FUNCTION
# ============================================================================================ 

def restore(restoreFileName, newRakontuShortName):
	print ''
	print ''
	print '-------------------- STARTING RESTORE -----------------------------------------'
	print '----------------------------------- PRESS CTRL-C or DEL or CMD-DOT to INTERRUPT'
	print 'FILE: %s' % restoreFileName
	print '-------------------- READING XML ENTITIES -------------------------------------'
	
	rakontuID = newRakontuShortName
	if rakontuID:
		rakontuID = rakontuID.strip()
		rakontuID = htmlEscape(rakontuID)
		rakontuID = rakontuID.replace(" ", "")
		rakontuID.encode("ascii", "ignore")
		
	dom = parse(restoreFileName)
	
	rakontu = None
	currentMember = None
	currentCharacter = None
	currentEntry = None
	currentFilter = None
	objectsAndNodes = []
	
	for node in dom.getElementsByTagName('entity'):
		kind = node.attributes['kind'].value
		if kind == "Rakontu":
			rakontu = processRakontuNode(node, rakontuID)
			objectsAndNodes.append((rakontu, node))
		elif kind == "Question":
			question = processQuestionNode(node, rakontu)
			objectsAndNodes.append((question, node))
		elif kind == "PendingMember":
			pendingMember = processPendingMemberNode(node, rakontu)
			objectsAndNodes.append((pendingMember, node))
		elif kind == "Member":
			currentMember = processMemberNode(node, rakontu)
			objectsAndNodes.append((currentMember, node))
		elif kind == "ViewOptions":
			viewOptions = processViewOptionsNode(node, rakontu, currentMember)
			objectsAndNodes.append((viewOptions, node))
		elif kind == "SavedFilter":
			currentFilter = processFilterNode(node, rakontu, currentMember)
			objectsAndNodes.append((currentFilter, node))
		elif kind == "SavedFilterQuestionReference":
			reference = processFilterQuestionRefNode(node, rakontu, currentMember, currentFilter)
			objectsAndNodes.append((reference, node))
		elif kind == "Character":
			currentCharacter = processCharacterNode(node, rakontu)
			objectsAndNodes.append((currentCharacter, node))
		elif kind == "Entry":
			currentEntry = processEntryNode(node, rakontu, currentMember)
			objectsAndNodes.append((currentEntry, node))
		elif kind == "Answer":
			referentType = getNonListPropertyFromObjectNode(node, "referentType")
			if referentType == "member":
				answer = processAnswerNode(node, rakontu, currentMember)
			elif referentType == "character":
				answer = processAnswerNode(node, rakontu, currentCharacter)
			elif referentType == "entry":
				answer = processAnswerNode(node, rakontu, currentEntry)
			objectsAndNodes.append((answer, node))
		elif kind == "Annotation":
			annotation = processAnnotationNode(node, rakontu, currentEntry)
			objectsAndNodes.append((annotation, node))
		elif kind == "Link":
			link = processLinkNode(node, rakontu, currentEntry)
			objectsAndNodes.append((link, node))
		elif kind == "Attachment":
			attachment = processAttachmentNode(node, rakontu, currentEntry)
			objectsAndNodes.append((attachment, node))
		elif kind == "TextVersion":
			version = processTextVersionNode(node, rakontu, currentEntry)
			objectsAndNodes.append((version, node))
		else:
			raise Exception("Unexpected entity kind: %s" % kind)
	print "-------------------- DONE READING XML ENTITIES ---------------------------------------- "
	
	print "-------------------- RESTORING MODELS -------------------------------------------------"
	
	# fix all the ReferenceProperties to point to the new keys
	for object, node in objectsAndNodes:
		cleanUpReferenceProperties(object, node)
		
	# put new objects into database
	if 1: # these 1s are for testing, and if for some reason you need to do one part but not another
		for object, node in objectsAndNodes:
			if object.__class__.__name__ in ["Rakontu"]:
				indentLevel = 0
			elif object.__class__.__name__ in ["Member", "PendingMember", "Character", "Question"]:
				indentLevel = 1
			elif object.__class__.__name__ in ["ViewOptions", "SavedFilter", "Entry"]:
				indentLevel = 2
			elif object.__class__.__name__ in ["Annotation", "Link", "Attachment", "TextVersion", "SavedFilterQuestionReference"]:
				indentLevel = 3
			elif object.__class__.__name__ == "Answer":
				if object.referent.__class__.__name__ in ["Member", "Character"]:
					indentLevel = 2
				else:
					indentLevel = 3
			else:
				raise Exception("Unexpected object class: %s" % object.__class__.__name__)
			objectWithSameKeyName = object.__class__.get_by_key_name(object.key().name(), parent=object.parent())
			if not objectWithSameKeyName:
				retries = 0
				while retries < 3:
					try:
						sleep(SLEEP_TIME_SECONDS)
						object.put()
						break
					except:
						retries += 1
						print "Problem putting %s %s to database: trying again" % (object.__class__.__name__, object.getNameForExport())
				print spacer * indentLevel, object.getNameForExport().strip(), " -- RESTORED"
			else:
				print spacer * indentLevel, objectWithSameKeyName.getNameForExport().strip(), ' -- exists; not restored'
				
	# we don't backup the sharded counters, so we recreate as many as we need here
	# so that the NEXT item created will not start over again at 1
	if 1:
		for object, node in objectsAndNodes:
			if object.__class__.__name__ != "Rakontu":
				if kind_type_maxindex.has_key(object.__class__.__name__):
					keyNameString = kind_type_maxindex[object.__class__.__name__][0]
					indexString = stringBeyond(object.key().name(), keyNameString + "_")
					index = 0
					try:
						index = int(indexString)
					except:
						raise Exception("Could not convert object index: %s %s" % (keyNameString, indexString))
					maxNow = kind_type_maxindex[object.__class__.__name__][1]
					if index > maxNow:
						kind_type_maxindex[object.__class__.__name__] = (keyNameString, index)
				else:
					raise Exception("Unhandled class: %s" % object.__class__.__name__)
		for className in kind_type_maxindex.keys():
			type = kind_type_maxindex[className][0]
			maxIndex = kind_type_maxindex[className][1]
			shardCount = GetShardCount(type, rakontu)
			howManyWeNeedToCatchUp = maxIndex - shardCount
			if howManyWeNeedToCatchUp > 0:
				throwAway = GenerateSequentialKeyName(type, rakontu=rakontu, amount=howManyWeNeedToCatchUp)
	print "-------------------- DONE RESTORING MODELS -------------------------------------------"
	
def findRestoreFile(restoreDir, fileName):
	# tries to find specified file in directory corresponding to rakontu name, which should
	# be in file name, if they didn't change it
	# if can't find it that way, does recursive walk and finds it that way
	afterFirstPart = stringBeyond(fileName, "Rakontu_backup_")
	shouldBeRakontuName = afterFirstPart[:-25] # constant number of chars for datetime stamp
	shouldBeFilePath = restoreDir + os.sep + shouldBeRakontuName + os.sep + fileName
	if os.path.exists(shouldBeFilePath):
		return shouldBeFilePath
	else:
		for dirPath, dirNames, fileNames in os.walk(restoreDir):
			 for aFileName in fileNames:
			 	if aFileName == fileName:
			 		return os.path.join(dirPath, aFileName)
	return None
				
# ============================================================================================ 
# MAIN
# ============================================================================================ 

os.environ['AUTH_DOMAIN'] = AUTH_DOMAIN
os.environ['USER_EMAIL'] = USER_EMAIL

def auth_func():
	return USER_NAME, getpass.getpass('Password for user %s:' % USER_NAME)

def main():
	helpString = "  Usage: python %s your_restore_file.xml <optional new url-safe rakontu short-name to copy data into>" % (sys.argv[0])
	if len(sys.argv) > 1 and sys.argv[1] in ["--help", "-help", "help", "-H", "-h"]:
		print helpString
		sys.exit()
	else:
		if len(sys.argv) < 2:
		  print helpString
		else:
			if len(sys.argv) > 2:
				newRakontuShortName = sys.argv[2]
			else:
				newRakontuShortName = None
			restoreFileName = findRestoreFile(RESTORE_DIR, sys.argv[1])
			prompt = "Restore from %s to %s" % (sys.argv[1], SERVER_NAME)
			if newRakontuShortName:
				prompt += ", creating a new Rakontu named %s" % newRakontuShortName
			prompt += "? (Y/n) "
			confirm = raw_input(prompt)
			if confirm == "Y":
				if os.path.exists(restoreFileName):
					try:
						remote_api_stub.ConfigureRemoteDatastore(APP_ID, '/remote_api', auth_func, servername=SERVER_NAME)
						restore(restoreFileName, newRakontuShortName)
					except KeyboardInterrupt:
						print "\nOK - quitting."
						sys.exit()
				else:
					print "Could not find file: %s" % restoreFileName
			else:
				print "OK - not restoring. Come again :)"
	
if __name__ == "__main__":
	main()
