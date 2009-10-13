#!/usr/bin/python

# ============================================================================================ 
# RAKONTU
# Description: Rakontu is open source story sharing software.
# Version: beta (0.9+)
# License: GPL 3.0
# Google Code Project: http://code.google.com/p/rakontu/ 
# ============================================================================================ 
# This Python script uses the Google App Engine remote_api service to backup the data 
# for all of the Rakontus on a Rakontu site to XML files.
#
# HEY! SET UP THE BACKUP_CONFIG.PY FILE TO MAKE THIS WORK CORRECTLY FOR YOUR SITUATION.
#
# ============================================================================================ 
# Pages to look at for more information on the GAE remote_api:
# http://code.google.com/appengine/articles/remote_api.html
# http://www.billkatz.com/2009/2/Remote-API-Hello-World
# ============================================================================================ 

import os, code, getpass, sys, datetime, codecs, base64
from time import sleep

from backup_config import *

sys.path.append("/Applications/GoogleAppEngineLauncher.app/Contents/Resources/GoogleAppEngine-default.bundle/Contents/Resources/google_appengine")
sys.path.append("/Applications/GoogleAppEngineLauncher.app/Contents/Resources/GoogleAppEngine-default.bundle/Contents/Resources/google_appengine/lib/yaml/lib")
from google.appengine.ext.remote_api import remote_api_stub
from google.appengine.ext import db

sys.path.insert(0, "..") 
sys.path.insert(0, "../config")
sys.path.insert(0, CONFIG_LANGUAGE_DIR) 
from models import *

os.environ['AUTH_DOMAIN'] = AUTH_DOMAIN
os.environ['USER_EMAIL'] = USER_EMAIL

def auth_func():
  return USER_NAME, getpass.getpass('Password for user %s:' % USER_NAME)

delimiter = "\n\n"
spacer = "     "

def writeKeyedObjectToFile(file, key, number, max, indentLevel):
	sleep(SLEEP_TIME_SECONDS)
	item = ReTryGet(key)
	file.write(delimiter)
	file.write(item.to_xml())
	message = spacer * indentLevel + "%s/%s %s" % (number+1, max, item.getNameForExport().strip()) + ' -- backed up'
	print message

def writeListOfKeyedObjectsToFile(file, keys, indentLevel=0):
	i = 0
	for key in keys:
		sleep(SLEEP_TIME_SECONDS)
		item = ReTryGet(key)
		file.write(delimiter)
		file.write(item.to_xml())
		message = spacer * indentLevel + "%s/%s %s" % (i+1, len(keys), item.getNameForExport().strip()) + ' -- backed up'
		print message
		i += 1
		
def FixUpKeys(keys):
	keysToUse = []
	for key in keys:
		if isinstance(key, db.Key):
			keysToUse.append(key)
		else:
			keysToUse.append(key.key())
	return keysToUse

def ReTryQueryWithAncestor(classObject, ancestor):
	retries = 0
	keys = None
	unfixedKeys = None
	while retries < 3:
		try:
			unfixedKeys = classObject.all(keys_only=True).ancestor(ancestor).fetch(1000)
			break
		except:
			retries += 1
			print "Retry %s failed for class %s: trying again" % (retries, classObject.__name__)
	keys = FixUpKeys(unfixedKeys)
	return keys

def ReTryQueryWithFilter(classObject, filterName, filterValue):
	filterQuery = "%s = " % filterName
	retries = 0
	keys = None
	unfixedKeys = None
	while retries < 3:
		try:
			unfixedKeys = classObject.all(keys_only=True).filter(filterQuery, filterValue).fetch(1000)
			break
		except:
			retries += 1
			print "Retry %s failed for class %s, filter %s: trying again" % (retries, classObject.__name__, "%s = " % filterName)
	keys = FixUpKeys(unfixedKeys)
	return keys

def ReTryGet(key):
	retries = 0
	object = None
	while retries < 3:
		try:
			object = db.get(key)
			break
		except:
			retries += 1
			print "Get failed for key %s: trying again" % key
	return object

