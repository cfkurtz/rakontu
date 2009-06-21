# ============================================================================================ 
# RAKONTU
# Description: Rakontu is open source story sharing software.
# Version: pre-0.1
# License: GPL 3.0
# Google Code Project: http://code.google.com/p/rakontu/
# ============================================================================================ 

# ============================================================================================ 
# ON CHANGING THESE VALUES
# ============================================================================================ 
# These site constants determine some aspects of the behavior of all community sites
# created in this Rakontu installation. You can of course change the source code of Rakontu itself, 
# but these constants are those the most amenable to change without architectural changes to the source code. 
# They have been placed here mainly as a convenience to the site administrator.
#
# There are several dependencies between different settings (e.g., if you change the number of options 
# you must change the options). These are noted in the comments below.
#
# Warning: This file uses Python syntax. You should be comfortable editing Python code before you edit this file.
#
# BACKUP THIS FILE before you make changes!
# ============================================================================================ 

# This determines how texts will be interpreted by default all over the site.
# Change this only if the people on your site will be MUCH more likely to prefer a simple HTML or Wiki format.
# MUST be (exactly) one of "plain text", "simple HTML", and "Wiki markup".
DEFAULT_TEXT_FORMAT = u"plain text"

# Note: The reason many of these texts have a "u" in front of them is to mark them as a unicode string.
# I have done this mainly to prepare (a little) for translation of things like these default strings
# and templates for use in other languages. If you need "special characters" like accents in these
# strings, make sure there is a "u" in front of them. There are a few exceptions where a unicode
# string will break things, mainly in the time/date formatting strings which must be ASCII.

# ============================================================================================ 
# MEMBERS
# ============================================================================================ 

# This is what members are called before they have set themselves a nickname.
NO_NICKNAME_SET = u"No nickname set"

# This is what shows if people don't enter anything in the "Please describe yourself to other members." area.
NO_PROFILE_TEXT = u"No profile information."

# How many nudge points members should get when they join.
# Giving people something to start with is encouraging.
DEFAULT_START_NUDGE_POINTS = 50

# The community contact email is the email address used as the SENDER in all email sent FROM the Rakontu.
# This appears as the default in the community settings.
# It MUST be a valid email address.
DEFAULT_CONTACT_EMAIL = "support@rakontu.org"

DEFAULT_WELCOME_MESSAGE = \
u"""
Hello and welcome to our community! 
"""

# ============================================================================================ 
# BROWSING
# ============================================================================================ 

# Don't change these. They are just here because they are needed by what follows.
MINUTE_SECONDS = 60
HOUR_SECONDS = 60 * MINUTE_SECONDS
DAY_SECONDS = 24 * HOUR_SECONDS
WEEK_SECONDS = 7 * DAY_SECONDS
MONTH_SECONDS = 30 * DAY_SECONDS
YEAR_SECONDS = 365 * DAY_SECONDS

# These are the time frames shown in the main "Look at stories" browser window.
# The names can be anything you like, but the number of seconds must match the time frame stated.
TIME_FRAMES = [(u"an hour", HOUR_SECONDS),
			 (u"12 hours", HOUR_SECONDS * 12),
			 (u"a day", DAY_SECONDS),
			 (u"3 days", DAY_SECONDS * 3),
			 (u"a week", WEEK_SECONDS),
			 (u"2 weeks", WEEK_SECONDS * 2),
			 (u"a month", MONTH_SECONDS),
			 (u"3 months", MONTH_SECONDS * 3),
			 (u"6 months", MONTH_SECONDS * 6),
			 (u"a year", YEAR_SECONDS),
			 (u"everything", 0), 
			 ]
TIME_FRAME_EVERYTHING_STRING = "everything"

# These would only be changed for internationalization. The first must always be the grid and the second the list.
GRID_OR_LIST = ["grid", "list"]
DEFAULT_GRID_OR_LIST = "grid"

# These are the available date and time formats. They affect all places where the date or time is displayed.
# The key in each dictionary (before the colon) is the django template format string.
# The value in each dictionary (after the colon) is the Python datetime format string.
# Note that the default (which shows up in all community settings pages) must )exactly) match one of the django strings.
DATE_FORMATS = {
			"j F Y": "%e %B %Y", # 3 January 2000
			"F j, Y": "%B %e, %Y", # January 3, 2000
			"j F": "%e %B", # 3 January
			"F j": "%B %e", # January 3
			"j/n/Y": "%d/%m/%Y", # 03/01/2000
			"n/j/Y": "%m/%d/%Y", # 01/03/2000
			}
DEFAULT_DATE_FORMAT = "F j, Y"

