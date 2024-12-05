"""
test_api_func.py contains pytest tests for api wrapper functions.
pytest discovers tests named "test_*".
Each function in this module is a test case.
"""

import pytest
from src.api_driver import Driver
from src.client_wrapper import ClientWrapper
from configparser import ConfigParser
import asyncio
import os
import time
from tkinter import PhotoImage
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
test_profile_uri = config.get('test-section', 'test_profile_uri')
followers_json_file = config.get('main-section', 'followers_json_file')
following_json_file = config.get('main-section', 'following_json_file')
test_image_path = config.get('test-section', 'test_image_path')
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
    follows = Driver().get_followers(client, account)
    assert len(follows)

def test_find_following():
    following = Driver().get_following(client, account)
    assert len(following)

def test_json_followers():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(Driver().create_follower_json(client, account, followers_json_file))
    file_path = followers_json_file
    assert os.path.isfile(file_path), f"File not found: {file_path}"

def test_json_following():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(Driver().create_following_json(client, account, following_json_file))
    file_path = following_json_file
    assert os.path.isfile(file_path), f"File not found: {file_path}"

def test_get_latest():
    skeet_list = Driver().perform_get_skeets(client)
    assert len(skeet_list)

def test_get_thread():
    thread_count = Driver().find_skeet_thread(client, thread_uri)
    assert thread_count != 0

def test_get_thread():
    thread_count = Driver().find_skeet_thread(client, threadless_uri)
    assert thread_count == 0

def test_get_profile_data():
    test_profile = Driver().get_profile_data(client, test_profile_uri)
    assert test_profile is not None

@pytest.mark.skip(reason="This test should only be run manually as all tests posting to the profile account")
def test_post_with_image():
    """
    Test for posting a skeet with an image attachment
    :return: true if successful post
    """
    text = "This image was a test post via atproto API. I try to run tests during the lightest traffic time of day on BlueSky, and test posts are deleted automatically. Apologies if you're a human looking at this."
    print("posting with image : " + test_image_path + " : " + text)
    post_status = Driver().post_with_image(client, text, test_image_path)
    assert post_status

