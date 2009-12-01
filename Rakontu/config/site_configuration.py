# ============================================================================================ 
# RAKONTU
# Description: Rakontu is open source story sharing software.

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
# All settings that could vary by language are in the language_config file. 
# Warning: This file uses Python syntax. You should be comfortable editing Python code before you edit this file.
#
# BACKUP THIS FILE before you make changes! 
# ============================================================================================ 

# ============================================================================================ 
# LANGUAGE SETUP
# ============================================================================================ 

# Which language files to load. This must match the directory name (under config) under which the language dependent files are stored.
from os import environ
app_id = environ["APPLICATION_ID"]
if app_id == "rakontu" or app_id == "rakontu-sandbox":
	SITE_LANGUAGE = "english" 
elif app_id == "rakontu-francais":
	SITE_LANGUAGE = "francais" 

# This is the language to use for files that are missing.
# Having this fallback allows the system to work with partial (usually in-progress) translations
# where only some of the files are available.
SITE_LANGUAGE_FALLBACK_FOR_MISSING_CONFIG_FILES = "english"

# You MUST replace this with an email address connected to a site administrator (as defined by Google).
# This MUST be the email address you are using for the Google account you use to administer the Rakontu site.
# If it is not a valid email, you will not be able to get error messages.
SITE_SUPPORT_EMAIL = "cynthia.f.kurtz@gmail.com"

# Don't touch this
import sys, os
if os.path.exists("config/%s/language_config.py" % SITE_LANGUAGE):
	sys.path.insert(0, "config/%s" % SITE_LANGUAGE) 
else:
	sys.path.insert(0, "config/%s" % SITE_LANGUAGE_FALLBACK_FOR_MISSING_CONFIG_FILES) 
from language_config import *
# Okay, you can start touching stuff again now

# ============================================================================================ 
# RAKONTUS
# ============================================================================================ 

# Rakontu types. These affect which default questions (in default_questions.csv) 
# are loaded when the Rakontu is created, as well as which sample questions (in config/sample_questions.csv)
# are available later. The Rakontu creator chooses one of these when they
# create the Rakontu. This gets saved in the Rakontu object and is also used to select sample questions.

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

# How many nudge points members should get when they join.
# Giving people something to start with is encouraging.
DEFAULT_START_NUDGE_POINTS = 50

# This is the size to which uploaded thumbnail pictures are resized, for the rakontu and for member/character images.
# If you set this very large the Google App Engine will probably start freaking out.
THUMBNAIL_WIDTH = 100
THUMBNAIL_HEIGHT = 60

# ============================================================================================ 
# BROWSING
# ============================================================================================ 

# This is the number of items to show on grid (time vs nudge) and list pages.
# It should not be increased (very much) unless you are fairly confident of your server processing capacity and speed.
MAX_ITEMS_PER_GRID_PAGE = 100
MAX_ITEMS_PER_LIST_PAGE = 100

# These are the time frames shown in the Rakontu home page.
# The names can be anything you like, but the number of seconds must match the time frame stated.
# These must match constants in the language_config file.
TIME_FRAMES = [
			 (TIMEFRAME_HOUR, HOUR_SECONDS),
			 (TIMEFRAME_6HOURS, HOUR_SECONDS * 6),
			 (TIMEFRAME_12HOURS, HOUR_SECONDS * 12),
			 (TIMEFRAME_DAY, DAY_SECONDS),
			 (TIMEFRAME_3DAYS, DAY_SECONDS * 3),
			 (TIMEFRAME_WEEK, WEEK_SECONDS),
			 (TIMEFRAME_10DAYS, DAY_SECONDS * 10),
			 (TIMEFRAME_2WEEKS, WEEK_SECONDS * 2),
			 (TIMEFRAME_3WEEKS, WEEK_SECONDS * 3),
			 (TIMEFRAME_MONTH, MONTH_SECONDS),
			 (TIMEFRAME_2MONTHS, MONTH_SECONDS * 2),
			 (TIMEFRAME_3MONTHS, MONTH_SECONDS * 3),
			 ]

