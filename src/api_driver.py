
from atproto import AtUri, models
from atproto_client import Client
import asyncio
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
    def get_follow_authors(client: Client, author: str):
        print(" fetching all the followers of an author")
        cursor = None
        follows = []
        while True:
            fetched = client.app.bsky.graph.get_follows(params={'actor': author, 'cursor': cursor})
            follows = follows + fetched.follows
            if not fetched.cursor:
                break
            cursor = fetched.cursor
        unique_authors = list(set(post.handle for post in follows))
        return unique_authors

    @staticmethod
    async def create_follower_json(client: Client, author: str):
        follows = Driver().get_follow_authors(client, author)
        for author in follows:
            print("author :" + str(author))
        # create json output file of followers
        filename = 'frequency.json'
        try:
            os.remove(filename)
        except OSError:
            pass
        print("writing followers list to jason file")
        with open(filename, 'w') as f:
            json.dump(follows, f, indent=4)

    @staticmethod
    def find_skeet_thread(client: Client, uri: str):
        count = 0
        print("Calling feed.post.get")
        threads = client.app.bsky.feed.get_post_thread(params={'uri': uri})
        replies = threads.thread.replies
        print("thread" + str(replies))
        for reply in replies:
            count = count + 1
        return count

    def get_deleted(self, client: Client):
        pass
        # print("calling get deleted posts")
        # driver_object.get_deleted(account, token)