def backup(rakontuShortNameToBackup):
	print '-------------------- STARTING BACKUP -----------------------------------------'
	rakontus = Rakontu.all().fetch(1000)
	rakontusToBackup = []
	if rakontuShortNameToBackup:
		for rakontu in rakontus:
			if rakontu.key().name() == rakontuShortNameToBackup:
				rakontusToBackup = [rakontu]
	else:
		rakontusToBackup.extend(rakontus)
	for rakontu in rakontusToBackup:
		timeStamp = datetime.strftime(datetime.now(), "%Y_%m_%d_%H_%M_%S")
		rakontuDir = BACKUP_DIR + os.sep + rakontu.getKeyName()
		if not os.path.exists(rakontuDir):
			os.mkdir(rakontuDir)
		fileName = rakontuDir + os.sep + "Rakontu_backup_%s__%s.partial" % (rakontu.getKeyName(), timeStamp)
		print '-------------------------------------------------------------------------------'
		print 'Rakontu: %s File name: %s' % (rakontu.name, fileName)
		print '-------------------------------------------------------------------------------'
		file = codecs.open(fileName, "w", "utf-8", "ignore")
		try:
			file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
			file.write("<Entities>\n")
			# rakontu
			writeKeyedObjectToFile(file, rakontu.key(), 0, 1, 0)
			# questions
			questionKeys = ReTryQueryWithAncestor(Question, rakontu)
			writeListOfKeyedObjectsToFile(file, questionKeys, 1)
			# pending members
			pendingMemberKeys = ReTryQueryWithAncestor(PendingMember, rakontu)
			writeListOfKeyedObjectsToFile(file, pendingMemberKeys, 1)
			# characters
			characterKeys = ReTryQueryWithAncestor(Character, rakontu)
			i = 0
			for characterKey in characterKeys:
				writeKeyedObjectToFile(file, characterKey, i, len(characterKeys), 1)
				character = ReTryGet(characterKey)
				# answers
				characterAnswerKeys = ReTryQueryWithFilter(Answer, "referent", character.key())
				writeListOfKeyedObjectsToFile(file, characterAnswerKeys, 2)
				i += 1
			# members
			memberKeys = ReTryQueryWithAncestor(Member, rakontu)
			i = 0
			for memberKey in memberKeys:
				writeKeyedObjectToFile(file, memberKey, i, len(memberKeys), 1)
				member = ReTryGet(memberKey)
				# view options
				viewOptionsKeys = ReTryQueryWithAncestor(ViewOptions, member)
				writeListOfKeyedObjectsToFile(file, viewOptionsKeys, 2)
				# filters
				filterKeys = ReTryQueryWithAncestor(SavedFilter, member)
				j = 0
				for filterKey in filterKeys:
					writeKeyedObjectToFile(file, filterKey, j, len(filterKeys), 2)
					filter = ReTryGet(filterKey)
					# filter question references
					refKeys = ReTryQueryWithAncestor(SavedFilterQuestionReference, filter)
					writeListOfKeyedObjectsToFile(file, refKeys, 3)
					j += 1
				# answers
				memberAnswerKeys = ReTryQueryWithFilter(Answer, "referent", member.key())
				writeListOfKeyedObjectsToFile(file, memberAnswerKeys, 2)
				# entries
				entryKeys = FixUpKeys(Entry.all(keys_only=True).ancestor(member).fetch(1000))
				j = 0
				for entryKey in entryKeys:
					writeKeyedObjectToFile(file, entryKey, j, len(entryKeys), 2)
					entry = ReTryGet(entryKey)
					# annotations
					annotationKeys = ReTryQueryWithAncestor(Annotation, entry)
					writeListOfKeyedObjectsToFile(file, annotationKeys, 3)
					# answers
					answerKeys = ReTryQueryWithFilter(Answer, "referent", entry.key())
					writeListOfKeyedObjectsToFile(file, answerKeys, 3)
					# links
					linkKeys = ReTryQueryWithAncestor(Link, entry)
					writeListOfKeyedObjectsToFile(file, linkKeys, 3)
					# attachments
					attachmentKeys = ReTryQueryWithAncestor(Attachment, entry)
					writeListOfKeyedObjectsToFile(file, attachmentKeys, 3)
					# versions
					versionKeys = ReTryQueryWithAncestor(TextVersion, entry)
					writeListOfKeyedObjectsToFile(file, versionKeys, 3)
					j += 1
				i += 1
			file.write("\n\n</Entities>\n")
		finally:
			print '-------------------- CLOSING XML FILe -----------------------------------------'
			file.close()
			finalFileName = fileName.replace(".partial", ".xml")
			os.rename(fileName, finalFileName)
	print '-------------------- BACKUP COMPLETED -----------------------------------------'

def main():
		if len(sys.argv) > 1:
			if sys.argv[1] in ["--help", "-help", "help", "-H", "-h"]:
				print "  Usage: python %s <optional rakontu short-name to backup, otherwise all>" % (sys.argv[0])
				sys.exit()
			else:
				rakontuShortNameToBackup = sys.argv[1]
				prompt = "Backup Rakontu %s from %s to %s? (Y/n) " % (rakontuShortNameToBackup, SERVER_NAME, BACKUP_DIR)
		else:
			rakontuShortNameToBackup = None
			prompt = "Backup all Rakontus from %s to %s? (Y/n) " % (SERVER_NAME, BACKUP_DIR)
		confirm = raw_input(prompt)
		if confirm == "Y":
			if os.path.exists(BACKUP_DIR):
				try:
					remote_api_stub.ConfigureRemoteDatastore(APP_ID, '/remote_api', auth_func, servername=SERVER_NAME)
					backup(rakontuShortNameToBackup)
				except KeyboardInterrupt:
					print "\nOK - quitting."
					sys.exit()
			else:
				print "Directory does not exist: %s" % BACKUP_DIR
		else:
			print "OK - not backing up. Come again :)"
	
if __name__ == "__main__":
	main()

