#!/usr/bin/python

# ============================================================================================ 
# RAKONTU
# Description: Rakontu is open source story sharing software.

# License: GPL 3.0
# Google Code Project: http://code.google.com/p/rakontu/ 
# ============================================================================================ 
# These are configuration options for the Rakontu utility restore.py.
# Change these things to suit your situation.
# ============================================================================================ 

# The directory where it can find your restore files
RESTORE_DIR = "/Users/cfkurtz/Documents/work_new/Rakontu project/test backup restore"

# The application ID (the part before appspot.com) for your GAE application
APP_ID = "rakontu"

# The server name - localhost:8080 or APP_ID.appspot.com - BE CAREFUL !!
#SERVER_NAME = APP_ID + '.appspot.com'
SERVER_NAME = 'localhost:8080'

# Your authentication details
USER_NAME = "cfkurtz@cfkurtz.com" # CHANGE THESE - THEY WON'T WORK FOR YOU !!!
USER_EMAIL = 'cfkurtz@cfkurtz.com'
AUTH_DOMAIN = 'cfkurtz.com' # this is the part of the email after the @

# ============================================================================================ 
# HARDLY EVER CHANGED
# ============================================================================================ 

# Change this if you are using a different language config file than english.
CONFIG_LANGUAGE_DIR = "../config/english"

# How long to wait between database hits - the shorter the faster, but the more impact on a site in use
SLEEP_TIME_SECONDS = 0.5