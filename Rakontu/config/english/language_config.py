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
# This is to prepare for translation of terms into other languages. 
# If you need "special characters" like accents in these strings, make sure there is a "u" in front of them. 
# Note that URL strings CANNOT contain special characters or spaces.
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
RAKONTU_CUSTOM = u"don't ask any questions by default (managers will add later)"

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

# These are names to be displayed to describe the color schemes available to Rakontu managers.
# The names on the left MUST match the color scheme names in the site_configuration.py file.
# The names on the right are shown to the user and should be translated.
COLOR_SCHEMES_DISPLAY_NAMES = {
							"grayscale": "grayscale",
							"sunset": "sunset",
							"pinky purple": "pinky purple",
							"growing things": "growing things",
							"funky": "funky",
							}

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
# These are bits of text that come out of the source code and display on pages.
# ============================================================================================ 

TERMS = {
		# used to refer to a group of answers
		"term_answer_set": "answer set",
		# used to send a reminder to manager about items flagged by curator
		"term_dear_manager": "Dear manager",
		"term_reminder": "Reminder about flagged items from", # person who is sending the reminder
		"term_wanted_you_to_know": "I wanted you to know that these items require your attention.",
		"term_thank_you": "Thank you for your attention.",
		"term_sincerely": "Sincerely",
		"term_your_site": "Your Rakontu site",
		"term_link": "link",
		# used to describe search filters
		"term_of_the_words": "of the words",
		"term_of_the_tags": "of the tags",
		"term_of_the_entry_questions": "of the entry questions",
		"term_of_the_creator_questions": "of the creator questions", 
		# used when displaying times on home page
		"term_now": "Now",
		"term_moments_ago": "Moments ago", # NOT followed by time
		"term_minutes_ago": "minutes ago", # preceded by number
		"term_yesterday_at": "Yesterday at", # followed by time
		"term_today_at": "Today at", # followed by time
		"term_at": "at", # followed by time
		# used when making a choice from a list  
		"term_choose": "choose",
		# used when exporting to files
		"term_export": "export",
		"term_print": "print",
		# miscellaneous
		"term_does_not_apply": "doesn't apply",
		"term_copy_of": "Copy of",
		"term_none": "none",
		}

# ============================================================================================ 
# TEMPLATE DISPLAY TERMS
# These are bits of text that are used on templates.
# ============================================================================================ 

TEMPLATE_TERMS = {
		# common_attribution.html
		"template_since_you_are_a_liaison": "Since you are a liaison",
		"template_collected_from_offline_member": "Was this collected from an off-line member?",
		"template_yes_collected_from": "Yes, it was collected from",
		"template_year": "year",
		"template_month": "month",
		"template_day": "day",
		"template_attributed_to": "It should be attributed to",
		"template_selected_member": "The selected member",
		"template_no_my_contribution": "No, this is my contribution", 
		"template_attribute_to": "I'd like to attribute it to", 
		"template_myself": "myself",
		"template_attribute_to_whom": "To whom would you like to attribute this contribution?",
		# common_footer.html
		"template_powered_by": "Powered by",
		# common_questions.html
		# read.html
		"template_you": "you",
		}

TEMPLATE_BUTTONS = {
		# common_grid.html
		"button_hide_details": "Hide details",
		"button_show_details": "Show details",
		
		}

TEMPLATE_MENUS = {
		# visit
		"menu_visit": "Visit",
		"menu_home_page": "Home page",
		"menu_about_this_rakontu": "About this Rakontu",
		"menu_about_rakontu_members": "About the members",
		"menu_start_page": "Start page",
		# create
		"menu_create": "Create",
		"menu_story": "Tell a story",
		"menu_invitation": "Invite people to tell stories",
		"menu_collage": "Build a story collage",
		"menu_pattern": "Describe a pattern",
		"menu_drafts": "Review saved drafts",
		"menu_filters": "Review saved search filters",
		# curate
		"menu_curate": "Curate",
		"menu_gaps": "Gaps",
		"menu_flags": "Flags",
		"menu_attachments": "Attachments",
		"menu_tags": "Tags",
		# guide
		"menu_guide": "Guide",
		"menu_invitations": "Invitations",
		"menu_requests": "Requests",
		"menu_resources": "Resources",
		"menu_resource": "Add a resource",
		# liaison
		"menu_liaise": "Liaise",
		"menu_manage_offline_members": "Manage off-line members",
		"menu_add_batch": "Add a batch of stories",
		"menu_review_batches": "Review entered batches",
		# manage
		"menu_manage": "Manage",
		"menu_members": "Members",
		"menu_settings": "Settings",
		"menu_questions": "Questions",
		"menu_characters": "Characters",
		"menu_export": "Export",
		# administer
		"menu_administer": "Administer",
		"menu_review_rakontus": "Review all Rakontus",
		"menu_site_initialization_tasks": "Site initialization tasks",
		# to right side of menus
		"menu_help": "Help",
		"menu_preferences": "Preferences",
		"menu_logout": "Log out",
		# this appears when site admin is looking ABOVE the Rakontu level
		"menu_site_administration": "Rakontu site administration",
		}

# ============================================================================================ 
# PAGE TITLES
# These show at the top of pages. Things in comments are things that follow after the specified words.
# ============================================================================================ 

