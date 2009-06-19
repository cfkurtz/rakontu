# --------------------------------------------------------------------------------------------
# RAKONTU
# Description: Rakontu is open source story sharing software.
# Version: pre-0.1
# License: GPL 3.0
# Google Code Project: http://code.google.com/p/rakontu/
# --------------------------------------------------------------------------------------------

import os
import string
import cgi
import htmllib

from models import *

import sys
sys.path.append("/Users/cfkurtz/Documents/personal/eclipse_workspace_kfsoft/Rakontu/lib/") 
from appengine_utilities.sessions import Session

from google.appengine.api import users
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import images
from google.appengine.api import mail

webapp.template.register_template_library('djangoTemplateExtras')
import csv
import pytz

def GetStandardTemplateDictionaryAndAddMore(newItems):
	items = {
		# constants
	   'text_formats': TEXT_FORMATS,
	   'num_nudge_categories': NUM_NUDGE_CATEGORIES,
	   'num_tags_in_tag_set': NUM_TAGS_IN_TAG_SET,
	   'time_zone_names': pytz.all_timezones,
	   'date_formats': DateFormatStrings(),
	   'time_formats': TimeFormatStrings(),
	   'time_frames': TIME_FRAMES, 
	   'entry_types': ENTRY_TYPES,
	   'request_types': REQUEST_TYPES,
	   'helping_role_names': HELPING_ROLE_TYPES,
	   'maxlength_subject_or_comment': MAXLENGTH_SUBJECT_OR_COMMENT,
	   'maxlength_name': MAXLENGTH_NAME,
	   'maxlength_tag_or_choice': MAXLENGTH_TAG_OR_CHOICE,
	   'maxlength_number': MAXLENGTH_NUMBER,
	   # stuff about user
	   'current_user': users.get_current_user(), 
	   'user_is_admin': users.is_current_user_admin(),
	   'logout_url': users.create_logout_url("/"),
	   }
	for key in newItems.keys():
		items[key] = newItems[key]
	return items

def GenerateHelps():
	db.delete(Help.all().fetch(FETCH_NUMBER))
	file = open('help.csv')
	helpStrings = csv.reader(file)
	for row in helpStrings:
		if len(row) >= 3 and len(row[0]) > 0 and row[0][0] != ";":
			help = Help(type=row[0].strip(), name=row[1].strip(), text=row[2].strip())
			help.put()
	file.close()
		
def helpLookup(name, type):
	return Help.all().filter("name = ", name).filter("type = ", type).get()

def helpTextLookup(name, type):
	match = Help.all().filter("name = ", name).filter("type = ", type).get()
	if match:
		return match.text
	else:
		return None
	
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

def GenerateSystemQuestions():
	db.delete(Question.all().filter("community = ", None).fetch(FETCH_NUMBER))
	file = open('questions.csv')
	questionStrings = csv.reader(file)
	for row in questionStrings:
		if len(row) >= 3 and row[0][0] != ";":
			try:
				minValue = int(row[6])
			except:
				minValue = DEFAULT_QUESTION_VALUE_MIN
			try:
				maxValue = int(row[7])
			except:
				maxValue = DEFAULT_QUESTION_VALUE_MAX
			question = Question(
							   refersTo=row[0],
							   name=row[1],
							   text=row[2],
							   type=row[3],
							   choices=row[4].split(", "),
							   multiple=row[5] == "yes",
							   minIfValue=minValue,
							   maxIfValue=maxValue,
							   help=row[8],
							   useHelp=row[9],
							   community=None,
							   )
			question.put()
	file.close()
	
def HTMLColorToRGB(colorstring):
    colorstring = colorstring.strip()
    r, g, b = colorstring[:2], colorstring[2:4], colorstring[4:]
    r, g, b = [int(n, 16) for n in (r, g, b)]
    return (r, g, b)

def RGBToHTMLColor(rgb_tuple):
    return '%02x%02x%02x' % rgb_tuple
	
