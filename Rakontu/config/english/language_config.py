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

# This is which skin is used by default (before a manager picks one).
# It MUST match one of the names in the skins.csv file.
DEFAULT_SKIN_NAME = "sunset"
START_CUSTOM_SKIN_NAME = "grayscale"

# ============================================================================================ 
# MEMBERS
# ============================================================================================ 

# This is what members are called before they have set themselves a nickname.
NO_NICKNAME_SET = u"No nickname set"

# This is what shows if people don't enter anything in the "Please describe yourself to other members." area.
NO_PROFILE_TEXT = u"No profile information."

# This is what shows by default in the guide introduction field.
DEFAULT_GUIDE_INTRO = u"Ask me anything."

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
LINK_TYPES_DISPLAY = ["retold from", "reminded by", "responded to", "related to", "included in", "referenced by"]

# ============================================================================================ 
# ANNOTATIONS
# ============================================================================================ 

# Types of annotation. These MUST match the order (tag set, comment, request, nudge).
ANNOTATION_TYPES_DISPLAY = ["tag set", "comment", "request", "nudge"]
# Same thing but plural
ANNOTATION_TYPES_PLURAL_DISPLAY = ["tag sets", "comments", "requests", "nudges"]
# URLs for annotation types. These MUST match the order (tag set, comment, request, nudge).
# Since they will be used for URLs they CANNOT contain special characters or spaces.
ANNOTATION_TYPES_URLS = ["tagset", "comment", "request", "nudge"]

# These need translation because they appear in selections to view in  member/character pages.
ANNOTATION_ANSWER_LINK_TYPES_DISPLAY = ["tag set", "comment", "request", "nudge", "answer", "link"]
ANNOTATION_ANSWER_LINK_TYPES_PLURAL_DISPLAY = ["tag sets", "comments", "requests", "nudges", "answers", "links"]

# List of entry AND annotation types. 
# Used in manage/settings where they are choosing which items can have character attribution.
# These MUST match the order (story, pattern, collage, invitation, resource, answer, tagset, comment, request, nudge).
ENTRY_AND_ANNOTATION_TYPES_DISPLAY = ["story", "pattern", "collage", "invitation", "resource", "answer", "tag set", "comment", "request", "nudge"]
# Same thing but plural
ENTRY_AND_ANNOTATION_TYPES_PLURAL_DISPLAY = ["stories", "patterns", "collages", "invitations", "resources", "answers", "tag sets", "comments", "requests", "nudges"]
# URLs for entry and annotation types. 
# These MUST match the order (story, pattern, collage, invitation, resource, answer, tagset, comment, request, nudge).
# Since they will be used for URLs they CANNOT contain special characters or spaces.
ENTRY_AND_ANNOTATION_TYPES_URLS = ["story", "pattern", "collage", "invitation", "resource", "answer", "tagset", "comment", "request", "nudge"]

# These are types of request people can set. They can be set to anything you like (and translated).
# Everyone can see them, and guides have a "review requests" page where they see all requests by type.
# CAUTION: The last type in this list should always be "other" or some other no-category name.
REQUEST_TYPES = ["comment on", "tag", "answer questions about", "curate", "link", "tell your version", "transcribe", "read aloud", "translate", "other"]
# The same as above but without spaces or special characters (to be used in URLs). MUST match above list in order.
REQUEST_TYPES_URLS = ["comment", "tag", "answer", "curate", "link", "tellversion", "transcribe", "readaloud", "translate", "other"]

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
TIMEFRAME_10MINUTES = u"10 minutes" # used for testing only
TIMEFRAME_HOUR = u"an hour"
TIMEFRAME_6HOURS = u"6 hours"
TIMEFRAME_12HOURS = u"12 hours"
TIMEFRAME_DAY = u"a day"
TIMEFRAME_3DAYS = u"3 days"
TIMEFRAME_WEEK = u"a week"
TIMEFRAME_2WEEKS = u"2 weeks"
TIMEFRAME_MONTH = u"a month"

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
# These are bits of text that come out of the source code (NOT the templates) and display on pages.
# The things on the left MUST remain as they are (they match things in the source code).
# The things on the right should be translated.
# ============================================================================================ 

