from consts import *

# Replication URL - change this to URL corresponding your application
ROCKET_URL = "http://www.rakontu.net/rocket"
#ROCKET_URL = "http://localhost:8080/rocket"

SECRET_KEY = "rakontu"

CURRENT_MODE = RECEIVE

ROCKET_ENTITIES = {
# Define entities that you want to be replicated here.
	"Rakontu": {MODE: CURRENT_MODE, TIMESTAMP_FIELD: "appRocketTimeStamp"}, 
	"Question": {MODE: CURRENT_MODE, TIMESTAMP_FIELD: "appRocketTimeStamp"}, 
	"Member":  {MODE: CURRENT_MODE, TIMESTAMP_FIELD: "appRocketTimeStamp"},
	"ViewOptions": {MODE: CURRENT_MODE, TIMESTAMP_FIELD: "appRocketTimeStamp"},
	"PendingMember":   {MODE: CURRENT_MODE, TIMESTAMP_FIELD: "appRocketTimeStamp"},
	"Character": {MODE: CURRENT_MODE, TIMESTAMP_FIELD: "appRocketTimeStamp", TABLE_NAME:"RakontuCharacter"},
	"SavedSearch": {MODE: CURRENT_MODE, TIMESTAMP_FIELD: "appRocketTimeStamp"}, 
	"SavedSearchQuestionReference":  {MODE: CURRENT_MODE, TIMESTAMP_FIELD: "appRocketTimeStamp"},
	"Answer":  {MODE: CURRENT_MODE, TIMESTAMP_FIELD: "appRocketTimeStamp"}, 
	"Entry":  {MODE: CURRENT_MODE, TIMESTAMP_FIELD: "appRocketTimeStamp"},
	"Link":  {MODE: CURRENT_MODE, TIMESTAMP_FIELD: "appRocketTimeStamp"},
	"Attachment":  {MODE: CURRENT_MODE, TIMESTAMP_FIELD: "appRocketTimeStamp"},
	"Annotation":  {MODE: CURRENT_MODE, TIMESTAMP_FIELD: "appRocketTimeStamp"}, 
	"TextVersion": {MODE: CURRENT_MODE, TIMESTAMP_FIELD: "appRocketTimeStamp"},
	# Helps are not synchonized
	# Exports are not synchronized
	}

# Example:
{"NotAComment": {},
"Comment": {EMBEDDED_LIST_FIELDS: ["list2"]},

# This is simplest format  where Comment and NotAComment are names of entities in AppEngine application.

# Optionally you can also provide few configuration parameters for each entity, for example like this:
#    "EntityName": {
#        MODE: RECEIVE, 
#        TIMESTAMP_FIELD: "t", 
#        TABLE_NAME: "test2", 
#        RECEIVE_FIELDS: ["prop1", "prop2"]
#    },

# Here's a full list of supported configuration parameters:
#    MODE: replication mode, possible values are:
#        RECEIVE_SEND: first replicate from AppEngine to MySql and then from Mysql to AppEngine. If some properties
#                      are replicated both ways and there is a replication conflict (entity has been updated
#                      in both MySql and AppEngine since last replication), AppEngine changes will overwrite
#                      MySql changes.
#        SEND_RECEIVE: first replicate from MySql to AppEngine and then from AppEngine to MySql. If some properties
#                      are replicated both ways and there is a replication conflict, MySql changes will overwrite
#                      AppEngine changes.
#        RECEIVE:      only replicate given entity from AppEngine to MySql, changes in MySql are ignored
#        SEND:         only replicate given entity from MySql to AppEngine, changes in AppEngine are ignored
#
#    TABLE_NAME: name of the table for this entity in MySQL, by default it's the same as AppEngine entity name
# 
#    TIMESTAMP_FIELD: name of the timestamp property for this entity, by default "timestamp". 
#                     Each entity that needs to be replicated must have a timestamp property, 
#                     defined in AppEngine model like this: timestamp = db.DateTimeProperty(auto_now=True). 
#                     In MySql timestamp field is created using data type TIMESTAMP.
# 
#    TABLE_KEY_FIELD: name of MySql table column that stores entity key id or name, by default "k".
#
#    RECEIVE_FIELDS: list of properties that are replicated from AppEngine to MySql. If omitted, all properties are replicated.
#
#    SEND_FIELDS: list of properties that are replicated from MySql to AppEngine. If omitted, all properties are replicated.
#
#    EMBEDDED_LIST_FIELDS: list of properties that will be stored in single TEXT column in MySql as |-separated list. By 
#                          default lists are stored in a separate table (with one to many relationship). Values of embedded lists 
#                          will always be stored a string values in AppEngine. 
}

BATCH_SIZE = 150

# MYSQL DATABASE CONFIGURATION
DATABASE_HOST = "localhost"
#DATABASE_NAME = "rakontu_local"
DATABASE_NAME = "rakontu"
DATABASE_USER = "approcket"
DATABASE_PASSWORD = "approcket"
DATABASE_PORT = 3306
DATABASE_ENGINE = "InnoDB"

#LOGGING CONFIGURATION
import logging, sys
LOG_LEVEL = logging.DEBUG

# DAEMON CONFIGURATION 
# This provides configuration for running AppRocket replicator (station.py) in daemon mode 
# (using -d command-line switch).
LOGFILE = '/var/log/approcket.log'
PIDFILE = '/var/run/approcket.pid'
GID = 103
UID = 103

IDLE_TIME = 10 # idle time in seconds after no more updates are pending, for daemon (-d) and loop modes (-s) 