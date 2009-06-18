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

def add(numberString, addString):
	try:
		number = int(numberString)
		addNumber = int(addString)
		return str(number + addNumber)
	except:
		return numberString
	
def timeZone(time, zoneName):
	if time:
		if time.tzinfo:
			return time.astimezone(timezone(zoneName))
		else:
			timeUTC = time.replace(tzinfo=pytz.utc)
			return timeUTC.astimezone(timezone(zoneName))
	else:
		return None
	
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
	
def orNothing(value):
	if value:
		if value == "None":
			return ""
		else:
			return value
	else:
		return ""
	
def sorted(value):
	result = []
	value.sort()
	result.extend(value)
	return result

def infoTipCaution(value, type):
	helpText = utils.helpTextLookup(value, type)
	if helpText:
		return '<img src="../images/%s.png" alt="help" border="0" valign="center" title="%s"/>' % (type, helpText)
	else:
		return ""

def info(value):
	return infoTipCaution(value, "info")

def tip(value):
	return infoTipCaution(value, "tip")

def caution(value):
	return infoTipCaution(value, "caution")

def upTo(value, number):
	if value:
		result = value[:number]
		if len(value) > number:
			result += "..."
	else:
		result = value
	return result

def yourOrThis(value):
	if value:
		return "your"
	else:
		return "this member's"

def youOrThis(value):
	if value:
		return "you"
	else:
		return "this member"
	
register.filter(listLookup)
register.filter(dictLookup)
register.filter(makeRange)
register.filter(timeZone)
register.filter(notNone)
register.filter(orNbsp)
register.filter(orNone)
register.filter(orNothing)
register.filter(sorted)
register.filter(info)
register.filter(tip)
register.filter(caution)
register.filter(upTo)
register.filter(yourOrThis)
register.filter(youOrThis)
register.filter(add)