TERMS = {
		# used to refer to a group of answers
		"term_answer_set": "answer set",
		"term_answer": "answer",
		"term_answers": "answers",
		# used to display list of things user can do while viewing story or other entry
		"term_tell_another_version_of_this_story": "Tell another version of what happened",
		"term_tell_a_story_this_reminds_you_of": "Tell a story this reminds you of",
		"term_answer_questions_about_this": "Answer questions about this",  # story, invitation collage, pattern, or resource
		"term_respond_to_invitation": "Respond to this invitation with a story",
		"term_make_a_comment": "Comment on this",  # story, invitation collage, pattern, or resource
		"term_tag_this": "Tag this", # story, invitation collage, pattern, or resource
		"term_request_something_about_this": "Request something about this", # story, invitation collage, pattern, or resource
		"term_relate_entry_to_others": "Relate this entry to other entries",
		"term_nudge_this": "Nudge this", # story, invitation collage, pattern, or resource
		"term_curate_this": "Curate this", # story, invitation collage, pattern, or resource
		"term_stop_curating_this": "Stop curating this", # story, invitation collage, pattern, or resource
		"term_change_this": "Change your", # story, invitation collage, pattern, or resource # YOUR because only the creator can do this
		"term_print_this": "Print content and annotations for this", # story, invitation collage, pattern, or resource
		# used to send a reminder to manager about items flagged by curator
		"term_dear_manager": "Dear manager",
		"term_reminder": "Reminder about flagged items from", # person who is sending the reminder
		"term_wanted_you_to_know": "I wanted you to know that these items require your attention.",
		"term_thank_you": "Thank you for your attention.",
		"term_sincerely": "Sincerely",
		"term_your_site": "Your Rakontu site",
		"term_link": "link",
		"term_links": "links",
		"term_question": "question",
		# used to describe search filters
		"term_of_the_words": "of the words",
		"term_of_the_tags": "of the tags",
		"term_of_the_entry_questions": "of the entry questions",
		"term_of_the_creator_questions": "of the creator questions", 
		"term_of_these_answers_to_questions": "of these answers to questions",
		"term_of_these_answers_to_questions_about_members_or_characters": "of these answers to questions about their creators (members or characters)",
		"term_of_these_answers_to_questions_about_creators": "of these answers to questions about their creators",
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
		# used when printing
		"term_printed_from_rakontu": "Printed from Rakontu",
		"term_selections_for": "Selections for", # rakontu name
		# miscellaneous
		"term_does_not_apply": "doesn't apply",
		"term_copy_of": "Copy of",
		"term_none": "none",
		"term_result": "A message from Rakontu",
		"term_help": "Rakontu help",
		"term_help_info": "Information about",
		"term_help_tip": "A tip about",
		"term_help_caution": "A caution about",
		"term_entries_contributed_by": "Entries, annotations, answers and links contributed by",
		"term_yes": "yes",
		"term_no": "no",
		"term_for": "for", # annotation for entry
		"term_points": "points",
		"term_accumulations_for": "Accumulations for",
		"term_custom": "custom",
		"term_links": "links",
		"term_too_many_items_warning": "most recent items shown. To show older items, use selections to reduce the number of items showing.", # preceded by number/number
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
		"template_yes": "yes",
		"template_no": "no",
		"template_and": "and",
		"template_or": "or",
		"template_you": "you",
		"template_none": "none",
		"template_none_found": "None found",
		"template_from": "from",
		"template_to": "to",
		"template_information": "information",
		"template_tip": "tip",
		"template_caution": "caution",
		"template_welcome": "Welcome",
		"template_never": "never",
		"template_go": "go",
		"template_choose": "choose",
		
		# types of people (singular and plural)
		"template_member": "Member",
		"template_members": "Members",
		"template_online_member": "On-line member",
		"template_online_members": "On-line members",
		"template_offline_member" :"Off-line member",
		"template_offline_members": "Off-line members",
		"template_active_members": "Active members",
		"template_active_online_members": "Active on-line members",
		"template_active_offline_members": "Active off-line members",
		"template_pending_member": "Pending member",
		"template_pending_members": "Pending members",
		"template_inactive_member": "Inactive member",
		"template_inactive_members": "Inactive members",
		"template_manager": "Manager",
		"template_managers": "Managers",
		"template_owner": "Owner",
		"template_owners": "Owners",
		"template_curator": "Curator",
		"template_curators": "Curators",
		"template_guide": "Guide",
		"template_guides": "Guides",
		"template_liaison": "Liaison",
		"template_liaisons": "Liaisons",
		"template_character": "Character",
		"template_characters": "Characters",
		
		# types of things (singular and plural)
		"template_attachment": "Attachment",
		"template_attachments": "Attachments",
		"template_entry": "Entry",
		"template_entries": "Entries",
		"template_story": "Story",
		"template_stories": "Stories",
		"template_invitation": "Invitation",
		"template_invitations": "Invitations",
		"template_pattern": "Pattern",
		"template_patterns": "Patterns",
		"template_collage": "Collage",
		"template_collages": "Collages",
		"template_resource": "Resource",
		"template_resources": "Resources",
		"template_attachment": "Attachment",
		"template_attachments": "Attachments",
		"template_response": "Response",
		"template_responses": "Responses",
		"template_annotation": "Annotation",
		"template_annotations": "Annotations",
		"template_request": "Request",
		"template_requests": "Requests",
		"template_draft": "Draft",
		"template_drafts": "Drafts",
		"template_tag": "Tag",
		"template_tags": "Tags",
		"template_tag_set": "Tag set",
		"template_tag_sets": "Tag sets",
		"template_question": "Question",
		"template_questions": "Questions",
		"template_answer": "Answer",
		"template_answers": "Answers",
		"template_message": "Message",
		"template_messages": "Messages",
		"template_link": "Link",
		"template_links": "Links",
		"template_filter": "Filter",
		"template_filters": "Filters",
		"template_search_filter": "Search filter",
		"template_search_filters": "Search filters",
		"template_word": "Word",
		"template_words": "Words",
		"template_type": "Type",
		"template_types": "Types",
		"template_email": "Email",
		"template_skin": "Skin",
		"template_skins": "Skins",
		
		# things lots of objects have
		"template_linked_to": "Linked to",
		"template_name": "Name",
		"template_file": "File",
		"template_nickname": "Nickname",
		"template_description": "Description",
		"template_picture": "Picture",
		"template_image": "Image",
		"template_etiquette_statement": "Etiquette statement",
		"template_title": "Title",
		"template_content": "Content",
		"template_interpret_as": "Interpret as",
		"template_first_part_of_text": "First part of text",
		"template_contributor": "Contributor",
		"template_comment": "Comment",
		"template_subject": "Subject",
		"template_joined": "Joined",
		"template_created": "Created",
		"template_published": "Published",
		"template_last_published": "Last published",
		"template_last_changed": "Last changed",
		"template_last_generated": "Last generated",
		"template_invited": "Invited",
		"template_collected": "Collected",
		"template_active": "Active",
		"template_inactive": "Inactive",
		"template_online": "On-line",
		"template_offline": "Off-line",
		"template_private": "Private",
		"template_shared": "Shared",
		"template_new": "New",
		"template_completed": "Completed",
		"template_not_completed": "Not completed",
		"template_remove": "Remove",
		"template_year": "year",
		"template_month": "month",
		"template_day": "day",
		"template_log_out": "Log out",
		"template_help": "Help",
		"template_newer": "Newer",
		"template_older": "Older",
		
		# things the user can do (but not buttons - usually links)
		"template_create_one": "Create one",
		"template_add_some": "Add some",
		"template_activate": "Activate",
		"template_inactivate": "Inactivate",
		"template_edit_drafts": "Edit drafts",
		"template_preview": "Preview",
		"template_change": "Change",
		"template_attach": "Attach",
		"template_replace": "Replace",
		"template_attach_or_replace": "Attach or replace",
		"template_copy": "Copy",
		"template_previous": "Previous",
		"template_next": "Next",
		
		# things used in specific template files
		
		# common_attribution (template file name)
		"template_the_former_member": "the former member",
		"template_the_former_character": "the former character",
		"template_since_you_are_a_liaison": "Since you are a liaison",
		"template_collected_from_offline_member": "Was this collected from an off-line member?",
		"template_yes_collected_from": "Yes, it was collected from",
		"template_attributed_to": "It should be attributed to",
		"template_selected_member": "The selected member",
		"template_no_my_contribution": "No, this is my contribution", 
		"template_attribute_to": "I'd like to attribute it to", 
		"template_myself": "myself",
		"template_attribute_to_whom": "To whom would you like to attribute this contribution?",
		# common_footer
		"template_site_start_page": "Site start page",
		"template_site_administration": "Site administration",
		"template_google_account": "Google account",
		# common_questions
		"template_answer_questions_about_yourself": "Please answer these questions about yourself.",
		"template_answer_questions_about_member": "Please answer these questions about",
		"template_answers_to_questions_about": "Answers to questions about",
		"template_answer_questions_about": "Please answer these questions about this",
		"template_enter_number": "Please enter a number between",
		"template_no_questions": "There are no questions for this type of item.",
		# error
		"template_error": "Oops! Sorry :(",
		"template_an_error_has_occurred_and_admin_notified": "Something went wrong. The system administrator has been notified.",
		"template_error_message": "If you want to talk about this error with the administrator, copy this message and paste it into your email.",
		# help 
		"template_click_back_button": "Click the Back button to return to the page you were on.",
		"template_or_would_you_like_more": "or would you like more",
		# notFound
		"template_URL_not_found": "Oops! Can't find it!",
		"template_the_page_could_not_be_found": "We can't find the page you asked for.",
		# result
		"template_or_return_to_home": "or perhaps you would like to return to the",
		"template_home_page": "Home page",
		"template_or_would_you_like_some": "or would you like some",
		# start
		"template_rakontu_motto": "Helping people take good care of their stories.",
		"template_you_are_member_of": "You are a member of these Rakontus.",
		"template_you_are_invited_to": "You have been invited to join these Rakontus.",
		"template_from_google": "from Google",
		"template_must_be_logged_in": "You must be logged in to a Google account to use Rakontu.",
		"template_login": "Log in",
		"template_at_google": "at Google",
		# admin/admin
		"template_site_initialization_tasks": "Site initialization tasks",
		"template_must_be_done_before_rakontus": "Must be done before any Rakontus are created",
		"template_generate": "Generate",
		"template_default_help_resources_from": "default help resources from",
		"template_skins_from": "skins from",
		"template_sample_questions_from": "sample questions from",
		"template_help_texts_from": "short mouse-over help texts from",
		"template_have_been_created": "have been created",
		"template_can_be_done_anytime": "Can be done anytime", 
		"template_last_activity": "Last activity",
		"template_approcket_timestamp": "AppRocket time stamp",
		"template_counts": "Counts",
		"template_dates": "Dates",
		"template_first_publish": "First activity",
		"template_join_as_a": "Join as a",
		"template_confirm_inactivate": "Are you sure you want to INACTIVATE the Rakontu",
		"template_confirm_activate": "Are you sure you want to ACTIVATE the Rakontu",
		"template_confirm_remove": "Are you REALLY SURE you want to PERMANENTLY REMOVE the Rakontu",
		"template_create_another": "Create another",
		"template_admin_warning": "Please remove Rakontus VERY carefully. Deleted Rakontus cannot be recovered. It is best to back up first.",
		# admin/create rakontu - step one
		"template_create_rakontu": "Create a new Rakontu",
		"template_step_one": "Step One",
		"template_short_rakontu_name": "Please enter a short URL name for the Rakontu web link. This name cannot be changed afterward. It cannot contain spaces or special characters.",
		"template_rakontu_name_taken": "That Rakontu name is already in use. Please choose another.",
		"template_cancel_rakontu_creation": "Cancel and return to the Rakontu site administration page",
		# admin/create rakontu - step two
		"template_step_two": "Step Two",
		"template_short_name_is": "The short name (URL) chosen for this Rakontu is:",
		"template_longer_rakontu_name": "Please provide a longer name to display on the Rakontu pages.",
		"template_choose_rakontu_type": "Which of these types best represents this Rakontu?",
		"template_rakontu_owner_email": "Please enter an email address for the new Rakontu's owner. ",
		"template_back_to_first_page": "Go back to the first page",
		# curate/attachments
		"template_file_name": "File name",
		"template_no_attachments": "There are no attachments in the data set.",
		# curate/flags
		"template_flagged": "Flagged",
		"template_notify": "Notify",
		"template_flag_noun": "Flag",
		"template_flag_verb": "Flag",
		"template_unflag": "Unflag",
		"template_items_flagged_for_removal": "Items flagged for removal",
		"template_comment_only": "comment only",
		"template_entry_questions": "Entry questions",
		"template_member_questions": "Member questions",
		"template_remove_warning": "Please remove items carefully. Deleted items cannot be recovered.",
		"template_flag_comment": "Flag comment",
		"template_click_here_to_unflag": "Click here to unflag this item",
		"template_click_here_to_flag": "Click here to flag this item for removal",
		"template_click_here_to_flag_this_set_of_tags": "Click here to flag this set of tags for removal",
		"template_click_here_to_flag_this_entry": "Click here to flag this entry for removal",
		"template_click_here_to_flag_this_resource": "Click here to flag this resource for removal",
		"template_no_flagged_items_of_this_type": "There are no flagged items of this type.",
		# curate/gaps
		"template_gaps": "Gaps",
		"template_sort_by": "sorted by",
		"template_most_recent": "most recent",
		"template_most_annotated": "most annotated",
		"template_highest_activity": "highest activity",
		"template_highest_nudged": "highest nudged",
		"template_entries_with_no_tags": "with no tags",
		"template_entries_with_no_links": "with no links",
		"template_entries_with_no_comments": "with no comments",
		"template_entries_with_no_answers_to_questions": "with no answers to questions",
		"template_collages_with_no_story_links": "with no story links (collages only)",
		# curate/tags
		"template_change_entry_tags": "Change entry tags",
		"template_no_tags": "There are no tags to review.",
		"template_tags_warning": "Please make changes carefully. Deleted or changed tags cannot be recovered.",
		# guide/invitations
		"template_all_invitations": "all invitations",
		"template_only_invitations_with_no_responses": "only invitations with no responses",
		"template_invitations_with_no_responses": "Invitations with no responses",
		"template_no_invitations": "There are no invitations in the Rakontu.",
		"template_no_invitations_without_responses": "There are not invitations without responses.",
		# guide/requests
		"template_all_requests": "all",
		"template_only_uncompleted_requests": "uncompleted",
		"template_requests_of_the_type": "requests of the type",
		"template_uncompleted_requests": "Requests that have not been marked as completed",
		"template_no_requests": "There are no requests of the selected type.",
		"template_no_uncompleted_requests": "There are no uncompleted requests of the selected type.",
		# guide/resources
		"template_category": "Category",
		"template_for_new_members": "For new members",
		"template_for_managers_only": "For managers only",
		"template_no_help_resources": "This Rakontu has no help resources.",
		"template_generate_default_help_resources": "Generate all default help resources",
		# liaise/batch
		"template_batch_story_entry": "Batch story entry",
		"template_choose_csv_file_for_batch": "Choose a CSV file to import entries from",
		"template_or_enter_stories": "or enter items in the boxes below and click any of the 'Add stories' buttons.",
		"template_collected_from": "Collected from",
		"template_attributed_to": "Attributed to",
		# liaise/members
		"template_links": "Links",
		"template_view_member_page": "Member page",
		"template_change_profile": "Profile",
		"template_change_preferences": "Preferences",
		"template_take_over_offline_member": "Become this member's liaison",
		"template_switch_offline_member_liaison_to": "Transfer to",
		"template_no_active_offline_members": "There are no active off-line members at this time.",
		"template_you_have_no_offline_members": "There are no active off-line members assigned to you at this time.",
		"template_add_offline_members": "Add off-line members",
		"template_inactive_members": "Inactive members",
		# liaise/review
		"template_batch_entered_stories": "Batch entered stories",
		"template_import": "Import",
		"template_no_stories_entered": "No stories have yet been entered.",
		# manage/character
		"template_name_and_description": "Name and description",
		# manage/characters
		"template_add_new_characters": "Add new characters",
		"template_change_characters": "Change characters",
		"template_view_character_page": "View character page",
		"template_change_character": "Change character",
		"template_inactive_characters": "Inactive characters",
		# manage/export
		"template_export_to_xml": "Export to XML",
		"template_what_to_export": "Export",
		"template_if_exporting_entries_select_range": "in the range",
		"template_export_entries_with_answers" : "Export to CSV",
		# manage/first
		"template_welcome_to_new": "Welcome to your new Rakontu",
		"template_here_are_terms": "To get you started, here is a brief explanation of some important terms.",
		# manage/inactivate
		"template_or_go_back_to_settings": "or go back to the settings page",
		# manage/members
		"template_google_email": "Google account email",
		"template_membership_type": "Membership type",
		"template_available": "available",
		"template_helping_roles_taken_on": "Helping roles taken on",
		"template_helping_roles_available": "Helping roles available",
		"template_add_new_members": "Add new members",
		"template_send_invitation_email": "Send invitation email",
		"template_invitation_to_join": "Invitation to join",
		# manage/questions
		"template_add_new_questions_about": "Add new questions about",
		"template_change_questions_about": "Change questions about",
		"template_import_export_questions_about": "Import and export questions about",
		"template_name_question_explanation": "Name, question, and explanation",
		"template_min_max": "Minimum and maximum",
		"template_if_value": "if value",
		"template_if_boolean": "if boolean",
		"template_if_ordinal_or_nominal": "if ordinal or nominal",
		"template_explanation": "Explanation",
		"template_choices": "Choices",
		"template_multiple_answers_allowed": "Multiple answers allowed",
		"template_choose_csv_question_file": "Choose a CSV file to import questions from",
		"template_export_questions_to_csv": "Export questions to CSV",
		"template_copy_sample_questions_about": "Copy sample questions about",
		"template_is_of_the_type": "is of the type",
		"template_min_max_are": "Minumum and maximum values are",
		"template_a_positive_answer_is": "The text of a positive answer is", 
		"template_choices_are": "Choices are",
		"template_multiple_answers_allowed": "Multiple answers are allowed.",
		"template_explanation_is": "The explanation given is", 
		"template_inactive_questions": "Inactive questions",
		# manage/questionsList
		"template_questions_about": "Questions about",
		# manage/appearance
		"template_visual_appearance": "Visual appearance",
		"template_tag_line": "Tag line",
		"template_custom_skin": "Custom skin",
		"template_custom": "custom",
		"template_external_style_sheet": "Enter a valid CSS URL to use as an external style sheet",
		"template_halping_role_texts": "Helping role texts",
		"template_rakontu_outoing_email": "Outgoing email address",
		"template_welcome_message_for_new_members": "Welcome message for new members",
		"template_time_zones_and_time_reporting": "Time zones and time reporting",
		"template_what_time_zone_should_members_see": "What time zone should members see as the default?",
		"template_how_should_dates_display": "How should dates be displayed by default?",
		"template_how_should_times_display": "How should times be displayed by default?",
		"template_read_before_text": "read-before text",
		# manage/settings
		"template_things_members_can_do": "Things members can do",
		"template_how_many_attachments": "How many attachments are allowed per entry?",
		"template_fictional_characters": "Fictional characters",
		"template_is_entry_by_character_allowed": "Is entry via fictional character allowed for each of these entry types?",
		"template_editing": "Editing",
		"template_non_managers_editing_tags": "Should curators who are not managers be able to edit existing tags?",
		"template_yes_non_manager_curators_can_edit_tags": "Yes, curators who are not managers can edit all tags",
		"template_activity_system": "Activity system",
		"template_activity_points_per_activity": "How many activity points are added to an item based on each activity?",
		"template_nudge_system": "Nudge system",
		"template_nudge_points_per_entry": "How many nudge points can be asssigned (maximum) per entry?",
		"template_nudge_category_names_and_questions": "What should the names and questions of nudge categories be?",
		"template_how_many_nudge_points_do_member_get": "How many nudge points do members accumulate by participating in the Rakontu?",
		# visit/annotation
		"template_enter_tags": "Please enter some tags that describe this entry.",
		"template_comment_on": "Comment on",
		"template_tag_set_for": "Tag set for",
		"template_request_about": "Request about",
		"template_nudge_for": "Nudge for",
		"template_what_is_request_type": "What type of request is this?",
		"template_nudge_points_can_assign_to_entry": "Points you can assign to this entry",
		"template_nudge_points_member_has_left": "Points you have remaining",
		# visit/ask
		"template_ask_this_guide": "Ask a guide",
		"template_ask_subject": "Please summarize your question in a few words.",
		"template_ask_body": "What question would you like to ask?",
		# visit/character
		"template_about": "About",
		"template_how_to_be_character": "How to be",
		"template_see_all_characters": "See all characters",
		"template_change_this_character": "Change this character",
		"template_curate_this_characters_entries": "Curate this character's contributions",
		"template_no_character_description": "no character description",
		"template_no_character_how_to": "no how-to statement",
		"template_no_entries_or_annotations_for_character": "There are no entries or annotations that match the current selections for this character.",
		# visit/drafts
		"template_name_click_to_edit": "Name (click to edit)",
		"template_versions_click_to_use": "Previous versions (click to recall)",
		"template_your_saved_drafts": "Your saved drafts",
		"template_saved_drafts_for": "Saved drafts for",
		"template_versions": "History",
		# visit/entry
		"template_restoring_version_from": "Recalling version from",
		"template_tell_new_story": "Please tell your story here.",
		"template_describe_new_pattern": "Please describe the pattern of stories you want to make note of here.",
		"template_describe_new_collage": "Please describe your collage here.",
		"template_describe_new_invitation": "Please describe to other members what you would like them to tell stories about.",
		"template_text_for_new_resource": "Type the text of your resource here.",
		"template_please_give_name_to_your": "Please provide a descriptive name for your",
		"template_since_you_retold": "Since you created this story as your own version of",
		"template_since_you_reminded": "Since you created this story because you were reminded of it by",
		"template_since_you_responded": "Since you created this story in response to the invitation",
		"template_comment_on_retold_link": "Would you like to comment on why you retold the original story?",
		"template_comment_on_reminded_link": "Would you like to comment on what reminded you of this story?",
		"template_comment_on_responded_link": "Would you like to comment on why you responded to the invitation?",
		"template_since_this_is_a_resource": "Since this is a resource",
		"template_which_resource_options_apply": "Which of these display options apply?",
		"template_yes_is_help_resource": "This is a help resource. Link to it from the general help page.",
		"template_yes_is_new_member_resource":"This resource will be helpful to new members. Link to it from the page new members see.",
		"template_yes_manager_only_resource": "This resource is only appropriate for managers. Hide it from other members.",
		"template_load_version": "Recall text version",
		"template_stories_included_in_collage": "Stories included in this collage",
		"template_link_comment": "Link comment",
		"template_add_stories_to_the_collage": "Add stories to the collage",
		"template_no_stories_to_add_to_collage": "No stories are available to add to this collage.",
		"template_search_filters_referred_to_by_this_pattern": "Search filters referred to by this pattern",
		"template_add_search_filters_to_the_pattern": "Add search filters to the pattern",
		"template_no_shared_searches_available": "There are no shared searches available.",
		"template_accepted_file_types": "Accepted file types",
		# visit/filter
		"template_filter_name_and_comment": "Search filter name and comment",
		"template_filter_should_be_shared": "Should this filter be shared?",
		"template_keep_filter_private": "No, keep it private",
		"template_share_filter": "Yes, share it",
		"template_filter_selections": "Filter selections",
		"template_of_these_selection_criteria": "of the following selection criteria",
		"template_of_these_words_or_phrases": "of these words of phrases",
		"template_of_these_tags": "of these tags",
		# visit/filters
		"template_saved_search_filters": "Saved search filters",
		"template_apply_to_home_page": "Apply to home page",
		"template_questions_about_entries": "Questions about entries",
		"template_questions_about_members_or_characters": "Questions about members or characters",
		# visit/help
		"template_help_resources": "Help! Read about using Rakontu",
		"template_ask_a_guide": "Help! Ask a guide about your Rakontu",
		"template_no_resources_manager": "Alert: No help resources have been created for this Rakontu. As a manager, you should make sure that your Rakontu members have at least a few resources they can read to learn how to use the site.",
		"template_no_resources_non_manager": "No help resources have yet been created for this Rakontu. Please ask a Rakontu manager for help.",
		"template_generate_default_resources": "Generate site-default help resources for this Rakontu",
		"template_create_a_resource": "Create a help resource",
		"template_no_system_resources": "There should be some default help resources you can use in your Rakontu, but apparently the site administrator has not yet set them up. Contact your site administrator for help:",
		"template_support_for_rakontu": "Support request for Rakontu ",
		"template_support": "Support request",
		"template_site_support": "Site support",
		"template_guide_has_not_entered_intro": "This guide has not yet specified which sorts of questions they can answer.",
		# visit/home
		"template_time_range": "Time range",
		"template_to_time": "to", # between two parts of time range
		"template_keep_end_time_at_now": "Ending now",
		"template_show": "Show",
		"template_entry_types": "Entry types",
		"template_annotation_types": "Annotation types",
		"template_nudges": "Nudges",
		"template_filtered_by": "Filtered by",
		"template_choose_one": "choose one",
		"template_my_filters": "My filters",
		"template_shared_filters": "Shared filters",
		"template_other_options": "Other options",
		"template_nudge_floor": "Hide entries below",
		# visit/home_grid
		"template_no_search_results_header": "No search results",
		"template_no_search_results_message": "The applied search filter resulted in no entries being shown. To see entries in this space, either stop applying the search or change it so that some entries meet the search criteria.",
		"template_no_matches_header": "No matching entries",
		"template_no_match_for_selections": "No entries match the current selections.",
		"template_empty_rakontu_header": "Nothing here yet!",
		"template_empty_rakontu_message": "This Rakontu has no entries in it. Use the Create menu to add the first story or invitation.",
		# visit/leave
		"template_are_you_sure": "Are you sure?",
		"template_leaving_warning": "Are you absolutely, completely, really, totally certain that you want to leave this Rakontu? If you do, you will have to ask a manager of the Rakontu if you want to rejoin.",
		# visit/member
		"template_information_about": "Information about",
		"template_information_about_this": "Information about this",
		"template_last_entry": "Last entry",
		"template_last_annotation": "Last annotation",
		"template_last_answer": "Last answer",
		"template_last_link": "Last link",
		"template_last_reading": "Last reading",
		"template_nudge_points_accumulated": "Nudge points",
		"template_member_answers_to_questions": "Answers to member questions",
		"template_send_a_message_to": "Send a message to",
		"template_change_your_preferences": "Change your preferences",
		"template_curate_this_members_entries": "Curate this member's contributions",
		"template_curate_your_entries": "Curate your contributions",
		"template_stop_curating": "Stop curating",
		"template_no_entries_or_annotations_for_member": "There are no entries or annotations that match the current selections for this member.",
		# visit/members
		"template_make_changes_to_members": "Make changes to memberships",
		"template_send_message": "Send message",
		# visit/message
		"template_what_should_reply_to_be": "What email address should the email be sent from? (To use the Rakontu address, leave this blank.)",
		# visit/new
		"template_resources_for_new_members": "You may find these resources helpful for getting started",
		"template_about_help_icons": "Around the site you will see little icons that provide help. Either hover over them with your mouse or click on them to read them.",
		# visit/preview
		"template_with_reference_to_the": "with reference to the",
		# visit/profile
		"template_you_profile": "Your profile",
		"template_offline_member_profile": "Off-line member profile",
		"template_nickname_and_description": "Nickname and description",
		"template_your_nickname_is": "Your nickname is",
		"template_offline_members_nickname_is": "This member's nickname is",
		"template_describe_yourself": "Please describe yourself to other members.",
		"template_describe_offline_member": "Please describe this off-line member to other members.",
		# visit/nickname
		"template_change_nickname": "Change nickname",
		"template_what_nickname_do_you_want": "What nickname would you like to use in the Rakontu?",
		"template_what_nickname_for_offline_member": "What nickname do you want to use to represent this off-line member in the Rakontu?",
		"template_nickname_taken": "That nickname is already being used by someone in the Rakontu. Please choose another.",
		"template_nickname_chosen_is": "The nickname you have chosen is",
		"template_nickname_chosen_for_offline_member_is": "The nickname you have chosen for this member is",
		"template_confirm_nickname": "Please confirm that you want to use this nickname. (This will effect the appearance of all of your contributions, in the past as well as the future.)",
		"template_cancel_changing_nickname": "Cancel and return to profile page",
		# visit/preferences
		"template_do_you_want_messages": "Do you want other Rakontu members to be able to send you messages via email?",
		"template_guides_must_accept_messages": "Since you are a guide you have to accept messages so you can answer questions.",
		"template_offline_member_accept_messages": "Do you want other Rakontu members to be able to send this member messages via email? (You, as the member's liaison, will get the messages.)",
		"template_yes_people_can_send_me_messages": "Yes, people can send me messages",
		"template_yes_people_can_send_messages_through_me": "Yes, people can send this off-line member messages through me",
		"template_email_for_reply_to_in_messages": "What reply-to email address would you like to use by default for messages sent from you?",
		"template_please_add_a_picture": "Please upload a picture of yourself.",
		"template_please_add_a_picture_of_offline_member": "Please upload a picture of this off-line member.",
		"template_leave_rakontu": "To stop being a member of this Rakontu, click here.",
		"template_other_options": "Other options",
		"template_helping_roles": "Helping roles",
		"template_i_am_a": "I am a", # if this doesn't translate you can leave it blank
		"template_guide_intro_question": "If you are a guide, what would you like to tell members about what sorts of questions you can answer?",
		"template_choose_member_default_text_format": "What text format should be chosen by default when a text box is shown?",
		"template_time_zone_choice": "What time zone should be displayed?",
		"template_date_display_choice": "How should dates be displayed",
		"template_time_display_choice": "How should times be displayed?",
		"template_rakontu_created_on": "This Rakontu was created on",
		"template_inline_image_display_choice": "Do you want to see attached images on the same page as the entries they are attached to?",
		# visit/rakontu
		"template_rakontu_created_on": "This Rakontu was created on",
		"template_make_changes_to_settings": "Make changes to Rakontu-level settings",
		"template_make_changes_to_characters": "Make changes to characters",
		"template_nudge_categories": "Nudge categories",
		"template_nudge_point_accumulations": "Nudge point accumulations",
		"template_activity_point_accumulations": "Activity point accumulations",
		"template_rakontu_allows_characters_for": "This Rakontu allows fictional character attribution for",
		# visit/read
		"template_contributed_by": "Contributed by",
		"template_entered_by": "entered by",
		"template_retelling_of": "A retelling of",
		"template_reminding_from": "Told because of a reminding from",
		"template_in_response_to_invitation": "Told in response to",
		"template_included_in_collages": "Included in the collages",
		"template_what_would_you_like_to_do_next": "What would you like to do next?",
		"template_hide_versions": "Hide", # right next to button that says History no need for longer name
		"template_show_versions": "Show history",
		"template_no_annotations_for_entry": "This entry has no annotations that match the current selections.",
		# visit/readAnnotation
		"template_request_type": "Request type",
		# visit/relate
		"template_entries_related_to": "Entries related to",
		"template_incoming_or_outgoing": "Incoming or outgoing",
		"template_incoming": "incoming",
		"template_outgoing": "outgoing",
		"template_add_relations": "Add relations",
		"template_related": "Related",
		"template_add_link": "Add link",
		"template_entry_has_no_related_links": "This entry has not yet been marked as related to other entries.",
		"template_no_entries_of_this_type_to_relate_to": "There are no entries of the selected type available for this entry to relate to.",
		}

