
from atproto import AtUri, models
from atproto_client import Client
import json
import os

#from post_data import PostData

def perform_get_skeets(client: Client):
    latest = []
    # try:
    posts = client.app.bsky.feed.post.list(client.me.did,limit=10)
    for uri, post in posts.records.items():
        print("retrieving post - uri : " + uri)
        #likes = self.find_skeet_likes(account, token, uri)
        latest.append({'uri' : uri, 'txt':post.text}) #, 'likes':likes})
    # except Exception as e: print(e)
    return latest


def find_single_skeet(client: Client, uri):
    return client.app.bsky.feed.post.get(client.me.did, AtUri.from_str(uri).rkey)


def create_skeet(client: Client, skeet_text):
    post_record = models.AppBskyFeedPost.Record(text=skeet_text,
                                                created_at=client.get_current_time_iso())
    new_post = client.app.bsky.feed.post.create(client.me.did, post_record)
    print("Created new skeet with the text : " + post_record.text + " : the new uri :" + new_post.uri)
    uri = new_post.uri
    return uri


def delete_skeet(client: Client, uri: str):
    print("Deleting the post at the uri : " + uri)
    deleted_post = client.app.bsky.feed.post.delete(client.me.did, AtUri.from_str(uri).rkey)
    print(deleted_post)


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


def find_skeet_likes(client: Client, uri: str):
    count = 0
    print("Calling feed.post.get")
    likes = client.app.bsky.feed.get_likes(params = {'uri': uri, 'limit': 10})
    like_list = likes['likes']
    for like in like_list:
        count = count + 1
        print("likes : " + str(like))
    return count


def create_follower_json(client: Client, account: str):
    follows = get_follow_authors(client, account)
    for author in follows:
        print("author :" + str(author))
    #create json output file of followers
    filename = 'frequency.json'
    try:
        os.remove(filename)
    except OSError:
        pass
    print("writing followers list to jason file")
    with open(filename, 'w') as f:
        json.dump(follows, f, indent=4)


class Driver:
    """
        class to wrap methods for generating output files after parsing
        """

    def get_deleted(self, client: Client):
        pass
        # print("calling get deleted posts")
        # driver_object.get_deleted(account, token)

