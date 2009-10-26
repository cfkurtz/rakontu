# ============================================================================================ 
# RAKONTU
# Description: Rakontu is open source story sharing software.

# License: GPL 3.0
# Google Code Project: http://code.google.com/p/rakontu/
# ============================================================================================ 

# ============================================================================================ 
# ON CHANGING THESE VALUES
# ============================================================================================ 
# These are all terms that appear in the web interface and should be translated to make Rakontu
# work in different languages. 
#
# Warning: This file uses Python syntax. You should be comfortable editing Python code before you edit this file.
#
# IMPORTANT: The reason many of these texts have a "u" in front of them is to mark them as a unicode string.
# This is to prepare for translation of terms into other languages. 
# If you need "special characters" like accents in these strings, make sure there is a "u" in front of them. 
# Note that URL strings CANNOT contain special characters or spaces,
# in any language, even if there is "u" in front of them.
#
# BACKUP THIS FILE before you make changes!
# ============================================================================================ 

# Don't touch this
from constants_base import *
# Okay, you can start touching stuff again now

# ============================================================================================ 
# AT THE SITE LEVEL
# ============================================================================================ 

# These are text formats used to process long text fields for display. 
# For this and all other _DISPLAY lists, the translated texts have to match the English texts
# in the ORDER of their meaning. 
# For example, this list must translate to (plain text, simple HTML, Wiki markup).
TEXT_FORMATS_DISPLAY = [u"plain text", u"simple HTML", u"Wiki markup"]

# This is what shows in the URL when looking up a short help (tooltip) text.
# These MUST match the order (info, tip, caution).
# Because these are used in URLs they can have no spaces or special characters.
HELP_TYPES_URLS = [u"info", u"tip", u"caution"]

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
Hello and welcome to our Rakontu.
"""

DEFAULT_INVITATION_MESSAGE = \
u"""
You have been invited to join our Rakontu. Paste this web address into your browser
and visit the site to become a member.

