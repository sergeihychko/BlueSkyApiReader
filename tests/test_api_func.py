"""
test_api_func.py contains pytest tests for api wrapper functions.
pytest discovers tests named "test_*".
Each function in this module is a test case.
"""

import pytest
from src import apidriver
from configparser import ConfigParser
import os

config = ConfigParser()
script_dir = os.path.dirname(os.path.abspath(__file__))
config_file_path = os.path.join(script_dir, "..//settings.ini")
config.read(config_file_path)
account = config.get('test-section', 'test_account')
token = config.get('test-section', 'test_api_token')
driver_object = apidriver.Driver()

#Test get likes
def test_likes():
    like_count =999
    test_likes_uri = "at://did:plc:7taofukbj2iy22gshmk562iu/app.bsky.feed.post/3lbvimzsix22p"
    like_count = driver_object.find_skeet_likes(account, token, test_likes_uri)
    if like_count == 999:
        assert False
    else:
        assert True

def test_get():
    test_get_uri = "at://did:plc:7taofukbj2iy22gshmk562iu/app.bsky.feed.post/3lbvimzsix22p"
    post = driver_object.find_single_skeet(account, token, test_get_uri)
    assert len(post.value.text) > 0
