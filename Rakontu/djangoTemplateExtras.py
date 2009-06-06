# from http://stackoverflow.com/questions/35948/django-templates-and-variable-attributes

from google.appengine.ext import webapp
import logging
from pytz import timezone

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
	return time.astimezone(timezone(zoneName))

register.filter("listLookup", listLookup)
register.filter("dictLookup", dictLookup)
register.filter("makeRange", makeRange)
register.filter("timeZone", timeZone)