# ============================================================================================ 
# TEMPLATE BUTTON NAMES
# These are texts that appear on buttons in html forms.
# The things on the left MUST remain as they are (they match things in the template files).
# The things on the right should be translated.
# ============================================================================================ 

TEMPLATE_BUTTONS = {
		"button_change": "Change",
		"button_cancel": "Cancel",
		"button_save_changes": "Save changes",
		"button_generate": "Generate",
		"button_regenerate": "Regenerate",
		"button_add": "Add",
		
		# start
		"button_visit": "Visit",
		# admin
		"button_join": "Join",
		"button_leave": "Leave",
		"button_activate": "Activate",
		"button_inactivate": "Inactivate",
		"button_remove": "Remove",
		"button_enter_short_name": "Enter Short Name",
		"button_create_rakontu": "Create the New Rakontu",
		"button_inactivate_shorter": "Inactivate",
		# curate
		"button_make_selected_changes": "Make selected changes",
		"button_send_selected_notifications": "Send selected notifications",
		"button_change_tags": "Change tags",
		# guide
		"button_show_uncompleted_requests": "Show only uncompleted requests",
		"button_show_all_requests": "Show all requests",
		"button_set_request_uncompleted": "Set to NOT completed",
		"button_set_request_completed": "Set to completed",
		# liaise
		"button_add_stories": "Add stories",
		"button_add_more_stories": "Add more stories",
		# manage
		"button_inactivate": "Really And Truly Inactivate This Rakontu",
		"button_export_xml": "Export to XML",
		"button_export_csv": "Export to CSV",
		# visit
		"button_hide_details": "Hide details",
		"button_show_details": "Show details",
		"button_save_changes_and_return": "Save changes and return",
		"button_preview": "Preview",
		"button_save_draft": "Save draft",
		"button_save_as_draft": "Save as draft",
		"button_edit_draft": "Edit draft",
		"button_view_all_drafts": "View all drafts",
		"button_change_entry": "Change entry",
		"button_publish": "Publish",
		"button_remove_selected_drafts": "Remove selected drafts",
		"button_save_and_apply": "Save and apply",
		"button_save_as_new_search_and_apply": "Save as new search and apply",
		"button_flag": "Flag",
		"button_unflag": "Unflag",
		"button_delete": "Delete",
		"button_remove_selected_searches": "Remove selected search filters",
		"button_send_question": "Send question",
		"button_send_message": "Send message",
		"button_send_messages": "Send message to selected members",
		"button_refresh": "Refresh",
		"button_move_choices_to_bottom": "Move Choices to Bottom",
		"button_move_choices_to_top": "Move Choices to Top",
		"button_stop_applying": "Stop applying",
		"button_make_copy": "Make a copy",
		"button_create_another": "Make another",
		"button_apply": "Apply",
		"button_make_new": "Make new",
		"button_print_selection": "Print selection",
		"button_export_selection": "Export selection",
		"button_really_and_truly_leave": "Really and Truly Leave this Rakontu",
		"button_go_back_to_prefs_page": "Go Back to My Preferences Page",
		"button_return_to_list": "Return to list",
		"button_mark_as_completed": "Mark as completed",
		"button_mark_as_not_completed": "Mark as not completed",
		"button_save_new_relations": "Save new relations",
		"button_load_version": "Recall",
		"button_enter_new_nickname": "Enter New Nickname",
		}

