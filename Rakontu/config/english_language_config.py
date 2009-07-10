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
# These are all terms that appear in the interface and should be translated to make Rakontu
# work in different languages. 
#
# Warning: This file uses Python syntax. You should be comfortable editing Python code before you edit this file.
#
# Note: The reason many of these texts have a "u" in front of them is to mark them as a unicode string.
# I have done this mainly to prepare (a little) for translation of things like these default strings
# and templates for use in other languages. If you need "special characters" like accents in these
# strings, make sure there is a "u" in front of them. There are a few exceptions where a unicode
# string will break things, mainly in the time/date formatting strings which must be ASCII.
#
# BACKUP THIS FILE before you make changes!
# ============================================================================================ 

# Don't touch this
from constants_base import *

# ============================================================================================ 
# AT THE SITE LEVEL
# ============================================================================================ 

# These are text formats used to process long text fields for display. 
# For this and all other _DISPLAY lists, the translated texts have to match the English texts
# in the ORDER of their meaning. 
# For example, this list must translate to (plain text, simple HTML, Wiki markup).
TEXT_FORMATS_DISPLAY = ["plain text", "simple HTML", "Wiki markup"]

# ============================================================================================ 
# AT THE RAKONTU LEVEL
# ============================================================================================ 

# Types of Rakontu. The list can be changed in site_configuration.py. The constant names MUST match what is here.
RAKONTU_NEIGHBORHOOD = u"neighborhood"
RAKONTU_INTEREST_SUPPORT_GROUP = u"interest or support group"
RAKONTU_WORK_GROUP = u"work group"
RAKONTU_FAMILY = u"family"
RAKONTU_CUSTOM = u"I'd rather choose the questions myself"

DEFAULT_RAKONTU_DESCRIPTION = \
u"""
This is a group of people who will come together to tell, keep and use their combined stories.
"""

DEFAULT_WELCOME_MESSAGE = \
u"""
Hello and welcome to our Rakontu! 
"""

DEFAULT_ETIQUETTE_STATEMENT = \
u"""
Telling a story is different than other ways of communicating. Stories can be complex, rich
ways of communicating about important and sometimes emotional topics. But stories can also
be damaging. Be considerate when you tell stories, both about who is listening and about
who is mentioned in the story.
"""

# ============================================================================================ 
# MEMBERS
# ============================================================================================ 

# This is what members are called before they have set themselves a nickname.
NO_NICKNAME_SET = u"No nickname set"

# This is what shows if people don't enter anything in the "Please describe yourself to other members." area.
NO_PROFILE_TEXT = u"No profile information."

# Display texts for helping roles. These MUST match the order (curator, guide, liaison).
HELPING_ROLE_TYPES_DISPLAY = ["curator", "guide", "liaison"]

# Display texts for governance roles. These MUST match the order (member, manager, owner).
GOVERNANCE_ROLE_TYPES_DISPLAY = ["member", "manager", "owner"]

# These appear in each member's preferences page, in the section where they are deciding whether 
# to take on each of the helping roles. You can add site-specific information here.
DEFAULT_ROLE_READMES = [
u"""
<p>A curator pays attention to the Rakontu's accumulated data. Curators add information, check for problems, create links, 
and in general maintain the vitality of the story bank.</p>""",

u"""
<p>A guide pays attention to people in the Rakontu. Guides answer questions, write tutorials, 
encourage people to tell and use stories, create patterns, write and respond to invitations,
and in general maintain the vitality of the on-line member community. Guides must agree to
receive email messages from the system so that they can answer questions.</p>
""",

u"""
<p>A liaison guides stories and other information over the barrier between on-line and off-line worlds. 
Liaisons conduct external interviews and add the stories people tell in them, read stories to people and gather 
comments and other annotations, and in general make the system work for both on-line and off-line Rakontu members.</p>
"""]

# These are the formats in which the default role readmes (above) are to be interpreted.
# Each setting MUST be (exactly) one of FORMAT_PLAIN_TEXT, FORMAT_SIMPLE_HTML, FORMAT_WIKI_MARKUP
DEFAULT_ROLE_READMES_FORMATS = [FORMAT_SIMPLE_HTML, FORMAT_SIMPLE_HTML, FORMAT_SIMPLE_HTML]
 
# ============================================================================================ 
# ENTRIES
# ============================================================================================ 

# Types of entry. These MUST match the order (story, invitation, collage, pattern, resource).
ENTRY_TYPES_DISPLAY = ["story", "invitation", "collage", "pattern", "resource"]
# Same thing but plural.
ENTRY_TYPES_PLURAL_DISPLAY = ["stories", "invitations", "collages", "patterns", "resources"]
# URLs for entry types. These MUST match the order (story, invitation, collage, pattern, resource).
# Since they will be used for URLs they CANNOT contain special characters or spaces.
ENTRY_TYPES_URLS = ["story", "invitation", "collage", "pattern", "resource"]