def HexColorStringForRowIndex(index):
	if index == 0:
		return GRID_DISPLAY_ROW_COLORS_TOP
	else:
		r,g,b = HTMLColorToRGB(GRID_DISPLAY_ROW_COLORS_TOP)
		r -= index * COLOR_DECREMENT
		g -= index * COLOR_DECREMENT
		b -= index * COLOR_DECREMENT
		return RGBToHTMLColor((r,g,b))
	
def MakeSystemResource(community, member, title, text, format, managersOnly):
	thereResource = Entry.all().filter("community = ", community).filter("creator = ", member.key()).filter("title = ", title).get()
	if thereResource:
		db.delete(thereResource)
	newResource = Entry(community=community, 
					type="resource",
					title=title,
					text=text,
					text_format=format,
					text_formatted=db.Text(InterpretEnteredText(text, format)),
					creator=member,
					draft=False,
					inBatchEntryBuffer=False,
					published=datetime.now(tz=pytz.utc),
					resourceForHelpPage=True,
					resourceForNewMemberPage=True,
					resourceForManagersAndOwnersOnly=managersOnly,
					resourceAtSystemLevel=True,
					)
	newResource.put()
	
def GenerateSystemResource(community, member, index):
	resourceArray = SYSTEM_RESOURCES[index]
	title = resourceArray[0]
	format = resourceArray[1]
	managersOnly = resourceArray[2]
	text = resourceArray[3]
	systemResource = Entry.all().filter("community = ", community.key()).filter("resourceAtSystemLevel = ", True).filter("title = ", title).get()
	if systemResource:
		db.delete(systemResource)
	MakeSystemResource(community, member, title, text, format, managersOnly)
	
class ImageHandler(webapp.RequestHandler):
	def get(self):
		if self.request.get("member_id"):
			member = db.get(self.request.get("member_id"))
			if member and member.profileImage:
				self.response.headers['Content-Type'] = "image/jpg"
				self.response.out.write(member.profileImage)
			else:
				self.error(404)
		elif self.request.get("community_id"):
			community = db.get(self.request.get("community_id"))
			if community and community.image:
				self.response.headers['Content-Type'] = "image/jpg"
				self.response.out.write(community.image)
			else:
				self.error(404)
		elif self.request.get("entry_id"):
			entry = db.get(self.request.get("entry_id"))
			if entry and entry.type == "pattern" and entry.screenshotIfPattern:
				self.response.headers['Content-Type'] = "image/jpg"
				self.response.out.write(entry.screenshotIfPattern)
		elif self.request.get("character_id"):
			character = db.get(self.request.get("character_id"))
			if character:
				self.response.headers['Content-Type'] = "image/jpg"
				self.response.out.write(character.image)
		elif self.request.get("attachment_id"):
			attachment = db.get(self.request.get("attachment_id"))
			if attachment:
				self.response.headers['Content-Type'] = attachment.mimeType
				self.response.out.write(attachment.data)
			   
class AttachmentHandler(webapp.RequestHandler):
	def get(self):
		if self.request.get("attachment_id"):
			attachment = db.get(self.request.get("attachment_id"))
			if attachment and attachment.data:
				if attachment.mimeType in ["image/jpeg", "image/png", "text/html", "text/plain"]:
					self.response.headers.add_header('Content-Disposition', 'filename="%s"' % attachment.fileName)
				else:
					self.response.headers.add_header('Content-Disposition', 'attachment; filename="%s"' % attachment.fileName)
				self.response.headers.add_header('Content-Type', attachment.mimeType)
				self.response.out.write(attachment.data)
			else:
				self.error(404)
				
class ExportHandler(webapp.RequestHandler):
	def get(self):
		if self.request.get("export_id"):
			export = db.get(self.request.get("export_id"))
			if export and export.data:
				self.response.headers.add_header('Content-Disposition', 'export; filename="%s"' % "test.csv")
				self.response.headers.add_header('Content-Type', "XML")
				self.response.out.write(export.data)
			else:
				self.error(404)
				
