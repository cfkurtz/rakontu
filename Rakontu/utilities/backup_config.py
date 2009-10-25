#!/usr/bin/python

# ============================================================================================ 
# RAKONTU
# Description: Rakontu is open source story sharing software.

# License: GPL 3.0
# Google Code Project: http://code.google.com/p/rakontu/ 
# ============================================================================================ 
# These are configuration options for the Rakontu utility backup.py.
# Change these things to suit your particular restoration.
# ============================================================================================ 

# The application ID (the part before appspot.com) for your GAE application
APP_ID = "rakontu"

# The server name - localhost:8080 or APP_ID.appspot.com - BE CAREFUL !!
#SERVER_NAME = APP_ID + '.appspot.com'
SERVER_NAME = 'localhost:8080'

# Your authentication details
USER_NAME = "cfkurtz@cfkurtz.com" # CHANGE THESE - THEY WON'T WORK FOR YOU !!!
USER_EMAIL = 'cfkurtz@cfkurtz.com'
AUTH_DOMAIN = 'cfkurtz.com' # this is the part of the email after the @

# Where to put the backup XML files
BACKUP_DIR = "/Users/cfkurtz/Documents/work_new/Rakontu project/test backup restore"

# ============================================================================================ 
# HARDLY EVER CHANGED
# ============================================================================================ 

# Whether to restrict member access to the Rakontu while backing it up. STRONGLY recommended.
# If this is turned off (zero), people using the Rakontu might change it while you are backing it up.
RESTRICT_ACCESS_WHILE_BACKING_UP = 1

# The message the backup program sets on your Rakontu when you are backing it up.
ACCESS_MESSAGE = "Backing up ..."

# Change this if you are using a different language config file than english.
CONFIG_LANGUAGE_DIR = "../config/english"

# How long to wait between database hits - the shorter the faster, but the more impact on a site in use
SLEEP_TIME_SECONDS = 0.25

