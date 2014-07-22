DEBUG = True
DEBUG_WITH_APTANA = False

JSON_SORT_KEYS = False

SECRET_KEY = 'p7i0-22@0eheas^kzw3=1qfug_x+5)5)8u4v=2iyiwwx1eh)37'

OPENID_FOLDER = '/home/rsgadmin/cache/portal/openID'
DATABASE_URI = 'sqlite:///' + OPENID_FOLDER + '/user_storage.db'
SHAPEFILE_PATH = '/home/thomass/temp/' #Complete Path to shapefile folder. Needs to begin and end with a /


LOG_LEVEL = "DEBUG"
# This path needs changing according to local server configuration
# Leave as empty if you want the log to be in the same place as the .wsgi
LOG_PATH = ''

# The error level of logging into the database
# E for errors only or W for warnings too
ERROR_LEVEL = "W"

# The URL of the openID relying party
OPENID_RP_URL = 'http://opec-portal-test:8585/openid-server/provider/discovery/gis-portal'

ACTION_REGISTRY = [
    {   'actionIdentifier' : 'userInfoAction',
        'actionDescription' : 'display user info',
        'jQueryCriteria' : [
            {'tag': 'label', 'attributes' : {'for' : 'userInfoToggleBtn'}}  # --> label[for='userInfoToggleBtn']
            ],
        'allowedUserGroups' : ['admins']
    },
    {
        'actionIdentifier' : 'shapefile',
        'actionDescription' : 'use shapefile features',
        'jQueryCriteria' : [
            {'tag': 'label', 'attributes' : {'for' : 'shapefile_button'}},
            {'id': 'shapefile_chooser'},
            {'id': 'shapename_chooser'}
        ],
        'allowedUserGroups' : ['admins']
    }
]

JAVA_HOME = '/opt/java'
JDK_HOME = '/opt/java'
PATH_extension = JAVA_HOME + '/bin'
LD_LIBRARY_PATH_extension = JDK_HOME + '/jre/lib/amd64/server'
BEAM_HOME = '/home/thomass/beam-5.0'