# These are the available date and time formats. They affect all places where the date or time is displayed.
# The key in each dictionary (before the colon) is the django template format string.
# The value in each dictionary (after the colon) is the Python datetime format string.
# Note that the default (which shows up in all Rakontu settings pages) must EXACTLY match one of the django strings.
DATE_FORMATS = {
			"j F Y": "%e %B %Y", # 3 January 2000
			"F j, Y": "%B %e, %Y", # January 3, 2000
			"j F": "%e %B", # 3 January
			"F j": "%B %e", # January 3
			"j/n/Y": "%d/%m/%Y", # 03/01/2000
			"n/j/Y": "%m/%d/%Y", # 01/03/2000
			}

DEFAULT_DATE_FORMAT = "F j" # January 3

TIME_FORMATS = {
			"h:i a": "%I:%M %p", #"5:00 pm"
			"H:i": "%H:%M", #"17:00"
			}

DEFAULT_TIME_FORMAT = "h:i a" #"5:00 pm"

# This time zone will show up in all Rakontu settings pages.
DEFAULT_TIME_ZONE = "US/Eastern"

# This is how many rows there are (nudge value slices) in the timlines.
BROWSE_NUM_ROWS = 10

# This is how many columns there are (time slices) in the timelines.
BROWSE_NUM_COLS = 7

# This is the default value for what causes an entry to disappear because it has been nudged too low.
DEFAULT_NUDGE_FLOOR = -10

# This is how many of things you can filter for of each type (texts, tags, answers)
NUM_SEARCH_FIELDS = 4

# ============================================================================================ 
# ENTRIES
# ============================================================================================ 

# This is the list of numbers of attachments Rakontus can choose from, and the choice
# that appears chosen by default.
# To disallow attachments completely for the site, set NUM_ATTACHMENT_CHOICES to [0] and DEFAULT_MAX_NUM_ATTACHMENTS to 0.
NUM_ATTACHMENT_CHOICES = [0, 1, 2, 3, 4, 5]
DEFAULT_MAX_NUM_ATTACHMENTS = 3

# MAX_POSSIBLE_ATTACHMENTS MUST be set to the highest number on the NUM_ATTACHMENT_CHOICES list.
MAX_POSSIBLE_ATTACHMENTS = 5

# The name of an attachment to which the user didn't give a name.
UNTITLED_ATTACHMENT_NAME = "Untitled"

# These are the accepted attachment file types. You can add or remove any types here.
# However, these two lists MUST match up exactly (by order).
# Lists of MIME types can be found here:
# http://www.iana.org/assignments/media-types/
# http://www.w3schools.com/media/media_mimeref.asp
ACCEPTED_ATTACHMENT_FILE_TYPES = ["jpg", "png", "pdf", "doc", "txt", "mpg", "mp3", "html", "zip", "py"]
ACCEPTED_ATTACHMENT_MIME_TYPES = ["image/jpeg", "image/png", "application/pdf", "application/msword", "text/plain", "video/mpeg", "audio/mpeg", "text/html", "application/zip", "text/plain"]

# This is whether fictional character attribution is allowed, by default.
# One setting for each of these entry types: story, pattern, collage, topic, resource, answer, tag set, comment, request, nudge
# The basic recommendation is to allow stories, topics, answers, comments, and nudges to be anonymous
# since these are most likely to be sensitive.
DEFAULT_ALLOW_CHARACTERS = [True, False, False, True, False, True, False, True, False, True]

# This is the number of stories that can be entered on a batch page (by a liaison or manager/owner)
# at any one time. Batch entry is mainly for entering the results of off-line story collections
# into the system.
# If you set this too high there is a greater possibility of the Google App Engine choking on the upload.
# Also, more can be confusing.
NUM_ENTRIES_PER_BATCH_PAGE = 10

# These determine how big and small entry titles can get on the main browse page.
# In some circumstances you might want to allow a wider or narrower range.
MIN_BROWSE_FONT_SIZE_PERCENT = 70
MAX_BROWSE_FONT_SIZE_PERCENT = 300