# This is the title given to entries which are not titled by their creators.
DEFAULT_UNTITLED_ENTRY_TITLE = u"Untitled"

NO_TEXT_IN_ENTRY = u"No text."

# Types of link. These MUST match the order (retold, reminded, responded, related, included, referenced).
LINK_TYPES_DISPLAY = ["retold", "reminded", "responded", "related", "included", "referenced"]

# ============================================================================================ 
# ANNOTATIONS
# ============================================================================================ 

# Types of annotation. These MUST match the order (tag set, comment, request, nudge).
ANNOTATION_TYPES_DISPLAY = ["tag set", "comment", "request", "nudge"]
# Same thing but plural
ANNOTATION_TYPES_PLURAL_DISPLAY = ["tag set", "comment", "request", "nudge"]
# URLs for annotation types. These MUST match the order (tag set, comment, request, nudge).
# Since they will be used for URLs they CANNOT contain special characters or spaces.
ANNOTATION_TYPES_URLS = ["tagset", "comment", "request", "nudge"]

# List of entry AND annotation types. 
# Used in manage/settings where they are choosing which items can have character attribution.
# These MUST match the order (story, pattern, collage, invitation, resource, answer, tagset, comment, request, nudge).
ENTRY_AND_ANNOTATION_TYPES_DISPLAY = ["story", "pattern", "collage", "invitation", "resource", "answer", "tag set", "comment", "request", "nudge"]
# URLs for entry and annotation types. 
# These MUST match the order (story, pattern, collage, invitation, resource, answer, tagset, comment, request, nudge).
# Since they will be used for URLs they CANNOT contain special characters or spaces.
ENTRY_AND_ANNOTATION_TYPES_URLS = ["story", "pattern", "collage", "invitation", "resource", "answer", "tagset", "comment", "request", "nudge"]

# These are types of request people can set. They can be anything you like. 
# Everyone can see them, and guides have a "review requests" page where they see all requests by type.
# They should be worded in reference to an entry, like "transcribe it"
# CAUTION: The last type in this list should always be "other" or some other no-category name.
# NOTE: Since these are not used for URLs or internal matchup, they don't need separate regular and "display" types.
REQUEST_TYPES = ["transcribe", "read aloud", "translate", "comment on", "tag", "answer questions about", "other"]

# ============================================================================================ 
# QUESTIONS
# ============================================================================================ 

# Things questions refer to. These MUST match the order (story, pattern, collage, invitation, resource, member, character).
QUESTION_REFERS_TO_DISPLAY = ["story", "pattern", "collage", "invitation", "resource", "member", "character"]
# Same thing but for URLs.
# Since they will be used for URLs they CANNOT contain special characters or spaces.
QUESTION_REFERS_TO_URLS = ["story", "pattern", "collage", "invitation", "resource", "member", "character"]
# Same thing but plural
QUESTION_REFERS_TO_PLURAL_DISPLAY = ["stories", "patterns", "collages", "invitations", "resources", "members", "characters"]

# Types of question. These MUST match the order (boolean, text, ordinal, nominal, value).
QUESTION_TYPES_DISPLAY = ["boolean", "text", "ordinal", "nominal", "value"]

# This is the name given to questions not named by their creators.
DEFAULT_QUESTION_NAME = u"Unnamed question"

# Default response (label on checkbox) for boolean questions
DEFAULT_QUESTION_BOOLEAN_RESPONSE = "Yes"

# ============================================================================================ 
# NUDGE SYSTEM
# ============================================================================================ 

# The default nudge category names that come up in Rakontu settings. 
# The number of strings in this list MUST match the number of categories (NUM_NUDGE_CATEGORIES) in site_configuration.py.
DEFAULT_NUDGE_CATEGORIES = [u"appropriate", 
						u"important", 
						u"useful to new members", 
						u"useful for resolving conflicts", 
						u"useful for understanding"]

# These questions appear next to the category names and give information about how to made nudge decisions.
# They MUST match up with the nudge category names in order.
DEFAULT_NUDGE_CATEGORY_QUESTIONS = [u"Is it helpful or harmful to the Rakontu?", 
						u"It is earth-shaking or trivial in impact?", 
						u"Would new members be especially interested in it?", 
						u"Would people in conflict be helped by it?", 
						u"Would it help people to make sense of things in our Rakontu?"]

# Event types are names for activities in the system that create activity points for entries and
# accumulate nudge points for members. (They only appear in the manage-settings screen.)
# These MUST match the order:
# (downdrift, 
# reading, adding story, adding pattern, adding collage, adding invitation, adding resource, 
# adding retold link, adding reminded link, adding related link, adding included link, adding responded link, adding referenced link,
# answering question, adding tag set, adding comment, adding request, adding nudge).
EVENT_TYPES_DISPLAY = [
			"downdrift", \
			"reading", "adding story", "adding pattern", "adding collage", "adding invitation", "adding resource", \
			"adding retold link", "adding reminded link", "adding related link", "adding included link", "adding responded link", "adding referenced link", \
			"answering question", "adding tag set", "adding comment", "adding request", "adding nudge"]

