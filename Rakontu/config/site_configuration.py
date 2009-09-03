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
# These site constants determine some aspects of the behavior of all Rakontus
# created in this Rakontu installation. You can of course change the source code of Rakontu itself, 
# but these constants are those the most amenable to change without architectural changes to the source code. 
# They have been placed here mainly as a convenience to the site administrator.
#
# There are several dependencies between different settings (e.g., if you change the number of options 
# you must change the options). These are noted in the comments below.
#
# All settings that could vary by language are in the language_config file. To 
# Warning: This file uses Python syntax. You should be comfortable editing Python code before you edit this file.
#
# BACKUP THIS FILE before you make changes! 
# ============================================================================================ 

# ============================================================================================ 
# LANGUAGE SETUP
# ============================================================================================ 

# Which language files to load. This must match the directory name (under config) under which the language dependent files are stored.
SITE_LANGUAGE = "english" 

# You MUST replace this with whomever is supporting the site.
# All Rakontu managers/owners see this email link at the bottom of each page.
SITE_SUPPORT_EMAIL = "support@xyz.org"

# Don't touch this
import sys
sys.path.insert(0, "config/%s" % SITE_LANGUAGE) 
from language_config import *

# ============================================================================================ 
# RAKONTUS
# ============================================================================================ 

# Rakontu types. These affect which default questions (in default_questions.csv) 
# are loaded when the Rakontu is created, as well as which sample questions (in config/sample_questions.csv)
# are available later. The Rakontu creator chooses one of these when they
# create the Rakontu. This gets saved in the Rakontu object in case of need later (but I am not otherwise using it).

# These must EXACTLY match the labels on questions in the config/default_questions.csv and config/sample_questions.csv files.
# You can add more of these, but they must all have strings attached to them in the language_config file.
# The LAST of these choices must always be a custom choice where NO default questions are added.
# If you want to remove this choice during Rakontu creation, reduce this list to only the last item
# and the drop-down box won't appear.

RAKONTU_TYPES = [
				RAKONTU_NEIGHBORHOOD,
				RAKONTU_INTEREST_SUPPORT_GROUP,
				RAKONTU_WORK_GROUP,
				RAKONTU_FAMILY,
				RAKONTU_CUSTOM]

# This determines how texts will be interpreted by default all over the site.
# Change this only if the people on your site will be MUCH more likely to prefer a simple HTML or Wiki format.
# MUST be (exactly) one of FORMAT_PLAIN_TEXT, FORMAT_SIMPLE_HTM, FORMAT_WIKI_MARKUP
DEFAULT_TEXT_FORMAT = FORMAT_PLAIN_TEXT

# The Rakontu contact email is the email address used as the SENDER in all email sent FROM the Rakontu.
# This appears as the default in the Rakontu settings.
# It MUST be a valid email address.
DEFAULT_CONTACT_EMAIL = "support@rakontu.org"
 
# How many nudge points members should get when they join.
# Giving people something to start with is encouraging.
DEFAULT_START_NUDGE_POINTS = 50

# This is the size to which uploaded thumbnail pictures are resized, for the rakontu and for member/character images.
THUMBNAIL_WIDTH = 100
THUMBNAIL_HEIGHT = 60

# ============================================================================================ 
# BROWSING
# ============================================================================================ 

# These are the time frames shown in the Rakontu home page.
# The names can be anything you like, but the number of seconds must match the time frame stated.
# These must match constants in the language_config file.
# These should not go beyond a month, to avoid excessive CPU limits on GAE.

if DEVELOPMENT:
	TIME_FRAMES = [
				 (TIMEFRAME_10MINUTES, MINUTE_SECONDS * 10),
				 (TIMEFRAME_HOUR, HOUR_SECONDS),
				 (TIMEFRAME_6HOURS, HOUR_SECONDS * 6),
				 (TIMEFRAME_12HOURS, HOUR_SECONDS * 12),
				 (TIMEFRAME_DAY, DAY_SECONDS),
				 (TIMEFRAME_3DAYS, DAY_SECONDS * 3),
				 (TIMEFRAME_WEEK, WEEK_SECONDS),
				 (TIMEFRAME_2WEEKS, WEEK_SECONDS * 2),
				 (TIMEFRAME_MONTH, MONTH_SECONDS),
				 ]
else:
	TIME_FRAMES = [
				 (TIMEFRAME_HOUR, HOUR_SECONDS),
				 (TIMEFRAME_6HOURS, HOUR_SECONDS * 6),
				 (TIMEFRAME_12HOURS, HOUR_SECONDS * 12),
				 (TIMEFRAME_DAY, DAY_SECONDS),
				 (TIMEFRAME_3DAYS, DAY_SECONDS * 3),
				 (TIMEFRAME_WEEK, WEEK_SECONDS),
				 (TIMEFRAME_2WEEKS, WEEK_SECONDS * 2),
				 (TIMEFRAME_MONTH, MONTH_SECONDS),
				 ]
	
# These are choices for how long the site should display cached state information before updating it.
# The more activity on the site, the shorter the cache time should be (but the slower the response).
# Text choices for these are in the lanugage_config.py file and MUST match these exactly.
SAVE_STATE_MINUTES_CHOICES = [0, 1, 5, 10, 15, 20, 30, 45, 60, 60*2, 60*6, 60*12, 60*24]
DEFAULT_SAVE_STATE_MINUTES = 15