# ============================================================================================ 
# TEMPLATE MENU NAMES
# These determine what appears on the menu that appears at the top of all pages.
# The things on the left MUST remain as they are (they match things in the template files).
# The things on the right should be translated.
# ============================================================================================ 

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
		"menu_appearance": "Appearance",
		"menu_settings": "Settings",
		"menu_questions": "Questions",
		"menu_characters": "Characters",
		"menu_export": "Export",
		# review
		"menu_my_stuff": "My stuff",
		"menu_profile": "Profile",
		"menu_preferences": "Preferences",
		"menu_filters": "Filters",
		"menu_drafts": "Drafts",
		"menu_help": "Help",
		# this appears when site admin is looking ABOVE the Rakontu level
		"menu_site_administration": "Rakontu site administration",
		}

# ============================================================================================ 
# NO ACCESS MESSAGES
# These are messages that appear if the user enters a URL for which they don't have adequate privileges.
# The things on the left MUST remain as they are (they match things in the template files).
# The things on the right should be translated.
# ============================================================================================ 

NO_ACCESS = {
		"attachments": "You are not a curator of this Rakontu and cannot review attachments. Either become a curator, or ask a curator to review any attachments you would like to be reviewed.",
		"flags": "You are not a curator or manager of this Rakontu and cannot review removal flags. Either become a curator or ask a curator or manager to make any changes you would like to see made.",
		"gaps": "You are not a curator of this Rakontu and cannot review its gaps. Please ask a curator to make any changes you would like to see made.",
		"tags_curator": "You are not a curator of this Rakontu and cannot review tags. Either become a curator or ask a curator to make any changes you would like to see made.",
		"tags_manager": "You are not a manager of this Rakontu and cannot review tags. Please ask a manager to make any changes you would like to see made.",
		"invitations": "You are not a guide of this Rakontu and cannot review invitations. Please ask a guide to make any changes you would like to see made.",
		"requests": "You are not a guide of this Rakontu and cannot review requests. Please ask a guide to make any changes you would like to see made.",
		"resources": "You are not a guide or manager of this Rakontu and cannot change its resources. Please ask a guide or manager to make any changes you would like to see made.",
		"batch": "You are not a liaison of this Rakontu and cannot import data collected offline. Either become a liaison, or ask a liaison to import any items you would like to see added.",
		"offline_members": "You are not a liaison or manager of this Rakontu and cannot change its off-line memberships. Please ask a liaison or manager to make any changes you would like to see made.",
		"batch_review": "You are not a liaison of this Rakontu and cannot import data collected offline. Either become a liaison, or ask a liaison to import any items you would like to see added.",
		"character": "You are not a manager of this Rakontu and cannot change its characters. Please ask a manager to make changes to the characters for you.",
		"characters": "You are not a manager of this Rakontu and cannot change its characters. Please ask a manager to make changes to the characters for you.",
		"export": "You are not a manager of this Rakontu (or a site administrator) and cannot export its data. Please ask a manager to export the Rakontu's data.",
		"inactivate": "You are not a manager of this Rakontu (or a site administrator) and cannot inactivate it. Please ask a manager to make any changes you would like to see made.",
		"members": "You are not a manager of this Rakontu and cannot change its memberships. Please ask a manager to make any changes you would like to see made.",
		"questions": "You are not a manager of this Rakontu and cannot change its questions. Please ask a manager to make any changes you would like to see made.",
		"settings": "You are not a manager of this Rakontu and cannot change its settings. Please ask a manager to make any changes you would like to see made.",
		}

