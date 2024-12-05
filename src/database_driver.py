import sqlalchemy as sa
from sqlalchemy import MetaData, Table, select, insert, update, func
from sqlalchemy.orm import declarative_base, sessionmaker
from configparser import ConfigParser
from post_data import PostData
import datetime
import os
config = ConfigParser()
script_dir = os.path.dirname(os.path.abspath(__file__))
config_file_path = os.path.join(script_dir, "..//settings.ini")
config.read(config_file_path)
author = config.get('main-section', 'account')
database_name = config.get('main-section', 'database_name')
database_con = 'sqlite:///' + database_name
# Create an engine to connect to the database
engine = sa.create_engine(database_con)

# Reflect the database metadata
metadata = MetaData()
metadata.reflect(bind=engine)

# Create a base class for declarative models
Base = declarative_base()

# Define a table
class Post(Base):
    __tablename__ = 'posts'
    id = sa.Column(sa.Integer, primary_key=True)
    author = sa.Column(sa.String)
    uri = sa.Column(sa.String)
    txt = sa.Column(sa.String)
    queued = sa.Column(sa.Boolean)
    queue_datetime = sa.Column(sa.DateTime)

# Create the table in the database
Base.metadata.create_all(engine)

def select_posts_table():
    # Access the table you want to query
    table_name = 'posts'  # Replace 'your_table' with the actual table name
    table = Table(table_name, metadata, autoload_with=engine)

    # Construct the select statement
    stmt = select(table)

    # Execute the query and fetch results
    with engine.connect() as conn:
        result = conn.execute(stmt)
        for row in result:
            print("row : " + str(row))

print("Table query executing")
select_posts_table()

def populate_dummy_posts():
    pass
    # Session = sessionmaker(bind=engine)
    # session = Session()
    # print("adding a post")
    # date_time = datetime.datetime(2024, 12, 2, 11, 11, 11)
    # new_post = Post(author=author, uri='3X', txt='3VVV' , queued=True, queue_datetime=date_time)
    # session.add(new_post)
    # session.commit()

def get_next_post_index():
    # Create a session
    Session = sessionmaker(bind=engine)
    session = Session()
    # Find the maximum value in the 'value' column
    max_value = session.query(func.max(Post.id)).scalar()
    return max_value

def get_future_posts():
    # Create a session
    Session = sessionmaker(bind=engine)
    session = Session()
    # Execute a query and get the results as objects
    posts = session.query(Post).all()
    post_list = []
    for post in posts:
        # print("one row object")
        # print(post.id, post.uri, post.author, post.txt, post.queued, post.queue_datetime)
        post_list.append({'id':str(post.id), 'uri':str(post.uri), 'author':str(post.author), 'txt':str(post.txt), 'queued':str(post.queued), 'time':str(post.queue_datetime)})
        #post_list.append(post)
    session.close()
    return post_list

def insert_scheduled_post(new: PostData):
    print("insert_scheduled_post Task contains : " + str(new))
    index = get_next_post_index() + 1
    print("index for insertion : " + str(index))
    #post = Post(author=new.author, uri=new.uri, txt=new.txt, queued=True, queue_datetime=new.queue_datetime)
    user_table = Table('posts', metadata,
        id=sa.Column(sa.Integer, primary_key=True),
        author = sa.Column(sa.String),
        uri = sa.Column(sa.String),
        txt = sa.Column(sa.String),
        queued = sa.Column(sa.Boolean),
        queue_datetime = sa.Column(sa.DateTime)
    )
    # Insert a single row
    with engine.begin() as conn:
        stmt = insert(user_table).values(author=new.author, uri=new.uri, txt=new.txt, queued=True, queue_datetime=new.queue_datetime)
        conn.execute(stmt)
    return True

def update_scheduled_post(edit: PostData):
    # Create a session
    Session = sessionmaker(bind=engine)
    session = Session()

    user_table = Table('posts', metadata,
        id=sa.Column(sa.Integer, primary_key=True),
        author = sa.Column(sa.String),
        uri = sa.Column(sa.String),
        txt = sa.Column(sa.String),
        queued = sa.Column(sa.Boolean),
        queue_datetime = sa.Column(sa.DateTime)
    )

    date_string = str(edit.queue_datetime)
    format_string = "%Y-%m-%d %H:%M:%S"
    # Convert string to datetime object
    datetime_object = datetime.datetime.strptime(date_string, format_string)

    posts = session.query(Post).filter_by(id=edit.id).first()
    if posts:
        posts.author=edit.author
        posts.uri=edit.uri
        posts.txt=edit.txt
        posts.queued=bool(edit.queued)
        posts.queue_datetime=datetime_object
        session.commit()
    return True




