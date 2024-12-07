
from atproto import AtUri, models
from atproto_client import Client
import asyncio
from profile import ProfileData
import json
import os

from atproto_client.request import Response


#from post_data import PostData

class Driver:
    """
        class to wrap methods for generating output files after parsing
        """

    @staticmethod
    def perform_get_skeets(client: Client):
        latest = []
        # try:
        posts = client.app.bsky.feed.post.list(client.me.did, limit=100)
        for uri, post in posts.records.items():
            print("retrieving post - uri : " + uri)
            latest.append({'txt': post.text, 'time': post.created_at, 'uri': uri})
        # except Exception as e: print(e)
        return latest

    @staticmethod
    def find_single_skeet(client: Client, uri):
        return client.app.bsky.feed.post.get(client.me.did, AtUri.from_str(uri).rkey)

    @staticmethod
    def create_skeet(client: Client, skeet_text):
        post_record = models.AppBskyFeedPost.Record(text=skeet_text,
                                                    created_at=client.get_current_time_iso())
        new_post = client.app.bsky.feed.post.create(client.me.did, post_record)
        print("Created new skeet with the text : " + post_record.text + " : the new uri :" + new_post.uri)
        uri = new_post.uri
        return uri

    @staticmethod
    def delete_skeet(client: Client, uri: str):
        print("Deleting the post at the uri : " + uri)
        deleted_post = client.app.bsky.feed.post.delete(client.me.did, AtUri.from_str(uri).rkey)
        print(deleted_post)

    @staticmethod
    def find_skeet_likes(client: Client, uri: str):
        count = 0
        print("Calling feed.post.get")
        likes = client.app.bsky.feed.get_likes(params={'uri': uri, 'limit': 10})
        like_list = likes['likes']
        for like in like_list:
            count = count + 1
            print("likes : " + str(like))
        return count

    @staticmethod
    def get_following(client: Client, author: str):
        cursor = None
        following = []
        while True:
            fetched = client.app.bsky.graph.get_follows(params={'actor': author, 'cursor': cursor})
            following = following + fetched.follows
            if not fetched.cursor:
                break
            cursor = fetched.cursor
        following_list = []
        for actor in following:
            following_list.append({'name': actor.display_name, 'handle': actor.handle, 'description': actor.description, 'avatar' :actor.avatar})
        return following_list

    @staticmethod
    async def create_following_json(client: Client, author: str, filename):
        following = Driver().get_following(client, author)
        try:
            print("attempting to remove file : " + filename)
            os.remove(filename)
        except OSError:
            pass
        print("writing following list to jason file len: " + str(len(following)))
        with open(filename, 'w') as f:
            json.dump(following, f, indent=4)
        print("file : " + filename + " : finished")

    @staticmethod
    def get_followers(client: Client, author: str):
        cursor = None
        followers = []
        while True:
            fetched = client.app.bsky.graph.get_followers(params={'actor': author, 'cursor': cursor})
            followers = followers + fetched.followers
            if not fetched.cursor:
                break
            cursor = fetched.cursor
        followers_list = []
        for actor in followers:
            followers_list.append({'name': actor.display_name, 'handle': actor.handle, 'description': actor.description,
                                   'avatar': actor.avatar})
        return followers_list

    @staticmethod
    async def create_follower_json(client: Client, author: str, filename):
        followers = Driver().get_followers(client, author)
        try:
            print("attempting to remove file : " + filename)
            os.remove(filename)
        except OSError:
            pass
        print("writing follows list to jason file len: " + str(len(followers)))
        with open(filename, 'w') as f:
            json.dump(followers, f, indent=4)
        print("file : " + filename + " : finished")

    @staticmethod
    def find_skeet_thread(client: Client, uri: str):
        count = 0
        threads = client.app.bsky.feed.get_post_thread(params={'uri': uri})
        replies = threads.thread.replies
        print("thread" + str(replies))
        for reply in replies:
            count = count + 1
        return count

    @staticmethod
    def get_profile_data(client: Client, profile_uri: str):
        print("retrieving date for profile :" + profile_uri)
        p = client.get_profile(actor=profile_uri)
        profile_obj = ProfileData(p.display_name, p.description, p.avatar, p.banner, int(p.followers_count),
                                  int(p.follows_count), p.posts_count, p.created_at)
        return profile_obj

    def get_deleted(self, client: Client):
        pass
        # print("calling get deleted posts")
        # driver_object.get_deleted(account, token)

    @staticmethod
    def post_with_image(client: Client, post_text: str, image_path: str):
        print("image path inside post_with_image is : " + image_path)
        status = True
        # Post with an image
        try:
            with open(image_path, 'rb') as f:
                img_data = f.read()
                client.send_image(text=post_text, image=img_data, image_alt="Teat image description")
        except:
            print("Failure posting with image")
            status = False
        return status