# These constants determine how input fields are implemented in the html forms (where "maxlength" is how many
# characters can be entered into a field.) There are two reasons to set these limits: first,
# because you don't want people to enter really long things; and second (and more importantly)
# Google App Engine sets an absolute limit of 500 bytes on every model property saved as a string
# (not the longer Text property which can be of any length). So none of these should be set ANY higher
# than 500 characters, ever. However, you may want to set them to smaller numbers if you want to keep things
# less verbose.

# For the subject lines of comments and requests; for link comments, flag comments, etc.
MAXLENGTH_SUBJECT_OR_COMMENT = 400

# For the names of all things that have names (including member nicknames)
MAXLENGTH_NAME = 100

# For tags in tag sets, for choices in questions
MAXLENGTH_TAG_OR_CHOICE = 40

# For all entered numbers
MAXLENGTH_NUMBER = 6

# This is the number of entries to export to XML in one request.
# Probably best to not set this too high (choke choke).
EXPORT_RANGE_XML = 50

# This is how much text to show where an entry (or comment or request) is being summarized in a details view
# The user can change this
DEFAULT_DETAILS_TEXT_LENGTH = 60
# These are choices to show the user on for that box.
DETAILS_TEXT_LENGTH_CHOICES = [20, 40, 60, 80, 100, 120, 140, 160, 180, 200, 250, 300, 350, 400, 450, 500, 600, 700, 800, 900, 1000]

# This is how much text shows on tooltips over names 
# The user can't change this (too many template references...)
TOOLTIP_LENGTH = 200

# This just determines the length of the drop-down list when setting the order for resources
# in a category. It's a constant so you can set it higher if for some reason you need more.
MAX_RESOURCES_PER_CATEGORY = 20

# This is just how many boxes to put up when people are choosing other members to allow to edit an entry.
MAX_NUM_ADDITIONAL_EDITORS = 10

# If there are many request collisions, it is possible that stored counts of 
# annotations, answers and links per entry may become inaccurate. 
# If an entry has not been read for at least this many seconds, 
# the system will recalculate the counts. This is a balance: the more people in your Rakontus,
# the more likely the counts will be off; but the longer it will take people to load pages.
UPDATE_ANNOTATION_COUNTS_SECONDS = 60 * 60 * 24

# These values are the choices for "quick" nudges.
# The order here determines the order they appear in the drop-down boxes,
# so it is best to have the positive values first.
QUICK_NUDGE_VALUES = [10, 5, 0, -5, -10]

# ============================================================================================ 
# QUESTIONS
# ============================================================================================ 

# Defaults for question value ranges.
DEFAULT_QUESTION_VALUE_MIN = 0
DEFAULT_QUESTION_VALUE_MAX = 1000

# How many choices can be offered for an ordinal or nominal question, maximum.
# A reasonable range is between 5 and 15.
MAX_NUM_CHOICES_PER_QUESTION = 15

# ============================================================================================ 
# NUDGE SYSTEM
# ============================================================================================ 

# The number of nudge categories. This MUST be set to at least one.
# It also MUST match the number of entries in DEFAULT_NUDGE_CATEGORIES in language_config.
NUM_NUDGE_CATEGORIES = 5

# How many nudge points can be assigned per entry, by default. Rakontu managers can change it for their Rakontu.
DEFAULT_MAX_NUDGE_POINTS_PER_ENTRY = 25

# How many nudge points members gain by doing each of these actions, by default.
DEFAULT_MEMBER_NUDGE_POINT_ACCUMULATIONS = [
					0,	# downdrift
					4,	# reading
					40,	# adding story
					20,	# adding pattern
					20,	# adding collage
					30,	# adding topic
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

# How many activity points entries gain through each of these events, by default.
DEFAULT_ARCTICLE_ACTIVITY_POINT_ACCUMULATIONS = [
					-1,	# downdrift
					4,	# reading
					40,	# adding story
					20,	# adding pattern
					20,	# adding collage
					30,	# adding topic
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




