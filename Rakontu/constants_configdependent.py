# ============================================================================================
# RAKONTU
# Description: Rakontu is open source story sharing software.
# Version: beta (0.9+)
# License: GPL 3.0
# Google Code Project: http://code.google.com/p/rakontu/
# ============================================================================================

from constants_base import *
from site_configuration import *

DEFAULT_QUESTIONS_FILE_NAME = "config/%s/default_questions.csv" % SITE_LANGUAGE
SAMPLE_QUESTIONS_FILE_NAME = "config/%s/sample_questions.csv" % SITE_LANGUAGE
DEFAULT_CHARACTERS_FILE_NAME = "config/%s/default_characters.csv" % SITE_LANGUAGE
DEFAULT_RESOURCES_FILE_NAME = "config/%s/default_resources.txt" % SITE_LANGUAGE
HELP_FILE_NAME = "config/%s/help.csv" % SITE_LANGUAGE
SKINS_FILE_NAME = "config/%s/skins.csv" % SITE_LANGUAGE

# rakontus
RAKONTU_ACCESS_STATES = ["all", "managers", "owners", "administrators"]

# members
HELPING_ROLE_TYPES = ["curator", "guide", "liaison"]
GOVERNANCE_ROLE_TYPES = ["member", "manager", "owner"]
VIEW_OPTION_LOCATIONS = ["home", "entry", "member", "character"]

# member groups who can be assigned as editors
ADDITIONAL_EDITOR_TYPES = ["curators", "guides", "liaisons", "managers", "members", "list"]

# events
EVENT_TYPES = ["downdrift", \
			"reading", "adding story", "adding pattern", "adding collage", "adding invitation", "adding resource", \
			"adding retold link", "adding reminded link", "adding related link", "adding included link", "adding responded link", "adding referenced link", \
			"answering question", "adding tag set", "adding comment", "adding request", "adding nudge"]

# entries
ENTRY_TYPES = ["story", "invitation", "collage", "pattern", "resource"]
ENTRY_TYPES_PLURAL = ["stories", "invitations", "collages", "patterns", "resources"]
ENTRY_TYPE_INDEX_STORY = 0
ENTRY_TYPE_INDEX_INVITATION = 1

# annotations
ANNOTATION_TYPES = ["tag set", "comment", "request", "nudge"]

# things that can be shown on member pages
ANNOTATION_ANSWER_LINK_TYPES = ["tag set", "comment", "request", "nudge", "answer", "link"]
ANNOTATION_ANSWER_LINK_TYPES_ANSWER_INDEX = 4
ANNOTATION_ANSWER_LINK_TYPES_LINK_INDEX = 5

# entries and annotations
ENTRY_AND_ANNOTATION_TYPES = ["story", "pattern", "collage", "invitation", "resource", "answer", "tag set", "comment", "request", "nudge"]
STORY_ENTRY_TYPE_INDEX = 0
ANSWERS_ENTRY_TYPE_INDEX = 5

# links
LINK_TYPES = ["retold", "reminded", "responded", "related", "included", "referenced"]

# questions
QUESTION_REFERS_TO = ["story", "pattern", "collage", "invitation", "resource", "member", "character"]
QUESTION_REFERS_TO_PLURAL = ["stories", "patterns", "collages", "invitations", "resources", "members", "characters"]
QUESTION_TYPES = ["boolean", "text", "ordinal", "nominal", "value"]

# filters
ANY_ALL = ["any", "all"]
SEARCH_LOCATIONS = ["in the title", "in the text", "in a comment", "in a request", "in a nudge comment", "in a link comment"]
ANSWER_COMPARISON_TYPES = ["contains", "is", "is greater than", "is less than"]

# sort by strings for gaps
GAPS_SORT_BY_CHOICES = ["date", "annotations", "activity", "nudges"]

# things to show in gaps
GAPS_SHOW_CHOICES = ["no tags", "no links", "no comments", "no answers", "no story links"]

# types of help tooltips
HELP_TYPES = ["info", "tip", "caution"]





