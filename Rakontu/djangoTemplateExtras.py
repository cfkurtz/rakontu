# from http://stackoverflow.com/questions/35948/django-templates-and-variable-attributes

from google.appengine.ext import webapp
import logging
from pytz import timezone
import pytz

import utils

register = webapp.template.create_template_register()

def dictLookup(dict, key):
	if key in dict:
		return dict[key]
	else:
		return None
	
def listLookup(list, index):
	try:
		number = int(index)
	except:
		return None
	if number <= len(list) - 1:
		return list[number]
	else:
		return None
	
def makeRange(numberString):
	result = []
	try:
		number = int(numberString)
	except:
		return result
	for i in range(number):
		result.append(i)
	return result
	
def timeZone(time, zoneName):
	if time.tzinfo:
		return time.astimezone(timezone(zoneName))
	else:
		timeUTC = time.replace(tzinfo=pytz.utc)
		return timeUTC.astimezone(timezone(zoneName))
	
def notNone(value):
	return value != None and value != "None"

def orNbsp(value):
	if value:
		if value == "None":
			return "&nbsp;"
		else:
			return value
	else:
		return "&nbsp;"

def orNone(value):
	if value:
		return value
	else:
		return "none"
	
def sorted(value):
	result = []
	value.sort()
	result.extend(value)
	return result

def infoTipCaution(value, visibleValue, type):
	if visibleValue:
		textToShow = value
	else:
		textToShow = ""
	helpText = utils.helpTextLookup(value, type)
	if helpText:
		return '%s <img src="../images/%s.png" alt="help" border="0" valign="center" title="%s"/>' % (textToShow, type, helpText)
	else:
		return textToShow

def info(value):
	return infoTipCaution(value, value.find("#") < 0, "info")

def tip(value):
	return infoTipCaution(value, value.find("#") < 0, "tip")

def caution(value):
	return infoTipCaution(value, value.find("#") < 0, "caution")

register.filter(listLookup)
register.filter(dictLookup)
register.filter(makeRange)
register.filter(timeZone)
register.filter(notNone)
register.filter(orNbsp)
register.filter(orNone)
register.filter(sorted)
register.filter(info)
register.filter(tip)
register.filter(caution)

