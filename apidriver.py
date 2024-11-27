
from atproto import AtUri, Client, models
from configparser import ConfigParser
import os

class Driver:
    """
        class to wrap methods for generating output files after parsing
        """

    def perform_get_skeets(self, account, token, limit):
        client = Client()
        client.login(account, token)

        posts = client.app.bsky.feed.post.list(client.me.did, limit=10)
        for uri, post in posts.records.items():
            print("retrieving post - uri : " + uri)
            print(uri, post.text)


    def get_deleted(self, account, token):
        client = Client()
        client.login(account, token)
        # deleted_post = client.app.bsky.feed.post.delete(client.me.did, AtUri.from_str(new_post.uri).rkey)
        # print(deleted_post)



        # post = client.app.bsky.feed.post.get(client.me.did, AtUri.from_str(uri).rkey)
        # print(post.value.text)
        #
        # post_record = models.AppBskyFeedPost.Record(text='test record namespaces',
        #                                             created_at=client.get_current_time_iso())
        # new_post = client.app.bsky.feed.post.create(client.me.did, post_record)
        # print(new_post)

    def find_single_skeep(self, account, token, uri):
        client = Client()
        client.login(account, token)
        print("Calling feed.post.get")
        post = client.app.bsky.feed.post.get(client.me.did, AtUri.from_str(uri).rkey)
        print("Post text : " + post.value.text)

    def create_skeet(self, account, token, skeet_text):
        client = Client()
        client.login(account, token)
        post_record = models.AppBskyFeedPost.Record(text=skeet_text,
                                                    created_at=client.get_current_time_iso())
        new_post = client.app.bsky.feed.post.create(client.me.did, post_record)
        print("Created new skeet with the text : " + post_record.text + " : the new uri :" + new_post.uri)
        uri = new_post.uri
        return uri

    def delete_skeet(self, account, token, uri):
        client = Client()
        client.login(account, token)
        print("Deleting the post at the uri : " + uri)
        deleted_post = client.app.bsky.feed.post.delete(client.me.did, AtUri.from_str(uri).rkey)
        print(deleted_post)

    def get_follow_authors(self, account, token, author):
        print(" fetching all the followers of an author")
        client = Client()
        client.login(account, token)
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