# ============================================================================================ 
# BROWSING and SEARCHING
# ============================================================================================ 

# These are the time frames shown in the Rakontu home page.
# These names must match the time frames described in site_configuration.py.
TIMEFRAME_HOUR = u"an hour"
TIMEFRAME_12HOURS = u"12 hours"
TIMEFRAME_DAY = u"a day"
TIMEFRAME_3DAYS = u"3 days"
TIMEFRAME_WEEK = u"a week"
TIMEFRAME_2WEEKS = u"2 weeks"
TIMEFRAME_MONTH = u"a month"
TIMEFRAME_3MONTHS = u"3 months"
TIMEFRAME_6MONTHS = u"6 months"
TIMEFRAME_YEAR = u"a year"
TIMEFRAME_EVERYTHING = u"everything"

# For search filters, whether any or all of selections are required for a match. These MUST match the order (any, all).
ANY_ALL_DISPLAY = ["any", "all"]
# Where to look for search words. These MUST match the order 
# (in the title, in the text, in a comment, in a request, in a nudge comment, in a link comment).
SEARCH_LOCATIONS_DISPLAY = ["in the title", "in the text", "in a comment", "in a request", "in a nudge comment", "in a link comment"]
# How to compare answers. These MUST match the order (contains, is, is greater than, is less than).
ANSWER_COMPARISON_TYPES_DISPLAY = ["contains", "is", "is greater than", "is less than"]

DEFAULT_SEARCH_NAME = "Untitled search filter"

# ============================================================================================ 
# DISPLAY TERMS
# These are just bits of text that come out of the source code and display on pages.
# ============================================================================================ 

# used to refer to a set of answers
TERMFOR_ANSWER_SET = "answer set"

# used to send a reminder to manager about items flagged by curator
TERMFOR_REMINDER = "Reminder about flagged items from" # person who is sending the reminder

# used to describe people
TERMFOR_YOUR = "your"
TERMFOR_YOU = "you"
TERMFOR_THISMEMBERS = "this member's"
TERMFOR_THISMEMBER = "this member"

TERMFOR_DOESNOTAPPLY = "doesn't apply"
TERMFOR_COPYOF = "Copy of"
TERMFOR_NONE = "none"

# used to describe search filters
TERMFOR_OFTHEWORDS = "of the words"
TERMFOR_OFTHETAGS = "of the tags"
TERMFOR_OFTHEENTRYQUESTIONS = "of the entry questions"
TERMFOR_OFTHECREATORQUESTIONS = "of the creator questions"

# used when printing entries
TERMFOR_ANSWEREDTHEQUESTION = "answered the question"

# used when displaying times on home page
TERMFOR_NOW = "Now"
TERMFOR_MOMENTSAGO = "Moments ago"
TERMFOR_MINUTESAGO = "minutes ago"
TERMFOR_YESTERDAYAT = "Yesterday at"
TERMFOR_AT = "at" # for reporting a time

# ============================================================================================ 
# PAGE TITLES
# These show at the top of pages. Things in comments are things that follow after the specified words.
# ============================================================================================ 

TITLE_REVIEW_RAKONTUS = "All Rakontus"
TITLE_CREATE_RAKONTU = "Create Rakontu"
TITLE_ANSWERS_FOR = "Answers for" # entry name
TITLE_PREVIEW_OF = "Preview of" # entry name
TITLE_RELATE_TO = "Relate to" # entry name
TITLE_REVIEW_FLAGS = "Review flags"
TITLE_REVIEW_GAPS = "Review gaps"
TITLE_REVIEW_ATTACHMENTS = "Review attachments"
TITLE_REVIEW_TAGS = "Review tags"
TITLE_REVIEW_RESOURCES = "Review resources"
TITLE_REVIEW_REQUESTS = "Review requests"
TITLE_REVIEW_INVITATIONS = "Review invitations"
TITLE_REVIEW_OFFLINE_MEMBERS = "Review off-line members"
TITLE_REVIEW_BATCH_ENTRIES = "Review batch entries"
TITLE_BATCH_ENTRY = "Batch entry"
TITLE_WELCOME = "Welcome"
TITLE_MANAGE_MEMBERS = "Manage members" 
TITLE_MANAGE_SETTINGS = "Manage settings" 
TITLE_MANAGE_QUESTIONS= "Manage questions" 
TITLE_MANAGE_QUESTIONS_ABOUT = "Manage questions about" # thing referred to
TITLE_MANAGE_CHARACTERS = "Manage characters"
TITLE_MANAGE_CHARACTER = "Manage character" # character name
TITLE_EXPORT_DATA = "Export data" 
TITLE_INACTIVATE = "Inactivate"
TITLE_HELP = "Help"
TITLE_HOME = "Home"
TITLE_ABOUT = "About"
TITLE_MEMBERS = "Members" 
TITLE_MEMBER = "Member" # member nickname
TITLE_CHARACTER = "Character" # character name
TITLE_PREFERENCES_FOR = "Preferences for" # member nickname
TITLE_DRAFTS_FOR = "Drafts for" # member nickname
TITLE_LEAVE_RAKONTU = "Leave" 
TITLE_SEARCH_FILTER = "Search filter"
TITLE_MESSAGE_TO_USER = "Message" # (on page that tells user something is completed or something is wrong)
TITLE_HELP_ON = "Help on" # help topic