# This is how much of a text is shown when the "Show details" setting is in place,
# on both the main screen and the per-entry screen.
DEFAULT_DETAILS_TEXT_LENGTH = 150

# These are the available date and time formats. They affect all places where the date or time is displayed.
# The key in each dictionary (before the colon) is the django template format string.
# The value in each dictionary (after the colon) is the Python datetime format string.
# Note that the default (which shows up in all Rakontu settings pages) must )exactly) match one of the django strings.
DATE_FORMATS = {
			"j F Y": "%e %B %Y", # 3 January 2000
			"F j, Y": "%B %e, %Y", # January 3, 2000
			"j F": "%e %B", # 3 January
			"F j": "%B %e", # January 3
			"j/n/Y": "%d/%m/%Y", # 03/01/2000
			"n/j/Y": "%m/%d/%Y", # 01/03/2000
			}

DEFAULT_DATE_FORMAT = "F j"

TIME_FORMATS = {
			"h:i a": "%I:%M %p", #"5:00 pm", 
			"H:i": "%H:%M", #"17:00",
			}

DEFAULT_TIME_FORMAT = "h:i a"

# This time zone will show up in all Rakontu settings pages.
DEFAULT_TIME_ZONE = "US/Eastern"

# This is the top (hex) color for the browsing tables for the home page and for each entry. 
GRID_DISPLAY_ROW_COLORS_TOP = "FAEBD7"
GRID_DISPLAY_ROW_COLORS_BOTTOM = "CD853F"

# This is how many rows there are (nudge values) in the main and entry browse tables.
BROWSE_NUM_ROWS = 10

# This is how many columns there are (time slices) in the main and entry browse tables.
BROWSE_NUM_COLS = 7

# This is the default value for what causes an entry to disappear because it has been nudged too low.
DEFAULT_NUDGE_FLOOR = -10

# This is how many of things you can search for of each type (texts, tags, answers)
NUM_SEARCH_FIELDS = 3 

# ============================================================================================ 
# ENTRIES
# ============================================================================================ 

# This is the list of numbers of attachments Rakontus can choose from, and the choice
# that appears chosen by default.
# To disallow attachments completely for the site, set NUM_ATTACHMENT_CHOICES to [0] and DEFAULT_MAX_NUM_ATTACHMENTS to 0.
# MAX_POSSIBLE_ATTACHMENTS should be set to the highest number on the list.
NUM_ATTACHMENT_CHOICES = [0, 1, 2, 3, 4, 5]
DEFAULT_MAX_NUM_ATTACHMENTS = 3
MAX_POSSIBLE_ATTACHMENTS = 5
UNTITLED_ATTACHMENT_NAME = "Untitled"

# These are the accepted attachment file types. You can add or remove any types here.
# However, these two lists MUST match up exactly (by order).
# Lists of MIME types can be found here:
# http://www.iana.org/assignments/media-types/
# http://www.w3schools.com/media/media_mimeref.asp
# You should make sure your entry in the help.csv file (which tells the user which types are accepted) matches this list.
ACCEPTED_ATTACHMENT_FILE_TYPES = ["jpg", "png", "pdf", "doc", "txt", "mpg", "mp3", "html", "zip", "py"]
ACCEPTED_ATTACHMENT_MIME_TYPES = ["image/jpeg", "image/png", "application/pdf", "application/msword", "text/plain", "video/mpeg", "audio/mpeg", "text/html", "application/zip", "text/plain"]

# This is whether fictional character attribution is allowed, by default.
# One setting for each of these entry types: story, pattern, collage, invitation, resource, answer, tag set, comment, request, nudge
# The basic recommendation is to allow stories, invitations, answers, comments, and nudges to be anonymous
# since these are most likely to be sensitive.
DEFAULT_ALLOW_CHARACTERS = [True, False, False, True, False, True, False, True, False, True]

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

# for printing entries
PRINT_DELIMITER = "=======\n"

# ============================================================================================ 
# QUESTIONS
# ============================================================================================ 

# Defaults for question value ranges.
DEFAULT_QUESTION_VALUE_MIN = 0
DEFAULT_QUESTION_VALUE_MAX = 1000

# How many choices can be offered for an ordinal or nominal question, maximum.
# A reasonable range is between 5 and 10.
MAX_NUM_CHOICES_PER_QUESTION = 10

# ============================================================================================ 
# NUDGE SYSTEM
# ============================================================================================ 

# The number of nudge categories. This MUST be set to at least one.
# It also MUST match the number of entries in the list of strings given in language_config.
# If you change this AFTER there are Rakontus using the site, their nudge categories
# will either get cut off (and not displayed), or new ones called "None" will be displayed.
# It's best to set it up at the start and not change it after any items have been entered.
NUM_NUDGE_CATEGORIES = 5

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
					10, # adding referenced link
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
					10, # adding referenced link
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
# CAUTION: You cannot set this number to zero; the system expects it to be at least one.
NUM_TAGS_IN_TAG_SET = 5