TIME_FORMATS = {
			"h:i a": "%I:%M %p", #"5:00 pm", 
			"H:i": "%H:%M", #"17:00",
			}
DEFAULT_TIME_FORMAT = "h:i a"

# This time zone will show up in all community settings pages.
DEFAULT_TIME_ZONE = "US/Eastern"

# This is the top (hex) color for the browsing tables for the main "look at" and for each entry. 
GRID_DISPLAY_ROW_COLORS_TOP = "FAEBD7"

# Lower rows in the main and entry browse tables get darker and darker by this increment.
COLOR_DECREMENT = 5

# This is how many rows there are (nudge values) in the main and entry browse tables.
BROWSE_NUM_ROWS = 10

# This is how many columns there are (time slices) in the main and entry browse tables.
BROWSE_NUM_COLS = 7

# This is how many of things you can search for of each type (texts, tags, answers)
NUM_SEARCH_FIELDS = 3

# ============================================================================================ 
# ENTRIES
# ============================================================================================ 

# This is the title given to entries which are not titled by their creators.
DEFAULT_UNTITLED_ENTRY_TITLE = u"Untitled"

NO_TEXT_IN_ENTRY = u"No text."

# This is the list of numbers of attachments communities can choose from, and the choice
# that appears chosen by default.
# To disallow attachments completely for the site, set NUM_ATTACHMENT_CHOICES to [0] and DEFAULT_MAX_NUM_ATTACHMENTS to 0.
NUM_ATTACHMENT_CHOICES = [0, 1, 2, 3, 4, 5]
DEFAULT_MAX_NUM_ATTACHMENTS = 3

# These are the accepted attachment file types. You can add or remove any types here.
# However, these two lists MUST match up exactly (by order).
# Lists of MIME types can be found here:
# http://www.iana.org/assignments/media-types/
# http://www.w3schools.com/media/media_mimeref.asp
ACCEPTED_ATTACHMENT_FILE_TYPES = ["jpg", "png", "pdf", "doc", "txt", "mpg", "mp3", "html", "zip"]
ACCEPTED_ATTACHMENT_MIME_TYPES = ["image/jpeg", "image/png", "application/pdf", "application/msword", "text/plain", "video/mpeg", "audio/mpeg", "text/html", "application/zip"]

# This is whether fictional character attribution is allowed, by default.
# One setting for each of these entry types: story, pattern, collage, invitation, resource, answer, tag set, comment, request, nudge
DEFAULT_ALLOW_CHARACTERS = [True,True,True,True,True,True,True,True,True,True]

# This is whether members are allowed to "re-enter" entries of each type after they are published.
# This can be great for things like resources, but it is usually NOT good for things like stories.
# One setting for each of these entry types: story, invitation, collage, pattern, resource
DEFAULT_ALLOW_EDITING_AFTER_PUBLISHING = [False, False, True, True, True]

# This is the number of stories that can be entered on a batch page (by a liaison or manager/owner)
# at any one time. Batch entry is mainly for entering the results of off-line story collections
# into the system.
NUM_ENTRIES_PER_BATCH_PAGE = 10

# These determine how big and small entry titles can get on the main browse page.
# In some circumstances you might want to allow a wider or narrower range.
MIN_BROWSE_FONT_SIZE_PERCENT = 70
MAX_BROWSE_FONT_SIZE_PERCENT = 300

# These constants determine how input fields are implemented in the html forms (where "maxlength" is how many
# characters can be entered into a field.) There are two reasons to set these limits: first,
# because you don't want people to enter really long things; and second (and more importantly)
# Google App Engine sets an absolute limit of 500 bytes on every model property saved as a string
# (not the longer Text property which can be of any length). So none of these should be set much higher
# than 200 characters. However, you may want to set them to smaller numbers if you want to keep things
# less verbose.

# For the subject lines of comments and requests; for link comments, flag comments, etc.
MAXLENGTH_SUBJECT_OR_COMMENT = 200

# For the names of all things that have names (including member nicknames)
MAXLENGTH_NAME = 100

# For tags in tag sets, for choices in questions
MAXLENGTH_TAG_OR_CHOICE = 40

# For all entered numbers
MAXLENGTH_NUMBER = 6

# ============================================================================================ 
# QUESTIONS
# ============================================================================================ 

# This is the name given to questions not named by their creators.
DEFAULT_QUESTION_NAME = u"Unnamed question"

# Defaults for question value ranges.
DEFAULT_QUESTION_VALUE_MIN = 0
DEFAULT_QUESTION_VALUE_MAX = 1000

# Default response (label on checkbox) for boolean questions
DEFAULT_QUESTION_BOOLEAN_RESPONSE = "Yes"

