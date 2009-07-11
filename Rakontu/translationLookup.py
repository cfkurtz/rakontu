# --------------------------------------------------------------------------------------------
# RAKONTU
# Description: Rakontu is open source story sharing software.
# Version: pre-0.1
# License: GPL 3.0
# Google Code Project: http://code.google.com/p/rakontu/
# --------------------------------------------------------------------------------------------

import sys

from constants_base import *
sys.path.insert(0,'config')
from site_configuration import *
from constants_configdependent import *

def BuildURL(dir=None, page=None, query=None, extraSlash=False):
	if dir:
		if DIRS.has_key(dir):
			dirString = DIRS[dir]
		else:
			dirString = dir # assume if it is not in the dictionary, they are specifying it directly
	else:
		dirString = None
	if page:
		if URLS.has_key(page):
			pageString = URLS[page]
		else:
			pageString = page # same here
	else:
		pageString = None
	if dirString and pageString and query:
		return "/%s/%s?%s" % (dirString, pageString, query)
	elif dirString and pageString:
		return "/%s/%s" % (dirString, pageString)
	elif dirString:
		if extraSlash:
			return "/%s/" % (dirString)
		else:
			return "/%s" % (dirString)
	elif pageString:
		return "/%s" % (pageString)
	else:
		return "/"
	
def BuildResultURL(query):
	return "/%s?%s" % (URLS["url_result"], RESULTS[query])
	
def DisplayTypeForEntryType(type):
	i = 0
	for aType in ENTRY_TYPES:
		if aType == type:
			return ENTRY_TYPES_DISPLAY[i]
		i += 1
	raise "No translation for %s" % type

def URLForEntryType(type):
	i = 0
	for aType in ENTRY_TYPES:
		if aType == type:
			return ENTRY_TYPES_URLS[i]
		i += 1
	raise "No translation for %s" % type

def URLForAnnotationType(type):
	i = 0
	for aType in ANNOTATION_TYPES:
		if aType == type:
			return ANNOTATION_TYPES_URLS[i]
		i += 1
	raise "No translation for %s" % type

def DisplayTypeForLinkType(type):
	i = 0
	for aType in LINK_TYPES:
		if aType == type:
			return LINK_TYPES_DISPLAY[i]
		i += 1
	raise "No translation for %s" % type

def DisplayTypeForQuestionReferType(type):
	i = 0
	for aType in QUESTION_REFERS_TO:
		if aType == type:
			return QUESTION_REFERS_TO_DISPLAY[i]
		i += 1
	raise "No translation for %s" % type

def DisplayTypeForAnnotationType(type):
	i = 0
	for aType in ANNOTATION_TYPES:
		if aType == type:
			return ANNOTATION_TYPES_DISPLAY[i]
		i += 1
	raise "No translation for %s" % type

def URLForQuestionRefersTo(type):
	i = 0
	for aType in QUESTION_REFERS_TO:
		if aType == type:
			return QUESTION_REFERS_TO_URLS[i]
		i += 1
	raise "No translation for %s" % type

def DisplayTypePluralForQuestionRefersTo(type):
	i = 0
	for aType in QUESTION_REFERS_TO:
		if aType == type:
			return QUESTION_REFERS_TO_PLURAL_DISPLAY[i]
		i += 1
	raise "No translation for %s" % type

