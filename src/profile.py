import datetime
from dataclasses import dataclass

@dataclass
class ProfileData:
    displayName: str
    description : str
    avatar_uri : str
    banner_uri : str
    followersCount : int
    followsCount : int
    postsCount : int
    createdAt : datetime