# ============================================================================================ 
# RESULTS
# These run the page that appears when the system has something (a result) to tell the user, like "I can't find that member."
# There are three sections to each line:
#	"internal name": ("URL lookup", "text presented to user"),
# DO NOT change the internal name. 
# You can translate the URL lookup (which appears in the page URL), 
# but if you do that you must also change the lookup name in the file "result.html" in the templates directory.
# The user-presented text should be translated.
# ============================================================================================ 

RESULTS = {
		"changessaved": ("changessaved", "Your changes have been saved."),
		"messagesent": ("messagesent", "Your message has been sent."),

		"entryNotFound": ("entryNotFound", "That entry was not found."),
		"memberNotFound": ("memberNotFound", "That member was not found."),
		"membersNotFound": ("membersNotFound", "None of the specified members were found."),
		"offlineMemberNotFound": ("offlineMemberNotFound", "That off-line member was not found."),
		"helpNotFound": ("helpNotFound", "No help message was found for that item. You may want to let your site administrator know there is a problem."),

		"noEntriesToRelate": ("noEntriesToRelate", "There are no entries to which this entry can be related."),
		"noSearchResultForPrinting": ("noSearchResultForPrinting", "There is no search filter result to print. You need to apply a search filter then come back to the print page."),
		"noQuestionsToExport": ("noQuestionsToExport", " are no questions of that type to export."),
		"noSearchResultForExport": ("noSearchResultForExport", "There is no search filter result to export. You need to apply a search filter then come back to the export page."),

		"attachmentsTooLarge": ("attachmentsTooLarge", "At least one of the attachment(s) you chose are too large. The entry was saved but (at least some of) the attachments were not."),
		"offlineMemberAlreadyAnsweredQuestions": ("offlineMemberAlreadyAnsweredQuestions", "That off-line member has already answered questions about this entry."),
		"nicknameAlreadyInUse": ("nicknameAlreadyInUse", "That nickname is already in use. Please choose another."),
		"ownerCannotLeave": ("ownerCannotLeave", "You are the only owner of this Rakontu. You can't leave it until you designate at least one other member as an owner."),
		"cannotGiveUpLiaisonWithMembers": ("cannotGiveUpLiaisonWithMembers", "You cannot stop being a liaison with off-line members assigned to you. Visit the Manage off-line members page and assign your off-line members to other liaisons first."),
		"reachedMaxEntriesPerRakontu": ("reachedMaxEntriesPerRakontu", "This Rakontu already has the maximum allowed number of entries in it, and no more can be added. To add new entries, ask a manager to remove some older entries and free up some room."),
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
	"""
	<p><b>What's a Rakontu?</b></p>
	<p>It's a place where people share and use stories together.</p>
	<p>You could see it as a living-history museum of stories, as well as
	a gathering place where people build their story museum together 
	and draw from it to remember the past, understand the present
	and find solutions for the future.</p>
	""",
"not logged in": 
	"""
	<p><b>What's Rakontu?</b></p>
	<p>Rakontu is an open source software package that helps groups of people share and work 
	with stories. You can find out more about it at <a href="http://www.rakontu.org">rakontu.org</a>.
	<p>This alpha stage prototype is currently being tested.
	If you want to help with testing, join the 
	<a href="http://groups.google.com/group/rakontu-discuss">Rakontu discussion group</a>
	and ask to try out the site.</p.
	<p>(If you're wondering: Rakontu is <a href="http://en.wikipedia.org/wiki/Esperanto">Esperanto</a> for "tell a story.")</p>
	""",
"manager_first": 
	"""
	<p>
	The most important thing in a Rakontu is, of course, its <b>stories</b>. 
	But there are four other types of <b>entry</b> as well: <b>invitations</b> to tell stories,
	story <b>collages</b>, <b>patterns</b> people have observed in the stories, and <b>resources</b> that help
	people remember and understand.
	All of these things can be commented on, given descriptive tags, rated, asked questions about, and searched. 
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
"inactivate": 
	"""
	<h2>Are you sure?</h2>
	<p>Are you <b>absolutely, completely, really, totally certain</b> that you want to inactivate this Rakontu?</p>
	<p>If you do, you will have to ask your site administrator if you want to either reinstate the Rakontu or
	remove its content.</p>
	""",

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
        "MANAGE_APPEARANCE": "Manage appearance",
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
        "GUIDE": "Guide", # member nickname
        "CHARACTER": "Character", # character name
        "PREFERENCES_FOR": "Preferences for", # member nickname
        "PROFILE_FOR": "Profile for", # member nickname
        "CHANGE_NICKNAME_FOR": "Change nickname for", # member nickname
        "DRAFTS_FOR": "Drafts for", # member nickname
        "SEND_MESSAGE": "Send message",
        "LEAVE_RAKONTU": "Leave" ,
        "SEARCH_FILTER": "Search filter",
        "MESSAGE_TO_USER": "Message", # (on page that tells user something is completed or something is wrong)
        "HELP_ON": "Help on", # help topic
        "INITIALIZE_SITE": "Initialize site",
        "ERROR": "Error",
        "URL_NOT_FOUND": "URL not found",
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
    "url_profile": "profile",
    "url_preferences": "preferences",
    "url_search_filter": "filter",
    "url_member": "member",
    "url_ask": "ask",
    "url_rakontu": "rakontu",
    "url_leave": "leave",
    "url_filters": "filters",
    "url_nickname": "nickname",
    "url_message": "message",
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
    "url_print_member": "printMemberContributions",
    "url_print_character": "printCharacterContributions",
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
    "url_appearance": "appearance",
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
    "url_skins": "skins",
    # testing
    "url_make_fake_data": "make_fake_data",
    "url_stress_test": "stress_test",
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
	"url_query_version": "version",
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
	"url_query_show": "show",
	'url_query_type': "type",
	"url_query_location": "location",
	"url_query_uncompleted": "uncompleted",
	"url_query_no_responses": "noresponses",
	"url_query_curate": "curate",
	"url_query_versions": "versions",
	"url_query_result": "message",
	"url_query_help": "help",
	"url_query_help_type": "type",
	"url_query_bookmark": "bookmark",
	"url_query_name_taken": "name_taken",
	}

