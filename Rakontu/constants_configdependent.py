# ============================================================================================
# RAKONTU
# Description: Rakontu is open source story sharing software.
# Version: pre-0.1
# License: GPL 3.0
# Google Code Project: http://code.google.com/p/rakontu/
# ============================================================================================
# NOTE: This file does NOT need to be changed for translation.

from constants_base import *
from site_configuration import *

# ============================================================================================
# NO LANGUAGE-SPECIFIC DEFINITION
# These are never displayed to the user so don't need to be translated and only appear here.
# ============================================================================================

DEVELOPMENT = False
FETCH_NUMBER = 1000
DATE_TIME_CSV_FORMAT = "%Y%m%dT%H%M%S"

# ============================================================================================
# GROUP LANGUAGE-SPECIFIC DEFINITION
# These are never referred to in the code single, so they have _DISPLAY counterparts in the language_config file.
# ============================================================================================

# members
HELPING_ROLE_TYPES = ["curator", "guide", "liaison"]
GOVERNANCE_ROLE_TYPES = ["member", "manager", "owner"]

# events
EVENT_TYPES = ["downdrift", \
			"reading", "adding story", "adding pattern", "adding collage", "adding invitation", "adding resource", \
			"adding retold link", "adding reminded link", "adding related link", "adding included link", "adding responded link", "adding referenced link", \
			"answering question", "adding tag set", "adding comment", "adding request", "adding nudge"]

# entries
ENTRY_TYPES = ["story", "invitation", "collage", "pattern", "resource"]
ENTRY_TYPES_PLURAL = ["stories", "invitations", "collages", "patterns", "resources"]

# annotations
ANNOTATION_TYPES = ["tag set", "comment", "request", "nudge"]

# entries and annotations
ENTRY_AND_ANNOTATION_TYPES = ["story", "pattern", "collage", "invitation", "resource", "answer", "tag set", "comment", "request", "nudge"]
ENTRY_AND_ANNOTATION_TYPES_URLS = ["story", "pattern", "collage", "invitation", "resource", "answer", "tagset", "comment", "request", "nudge"]
STORY_ENTRY_TYPE_INDEX = 0
ANSWERS_ENTRY_TYPE_INDEX = 5

# links
LINK_TYPES = ["retold", "reminded", "responded", "related", "included", "referenced"]

# questions
QUESTION_REFERS_TO = ["story", "pattern", "collage", "invitation", "resource", "member", "character"]
QUESTION_REFERS_TO_PLURAL = ["stories", "patterns", "collages", "invitations", "resources", "members", "characters"]
QUESTION_TYPES = ["boolean", "text", "ordinal", "nominal", "value"]

# search filters
ANY_ALL = ["any", "all"]
SEARCH_LOCATIONS = ["in the title", "in the text", "in a comment", "in a request", "in a nudge comment", "in a link comment"]
ANSWER_COMPARISON_TYPES = ["contains", "is", "is greater than", "is less than"]