def RequireLogin(func):
	def check_login(request):
		if not users.get_current_user():
			loginURL = users.create_login_url("/")
			request.redirect(loginURL)
			return
		func(request)
	return check_login 

def GetCurrentCommunityAndMemberFromSession():
	session = Session()
	if session and session.has_key('community_key'):
		community_key = session['community_key']
	else:
		community_key = None
	if session and session.has_key('member_key'):
		member_key = session['member_key']
	else:
		member_key = None
	if community_key: 
		community = db.get(community_key) 
	else:
		community = None
	if member_key:
		member = db.get(member_key)
		if not member.community.key() == community.key():
			member = None
	else:
		member = None
	okayToAccess = community and community.active and member and member.active
	return community, member, okayToAccess

def GetKeyFromQueryString(queryString, keyname):
	if queryString:
		nameAndKey = queryString.split("=")
		if len(nameAndKey) > 1:
			return nameAndKey[1]
		else:
			return None
	else:
		return None

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
		when = whenUTC.astimezone(timezone(member.timeZoneName))
		delta = datetime.now(tz=timezone(member.timeZoneName)) - when
		if delta.days < 1 and delta.seconds < 1: 
			return "Now"
		elif delta.days < 1 and delta.seconds < 60: # one minute
			return "Moments ago"
		elif delta.days < 1 and delta.seconds < 60*60: # one hour
			return "%s minutes ago" % (delta.seconds // 60)
		elif delta.days < 1:
			return when.strftime(DjangoToPythonTimeFormat(member.timeFormat))
		elif delta.days < 2:
			return "Yesterday at %s" % when.strftime(DjangoToPythonTimeFormat(member.timeFormat))
		elif delta.days < 7:
			return when.strftime("%s at %s" % (DjangoToPythonDateFormat(member.dateFormat), 
											DjangoToPythonTimeFormat(member.timeFormat)))
		else:
			return when.strftime("%s at %s" % (DjangoToPythonDateFormat(member.dateFormat), 
											DjangoToPythonTimeFormat(member.timeFormat)))
	else:
		return None

def MakeSomeFakeData():
	user = users.get_current_user()
	community = Community(name="Test community", description="Test description")
	community.put()
	member = Member(googleAccountID=user.user_id(), googleAccountEmail=user.email(), nickname="Tester", community=community, governanceType="owner")
	member.initialize()
	member.put()
	if user.email() != "test@example.com":
		PendingMember(community=community, email="test@example.com").put()
	else:
		PendingMember(community=community, email="cfkurtz@cfkurtz.com").put()
	PendingMember(community=community, email="admin@example.com").put()
	Character(name="Little Bird", community=community).put()
	Character(name="Old Coot", community=community).put()
	Character(name="Blooming Idiot", community=community).put()
	entry = Entry(community=community, type="story", creator=member, title="The dog", text="The dog sat on a log.", draft=False)
	entry.put()
	entry.publish()
	annotation = Annotation(community=community, type="comment", creator=member, entry=entry, shortString="Great!", longString="Wonderful!", draft=False)
	annotation.put()
	annotation.publish()
	annotation = Annotation(community=community, type="comment", creator=member, entry=entry, shortString="Dumb", longString="Silly", draft=False)
	annotation.put()
	annotation.publish()
	entry = Entry(community=community, type="story", creator=member, title="The circus", text="I went the the circus. It was great.", draft=False)
	entry.put()
	entry.publish()

def checkedBlank(value):
	if value:
		return "checked"
	return ""

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

TEXT_FORMATS = ["plain text", "simple HTML", "Wiki markup"]

def InterpretEnteredText(text, mode="text"):
	result = text
	if mode == "plain text":
		result = cgi.escape(result)
		lines = result.split("\n")
		changedLines = []
		for line in lines:
			changedLines.append("<p>%s</p>" % line)
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
		result = cgi.escape(result)
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
		result = cgi.escape(result)
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


