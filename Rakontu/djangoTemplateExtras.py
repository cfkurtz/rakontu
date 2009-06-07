# from http://stackoverflow.com/questions/35948/django-templates-and-variable-attributes

from google.appengine.ext import webapp
import logging
from pytz import timezone
import pytz

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

register.filter("listLookup", listLookup)
register.filter("dictLookup", dictLookup)
register.filter("makeRange", makeRange)
register.filter("timeZone", timeZone)
register.filter("notNone", notNone)