# How many choices can be offered for an ordinal or nominal question, maximum.
# A reasonable range is between 5 and 10.
MAX_NUM_CHOICES_PER_QUESTION = 10

# ============================================================================================ 
# NUDGE SYSTEM
# ============================================================================================ 

# The number of nudge categories. This MUST be set to at least one.
# It also MUST match the number of entries in the next list.
# If you change this AFTER there are communities using the site, their nudge categories
# will either get cut off (and not displayed), or new ones called "None" will be displayed.
# It's best to set it up at the start and not change it after any items have been entered.
NUM_NUDGE_CATEGORIES = 5

# The default nudge category names that come up in community settings. 
# The number of strings in this list MUST match the number of categories above.
DEFAULT_NUDGE_CATEGORIES = [u"appropriate", 
						u"important", 
						u"useful to new members", 
						u"useful for resolving conflicts", 
						u"useful for understanding"]

# These questions appear next to the category names and give information about how to made nudge decisions.
# They must match up with the nudge category names in order.
DEFAULT_NUDGE_CATEGORY_QUESTIONS = [u"Is it helpful or harmful to the community?", 
						u"It is earth-shaking or trivial in impact?", 
						u"Would new members be especially interested in it?", 
						u"Would people in conflict be helped by it?", 
						u"Would it help people to make sense of things in our community?"]

# How many nudge points can be assigned per entry, by default.
DEFAULT_MAX_NUDGE_POINTS_PER_ENTRY = 25

# How many nudge points members gain by doing each of these actions.
DEFAULT_MEMBER_NUDGE_POINT_ACCUMULATIONS = [
					0,	# downdrift
					4,	# reading
					40,	# adding story
					20,	# adding pattern
					20,	# adding collage
					30,	# adding invitation
					10,	# adding resource
					10,	# adding retelling link
					5,	# adding reminding link
					5,	# adding relating link
					5,	# adding including link
					10,	# adding responding link
					2,	# answering question
					10,	# adding tag set
					15,	# adding comment
					15,	# adding request
					5,	# adding nudge
					]

# How many activity points entries gain through each of these events.
DEFAULT_ARCTICLE_ACTIVITY_POINT_ACCUMULATIONS = [
					-1,	# downdrift
					4,	# reading
					40,	# adding story
					20,	# adding pattern
					20,	# adding collage
					30,	# adding invitation
					10,	# adding resource
					10,	# adding retelling link
					5,	# adding reminding link
					5,	# adding relating link
					5,	# adding including link
					10,	# adding responding link
					2,	# answering question
					10,	# adding tag set
					15,	# adding comment
					15,	# adding request
					5,	# adding nudge
					]

# ============================================================================================ 
# ANNOTATIONS
# ============================================================================================ 

# The number of tags in each tag set. Reasonable values are between 3 and 7.
NUM_TAGS_IN_TAG_SET = 5

# These are types of request people can set. They can be anything you like. 
# Everyone can see them, and guides have a "review requests" page where they see all requests by type.
# They should be worded in reference to an entry, like "transcribe it"
# CAUTION: The last type in this list should always be "other" or some other no-category name.
REQUEST_TYPES = ["transcribe", "read aloud", "translate", "comment on", "tag", "answer questions about", "other"]
NUM_REQUEST_TYPES = 7

# ============================================================================================ 
# HELPING ROLES
# ============================================================================================ 

# These appear in each member's profile page, in the section where they are deciding whether 
# to take on each of the helping roles. You can add site-specific information here.
DEFAULT_ROLE_READMES = [
u"""
A curator pays attention to the community's accumulated data. Curators add information, check for problems, create links, 
and in general maintain the vitality of the story bank.""",

u"""
A guide pays attention to the on-line human community. Guides answer questions, write tutorials, 
encourage people to tell and use stories, create patterns, write and respond to invitations,
and in general maintain the vitality of the on-line member community. Guides must agree to
receive email messages from the system so that they can answer questions.
""",

u"""
A liaison guides stories and other information over the barrier between on-line and off-line worlds. 
Liaisons conduct external interviews and add the stories people tell in them, read stories to people and gather 
comments and other annotations, and in general make the system work for both on-line and off-line community members.
"""]

# These are the formats in which the default role readmes (above) are to be interpreted.
# Each setting MUST be (exactly) one of "plain text", "simple HTML", and "Wiki markup".
DEFAULT_ROLE_READMES_FORMATS = [u"plain text", u"plain text", u"plain text"]

# Whether people have to click "I agree" to become a curator, guide or liaison.
# One setting for each of these helping roles: curator, guide, liaison.
DEFAULT_ROLE_AGREEMENTS = [False, False, False]

# Information that builds system resources (mainly help pages) is in a separate file.
from site_resources import *