# --------------------------------------------------------------------------------------------
# RAKONTU
# Description: Rakontu is open source story sharing software.
# Version: pre-0.1
# License: GPL 3.0
# Google Code Project: http://code.google.com/p/rakontu/
# --------------------------------------------------------------------------------------------

from google.appengine.ext import webapp
import logging
from pytz import timezone
import pytz

from translationLookup import *
import models
import utils
import site_configuration

register = webapp.template.create_template_register()

# --------------------------------------------------------------------------------------------
# getting things 
# --------------------------------------------------------------------------------------------

# from http://stackoverflow.com/questions/35948/django-templates-and-variable-attributes
def dictLookup(dict, key):
	if dict: 
		if key in dict:
			return dict[key]
		else:
			return None
	else:
		return None
register.filter(dictLookup)

def dictKeys(dict):
	return dict.keys()
register.filter(dictKeys)
	
def listLookup(list, index):
	if list:
		try:
			number = int(index)
		except:
			return None
		if number >= 0 and number <= len(list) - 1:
			return list[number]
		else:
			return None
	else:
		return None
register.filter(listLookup)

def contains(item, list):
	if list:
		try:
			index = list.index(item)
			return True
		except:
			return False
	else:
		return False
register.filter(contains)

def isLastInSeries(list, object):
	try:
		isLast = list.index(object) == len(list) - 1
		return isLast
	except:
		return False 
register.filter(isLastInSeries)

def isFirstInSeries(list, object):
	try:
		isFirst = list.index(object) == 0
		return isFirst
	except:
		return False
register.filter(isFirstInSeries)

def isInList(object, list):
	if list and object:
		return object in list
	else:
		return False
register.filter(isInList)

def get(object, fieldName):
	if object:
		if callable(getattr(object, fieldName)):
			function = getattr(object, fieldName)
			return function()
		else:
			return getattr(object, fieldName)
	else:
		return None
register.filter(get)
	
def sorted(value):
	result = []
	value.sort()
	result.extend(value)
	return result
register.filter(sorted)

def sortedReversed(value):
	result = []
	value.sort()
	value.reverse()
	result.extend(value)
	return result
register.filter(sortedReversed)

# --------------------------------------------------------------------------------------------
# calculations
# --------------------------------------------------------------------------------------------

def equalTest(value, otherValue):
	if value == otherValue:
		return True
	return False
register.filter(equalTest)

def notEqualTest(value, otherValue):
	if value != otherValue:
		return True
	return False
register.filter(notEqualTest)

def strEqualTest(value, otherValue):
	if str(value) == str(otherValue):
		return True
	return False
register.filter(strEqualTest)

def add(numberString, addString):
	try:
		number = int(numberString)
		addNumber = int(addString)
		return str(number + addNumber)
	except:
		return numberString
register.filter(add)
	
def subtract(numberString, subtractString):
	try:
		number = int(numberString)
		subtractNumber = int(subtractString)
		return str(number - subtractNumber)
	except:
		return numberString
register.filter(subtract)
	
def dividesBy(value, divideBy):
	return value != 0 and value % divideBy == 0
register.filter(dividesBy)

def length(list):
	return len(list)
register.filter(length)
	
def makeRange(numberString):
	result = []
	try:
		number = int(numberString)
	except:
		return result
	for i in range(number):
		result.append(i)
	return result
register.filter(makeRange)

def makeRangeFromListLength(list):
	return range(len(list))
register.filter(makeRangeFromListLength)

def makeRangeStartingAtOne(numberString):
	result = []
	try:
		number = int(numberString)
	except:
		return result
	for i in range(1, number, 1):
		result.append(i)
	result.append(number) # range does one less
	return result
register.filter(makeRangeStartingAtOne)

# --------------------------------------------------------------------------------------------
# display
# --------------------------------------------------------------------------------------------
	
def timeZone(time, zoneName):
	if time:
		if time.tzinfo:
			timeZone = utils.getTimeZone(zoneName)
			return time.astimezone(timeZone)
		else:
			timeUTC = time.replace(tzinfo=pytz.utc)
			return timeUTC.astimezone(timezone(zoneName))
	else:
		return None
register.filter(timeZone)
	
def notNone(value):
	return value != None and value != "None"
register.filter(notNone)

def orNbsp(value):
	if value:
		if value == "None":
			return "&nbsp;"
		else:
			return value
	else:
		return "&nbsp;"
register.filter(orNbsp)

def orNone(value):
	if value:
		return value
	else:
		return TERMS["term_none"]
register.filter(orNone)
	
def orNothing(value):
	if value:
		if value == "None":
			return ""
		else:
			return value
	else:
		return ""
register.filter(orNothing)
	
def upTo(value, number):
	if value:
		result = value[:number]
		if len(value) > number:
			result += "..."
	else:
		result = value
	return result
register.filter(upTo)

def toString(value):
	return "%s" % value
register.filter(toString)

def toUnicode(value):
	if value:
		return unicode(value)
	else:
		return None
register.filter(toUnicode)
	
def spacify(value):
	return value.replace("_", " ").capitalize()
register.filter(spacify)

def allcaps(value):
	return value.upper()
register.filter(allcaps)

def capitalize(value):
	return value.capitalize()
register.filter(capitalize)

def lower(value):
	return value.lower()
register.filter(lower)

def stringLengthExceeds(value, limit):
	return len(value) > limit
register.filter(stringLengthExceeds)


def strip(value):
	return value.strip()
register.filter(strip)

def isCommentOrRequest(value):
	return value == "comment" or value == "request"
register.filter(isCommentOrRequest)

# --------------------------------------------------------------------------------------------
# help
# --------------------------------------------------------------------------------------------
	
def infoTipCaution(name, typeURL):
	type = models.CorrespondingItemFromMatchedOrderList(typeURL, HELP_TYPES_URLS, HELP_TYPES)
	helpText, translatedName = models.helpTextLookup(name, type)
	if helpText:
		return '<a href="/%s?%s=%s&%s=%s"><img src="../images/%s.png" alt="help" border="0" valign="center" title="%s"/></a>' % \
			(URLS["url_help"], URL_OPTIONS["url_query_help"], translatedName, URL_OPTIONS["url_query_help_type"], typeURL, type, helpText)
	else:
		return ""

def info(value):
	return infoTipCaution(value, "info")
register.filter(info)

def tip(value):
	return infoTipCaution(value, "tip")
register.filter(tip)

def caution(value):
	return infoTipCaution(value, "caution")
register.filter(caution)

def buttonTooltip(name):
	helpText, translatedName = models.helpTextLookup(name, "button")
	if helpText:
		return helpText
	else:
		return ""
register.filter(buttonTooltip)
	