# ============================================================================================ 
# URLS
# These define what locations are used to display the pages.
# If you don't care if the URLs appear in English, you don't have to change these.
# ============================================================================================ 

DIRS = {
	"dir_visit": "visit",
	"dir_manage": "manage",
	"dir_curate": "curate",
	"dir_guide": "guide",
	"dir_liaise": "liaise",
	"dir_admin": "admin",
	}

# Special home page - used often
HOME = "/visit/home"

URLS = {
	# visit
    "url_new": "new",
    "url_entry": "entry",
    "url_annotation": "annotation",
    "url_preview": "preview",
    "url_drafts": "drafts",
    "url_read": "read",
    "url_read_annotation": "readAnnotation",
    "url_preview_answers": "previewAnswers",
    "url_answers": "answers",
    "url_preferences": "preferences",
    "url_search_filter": "filter",
    "url_member": "member",
    "url_rakontu": "rakontu",
    "url_leave": "leave",
	# link creating 
    "url_retell": "retell",
    "url_remind": "remind",
    "url_respond": "respond",
    "url_relate": "relate",
	# guide
    "url_resources": "resources",
    "url_requests": "requests",
    "url_invitations": "invitations",
    "url_batch": "batch",
    "url_copy_resources": "copySystemResourcesToRakontu",
	# liaise
    "url_print_search": "printSearch",
    "url_print_entry": "printEntryAndAnnotations",
	# curate
    "url_curate": "curate",
    "url_flag": "flag",
    "url_flags": "flags",
    "url_gaps": "gaps",
    "url_attachments": "attachments",
    "url_tags": "tags",
	# manage
    "url_create": "create",
    "url_first": "first",
    "url_members": "members",
    "url_questions_list": "questions_list",
    "url_questions": "questions",
    "url_questions_to_csv": "questionsToCSV",
    "url_characters": "characters",
    "url_character": "character",
    "url_settings": "settings",
    "url_export_search": "exportSearch",
    "url_inactivate": "inactivate",
	# admin 
    "url_export": "export",
    "url_review": "review",
    "url_generate_sample_questions": "generateSampleQuestions",
    "url_generate_default_resources": "generateDefaultResources",
    "url_generate_helps": "generateHelps",
	# general
    "url_help": "help",
    "url_result": "result",
    "url_image": "img",
    "url_attachment": "attachment",
    }

# ============================================================================================ 
# RESULTS
# These are parameters passed to the result.html template to choose which thing to tell the user.
# These MUST match the strings in the result.html template.
# They are translatable because the user can see them in the URL. 
# These cannot contain spaces or special characters.
# If you don't care if the URLs appear in English, you don't have to change these.
# ============================================================================================ 

RESULT_sampleQuestionsGenerated = "sampleQuestionsGenerated"
RESULT_systemResourcesGenerated = "systemResourcesGenerated"
RESULT_helpsGenerated = "helpsGenerated"
RESULT_offlineMemberNotFound = "offlineMemberNotFound"
RESULT_attachmentsTooLarge = "attachmentsTooLarge"
RESULT_offlineMemberAlreadyAnsweredQuestions = "offlineMemberAlreadyAnsweredQuestions"
RESULT_offlineMemberNotFound = "offlineMemberNotFound"
RESULT_noEntriesToRelate = "noEntriesToRelate"
RESULT_changessaved = "changessaved"
RESULT_noSearchResultForPrinting = "noSearchResultForPrinting"
RESULT_noQuestionsToExport = "noQuestionsToExport"
RESULT_noSearchResultForExport = "noSearchResultForExport"
RESULT_entryNotFound = "entryNotFound"
RESULT_nicknameAlreadyInUse = "nicknameAlreadyInUse"
RESULT_messagesent = "messagesent"
RESULT_memberNotFound = "memberNotFound"
RESULT_ownerCannotLeave = "ownerCannotLeave"
RESULT_helpNotFound = "helpNotFound"