TITLES = {
        "REVIEW_RAKONTUS": "All Rakontus",
        "CREATE_RAKONTU": "Create Rakontu",
        "ANSWERS_FOR": "Answers for", # entry name
        "PREVIEW_OF": "Preview of", # entry name
        "RELATE_TO": "Relate to", # entry name
        "REVIEW_FLAGS": "Review flags",
        "REVIEW_GAPS": "Review gaps",
        "REVIEW_ATTACHMENTS": "Review attachments",
        "REVIEW_TAGS": "Review tags",
        "REVIEW_RESOURCES": "Review resources",
        "REVIEW_REQUESTS": "Review requests",
        "REVIEW_INVITATIONS": "Review invitations",
        "REVIEW_OFFLINE_MEMBERS": "Review off-line members",
        "REVIEW_BATCH_ENTRIES": "Review batch entries",
        "BATCH_ENTRY": "Batch entry",
        "WELCOME": "Welcome",
        "MANAGE_MEMBERS": "Manage members" ,
        "MANAGE_SETTINGS": "Manage settings" ,
        "MANAGE_QUESTIONS": "Manage questions" ,
        "MANAGE_QUESTIONS_ABOUT": "Manage questions about", # thing referred to
        "MANAGE_CHARACTERS": "Manage characters",
        "MANAGE_CHARACTER": "Manage character", # character name
        "EXPORT_DATA": "Export data" ,
        "INACTIVATE": "Inactivate",
        "HELP": "Help",
        "HOME": "Home",
        "ABOUT": "About",
        "MEMBERS": "Members" ,
        "MEMBER": "Member", # member nickname
        "CHARACTER": "Character", # character name
        "PREFERENCES_FOR": "Preferences for", # member nickname
        "DRAFTS_FOR": "Drafts for", # member nickname
        "LEAVE_RAKONTU": "Leave" ,
        "SEARCH_FILTER": "Search filter",
        "MESSAGE_TO_USER": "Message", # (on page that tells user something is completed or something is wrong)
        "HELP_ON": "Help on", # help topic
        "INITIALIZE_SITE": "Initialize site",
		}

# ============================================================================================ 
# URLS
# These define what locations are used to display the pages.
# Don't change the items on the left, because they are used for internal lookup.
# You can change the items on the right.
# Since they are used for URLs, they cannot contain spaces or special characters.
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
	"url_home": "home",
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
    "url_filters": "filters",
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
    "url_review": "review",
	# curate
    "url_curate": "curate",
    "url_flag": "flag",
    "url_flags": "flags",
    "url_gaps": "gaps",
    "url_attachments": "attachments",
    "url_tags": "tags",
	# manage
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
	"url_create1": "create1",
	"url_create2": "create2",
    "url_export": "export",
    "url_admin": "admin",
    "url_sample_questions": "sample_questions",
    "url_default_resources": "default_resources",
    "url_helps": "helps",
	# general
    "url_help": "help",
    "url_result": "result",
    "url_image": "img",
    "url_attachment": "attachment",
    }

# ============================================================================================ 
# URL IDS
# These are the parts of URLs after the ?, and specifically those that look up items in the database.
# The things on the left MUST stay as is, because they match strings in the source code. Don't change them!
# The things on the right can be translated.
# Because these appear in URLs they cannot contain spaces or special characters.
# ============================================================================================ 

URL_IDS = {
	# used to send database keynames
	"url_query_rakontu": "rakontu",
	"url_query_entry": "entry",
	"url_query_attachment": "attachment",
	"url_query_annotation": "annotation",
	"url_query_answer": "answer",
	"url_query_member": "member",
	"url_query_character": "character",
	"url_query_search_filter": "filter",
	"url_query_attachment": "attachment",
	"url_query_export_csv": "csv",
	"url_query_export_txt": "txt",
	"url_query_export_xml": "xml",
	}

# ============================================================================================ 
# URL OPTIONS
# These are the parts of URLs after the ?, and specifically those that provide options to the page.
# The things on the left MUST stay as is, because they match strings in the source code. Don't change them!
# The things on the right can be translated.
# Because these appear in URLs they cannot contain spaces or special characters.
# ============================================================================================ 

URL_OPTIONS = {
	# used to send options or strings
	"url_query_export_type": "exporttype",
	"url_query_link_type": "linktype",
	"url_query_sort_by": "sortby",
	"url_query_uncompleted": "uncompleted",
	"url_query_no_responses": "noresponses",
	"url_query_curate": "curate",
	"url_query_result": "message",
	"url_query_help": "help",
	}

# ============================================================================================ 
# RESULTS
# These are parameters passed to the result.html template to choose which thing to tell the user.
# The things on the left MUST stay as is, because they match strings in the source code. Don't change them!
# The things on the right MUST match the strings in the result.html template.
# The things on the right are translatable because the user can see them in the URL.
# They cannot contain spaces or special characters.
# If you don't care if the URLs appear in English, you don't have to change these.
# ============================================================================================ 

RESULTS = {
		"sampleQuestionsGenerated": "sampleQuestionsGenerated",
		"systemResourcesGenerated": "systemResourcesGenerated",
		"helpsGenerated": "helpsGenerated",
		"offlineMemberNotFound": "offlineMemberNotFound",
		"attachmentsTooLarge": "attachmentsTooLarge",
		"offlineMemberAlreadyAnsweredQuestions": "offlineMemberAlreadyAnsweredQuestions",
		"offlineMemberNotFound": "offlineMemberNotFound",
		"noEntriesToRelate": "noEntriesToRelate",
		"changessaved": "changessaved",
		"noSearchResultForPrinting": "noSearchResultForPrinting",
		"noQuestionsToExport": "noQuestionsToExport",
		"noSearchResultForExport": "noSearchResultForExport",
		"entryNotFound": "entryNotFound",
		"nicknameAlreadyInUse": "nicknameAlreadyInUse",
		"messagesent": "messagesent",
		"memberNotFound": "memberNotFound",
		"ownerCannotLeave": "ownerCannotLeave",
		"helpNotFound": "helpNotFound",
		"rakontuNameTaken": "rakontuNameTaken", 
		}
