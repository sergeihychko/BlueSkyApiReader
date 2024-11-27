from configparser import ConfigParser
import os
import apidriver
import json

account = ""
token = ""
default_limit = 0
application_title = ""
database_name = ""

# load configuration options
print("loading config")
config = ConfigParser()
script_dir = os.path.dirname(os.path.abspath(__file__))
config_file_path = os.path.join(script_dir, "settings.ini")
# Use the config file
config.read(config_file_path)
account = config.get('main-section', 'account')
token = config.get('main-section', 'api_token')
default_limit = config.get('main-section', 'default_limit')

application_title = config.get('main-section', 'application_title')
database_name = config.get('main-section', 'database_name')
print("calling api driver :" + account + ":" + token + ":" + default_limit)
driver_object = apidriver.Driver()
driver_object.perform_get_skeets(account, token, default_limit)

# print("calling get deleted posts")
# driver_object.get_deleted(account, token)

follows = driver_object.get_follow_authors(account, token, account)
# for author in follows:
#     print("author :" + str(author))
#create json output file of followers
filename = 'frequency.json'
try:
    os.remove(filename)
except OSError:
    pass
print("writing followers list to jason file")
with open(filename, 'w') as f:
    json.dump(follows, f, indent=4)

print("ending TEST DRIVER")
#testing git branch

def create_follows_file():
    follows = driver_object.get_follow_authors(account, token, account)
    # for author in follows:
    #     print("author :" + str(author))

    # create json output file of followers
    filename = 'frequency.json'
    try:
        os.remove(filename)
    except OSError:
        pass
    print("writing followers list to jason file")
    with open(filename, 'w') as f:
        json.dump(follows, f, indent=4)