Note that you will need to sign in to a Google account
with this email address in order to join. If you don't have a Google account with this
email address, please contact me with a different email to use for you.
"""

DEFAULT_ETIQUETTE_STATEMENT = \
u"""
Telling a story is different than other ways of communicating. Stories can be complex, rich
ways of communicating about important and sometimes emotional topics. But stories can also
be damaging. Be considerate when you tell stories, both about who is listening and about
who is mentioned in the story.
"""

# This is which skin is used by default (before a manager picks one).
# It MUST match one of the names in the skins.csv file.
DEFAULT_SKIN_NAME = u"sunset"
START_CUSTOM_SKIN_NAME = u"grayscale"

# Display names for Rakontu access states. The order MUST match (all members, managers only, owners only, admin only).
RAKONTU_ACCESS_STATES_DISPLAY = [u"all members", u"managers only", u"owners only", u"administrators only"]

# ============================================================================================ 
# MEMBERS
# ============================================================================================ 

# This is what shows if people don't enter anything in the "Please describe yourself to other members." area.
NO_PROFILE_TEXT = u"No profile information."

# This is what shows by default in the guide introduction field.
DEFAULT_GUIDE_INTRO = u"Ask me anything."

# Display texts for helping roles. These MUST match the order (curator, guide, liaison).
HELPING_ROLE_TYPES_DISPLAY = [u"curator", u"guide", u"liaison"]

# Display texts for governance roles. These MUST match the order (member, manager, owner).
GOVERNANCE_ROLE_TYPES_DISPLAY = [u"member", u"manager", u"owner"]

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
ENTRY_TYPES_DISPLAY = [u"story", u"invitation", u"collage", u"pattern", u"resource"]
# Same thing but plural.
ENTRY_TYPES_PLURAL_DISPLAY = [u"stories", u"invitations", u"collages", u"patterns", u"resources"]
# URLs for entry types. These MUST match the order (story, invitation, collage, pattern, resource).
# Since they will be used for URLs they CANNOT contain special characters or spaces.
ENTRY_TYPES_URLS = [u"story", u"invitation", u"collage", u"pattern", u"resource"]

# This is the title given to entries which are not titled by their creators.
DEFAULT_UNTITLED_ENTRY_TITLE = u"Untitled"

# This is what is put in if the person creates an entry but doesn't type anything into it.
NO_TEXT_IN_ENTRY = u"No text."

# Types of link. These MUST match the order (retold, reminded, responded, related, included, referenced).
LINK_TYPES_DISPLAY = [u"retold from", u"reminded by", u"responded to", u"related to", u"included in", u"referenced by"]

# Types of people who can edit an entry (in addition to its creator).
# These MUST match the order (curators, guides, liaisons, managers, members, list).
# Note that these are always plural.
ADDITIONAL_EDITOR_TYPES_DISPLAY = [u"all curators", u"all guides", u"all liaisons", u"all managers", u"all members", u"members in the following list"]

# These are shown in the curate-gaps page as things entries can be sorted by.
# They MUST match the order (date, annotations, activity, nudges).
GAPS_SORT_BY_CHOICES_DISPLAY = [u"most recent", u"most annotated", u"highest activity", u"highest nudged"]
# And now a set to use for translated URLS (no spaces, no special characters)
GAPS_SORT_BY_CHOICES_URLS = [u"date", u"annotated", u"activity", u"nudged"]

# Also for the gaps page, these are types of gaps to show.
# They MUST match the order (no tags, no links, no comments, no answers, no story links).
GAPS_SHOW_CHOICES_DISPLAY = [u"with no tags", u"with no links", u"with no comments", u"with no answers to questions", u"with no story links (collages only)"]
# And now a set to use for translated URLS (no spaces, no special characters)
GAPS_SHOW_CHOICES_URLS = [u"no_tags", u"no_links", u"no_comments", u"no_answers", u"no_story_links"]

# ============================================================================================ 
# ANNOTATIONS
# ============================================================================================ 

# Types of annotation. These MUST match the order (tag set, comment, request, nudge).
ANNOTATION_TYPES_DISPLAY = [u"tag set", u"comment", u"request", u"nudge"]
# Same thing but plural
ANNOTATION_TYPES_PLURAL_DISPLAY = [u"tag sets", u"comments", u"requests", u"nudges"]
# URLs for annotation types. These MUST match the order (tag set, comment, request, nudge).
# Since they will be used for URLs they CANNOT contain special characters or spaces.
ANNOTATION_TYPES_URLS = [u"tagset", u"comment", u"request", u"nudge"]

# These need translation because they appear in selections to view in  member/character pages.
ANNOTATION_ANSWER_LINK_TYPES_DISPLAY = [u"tag set", u"comment", u"request", u"nudge", u"answer", u"link"]
ANNOTATION_ANSWER_LINK_TYPES_PLURAL_DISPLAY = [u"tag sets", u"comments", u"requests", u"nudges", u"answers", u"links"]

# List of entry AND annotation types. 
# Used in manage/settings where they are choosing which items can have character attribution.
# These MUST match the order (story, pattern, collage, invitation, resource, answer, tagset, comment, request, nudge).
ENTRY_AND_ANNOTATION_TYPES_DISPLAY = [u"story", u"pattern", u"collage", u"invitation", u"resource", u"answer", u"tag set", u"comment", u"request", u"nudge"]
# Same thing but plural
ENTRY_AND_ANNOTATION_TYPES_PLURAL_DISPLAY = [u"stories", u"patterns", u"collages", u"invitations", u"resources", u"answers", u"tag sets", u"comments", u"requests", u"nudges"]
# URLs for entry and annotation types. 
# These MUST match the order (story, pattern, collage, invitation, resource, answer, tagset, comment, request, nudge).
# Since they will be used for URLs they CANNOT contain special characters or spaces.
ENTRY_AND_ANNOTATION_TYPES_URLS = [u"story", u"pattern", u"collage", u"invitation", u"resource", u"answer", u"tagset", u"comment", u"request", u"nudge"]

# These are types of request people can set. They can be set to anything you like (and translated).
# Everyone can see them, and guides have a "review requests" page where they see all requests by type.
# CAUTION: The last type in this list should always be "other" or some other no-category name.
REQUEST_TYPES = [u"comment on", u"tag", u"answer questions about", u"curate", u"link", u"tell your version", u"transcribe", u"read aloud", u"translate", u"other"]
# The same as above but without spaces or special characters (to be used in URLs). MUST match above list in order.
REQUEST_TYPES_URLS = [u"comment", u"tag", u"answer", u"curate", u"link", u"tellversion", u"transcribe", u"readaloud", u"translate", u"other"]

# ============================================================================================ 
# QUESTIONS
# ============================================================================================ 

# Things questions refer to. These MUST match the order (story, pattern, collage, invitation, resource, member, character).
QUESTION_REFERS_TO_DISPLAY = [u"story", u"pattern", u"collage", u"invitation", u"resource", u"member", u"character"]
# Same thing but for URLs.
# Since they will be used for URLs they CANNOT contain special characters or spaces.
QUESTION_REFERS_TO_URLS = [u"story", u"pattern", u"collage", u"invitation", u"resource", u"member", u"character"]
# Same thing but plural
QUESTION_REFERS_TO_PLURAL_DISPLAY = [u"stories", u"patterns", u"collages", u"invitations", u"resources", u"members", u"characters"]

# Types of question. These MUST match the order (boolean, text, ordinal, nominal, value).
QUESTION_TYPES_DISPLAY = [u"boolean", u"text", u"ordinal", u"nominal", u"value"]

# This is the name given to questions not named by their creators.
DEFAULT_QUESTION_NAME = u"Unnamed question"

# Default responses for boolean questions
DEFAULT_QUESTION_YES_BOOLEAN_RESPONSE = u"Yes"
DEFAULT_QUESTION_NO_BOOLEAN_RESPONSE = u"No"

# ============================================================================================ 
# NUDGE SYSTEM
# ============================================================================================ 

# The default nudge category names that come up in Rakontu settings. 
# The number of strings in this list MUST match the number of categories (NUM_NUDGE_CATEGORIES) in site_configuration.py.
DEFAULT_NUDGE_CATEGORIES = [
						u"important", 
						u"appropriate", 
						u"for new members", 
						u"for learning", 
						u"for understanding"]

# These questions appear next to the category names and give information about how to made nudge decisions.
# They MUST match up with the nudge category names in order.
DEFAULT_NUDGE_CATEGORY_QUESTIONS = [
						u"It is earth-shaking or trivial in impact?", 
						u"Is it helpful or harmful to the Rakontu?", 
						u"Would new members be especially interested in it?", 
						u"Would it be especially helpful for learning from each other?", 
						u"Would it help us understand each other better?"]

# Event types are names for activities in the system that create activity points for entries and
# accumulate nudge points for members. (They only appear in the manage-settings screen.)
# These MUST match the order:
# (downdrift, 
# reading, adding story, adding pattern, adding collage, adding invitation, adding resource, 
# adding retold link, adding reminded link, adding related link, adding included link, adding responded link, adding referenced link,
# answering question, adding tag set, adding comment, adding request, adding nudge).
EVENT_TYPES_DISPLAY = [
			"downdrift", \
			"reading", u"adding story", u"adding pattern", u"adding collage", u"adding invitation", u"adding resource", \
			"adding retold link", u"adding reminded link", u"adding related link", u"adding included link", u"adding responded link", u"adding referenced link", \
			"answering question", u"adding tag set", u"adding comment", u"adding request", u"adding nudge"]

# ============================================================================================ 
# BROWSING and SEARCHING
# ============================================================================================ 

# These are the time frames shown in the Rakontu home page.
# These names must match the time frames described in site_configuration.py.
TIMEFRAME_HOUR = u"an hour"
TIMEFRAME_6HOURS = u"six hours"
TIMEFRAME_12HOURS = u"twelve hours"
TIMEFRAME_DAY = u"a day"
TIMEFRAME_3DAYS = u"three days"
TIMEFRAME_WEEK = u"a week"
TIMEFRAME_10DAYS = u"ten days"
TIMEFRAME_2WEEKS = u"two weeks"
TIMEFRAME_3WEEKS = u"three weeks"
TIMEFRAME_MONTH = u"a month"
TIMEFRAME_2MONTHS = u"two months"
TIMEFRAME_3MONTHS = u"three months"

# For filters, whether any or all of selections are required for a match. These MUST match the order (any, all).
ANY_ALL_DISPLAY = [u"any", u"all"]
# Where to look for filter words. These MUST match the order 
# (in the title, in the text, in a comment, in a request, in a nudge comment, in a link comment).
FILTER_LOCATIONS_DISPLAY = [u"in the title", u"in the text", u"in a comment", u"in a request", u"in a nudge comment", u"in a link comment"]
# How to compare answers. These MUST match the order (contains, is, is greater than, is less than).
ANSWER_COMPARISON_TYPES_DISPLAY = [u"contains", u"is", u"is greater than", u"is less than"]

DEFAULT_SEARCH_NAME = u"Untitled filter"

# These describe the locations of the timeline grid views. 
# They MUST match the order (home, entry, member, character).
VIEW_OPTION_LOCATIONS_DISPLAY = [u"home page", u"entry page", u"member page", u"character page"]
# Same but for URLs. No spaces, no special characters.
VIEW_OPTION_LOCATIONS_URLS = [u"home", u"entry", u"member", u"character"]

# ============================================================================================ 
# DISPLAY TERMS
# These are bits of text that come out of the source code (NOT the templates) and display on pages.
# The things on the left MUST remain as they are (they match things in the source code).
# The things on the right should be translated.
# ============================================================================================ 

TERMS = {
		# used to refer to a group of answers
		"term_answer_set": u"answer set",
		"term_answer": u"answer",
		"term_answers": u"answers",
		"term_multiple": u"multiple", # multiple answers to a question allowed
		# used to display list of things user can do while viewing story or other entry
		"term_tell_another_version_of_this_story": u"Tell another version of what happened",
		"term_tell_a_story_this_reminds_you_of": u"Tell a story this reminds you of",
		"term_answer_questions_about_this": u"Answer questions about this",  # story, invitation collage, pattern, or resource
		"term_respond_to_invitation": u"Respond to this invitation with a story",
		"term_make_a_comment": u"Comment on this",  # story, invitation collage, pattern, or resource
		"term_tag_this": u"Tag this", # story, invitation collage, pattern, or resource
		"term_request_something_about_this": u"Request something about this", # story, invitation collage, pattern, or resource
		"term_relate_entry_to_others": u"Relate this entry to other entries",
		"term_nudge_this": u"Nudge this", # story, invitation collage, pattern, or resource
		"term_curate_this": u"Curate this", # story, invitation collage, pattern, or resource
		"term_stop_curating_this": u"Stop curating this", # story, invitation collage, pattern, or resource
		"term_change_this": u"Change your", # story, invitation collage, pattern, or resource # YOUR because only the creator can do this
		"term_print_this": u"Print content and annotations for this", # story, invitation collage, pattern, or resource
		# used to send a reminder to manager about items flagged by curator
		"term_dear_manager": u"Dear manager",
		"term_reminder": u"Reminder about flagged items from", # person who is sending the reminder
		"term_wanted_you_to_know": u"I wanted you to know that these items require your attention.",
		"term_thank_you": u"Thank you for your attention.",
		"term_sincerely": u"Sincerely",
		"term_your_site": u"Your Rakontu site",
		"term_link": u"link",
		"term_links": u"links",
		"term_question": u"question",
		"term_online": u"on-line",
		"term_offline": u"off-line",
		# used to describe filters
		"term_of_the_words": u"of the words",
		"term_of_the_tags": u"of the tags",
		"term_of_the_entry_questions": u"of the entry questions",
		"term_of_the_creator_questions": u"of the creator questions", 
		# used when displaying times on home page
		"term_now": u"Now",
		"term_moments_ago": u"Moments ago", # NOT followed by time
		"term_minutes_ago": u"minutes ago", # preceded by number
		"term_yesterday_at": u"Yesterday at", # followed by time
		"term_today_at": u"Today at", # followed by time
		"term_at": u"at", # followed by time
		# used when making a choice from a list  
		"term_choose": u"choose",
		# used when exporting to files
		"term_export": u"export",
		"term_print": u"print",
		# used when printing
		"term_printed_from_rakontu": u"Printed from Rakontu",
		"term_selections_for": u"Selections for", # rakontu name
		# miscellaneous
		"term_does_not_apply": u"doesn't apply",
		"term_copy_of": u"Copy of",
		"term_none": u"none",
		"term_result": u"A message from Rakontu",
		"term_help": u"Rakontu help",
		"term_help_info": u"Information:",
		"term_help_tip": u"Tip:",
		"term_help_caution": u"Caution:",
		"term_entries_contributed_by": u"Contribution timeline", 
		"term_yes": u"yes",
		"term_no": u"no",
		"term_for": u"for", # annotation for entry
		"term_points": u"points",
		"term_accumulations_for": u"Accumulations for",
		"term_custom": u"custom",
		"term_links": u"links",
		"term_too_many_items_warning": u"most recent items shown. To show older items, use selections to reduce the number of items showing.", # preceded by number/number
		"term_untitled": u"Untitled",
		"term_no_subject": u"No subject", # for a comment or request
		"term_could_not_email_admins": u"Actually, that's not true. Rakontu could NOT send an email about this issue to the site administrator(s) because the saved email address is invalid. Please contact your site administrator for help.",
		 "term_linked_item_removed": u"(linked item removed)",
		 "term_member": "member",
		}

# ============================================================================================ 
# TEMPLATE DISPLAY TERMS
# These are bits of text that are used on templates. The templates contain NO "raw" text,
# only text bits that can be translated here. By editing this file, you should be able
# to translate all parts of the web site without editing the template files themselves.
# The things on the left MUST remain as they are (they match things in the template files).
# The things on the right should be translated.
# ============================================================================================ 

TEMPLATE_TERMS = {
		# simplest words
		"template_yes": u"yes",
		"template_no": u"no",
		"template_and": u"and",
		"template_or": u"or",
		"template_you": u"you",
		"template_none": u"none",
		"template_none_found": u"None found",
		"template_from": u"from",
		"template_to": u"to",
		"template_information": u"information",
		"template_tip": u"tip",
		"template_caution": u"caution",
		"template_welcome": u"Welcome",
		"template_never": u"never",
		"template_go": u"go",
		"template_choose": u"choose",
		"template_why": u"why",
		"template_click_to_change": u"click to change",
		
		# types of people (singular and plural)
		"template_member": u"Member",
		"template_members": u"Members",
		"template_online_member": u"On-line member",
		"template_online_members": u"On-line members",
		"template_offline_member" :"Off-line member",
		"template_offline_members": u"Off-line members",
		"template_active_members": u"Active members",
		"template_active_online_members": u"Active on-line members",
		"template_active_offline_members": u"Active off-line members",
		"template_pending_member": u"Pending member",
		"template_pending_members": u"Pending members",
		"template_inactive_member": u"Inactive member",
		"template_inactive_members": u"Inactive members",
		"template_manager": u"Manager",
		"template_managers": u"Managers",
		"template_owner": u"Owner",
		"template_owners": u"Owners",
		"template_curator": u"Curator",
		"template_curators": u"Curators",
		"template_guide": u"Guide",
		"template_guides": u"Guides",
		"template_liaison": u"Liaison",
		"template_liaisons": u"Liaisons",
		"template_character": u"Character",
		"template_characters": u"Characters",
		
		# types of things (singular and plural)
		"template_attachment": u"Attachment",
		"template_attachments": u"Attachments",
		"template_entry": u"Entry",
		"template_entries": u"Entries",
		"template_story": u"Story",
		"template_stories": u"Stories",
		"template_invitation": u"Invitation",
		"template_invitations": u"Invitations",
		"template_pattern": u"Pattern",
		"template_patterns": u"Patterns",
		"template_collage": u"Collage",
		"template_collages": u"Collages",
		"template_resource": u"Resource",
		"template_resources": u"Resources",
		"template_attachment": u"Attachment",
		"template_attachments": u"Attachments",
		"template_response": u"Response",
		"template_responses": u"Responses",
		"template_annotation": u"Annotation",
		"template_annotations": u"Annotations",
		"template_comment": u"Comment",
		"template_comments": u"Comments",
		"template_request": u"Request",
		"template_requests": u"Requests",
		"template_draft": u"Draft",
		"template_drafts": u"Drafts",
		"template_tag": u"Tag",
		"template_tags": u"Tags",
		"template_tag_set": u"Tag set",
		"template_tag_sets": u"Tag sets",
		"template_nudge": u"Nudge",
		"template_nudges": u"Nudges",
		"template_question": u"Question",
		"template_questions": u"Questions",
		"template_answer": u"Answer",
		"template_answers": u"Answers",
		"template_message": u"Message",
		"template_messages": u"Messages",
		"template_link": u"Link",
		"template_links": u"Links",
		"template_filter": u"Filter",
		"template_filters": u"Filters",
		"template_filter": u"Filter",
		"template_filters": u"Filters",
		"template_word": u"Word",
		"template_words": u"Words",
		"template_type": u"Type",
		"template_types": u"Types",
		"template_email": u"Email",
		"template_skin": u"Skin",
		"template_skins": u"Skins",
		"template_range": u"Range",
		
		# things lots of objects have
		"template_linked_to": u"Linked to",
		"template_name": u"Name",
		"template_text": u"Text",
		"template_file": u"File",
		"template_nickname": u"Nickname",
		"template_description": u"Description",
		"template_picture": u"Picture",
		"template_image": u"Image",
		"template_etiquette_statement": u"Etiquette statement",
		"template_title": u"Title",
		"template_content": u"Content",
		"template_interpret_as": u"Interpret as",
		"template_first_part_of_text": u"First part of text",
		"template_contributor": u"Contributor",
		"template_subject": u"Subject",
		"template_joined": u"Joined",
		"template_created": u"Created",
		"template_created_by": u"Created by",
		"template_published": u"Published",
		"template_last_published": u"Last published",
		"template_last_changed": u"Last changed",
		"template_last_generated": u"Last generated",
		"template_invited": u"Invited",
		"template_collected": u"Collected",
		"template_active": u"Active",
		"template_inactive": u"Inactive",
		"template_online": u"On-line",
		"template_offline": u"Off-line",
		"template_private": u"Private",
		"template_shared": u"Shared",
		"template_new": u"New",
		"template_completed": u"Completed",
		"template_not_completed": u"Not completed",
		"template_remove": u"Remove",
		"template_year": u"year",
		"template_month": u"month",
		"template_day": u"day",
		"template_hours": u"hours",
		"template_log_out": u"Sign out",
		"template_help": u"Help",
		"template_newer": u"Newer",
		"template_older": u"Older",
		
		# things the user can do (but not buttons - usually links)
		"template_create_one": u"Create one",
		"template_add_some": u"Add some",
		"template_activate": u"Activate",
		"template_inactivate": u"Inactivate",
		"template_edit_drafts": u"Edit drafts",
		"template_preview": u"Preview",
		"template_change": u"Change",
		"template_attach": u"Attach",
		"template_replace": u"Replace",
		"template_copy": u"Copy",
		"template_previous": u"Previous",
		"template_next": u"Next",
		"template_changes_saved": u"Your changes have been saved.",
		
		# things on alt tags for pictures
		"template_rakontu_logo": u"Rakontu logo",
		"template_powered_by_GAE": u"Powered by Google App Engine",
		
		# things used in specific template files
		
		# common_attribution (template file name)
		"template_the_former_member": u"the former member",
		"template_the_former_character": u"the former character",
		"template_since_you_are_a_liaison": u"Since you are a liaison",
		"template_collected_from_offline_member": u"Was this collected from an off-line member?",
		"template_yes_collected_from": u"Yes, it was collected from",
		"template_attributed_to": u"It should be attributed to",
		"template_selected_member": u"The selected member",
		"template_no_my_contribution": u"No, this is my contribution", 
		"template_attribute_to": u"I'd like to attribute it to", 
		"template_myself": u"myself",
		"template_attribute_to_whom": u"To whom would you like to attribute this contribution?",
		# common_footer
		"template_site_start_page": u"Site start page",
		"template_site_administration": u"Site administration",
		"template_google_account": u"Google account",
		# common_questions
		"template_answer_questions_about_yourself": u"Please answer these questions about yourself.",
		"template_answer_questions_about_member": u"Please answer these questions about",
		"template_answers_to_questions_about": u"Answers to questions about",
		"template_answer_questions_about": u"Please answer these questions about this",
		"template_enter_number": u"Please enter a number between",
		"template_no_questions": u"There are no questions for this type of item.",
		# -------- access denied pages
		# error/notFound
		"template_URL_not_found": u"We've looked everywhere and we just can't find it!",
		"template_the_page_could_not_be_found": u"Rakontu can't find the page you asked for. Please check the web address.",
		# error/noRakontu
		"template_could_not_find_rakontu": u"Can't see it from here. Sorry.",
		"template_the_rakontu_could_not_be_found": u"The specified Rakontu could not be found. Please check with your system administrator for the link to the Rakontu you want to access.",
		# error/noMember
		"template_could_not_find_member": u"We have no member by that name.",
		"template_the_member_could_not_be_found": u"The specified member could not be found, or the membership has been inactivated. Please check with a manager of the Rakontu.",
		# error/roleNotFound
		"template_role_not_found": u"Helpers only, please.",
		"template_to_access_page_take_on_role": u"To access this page you must take on this helping role",
		"template_how_to_take_on_a_role": u"To take on a helping role, see your Preferences page.", 
		# error/managersOnly
		"template_not_a_manager": u"Rakontu managers only, please.",
		"template_manager_only_page": u"This page is available only to Rakontu managers. If you want to become a manager of your Rakontu, talk to a manager.",
		# error/ownersOnly
		"template_not_an_owner": u"Rakontu owners only, please.",
		"template_owners_only_page": u"This page is available only to owners of the Rakontu. If you want to become an owner of your Rakontu, talk to a manager.",
		# error/adminOnly
		"template_not_admin": u"Administrator-class nerds only, please.",
		"template_admin_only_page": u"This page is available only to Rakontu site administrators.",
		# error/rakontuNotAvailable
		"template_rakontu_sleeping": u"Shh! It's resting.",
		"template_rakontu_not_available": u"This Rakontu is temporarily unavailable due to system maintenance. Please check back again later.",
		# -------- error pages
		# error/error
		"template_error": u"Oops! Sorry :(",
		"template_an_error_has_occurred_and_admin_notified": u"Something went wrong. The system administrator has been notified.",
		"template_error_message": u"If you want to talk about this error with the administrator, copy this message and paste it into your email.",
		# error/databaseError
		"template_database_error": u"Bad Google. Bad.",
		"template_there_was_a_database_error": u"Apparently Google is not working very well at the moment. Could you please try what you were doing again?",
		# error/transactionFailed
		"template_transaction_failed_error": u"Can't ... handle ... demand ... trying ...",
		"template_too_many_transactions": u"Your transaction was unable to complete because there were lots of people using the site at once. Sorry about that. Could you please try what you were doing again?",
		# error/attachmentTooLarge
		"template_attachment_too_large_error": u"Whoa, that's more than I can handle!",
		"template_the_attachment_was_too_large_and_was_not_saved": u"The file you chose was too large, and Rakontu could not upload it. Please try uploading a smaller file.",
		# error/attachmentWrongType
		"template_attachment_wrong_type_error": u"What's this, some kind of newfangled contraption? I can't make head or tails of it.",
		"template_attachment_is_of_wrong_type": u"This Rakontu site does not accept the type of attachment you chose. Please check the list of acceptable types on the page where you add an attachment.",
		
		# help 
		"template_click_back_button": u"Click the Back button to return to the page you were on.",
		"template_or_would_you_like_more": u"or would you like more",
		# result
		"template_or_return_to_home": u"or perhaps you would like to return to the",
		"template_home_page": u"Home page",
		"template_or_would_you_like_some": u"or would you like some",
		# start
		"template_rakontu_motto": u"Helping people take good care of their stories.",
		"template_you_are_member_of": u"You are a member of these Rakontus.",
		"template_you_are_invited_to": u"You have been invited to join these Rakontus.",
		"template_you_can_join": u"You can join these Rakontus.", # << TRANSLATION REQUIRED >>
		"template_from_google": u"from Google",
		"template_must_be_logged_in": u"You must be signed in to a Google account to use Rakontu.",
		"template_login": u"Sign in",
		"template_at_google": u"at Google",
		"template_you_have_no_rakontus_to_visit": u"You are not a member of (or invited to join) any Rakontus on this site. Rakontus are invitation-only, private spaces. To join a Rakontu, ask one of its managers to invite you to it.",
		# admin/admin
		"template_site_initialization_tasks": u"Site initialization tasks",
		"template_generate": u"Generate",
		"template_default_help_resources_from": u"default help resources from",
		"template_skins_from": u"skins from",
		"template_sample_questions_from": u"sample questions from",
		"template_help_texts_from": u"short mouse-over help texts from",
		"template_have_been_created": u"have been created",
		"template_membership": u"Membership",
		"template_click_rakontu_name_to_join": u"click rakontu name to join",
		"template_join_as_a": u"Join as",
		"template_last_activity": u"Last activity",
		"template_cannot_leave_only_owner": u"cannot leave - only owner",
		"template_rakontu_access_state": u"Available to",
		"template_create_another": u"Create another",
		"template_remove_this_rakontu": u"Remove this Rakontu",
		"template_access_message": u"Access message",
		"template_fake_data": u"Development: Fake data for testing",
		"template_add_fake_data": u"Add fake data to existing Rakontus",
		"template_fake_rakontu": u"Generate fake testing Rakontu",
		# admin/create rakontu - step one
		"template_create_rakontu": u"Create a new Rakontu",
		"template_step_one": u"Step One",
		"template_short_rakontu_name": u"Please enter a short URL name for the Rakontu web link. This name cannot be changed afterward. It cannot contain spaces or special characters.",
		"template_rakontu_name_taken": u"That Rakontu name is already in use. Please choose another.",
		"template_cancel_rakontu_creation": u"Cancel and return to the Rakontu site administration page",
		# admin/create rakontu - step two
		"template_step_two": u"Step Two",
		"template_short_name_is": u"The short name (URL) chosen for this Rakontu is:",
		"template_longer_rakontu_name": u"Please provide a longer name to display on the Rakontu pages.",
		"template_choose_rakontu_type": u"Which of these types best represents this Rakontu?",
		"template_rakontu_owner_email": u"Please enter an email address for the new Rakontu's owner. ",
		"template_back_to_first_page": u"Go back to the first page",
		# admin/confirmRemoveRakontu
		"template_confirm_removal_of_rakontu": u"Confirm PERMANENT removal of Rakontu", # rakontu name
		"template_removal_warning1": u"Are you really, truly, ABSOLUTELY SURE you want to remove this Rakontu PERMANENTLY?",
		"template_removal_warning2": u"This action CANNOT be undone. The Rakontu and all of its content will be DELETED from the database. Forever and ever.",
		"template_removal_warning3": u"The system does not make backups automatically. Have you backed up this Rakontu?",
		"template_removal_warning4": u"(For more information about backing up Rakontu data, see your Rakontu adminstrator's guide.)",
		"template_cancel_rakontu_removal": u"Cancel removal",
		# curate/attachments
		"template_file_name": u"File name",
		"template_no_attachments": u"There are no attachments in the data set.",
		# curate/flags
		"template_flagged": u"Flagged",
		"template_notify": u"Notify",
		"template_flag_noun": u"Flag",
		"template_flag_verb": u"Flag",
		"template_unflag": u"Unflag",
		"template_items_flagged_for_removal": u"Items flagged for removal",
		"template_comment_only": u"comment only",
		"template_entry_questions": u"Entry questions",
		"template_member_questions": u"Member questions",
		"template_remove_warning": u"Please remove items carefully. Deleted items cannot be recovered.",
		"template_flag_comment": u"Flag comment",
		"template_click_here_to_unflag": u"Click here to unflag this item",
		"template_click_here_to_flag": u"Click here to flag this item for removal",
		"template_click_here_to_flag_this_set_of_tags": u"Click here to flag this set of tags for removal",
		"template_click_here_to_flag_this_entry": u"Click here to flag this entry for removal",
		"template_click_here_to_flag_this_resource": u"Click here to flag this resource for removal",
		"template_no_flagged_items_of_this_type": u"There are no flagged items of this type.",
		# curate/gaps
		"template_gaps": u"Gaps",
		"template_sort_by": u"sorted by",
		# curate/tags
		"template_change_entry_tags": u"Change entry tags",
		"template_no_tags": u"There are no tags to review.",
		"template_tags_warning": u"Please make changes carefully. Deleted or changed tags cannot be recovered.",
		# guide/invitations
		"template_all_invitations": u"all invitations",
		"template_only_invitations_with_no_responses": u"only invitations with no responses",
		"template_invitations_with_no_responses": u"Invitations with no responses",
		"template_no_invitations": u"There are no invitations in the Rakontu.",
		"template_no_invitations_without_responses": u"There are no invitations without responses.",
		# guide/requests
		"template_all_requests": u"all",
		"template_only_uncompleted_requests": u"uncompleted",
		"template_requests_of_the_type": u"requests of the type",
		"template_uncompleted_requests": u"Requests that have not been marked as completed",
		"template_no_requests": u"There are no requests of the selected type.",
		"template_no_uncompleted_requests": u"There are no uncompleted requests of the selected type.",
		# guide/resources
		"template_all_resources": u"all resources",
		"template_only_help_resources": u"only help resources",
		"template_only_new_member_resources": u"only resources for new members",
		"template_only_non_help_resources": u"only non-help (reminding) resources",
		"template_category": u"Category",
		"template_order_in_category": u"Order in category",
		"template_appears_on_help_page": u"Appears on help page",
		"template_for_new_members": u"For new members",
		"template_for_managers_only": u"For managers only",
		"template_not_for_managers_only": u"Not for managers only",
		"template_for_managers_and_non_managers": u"For managers or non-managers",
		"template_no_resources": u"No resources were found that match the current selections.",
		"template_generate_default_help_resources": u"Generate all default help resources",
		# liaise/batch
		"template_batch_story_entry": u"Batch story entry",
		"template_choose_csv_file_for_batch": u"Choose a CSV file to import entries from",
		"template_or_enter_stories": u"or enter items in the boxes below and click any of the 'Add stories' buttons.",
		"template_collected_from": u"Collected from",
		"template_attributed_to": u"Attributed to",
		# liaise/members
		"template_links": u"Links",
		"template_view_member_page": u"Member page",
		"template_change_profile": u"Profile",
		"template_change_preferences": u"Preferences",
		"template_take_over_offline_member": u"Become this member's liaison",
		"template_switch_offline_member_liaison_to": u"Transfer to",
		"template_no_active_offline_members": u"There are no active off-line members at this time.",
		"template_you_have_no_offline_members": u"There are no active off-line members assigned to you at this time.",
		"template_add_offline_members": u"Add off-line members",
		"template_inactive_members": u"Inactive members",
		# liaise/review
		"template_batch_entered_stories": u"Batch entered stories",
		"template_import": u"Import",
		"template_no_stories_entered": u"No stories have yet been entered.",
		# manage/character
		"template_name_and_description": u"Name and description",
		# manage/characters
		"template_add_new_characters": u"Add new characters",
		"template_change_characters": u"Change characters",
		"template_view_character_page": u"View character page",
		"template_change_character": u"Change character",
		"template_inactive_characters": u"Inactive characters",
		# manage/export
		"template_export_to_xml": u"Export to XML",
		"template_what_to_export": u"Export",
		"template_if_exporting_entries_select_range": u"in the range",
		"template_export_entries_with_answers" : u"Export to CSV",
		# manage/first
		"template_welcome_to_new": u"Welcome to your new Rakontu",
		"template_here_are_terms": u"To get you started, here is a brief explanation of some important terms.",
		"template_resources_for_new_managers": u"Here are some resources that might get you started.",
		# manage/setAvailability
		"set_rakontu_availability": u"Set Rakontu availability",
		"template_current_rakontu_availability_is": u"This Rakontu is currently available to",
		"template_everyone_else_sees_this_message": u"Everyone else sees this message when they attempt to access a Rakontu page",
		"template_set_rakontu_availability_to": u"Change the Rakontu's availability to",
		"template_edit_access_message": u"What message, if any, would you like members to see when they cannot access the Rakontu?",
		"template_see_what_the_not_available_page_looks_like": u"See what the not-available page looks like",
		# manage/members
		"template_google_email": u"Google account email",
		"template_membership_type": u"Membership type",
		"template_available": u"available",
		"template_helping_roles_taken_on": u"Helping roles taken on",
		"template_helping_roles_available": u"Helping roles available",
		"template_add_new_members": u"Add new members",
		"template_send_invitation_email": u"Send invitation email",
		"template_invitation_to_join": u"Invitation to join",
		"template_invite_as_manager": u"Invite as manager",
		# manage/invitation_message
		"template_send_an_invitation_message_to": u"Send an invitation email to",
		# manage/questions
		"template_order": u"Order",
		"template_add_new_questions_about": u"Add new questions about",
		"template_change_questions_about": u"Change questions about",
		"template_import_export_questions_about": u"Import and export questions about",
		"template_choose_csv_question_file": u"Choose a CSV file to import questions from",
		"template_export_questions_to_csv": u"Export questions to CSV",
		"template_copy_sample_questions_about": u"Copy sample questions about",
		"template_is_of_the_type": u"is of the type",
		"template_min_max_are": u"Minumum and maximum values are",
		"template_a_positive_answer_is": u"The text of a positive answer is", 
		"template_a_negative_answer_is": u"The text of a negative answer is",
		"template_choices_are": u"Choices are",
		"template_yes_multiple_answers_allowed": u"Yes, allow multiple answers",
		"template_explanation_is": u"The explanation given is", 
		"template_inactive_questions": u"Inactive questions",
		# manage/questionsList
		"template_questions_and_response_counts_about": u"Responses to questions about",
		# manage/question
		"template_help_on_using_this_question": u"Help in using this question",
		"template_min_max": u"Minimum and maximum",
		"template_if_value": u"only applies if question is of the value type",
		"template_if_boolean": u"only applies if question is of the boolean type",
		"template_if_ordinal_or_nominal": u"only applies if question is of the ordinal or nominal type",
		"template_explanation": u"Explanation",
		"template_choices": u"Choices",
		"template_multiple": u"multiple",
		"template_multiple_answers_allowed": u"Multiple answers allowed",
		"template_answer_counts_by_choice": u"How many answers have been recorded for each choice?",
		"template_answer_responses": u"Collected answers",
		"template_no_responses_to_question": u"No answers have yet been collected for this question.",
		"template_positive_response": u"Positive response",
		"template_negative_response": u"Negative response",
		# manage/hangingAnswerCounts
		"template_fix_unlinked_answers_for_question": 'Change unlinked answer choices for question', # question name
		"template_these_answer_choices_are_unlinked": u"These choices have been removed or renamed, but answers remain in the system linked to them. If you don't change those answers to another choice, they will no longer be filterable. Select another choice to remap the existing answers.",
		"template_change_all_answers_with_choice": u"Change all answers with the choice", # choice name
		# manage/appearance
		"template_visual_appearance": u"Visual appearance",
		"template_tag_line": u"Tag line",
		"template_custom_skin": u"Custom skin",
		"template_custom": u"custom",
		"template_external_style_sheet": u"Enter a valid CSS URL to use as an external style sheet",
		"template_halping_role_texts": u"Helping role texts",
		"template_welcome_message_for_new_members": u"Welcome message for new members",
		"template_invitation_message_for_invitation_email": u"Invitation message for email invitation",
		"template_time_zones_and_time_reporting": u"Time zones and time reporting",
		"template_what_time_zone_should_members_see": u"What time zone should members see as the default?",
		"template_how_should_dates_display": u"How should dates be displayed by default?",
		"template_how_should_times_display": u"How should times be displayed by default?",
		"template_read_before_text": u"read-before text",
		"template_discussion_group_url": u"Discussion group link",
		# manage/settings
		"template_things_members_can_do": u"Things members can do",
		
		"template_accept_non_invited_members": u"Are visitors allowed to join without being explicitly invited?", # << TRANSLATION REQUIRED >>
		"template_yes_rakontu_accepts_non_invited_members": u"Yes, visitors can join by clicking on a link",  # << TRANSLATION REQUIRED >>
		"template_show_start_icon_for_non_invited_members": u"If non-invited visitors can join, does the icon show on the site start page?",  # << TRANSLATION REQUIRED >>
		"template_yes_show_start_icon": u"Yes, show the Rakontu icon on the start page for non-member visitors", # << TRANSLATION REQUIRED >>
		"template_use_email_as_new_member_nickname": u"Should new member nicknames default to emails?", # << TRANSLATION REQUIRED >>
		"template_yes_use_email_as_new_member_nickname": u"Yes, use emails for new member nicknames", # << TRANSLATION REQUIRED >>
		
		"template_how_many_attachments": u"How many attachments are allowed per entry?",
		"template_fictional_characters": u"Fictional characters",
		"template_is_entry_by_character_allowed": u"Is entry via fictional character allowed for each of these entry types?",
		"template_editing": u"Editing",
		"template_non_managers_editing_tags": u"Should curators who are not managers be able to edit existing tags?",
		"template_yes_non_manager_curators_can_edit_tags": u"Yes, curators who are not managers can edit all tags",
		"template_activity_system": u"Activity system",
		"template_activity_points_per_activity": u"How many activity points are added to an item based on each activity?",
		"template_nudge_system": u"Nudge system",
		"template_nudge_points_per_entry": u"How many nudge points can be asssigned (maximum) per entry?",
		"template_nudge_category_names_and_questions": u"What should the names and questions of nudge categories be?",
		"template_how_many_nudge_points_do_member_get": u"How many nudge points do members accumulate by participating in the Rakontu?",
		# visit/annotation
		"template_enter_tags": u"Please enter some tags that describe this entry.",
		"template_comment_on": u"Comment on",
		"template_tag_set_for": u"Tag set for",
		"template_request_about": u"Request about",
		"template_nudge_for": u"Nudge for",
		"template_what_is_request_type": u"What type of request is this?",
		"template_nudge_points_can_assign_to_entry": u"Points you can assign to this entry",
		"template_nudge_points_member_has_left": u"Points you have remaining",
		# visit/ask
		"template_ask_this_guide": u"Ask a guide",
		"template_ask_subject": u"Please summarize your question in a few words for the email subject line.",
		"template_ask_body": u"What question would you like to ask?",
		"template_ask_question_your_own_real_email_warning": u"Warning: The Google App Engine only allows Rakontu to send an email if it uses the real email you have associated with your Google account. That means the guide you are sending this question to will see your email address. If you don't want them to see it, don't send the question.",
		# visit/character
		"template_about": u"About",
		"template_how_to_be_character": u"How to be",
		"template_see_all_characters": u"See all characters",
		"template_change_this_character": u"Change this character",
		"template_curate_this_characters_entries": u"Curate this character's contributions",
		"template_no_character_description": u"no character description",
		"template_no_character_how_to": u"no how-to statement",
		"template_no_entries_or_annotations_for_character": u"No entries or annotations match the current selections for this character.",
		# visit/drafts
		"template_name_and_information_click_to_edit": u"Name and information (click to edit)",
		"template_versions_click_to_use": u"Previous versions (click to revert)",
		"template_your_saved_drafts": u"Your saved drafts",
		"template_saved_drafts_for": u"Saved drafts for",
		"template_versions": u"History",
		"template_add_or_change_editors": u"Add or change editors",
		"template_additional_editors": u"Additional editors",
		"template_other_peoples_drafts_you_can_edit": u"Draft entries on which you are an additional editor",
		"template_add_attachments": u"Add an attachment",
		"template_change_attachments": u"Change attachments",
		# visit/editors
		"template_change_additional_editors": u"Add or change editors of ", # the entry name
		"template_who_can_edit_this_entry": u"Besides yourself, who can change this", # story, etc
		"template_can_edit": u"Can change this entry",
		# visit/entry
		"template_restoring_version_from": u"Reverting to version from",
		"template_tell_new_story": u"Please tell your story here.",
		"template_describe_new_pattern": u"Please describe the pattern of stories you want to make note of here.",
		"template_describe_new_collage": u"Please describe your collage here.",
		"template_describe_new_invitation": u"Please describe to other members what you would like them to tell stories about.",
		"template_text_for_new_resource": u"Type the text of your resource here.",
		"template_please_give_name_to_your": u"Please provide a descriptive name for your",
		"template_since_you_retold": u"Since you created this story as your own version of",
		"template_since_you_reminded": u"Since you created this story because you were reminded of it by",
		"template_since_you_responded": u"Since you created this story in response to the invitation",
		"template_comment_on_retold_link": u"Would you like to comment on why you retold the original story?",
		"template_comment_on_reminded_link": u"Would you like to comment on what reminded you of this story?",
		"template_comment_on_responded_link": u"Would you like to comment on why you responded to the invitation?",
		"template_since_this_is_a_resource": u"Since this is a resource",
		"template_which_resource_options_apply": u"Which of these display options apply?",
		"template_yes_is_help_resource": u"This is a help resource. Link to it from the general help page.",
		"template_yes_is_new_member_resource":"This resource will be helpful to new members. Link to it from the page new members see.",
		"template_yes_manager_only_resource": u"This resource is only appropriate for managers. Hide it from other members.",
		"template_what_category_should_this_resource_be_in": u"If this is a help or new-members resource, in which category should it be displayed?",
		"template_or_enter_a_new_category_here": u"or enter a new category here",
		"template_load_version": u"Revert to text version",
		"template_stories_included_in_collage": u"Stories included in this collage",
		"template_link_comment": u"Link comment",
		"template_add_stories_to_the_collage": u"Add stories to the collage",
		"template_no_stories_to_add_to_collage": u"No stories are available to add to this collage.",
		"template_filters_referred_to_by_this_pattern": u"Filters referred to by this pattern",
		"template_add_filters_to_the_pattern": u"Add filters to the pattern",
		"template_no_shared_filters_available": u"There are no shared filters available.",
		"template_accepted_file_types": u"Accepted file types",
		"template_add_attachments_to_entry": u"You can add some attachments to your", # story, etc
		"template_change_attachments": u"These attachments have been added to the", # story, etc
		# visit/attachments
		"template_add_attachment": u"Add an attachment",
		"template_add_another_attachment": u"Add another attachment",
		"template_change_attachments": u"Change attachments",
		"template_change_attachments_for": u"Change attachments for", # entry name
		"template_no_attachments_for_entry": u"This entry has no attachments attached to it.",
		"template_cannot_add_more_attachments": u"This entry has the maximum number of attachments allowed for this Rakontu. You cannot add any more attachments to it unless you remove some.",
		# visit/attachment
		"template_add_attachment_to": u"Add an attachment to", # entry name
		"template_what_name_for_attachment": u"What name would you like to use to refer to the attachment?",
		"template_click_browse_to_choose_file": u"Click the Browse button to choose a file to upload.",
		# visit/filter
		"template_filter_name_and_comment": u"Filter name and comment",
		"template_filter_should_be_shared": u"Should this filter be shared?",
		"template_keep_filter_private": u"No, keep it private",
		"template_share_filter": u"Yes, share it",
		"template_filter_selections": u"Filter selections",
		"template_of_these_selection_criteria": u"of the following selection criteria",
		"template_of_these_words_or_phrases": u"of these words of phrases",
		"template_of_these_tags": u"of these tags",
		"template_of_these_answers_to_questions_about_entries": u"of these answers to questions about entries",
		"template_of_these_answers_to_questions_about_creators_of_entries": u"of these answers about creators of entries",
		# visit/filters
		"template_saved_filters": u"Saved filters",
		"template_apply_to_home_page": u"Apply to home page",
		"template_questions_about_entries": u"Questions about entries",
		"template_questions_about_members_or_characters": u"Questions about members or characters",
		# visit/find
		"template_find": u"Find",
		"template_include_help_resources": u"Include help resources",
		"template_matching_entries_for": u"Matching entries for",
		"template_sorted_by_relevance": u"sorted by relevance",
		"template_no_entries_match_search": u"No entries match",
		"template_matching_annotations_answers_and_links": u"Matching annotations, answers and links for",
		"template_no_annotations_answers_or_links_match_search": u"No annotations, answers or links match",
		# visit/help
		"template_help_resources": u"Help! Read about using Rakontu",
		"template_ask_a_guide": u"Help! Ask a guide about your Rakontu",
		"template_no_resources_manager": u"Alert: No help resources have been created for this Rakontu. As a manager, you should make sure that your Rakontu members have at least a few resources they can read to learn how to use the site.",
		"template_no_resources_non_manager": u"No help resources have yet been created for this Rakontu. Please ask a Rakontu manager for help.",
		"template_generate_default_resources": u"Generate site-default help resources for this Rakontu",
		"template_create_a_resource": u"Create a help resource",
		"template_no_system_resources": u"There should be some default help resources you can use in your Rakontu, but apparently the site administrator has not yet set them up. Contact your site administrator for help:",
		"template_support_for_rakontu": u"Support request for Rakontu ",
		"template_support": u"Support request",
		"template_site_support": u"Site support",
		"template_guide_has_not_entered_intro": u"This guide has not yet specified which sorts of questions they can answer.",
		"template_show_new_member_page": u"Visit the new-member page",
		"template_show_new_manager_page": u"Visit the new-manager page",
		# visit/home
		"template_time_range": u"Time range",
		"template_to_time": u"to", # between two parts of time range
		"template_keep_end_time_at_now": u"Ending now",
		"template_show": u"Show",
		"template_entry_types": u"Entry types",
		"template_annotation_types": u"Annotation types",
		"template_filtered_by": u"Filtered by",
		"template_choose_one": u"choose one",
		"template_my_filters": u"My filters",
		"template_shared_filters": u"Shared filters",
		"template_other_options": u"Other options",
		"template_nudge_floor": u"Hide items nudged below",
		# visit/home_grid
		"template_no_filter_results_header": u"No filter results",
		"template_no_filter_results_message": u"The applied filter resulted in no entries being shown. To see entries in this space, either stop applying the filter or change it so that some entries meet the filter criteria.",
		"template_no_matches_header": u"No matching entries",
		"template_no_match_for_selections": u"No entries match the current selections.",
		"template_empty_rakontu_header": u"Nothing here yet!",
		"template_empty_rakontu_message": u"This Rakontu has no entries in it. Use the Create menu to add the first story or invitation.",
		# visit/leave
		"template_are_you_sure": u"Are you sure?",
		"template_leaving_warning": u"Are you absolutely, completely, really, totally certain that you want to leave this Rakontu? If you do, you may have to ask a manager of the Rakontu if you want to rejoin.",
		# visit/member
		"template_information_about": u"Information about",
		"template_information_about_this": u"Information about this",
		"template_counts_of_items_contributed_by": u"Counts of items contributed by", # member nickname
		"template_last_entry": u"Last entry",
		"template_last_annotation": u"Last annotation",
		"template_last_answer": u"Last answer",
		"template_last_link": u"Last link",
		"template_last_reading": u"Last reading",
		"template_nudge_points_accumulated": u"Nudge points accumulated",
		"template_member_answers_to_questions": u"Answers to member questions",
		"template_send_a_message_to": u"Send a message to",
		"template_change_your_preferences": u"Change your preferences",
		"template_curate_this_members_entries": u"Curate this member's contributions",
		"template_curate_your_entries": u"Curate your contributions",
		"template_stop_curating": u"Stop curating",
		"template_no_entries_or_annotations_for_member": u"No entries or annotations match the current selections for this member.",
		# visit/members
		"template_make_changes_to_members": u"Make changes to memberships",
		"template_send_message": u"Send message",
		# visit/message
		"template_send_message_your_own_real_email_warning": u"Warning: The Google App Engine only allows Rakontu to send an email if it uses the real email you have associated with your Google account. That means the people you are sending this message to will see your email address. If you don't want them to see it, don't send the message.",
		# visit/new
		"template_resources_for_new_members": u"You may find these resources helpful for getting started",
		"template_about_help_icons": u"Around the site you will see little icons that provide help. Either hover over them with your mouse or click on them to read them.",
		"template_how_to_get_to_new_member_page_again": u"You can return to this page later by clicking the link at the bottom of the Help page.",
		"template_leave_rakontu_for_new_member_page": u"To cancel joining this Rakontu, click here.", # << TRANSLATION REQUIRED >>
		# visit/preview
		"template_with_reference_to_the": u"with reference to the",
		# visit/previewAnswers
		"template_answers_to_questions_about": u"Answers to questions about",
		# visit/profile
		"template_your_profile": u"Your profile",
		"template_offline_member_profile": u"Off-line member profile",
		"template_nickname_and_description": u"Nickname and description",
		"template_your_nickname_is": u"Your nickname is",
		"template_offline_members_nickname_is": u"This member's nickname is",
		"template_describe_yourself": u"Please describe yourself to other members.",
		"template_describe_offline_member": u"Please describe this off-line member to other members.",
		# visit/nickname
		"template_change_nickname": u"Change nickname",
		"template_what_nickname_do_you_want": u"What nickname would you like to use in the Rakontu?",
		"template_what_nickname_for_offline_member": u"What nickname do you want to use to represent this off-line member in the Rakontu?",
		"template_nickname_taken": u"That nickname is already being used by someone in the Rakontu. Please choose another.",
		"template_nickname_chosen_is": u"The nickname you have chosen is",
		"template_nickname_chosen_for_offline_member_is": u"The nickname you have chosen for this member is",
		"template_confirm_nickname": u"Please confirm that you want to use this nickname. (This will effect the appearance of all of your contributions, in the past as well as the future.)",
		"template_cancel_changing_nickname": u"Cancel and return to profile page",
		# visit/preferences
		"template_do_you_want_messages": u"Do you want other Rakontu members to be able to send you messages via email?",
		"template_guides_must_accept_messages": u"Since you are a guide you have to accept messages so you can answer questions.",
		"template_offline_member_accept_messages": u"Do you want other Rakontu members to be able to send this member messages via email? (You, as the member's liaison, will get the messages.)",
		"template_yes_people_can_send_me_messages": u"Yes, people can send me messages",
		"template_yes_people_can_send_messages_through_me": u"Yes, people can send this off-line member messages through me",
		"template_please_add_a_picture": u"Please upload a picture of yourself.",
		"template_please_add_a_picture_of_offline_member": u"Please upload a picture of this off-line member.",
		"template_leave_rakontu": u"I want to stop being a member of this Rakontu",
		"template_other_options": u"Other options",
		"template_helping_roles": u"Helping roles",
		"template_i_am_a": u"I am a", # if this doesn't translate you can leave it blank
		"template_guide_intro_question": u"If you are a guide, what would you like to tell members about what sorts of questions you can answer?",
		"template_choose_member_default_text_format": u"What text format should be chosen by default when a text box is shown?",
		"template_time_zone_choice": u"What time zone should be displayed?",
		"template_date_display_choice": u"How should dates be displayed",
		"template_time_display_choice": u"How should times be displayed?",
		"template_rakontu_created_on": u"This Rakontu was created on",
		"template_inline_image_display_choice": u"Do you want to see attached images on the same page as the entries they are attached to?",
		"template_details_text_length_choice": u"How many characters (letters) long would you like texts displayed in details views to be?",
		"template_view_options_on_top": u"On which of these timeline views should the options (other than the time range) be shown above the timeline?",
		"template_view_help_resources_in_timelines": u"On which of these timeline views should help resources be shown?",
		"template_show_button_tooltips": u"Should tooltips with information appear when you hover the mouse over small option buttons?",
		"template_show_button_tooltips_yes": u"Yes, show tooltips on buttons",
		# visit/rakontu
		"template_rakontu_created_on": u"This Rakontu was created on",
		"template_discussion_group": u"Discussion group",
		"template_counts_of_items_in": u"Counts of items in", # rakontu name
		"template_nudge_categories": u"Nudge categories",
		"template_nudge_point_accumulations": u"Nudge point accumulations",
		"template_activity_point_accumulations": u"Activity point accumulations",
		"template_rakontu_allows_characters_for": u"This Rakontu allows fictional character attribution for",
		# visit/read
		"template_contributed_by": u"Contributed by",
		"template_entered_by": u"entered by",
		"template_retelling_of": u"A retelling of",
		"template_retold_as": u"Retold as",
		"template_reminding_from": u"Told because of a reminding from",
		"template_reminding_to": u"Reminded someone of",
		"template_in_response_to_invitation": u"Told in response to",
		"template_included_in_collages": u"Included in the collages",
		"template_annotations_to_this": u"Annotation timeline", 
		"template_hide_versions": u"Hide", # right next to button that says History so no need for longer name
		"template_show_versions": u"Show history",
		"template_no_annotations_for_entry": u"This entry has no annotations that match the current selections.",
		"template_add_editors": u"Allow others to edit this", # story, etc
		"template_change_editors": u"Change who can edit this", # story, etc
		"template_counts_of_annotations_to": u"Counts of annotations to", # entry title
		"template_shift_by": u"Admin only: Shift times by", # this is for admin only, to prepare demos mainly
		"template_activity_points": u"Activity points",
		"template_recopy_system_resource": u"Recopy this resource from the system - overwrite any changes", # # this is for admin only, to update help resources for changes
		# visit/readAnnotation
		"template_request_type": u"Request type",
		"template_completion_status": u"Status",
		"template_change_comment": u"Change comment",
		# visit/relate
		"template_entries_related_to": u"Entries related to",
		"template_incoming_or_outgoing": u"Incoming or outgoing",
		"template_incoming": u"incoming",
		"template_outgoing": u"outgoing",
		"template_add_relations": u"Add relations",
		"template_related": u"Related",
		"template_related_to": u"Related to",
		"template_add_link": u"Add link",
		"template_entry_has_no_related_links": u"This entry has not yet been marked as related to other entries.",
		"template_no_entries_of_this_type_to_relate_to": u"There are no entries of the selected type available for this entry to relate to.",
		}

# ============================================================================================ 
# TEMPLATE BUTTON NAMES
# These are texts that appear on buttons in html forms.
# The things on the left MUST remain as they are (they match things in the template files).
# The things on the right should be translated.
# ============================================================================================ 

TEMPLATE_BUTTONS = {
		"button_change": u"Change",
		"button_cancel": u"Cancel",
		"button_save_changes": u"Save changes",
		"button_generate": u"Generate",
		"button_regenerate": u"Regenerate",
		"button_add": u"Add",
		
		# start
		"button_visit": u"Visit",
		# admin
		"button_join": u"Join",
		"button_switch": u"Switch",
		"button_leave": u"Leave",
		"button_remove": u"Remove",
		"button_enter_short_name": u"Enter Short Name",
		"button_create_rakontu": u"Create the New Rakontu",
		"button_confirm_removal": u"Permanently Remove Rakontu",
		# curate
		"button_make_selected_changes": u"Make selected changes",
		"button_send_selected_notifications": u"Unflag items and send selected notifications",
		"button_change_tags": u"Change tags",
		# guide
		"button_show_uncompleted_requests": u"Show only uncompleted requests",
		"button_show_all_requests": u"Show all requests",
		"button_set_request_uncompleted": u"Set to NOT completed",
		"button_set_request_completed": u"Set to completed",
		# liaise
		"button_add_stories": u"Add stories",
		"button_add_a_batch_ofstories": u"Add a batch of stories",
		"button_add_more_stories": u"Add more stories",
		"button_import_or_remove_selected_stories": u"Import or remove selected stories",
		# manage
		"button_inactivate": u"Really And Truly Inactivate This Rakontu",
		"button_export_xml": u"Export to XML",
		"button_export_csv": u"Export to CSV",
		"button_send_invitation_email": u"Send invitation email",
		# visit
		# timelines
		"button_change_time_range_view": u"Change timeline view",
		"button_change_entry_types_view": u"Change entry types view",
		"button_change_annotation_types_view": u"Change annotation types view",
		"button_change_nudge_view": u"Change nudges view",
		"button_hide_details": u"Hide details",
		"button_show_details": u"Show details",
		"button_hide_activity_levels": u"Hide activity levels",
		"button_show_activity_levels": u"Show activity levels",
		"button_search": "Search",
		# entering things
		"button_save_changes_and_return": u"Save changes and return",
		"button_preview": u"Preview",
		"button_save_draft": u"Save draft",
		"button_unpublish": u"Unpublish (make into draft)",
		"button_save_as_draft": u"Save as draft",
		"button_save_attachment": u"Save attachment",
		"button_edit_draft": u"Edit draft",
		"button_view_all_drafts": u"View all drafts",
		"button_change_entry": u"Change entry",
		"button_publish": u"Publish",
		"button_remove_selected_drafts": u"Remove selected drafts and versions",
		"button_save_and_apply": u"Save and apply",
		"button_save_and_apply_to_member": u"Save and apply to member page",
		"button_save_and_apply_to_character": u"Save and apply to character page",
		"button_save_and_apply_to_home_page": u"Save and apply to home page",
		"button_save_as_new_filter_and_apply_to_member": u"Save as new copy and apply to member page",
		"button_save_as_new_filter_and_apply_to_character": u"Save as new copy and apply to character page",
		"button_save_as_new_filter_and_apply_to_home_page": u"Save as new copy and apply to home page",
		# helping roles
		"button_curate": u"Curate",
		"button_stop_curating": u"Stop curating",
		"button_flag": u"Flag",
		"button_unflag": u"Unflag",
		"button_delete": u"Delete",
		"button_remove_selected_filters": u"Remove selected filters",
		"button_send_question": u"Send question",
		"button_compose_message": u"Compose message to selected members",
		"button_send_message": u"Send message",
		"button_send_messages": u"Send message to selected members",
		"button_send_invitation": u"Send invitation",
		"button_refresh": u"Refresh",
		"button_stop_applying": u"Stop applying",
		"button_make_copy": u"Make a copy",
		"button_create_another": u"Make another",
		"button_apply": u"Apply",
		"button_make_new": u"Make new",
		"button_make_new_filter": u"Make new filter",
		"button_print_selection": u"Print selection",
		"button_export_selection": u"Export selection",
		"button_really_and_truly_leave": u"Really and Truly Leave this Rakontu",
		"button_go_back_to_prefs_page": u"Go Back to My Preferences Page",
		"button_return_to_list": u"Return to list",
		"button_mark_as_completed": u"Mark as completed",
		"button_mark_as_not_completed": u"Mark as not completed",
		"button_save_new_relations": u"Save new relations",
		"button_load_version": u"Revert to version",
		"button_enter_new_nickname": u"Enter New Nickname",
		}

# ============================================================================================ 
# TEMPLATE MENU NAMES
# These determine what appears on the menu that appears at the top of all pages.
# The things on the left MUST remain as they are (they match things in the template files).
# The things on the right should be translated.
# ============================================================================================ 

TEMPLATE_MENUS = {
		# visit
		"menu_visit": u"Visit",
		"menu_home_page": u"Home page",
		"menu_about_this_rakontu": u"About this Rakontu",
		"menu_about_rakontu_members": u"About the members",
		# create
		"menu_create": u"Create",
		"menu_story": u"Tell a story",
		"menu_invitation": u"Invite people to tell stories",
		"menu_collage": u"Build a story collage",
		"menu_pattern": u"Describe a pattern",
		# curate
		"menu_curate": u"Curate",
		"menu_gaps": u"Gaps",
		"menu_flags": u"Flags",
		"menu_attachments": u"Attachments",
		"menu_tags": u"Tags",
		# guide
		"menu_guide": u"Guide",
		"menu_invitations": u"Invitations",
		"menu_requests": u"Requests",
		"menu_resources": u"Resources",
		"menu_resource": u"Add a resource",
		# liaise
		"menu_liaise": u"Liaise",
		"menu_manage_offline_members": u"Manage off-line members",
		"menu_add_batch": u"Add a batch of stories",
		"menu_review_batches": u"Review entered batches",
		# manage
		"menu_manage": u"Manage",
		"menu_members": u"Members",
		"menu_appearance": u"Appearance",
		"menu_settings": u"Settings",
		"menu_questions": u"Questions",
		"menu_characters": u"Characters",
		"menu_export": u"Export",
		"menu_set_availability": u"Availability",
		# my stuff
		"menu_my_stuff": u"My stuff",
		"menu_profile": u"Profile",
		"menu_preferences": u"Preferences",
		"menu_filters": u"Filters",
		"menu_drafts": u"Drafts",
		"menu_search": u"Simple search",
		"menu_help": u"Help",
		# this appears when site admin is looking ABOVE the Rakontu level
		"menu_site_administration": u"Rakontu site administration",
		}

# ============================================================================================ 
# RESULTS
# These run the page that appears when the system has something (a result) to tell the user, like "I can't find that member."
# There are three sections to each line:
#	"internal name": (u"URL lookup", u"text presented to user"),
# DO NOT change the internal name. 
# You can translate the URL lookup (which appears in the page URL), 
# but if you do that you must also change the lookup name in the file "result.html" in the templates directory.
# The user-presented text should be translated.
# ============================================================================================ 

RESULTS = {
		"messagesent": (u"messagesent", u"Your message has been sent."),
		"memberNotFound": (u"memberNotFound", u"That member was not found."),
		"membersNotFound": (u"membersNotFound", u"None of the specified members were found."),
		"couldNotSendMessage": (u"couldNotSendMessage", u"Could not send the requested email message. Please check the sender and recipient addresses or ask your site administrator for help."),
		"offlineMemberNotFound": (u"offlineMemberNotFound", u"That off-line member was not found."),
		"helpNotFound": (u"helpNotFound", u"No help message was found for that item. You may want to let your site administrator know there is a problem."),
		"noEntriesToRelate": (u"noEntriesToRelate", u"There are no entries of the selected type to which this entry can be related."),
		"noQuestionsToExport": (u"noQuestionsToExport", u" are no questions of that type to export."),
		"offlineMemberAlreadyAnsweredQuestions": (u"offlineMemberAlreadyAnsweredQuestions", u"That off-line member has already answered questions about this entry."),
		"nicknameAlreadyInUse": (u"nicknameAlreadyInUse", u"That nickname is already in use. Please choose another."),
		"ownerCannotLeave": (u"ownerCannotLeave", u"You are the only owner of this Rakontu. You can't leave it until you designate at least one other member as an owner."),
		"cannotGiveUpLiaisonWithMembers": (u"cannotGiveUpLiaisonWithMembers", u"You cannot stop being a liaison with off-line members assigned to you. Visit the Manage off-line members page and assign your off-line members to other liaisons first."),
		"reachedMaxEntriesPerRakontu": (u"reachedMaxEntriesPerRakontu", u"This Rakontu already has the maximum allowed number of entries in it, and no more can be added. To add new entries, ask a manager to remove some older entries and free up some room."),
		}

# ============================================================================================ 
# BLURBS
# These are longer blurbs that appear in various places:
# on the start page of the Rakontu site,
# on the inactivate page,
# on the first pages that new users see.
# The first part of each pair is a lookup string - don't change that.
# The second part (in the triple quotes) is what to show the user. That should be translated.
# ============================================================================================ 

BLURBS = {
"logged in": 
	u"""
	<p><b>What's a Rakontu?</b></p>
	<p>It's a place where people share and use stories together.</p>
	<p>You could see it as a living-history museum of stories, as well as
	a gathering place where people build their story museum together 
	and draw from it to remember the past, understand the present
	and find solutions for the future.</p>
	<p>For more information, visit <a href="http://www.rakontu.org">rakontu.org</a>.
	</p>
	""",
"not logged in": 
	u"""
	<p><b>What's Rakontu?</b></p>
	<p>Rakontu is an open source software package that helps groups of people share and work 
	with stories. You can find out more about it at <a href="http://www.rakontu.org">rakontu.org</a>.
	<p>Rakontu is currently being beta tested.
	If you want to create or join a beta testing group, join the 
	<a href="http://groups.google.com/group/rakontu-discuss">Rakontu discussion group</a>.</p.
	<p>(If you're wondering: Rakontu is <a href="http://en.wikipedia.org/wiki/Esperanto">Esperanto</a> for "tell a story.")</p>
	""",
"member_new":
	u"""
	<p>
	The most important thing you do in a Rakontu is, of course, is <b>tell stories</b>. 
	But you can do other things as well: <b>invite</b> other people to tell stories about
	particular subjects; <b>filter</b> for stories and find <b>patterns</b> in them;
	build story <b>collages</b>; and make <b>comments</b> and other annotations 
	to the stories you read.
	</p>
	<hr>
	<p>The best way to get started in your Rakontu is to start <b>reading</b> the stories others have already
	told. To do that, choose Visit - <b>Home page</b>, or just click on the picture in the upper-left hand corner
	of the page. Stories are shown in a <b>timeline</b> from left to right. Click on a story <b>title</b> to read it.
	If there aren't any stories yet, why not tell the first one! Choose Create - <b>Tell a story</b>.</p>
	<hr>
	<p>You might also like to change your <b>nickname</b> to something nicer,
	and you can add a picture and some details about yourself, if you like. Choose My stuff - <b>Profile</b> 
	to do that.
	</p>
	<hr>
	<p>You can participate in your Rakontu as a regular <b>member</b>; but if you like, you can <b>volunteer</b> to take on
	any of three <b>roles</b> that will help your Rakontu become more useful to everyone in it.</p>
	<ol>
	<li><b>Curators</b> watch over the stories. They locate and fix problems in the story "museum."</li>
	<li><b>Guides</b> watch over the people. They help new members get started and answer questions.</li>
	<li><b>Liaisons</b> bridge worlds. They help people who don't use computers to participate in the Rakontu by entering
	their stories and reading them stories others have told.</li>
	</ol>
	<p>To take on any of these roles, choose My stuff - <b>Preferences</b>, check the appropriate box, and
	click Save changes. New menus will appear for each role.</p>
	<hr>
	<p>One more thing: around the site you will see little icons that provide help. Either hover over them with your mouse or click on them
	to read a bit of help about the area in which they appear.
	<i>If you do not see any icons below, your site administrator has not yet generated the help system. Contact them for help.</i></p>
	""",
"manager_first": 
	u"""
	<p>
	The most important thing in a Rakontu is, of course, its <b>stories</b>. 
	But there are four other types of <b>entry</b> as well: <b>invitations</b> to tell stories,
	story <b>collages</b>, <b>patterns</b> people have observed in the stories, and <b>resources</b> that help
	people remember and understand.
	All of these things can be commented on, given descriptive tags, rated, asked questions about, and filtered. 
	</p>
	<hr>
	<p>Many of the people in your Rakontu will participate as regular members.
	However, there are three "helper" roles people can volunteer to take on to help the Rakontu become more useful to everyone.
	<ol>
	<li><b>Curators</b> watch over the stories. They locate and fix problems in your story "museum."</li>
	<li><b>Guides</b> watch over the people. They help new members get started and answer questions.</li>
	<li><b>Liaisons</b> bridge worlds. They help people who don't use computers to participate in the Rakontu by entering
	their stories and reading them stories others have told.</li>
	</ol>
	<p>Of course there are also <b>managers</b>, who make the decisions. You, as the group's first owner, are also its first manager.
	Note that you have to "become" a curator, guide or liaison to access those special pages (even though you are a manager).
	Visit your preferences page to do that.
	<hr>
	<p>The best way to get started with your new site is to simply go down the items in the "Manage" menu (at the top of the page)
		clicking on each one, and look at all the options you see there. Then start
		asking some people to join you; then ask them to tell stories, and tell some stories yourself!
	</p>
	<hr>
	<p>One more thing: around the site you will see little icons that provide help. Either hover over them with your mouse or click on them
	to read a bit of help about the area in which they appear.
	<i>If you do not see any icons below, your site administrator has not yet generated the help system. Contact them for help.</i></p>
	""",
"no_filters":
	u"""
	<h2>No saved filters</h2>
	<p>You have no saved filters. Filters are selections that reduce the items showing in the timelines on the 
	home page or on member or character pages. For example, you might want to see only items with the word "planning" in them, or 
	whose answer to the question "Why was this story told?" is "to persuade." To create a filter, go to the home 
	page (Visit-Home page) and click "Make new filter" in the options shown.</p>
	""",
"no_drafts":
	u"""
	<h2>No drafts</h2>
	<p>You have no saved drafts. Drafts are entries (stories, invitations, collages, patterns, resources) 
	that you are working on and that nobody but you can see. To save a draft, create a story (or other entry) 
	and click "Save draft" instead of "Publish." You can then review them on this page.
	</p>
	<p>Other people can also invite you to edit their entries. If they do so, you will see those drafts on this
	page as well.</p>
	""",
"cannot_enter_batch":
	u"""
	<h2>Cannot add batch stories: no off-line members</h2>
	<p>You cannot add stories in batches because you have no off-line members assigned to you. 
	To add a batch of stories, choose Liaise - Manage off-line members and either create new off-line members
	or transfer them to you (as their liaison). Once you do that you can return here and add batches of stories for them.
	</p>
	""",
"no_entry_batches":
	u"""
	<h2>No story batches to review</h2>
	<p>There are no batches of stories to review. Batch story entry is a two-step process. 
	First you choose Liaise - Add a batch of stories and fill out the batch-story-entry form. 
	After that you come to this screen to review the entries you are about to add to the Rakontu. This two-step process is to give
	you an opportunity to make changes to stories before you import them to the Rakontu.
	To add some stories, first make sure you have some off-line members assigned to you,
	then add a batch of stories, then come back here to review the stories and import them to the Rakontu.
	</p>
	""",
}

# ============================================================================================ 
# PAGE TITLES
# These show at the top of pages. Things in comments are things that follow after the specified words.
# ============================================================================================ 

TITLES = {
       # visiting
        "ANSWERS_FOR": u"Answers for", # entry name
        "PREVIEW_OF": u"Preview of", # entry name
        "ADDITIONAL_EDITORS_FOR": u"Additional editors for", # entry name
        "RELATE_TO": u"Relate to", # entry name
        "ADD_ATTACHMENT_TO": u"Add attachment to", # entry name
        "FIND_ENTRY": u"Find entry in", # rakontu name
 		"HELP": u"Help",
		"HOME": u"Home",
		"ABOUT": u"About",
		"MEMBERS": u"Members" ,
		"MEMBER": u"Member", # member nickname
		"GUIDE": u"Guide", # member nickname
		"CHARACTER": u"Character", # character name
		"PREFERENCES_FOR": u"Preferences for", # member nickname
		"PROFILE_FOR": u"Profile for", # member nickname
		"CHANGE_NICKNAME_FOR": u"Change nickname for", # member nickname
		"DRAFTS_FOR": u"Drafts for", # member nickname
		"SEND_MESSAGE": u"Send message",
		"LEAVE_RAKONTU": u"Leave" ,
		"SEARCH_FILTER": u"Filter",
		"MESSAGE_TO_USER": u"Message", # (on page that tells user something is completed or something is wrong)
		"HELP_ON": u"Help on", # help topic
        # helping roles
        "ATTACHMENTS_TO": u"Attachments for", # entry name
        "REVIEW_FLAGS": u"Review flags",
        "REVIEW_GAPS": u"Review gaps",
        "REVIEW_ATTACHMENTS": u"Review attachments",
        "REVIEW_TAGS": u"Review tags",
        "REVIEW_RESOURCES": u"Review resources",
        "REVIEW_REQUESTS": u"Review requests",
        "REVIEW_INVITATIONS": u"Review invitations",
        "REVIEW_OFFLINE_MEMBERS": u"Review off-line members",
        "REVIEW_BATCH_ENTRIES": u"Review batch entries",
        "BATCH_ENTRY": u"Batch entry",
        "WELCOME": u"Welcome",
        # managing
        "MANAGE_MEMBERS": u"Manage members" ,
        "MANAGE_APPEARANCE": u"Manage appearance",
        "MANAGE_SETTINGS": u"Manage settings" ,
        "MANAGE_QUESTIONS": u"Manage questions" ,
        "MANAGE_QUESTION": u"Manage question", # question name
        "FIX_HANGING_ANSWERS_FOR": u"Change hanging answers for", # question name
        "MANAGE_QUESTIONS_ABOUT": u"Manage questions about", # thing referred to
        "MANAGE_CHARACTERS": u"Manage characters",
        "MANAGE_CHARACTER": u"Manage character", # character name
        "EXPORT_DATA": u"Export data" ,
        "SET_RAKONTU_AVAILABILITY": u"Set availability of", # rakontu name
 		 # admin
        "REVIEW_RAKONTUS": u"All Rakontus",
        "CREATE_RAKONTU": u"Create Rakontu",
 		"CONFIRM_REMOVE_RAKONTU": u"Confirm removal of", # rakontu name
        # errors
        "ERROR": u"Error",
        "URL_NOT_FOUND": u"URL not found",
        "DATABASE_ERROR": u"Google database temporarily unreachable",
        "ROLE_NOT_FOUND": u"Required role missing",
        "NO_RAKONTU": u"Rakontu not found",
		"NO_MEMBER": u"Rakontu member not found",
		"RAKONTU_NOT_AVAILABLE": u"Rakontu temporarily unavailable",
        "MANAGERS_ONLY": u"For managers only",
        "OWNERS_ONLY": u"For Rakontu owners only",
        "ADMIN_ONLY": u"For site administrators only",
        "TRANSACTION_FAILED_ERROR": u"Transaction failed",
        "ATTACHMENT_TOO_LARGE_ERROR": u"Attachment too large",
        "ATTACHMENT_WRONG_TYPE_ERROR": u"Attachment is of the wrong type",
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
	"dir_visit": u"visit",
	"dir_manage": u"manage",
	"dir_curate": u"curate",
	"dir_guide": u"guide",
	"dir_liaise": u"liaise",
	"dir_admin": u"admin",
	}

# Special home page - used often
HOME = u"/visit/home"

URLS = {
	# visit
	"url_home": u"home",
    "url_new": u"new",
    "url_entry": u"entry",
    "url_attachment": u"attachment",
    "url_annotation": u"annotation",
    "url_preview": u"preview",
    "url_drafts": u"drafts",
    "url_read": u"read",
    "url_read_annotation": u"readAnnotation",
    "url_preview_answers": u"previewAnswers",
    "url_answers": u"answers", 
    "url_profile": u"profile",
    "url_preferences": u"preferences",
    "url_filter": u"filter",
    "url_member": u"member",
    "url_ask": u"ask",
    "url_rakontu": u"rakontu",
    "url_find": u"find",
    "url_leave": u"leave",
    "url_filters": u"filters",
    "url_nickname": u"nickname",
    "url_message": u"message",
    "url_counts": u"counts",
    "url_editors": u"editors",
	# link creating 
    "url_retell": u"retell",
    "url_remind": u"remind",
    "url_respond": u"respond",
    "url_relate": u"relate",
	# guide
    "url_resources": u"resources",
    "url_requests": u"requests",
    "url_invitations": u"invitations",
    "url_batch": u"batch",
    "url_copy_resources": u"copySystemResourcesToRakontu",
	# liaise
    "url_print_filter": u"printFilteredItems",
    "url_print_entry": u"printEntryAndAnnotations",
    "url_print_member": u"printMemberContributions",
    "url_print_character": u"printCharacterContributions",
    "url_review": u"review",
	# curate
    "url_curate": u"curate",
    "url_flag": u"flag",
    "url_flags": u"flags",
    "url_gaps": u"gaps",
    "url_attachments": u"attachments",
    "url_tags": u"tags",
	# manage
    "url_first": u"first",
    "url_members": u"members",
    "url_questions_list": u"questionsList",
    "url_questions": u"questions",
    "url_question": u"question",
    "url_unlinked_answers": u"hanging_answers",
    "url_questions_to_csv": u"questionsToCSV",
    "url_characters": u"characters",
    "url_character": u"character",
    "url_appearance": u"appearance",
    "url_settings": u"settings",
    "url_export_filter": u"exportFilteredItems",
    "url_inactivate": u"inactivate",
    "url_invitation_message": u"invitation_message",
    "url_availability": u"availability",
	# admin 
	"url_create1": u"create1",
	"url_create2": u"create2",
    "url_export": u"export",
    "url_admin": u"admin",
    "url_sample_questions": u"sampleQuestions",
    "url_default_resources": u"defaultResources",
    "url_helps": u"helps",
    "url_skins": u"skins",
    "url_confirm_remove_rakontu": u"confirmRemoval",
    "url_recopy_system_resource": u"recopyResource", # << TRANSLATION REQUIRED >>
    # testing
    "url_make_fake_data": u"makeFakeData",
    "url_stress_test": u"stressTest",
	# general
    "url_help": u"help",
    "url_result": u"result",
    "url_image": u"img",
    "url_attachment": u"attachment",
    # errors
    "url_not_found": u"urlNotFound",
    "url_role_not_found": u"roleNotFound",
    "url_no_member": u"memberNotFound",
    "url_no_rakontu": u"rakontuNotFound",
    "url_rakontu_not_available": u"notAvailable",
    "url_managers_only": u"managersOnly",
    "url_owners_only": u"ownersOnly",
    "url_admin_only": u"adminOnly",
    "url_database_error": u"databaseError",
    "url_attachment_too_large": u"attachmentTooLarge",
    "url_transaction_failed": u"transactionFailed",
    "url_attachment_wrong_type": u"attachmentWrongType",
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
	"url_query_rakontu": u"rakontu",
	"url_query_entry": u"entry",
	"url_query_attachment": u"attachment",
	"url_query_annotation": u"annotation",
	"url_query_version": u"version",
	"url_query_member": u"member",
	"url_query_character": u"character",
	"url_query_filter": u"filter",
	"url_query_attachment": u"attachment",
	"url_query_export_csv": u"csv",
	"url_query_export_txt": u"txt",
	"url_query_export_xml": u"xml",
	"url_query_question": u"question",
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
	"url_query_export_type": u"exporttype",
	"url_query_sort_by": u"sortby",
	"url_query_show": u"show",
	'url_query_type': u"type",
	'url_query_resource_type': u"resource_type",
	'url_query_request_type': u"request_type",
	"url_query_role": u"role",
	"url_query_location": u"location",
	"url_query_uncompleted": u"uncompleted",
	"url_query_no_responses": u"noresponses",
	"url_query_curate": u"curate",
	"url_query_versions": u"versions",
	"url_query_result": u"message",
	"url_query_help": u"help",
	"url_query_help_type": u"type",
	"url_query_bookmark": u"bookmark",
	"url_query_name_taken": u"name_taken",
	"url_query_managers_only": u"managers_only",
	}

# ============================================================================================ 
# URL OPTION NAMES
# These are the parts of URLs after the ?URL_OPTIONS=.
# The things on the left MUST stay as is, because they match strings in the source code. Don't change them!
# The things on the right can be translated.
# Because these appear in URLs they cannot contain spaces or special characters.
# ============================================================================================ 

URL_OPTION_NAMES = {
	"url_option_all": u"all",
	"url_option_help": u"help",
	"url_option_new": u"new",
	"url_option_remind": u"remind",
	"url_option_managers_only": u"managers",
	"url_option_not_managers_only": u"not_managers",
	"url_option_yes": u"yes",
	}

