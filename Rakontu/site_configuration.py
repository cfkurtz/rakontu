# --------------------------------------------------------------------------------------------
# RAKONTU
# Description: Rakontu is open source story sharing software.
# Version: pre-0.1
# License: GPL 3.0
# Google Code Project: http://code.google.com/p/rakontu/
# --------------------------------------------------------------------------------------------

# --------------------------------------------------------------------------------------------
# ON CHANGING THESE VALUES
# --------------------------------------------------------------------------------------------
# These site constants determine some aspects of the behavior of all community sites
# created in this Rakontu installation. You can of course change the source code of Rakontu itself, 
# but these constants are those the most amenable to change without architectural changes to the source code. 
# They have been placed here mainly as a convenience to the site administrator.
#
# Warning: This file uses Python syntax. You should be comfortable editing Python code before you edit this file.
#
# BACKUP THIS FILE before you make changes!
# --------------------------------------------------------------------------------------------

# --------------------------------------------------------------------------------------------
# MEMBERS
# --------------------------------------------------------------------------------------------

# This is what members are called before they have set themselves a nickname.
NO_NICKNAME_SET = "No nickname set"

# The community contact email is the email address used as the SENDER in all email sent FROM the Rakontu.
# This appears as the default in the community settings.
# It MUST be a valid email address.
DEFAULT_CONTACT_EMAIL = "support@rakontu.org"

# --------------------------------------------------------------------------------------------
# BROWSING
# --------------------------------------------------------------------------------------------

# These are the time frames shown in the main "Look at stories" browser window.
# You can remove time frames from this list, but you cannot change them or add any. 
# (They must match other names in the system.)
# However, depending on your community one or two of these may not apply (perhaps minutes or years).
TIME_FRAMES = ["minute", "hour", "day", "week", "month", "year"]

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

# --------------------------------------------------------------------------------------------
# ARTICLES
# --------------------------------------------------------------------------------------------

# This is the title given to articles which are not titled by their creators.
DEFAULT_UNTITLED_ARTICLE_TITLE = "Untitled"

# These are the accepted attachment file types. You can add or remove any types here.
# However, these two lists MUST match up exactly (by order).
# Lists of MIME types can be found here:
# http://www.iana.org/assignments/media-types/
# http://www.w3schools.com/media/media_mimeref.asp
ACCEPTED_ATTACHMENT_FILE_TYPES = ["jpg", "png", "pdf", "doc", "txt", "mpg", "mp3", "html", "zip"]
ACCEPTED_ATTACHMENT_MIME_TYPES = ["image/jpeg", "image/png", "application/pdf", "application/msword", "text/plain", "video/mpeg", "audio/mpeg", "text/html", "application/zip"]

# This is the name given to questions not named by their creators.
DEFAULT_QUESTION_NAME = "Unnamed question"

# --------------------------------------------------------------------------------------------
# NUDGE SYSTEM
# --------------------------------------------------------------------------------------------

# The number of nudge categories. This must be set to at least one.
NUM_NUDGE_CATEGORIES = 5

# The default nudge category names that come up in community settings. 
# The number of strings in this list MUST match the number of categories above.
DEFAULT_NUDGE_CATEGORIES = ["appropriate", "important", "useful to new members", "useful for resolving conflicts", "useful for understanding"]

# How many nudge points can be assigned per article, by default.
DEFAULT_MAX_NUDGE_POINTS_PER_ARTICLE = 25

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

# How many activity points articles gain through each of these events.
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

# --------------------------------------------------------------------------------------------
# HELPING ROLES
# --------------------------------------------------------------------------------------------

# These appear in each member's profile page, in the section where they are deciding whether 
# to take on each of the helping roles. You can add site-specific information here.
DEFAULT_ROLE_READMES = [
"""
A curator pays attention to the community's accumulated data. Curators add information, check for problems, create links, 
and in general maintain the vitality of the story bank.""",

"""
A guide pays attention to the on-line human community. Guides answer questions, write tutorials, 
encourage people to tell and use stories, create patterns, write and respond to invitations,
and in general maintain the vitality of the on-line member community.
""",

"""
A liaison guides stories and other information over the barrier between on-line and off-line worlds. 
Liaisons conduct external interviews and add the stories people tell in them, read stories to people and gather 
comments, nudges, and other annotations, and in general make the system work for both on-line and off-line community members.
"""]

# These are the formats in which the default role readmes (above) are to be interpreted.
# Available options are "plain text", "simple HTML", and "Wiki markup" ONLY.
DEFAULT_ROLE_READMES_FORMATS = ["plain text", "plain text", "plain text"]







