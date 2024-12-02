"""
test_api_func.py contains pytest tests for api wrapper functions.
pytest discovers tests named "test_*".
Each function in this module is a test case.
"""

import pytest
from src.api_driver import Driver
from src.client_wrapper import ClientWrapper
from configparser import ConfigParser
import os
import time
from atproto_client import Client

config = ConfigParser()
script_dir = os.path.dirname(os.path.abspath(__file__))
config_file_path = os.path.join(script_dir, "..//settings.ini")
config.read(config_file_path)
account = config.get('test-section', 'test_account')
token = config.get('test-section', 'test_api_token')
default_limit = config.get('main-section', 'default_limit')
test_likes_uri = config.get('test-section', 'test_likes_uri')
test_get_uri = config.get('test-section', 'test_thread_uri')
thread_uri = config.get('test-section', 'test_thread_uri')
threadless_uri = config.get('test-section', 'test_get_uri')
client_wrapper = ClientWrapper(account, token)
client = client_wrapper.init_client()


#Test get likes
def test_likes():
    """
    Test the wrapper for the get_likes() function
    """
    like_count = 999
    like_count = Driver().find_skeet_likes(client, test_likes_uri)
    print("Number of likes : " + str(like_count))
    if like_count == 0:
        assert False
    else:
        assert True

def test_get():
    post = Driver().find_single_skeet(client, test_get_uri)
    assert len(post.value.text) > 0

@pytest.mark.skip(reason="The test affects the test account, so by default it should be skipped.")
def test_delete():
    """
    Test creating a new skeet, query the skeet, then delete the skeet
    """
    new_skeet_uri = Driver().create_skeet(client, "This a test skeet using an api call. It will be deleted momentarily")
    print("sleep for 5.....")
    time.sleep(5)
    Driver().find_single_skeet(client, new_skeet_uri)
    time.sleep(5)
    print("sleep for 5.....")
    Driver().delete_skeet(client, new_skeet_uri)

def test_find_followers():
    follows = Driver().get_follow_authors(client, account)
    assert len(follows)

def test_json_followers():
    Driver().create_follower_json(client, account)
    path = '..//frequency.json'
    try:
        check_file = os.path.isfile(path)
        assert True
    except:
        print("JSON file not found")
        assert False

def test_get_latest():
    skeet_list = Driver().perform_get_skeets(client)
    assert len(skeet_list)

def test_get_thread():
    thread_count = Driver().find_skeet_thread(client, thread_uri)
    assert thread_count != 0

def test_get_thread():
    thread_count = Driver().find_skeet_thread(client, threadless_uri)
    assert thread_count == 0



