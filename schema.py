#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from sqlalchemy import (create_engine, MetaData, Table, Column, Integer,
        String, ForeignKey, Unicode, DateTime, UnicodeText, Boolean)
from sqlalchemy.orm import mapper, scoped_session, sessionmaker, relation
from datetime import datetime
from config import url, params

engine = create_engine(url, **params)
Session = scoped_session(sessionmaker(engine))
metadata = MetaData()

feeds_table = Table('feeds', metadata
        ,Column('id', Integer, primary_key=True, autoincrement=True)
        ,Column('title', Unicode(40), nullable=False)
        ,Column('url', String(2038), nullable=False)
        ,Column('updated', DateTime, nullable=True)
        ,Column('description', Unicode(300))
    )

class Feed(object):
    pass

posts_table = Table('posts', metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('feed_id', ForeignKey('feeds.id'), nullable=False),
        Column('entry_id', String(300), nullable=False),
        Column('title', Unicode(80), nullable=False),
        Column('link', String(2038), nullable=False),
        Column('author', Unicode(40), nullable=False),
        Column('summary', UnicodeText),
        Column('content', UnicodeText),
        Column('read', Boolean, default=False),
        Column('published', DateTime, nullable=False),
        Column('updated', DateTime, nullable=True),
    )

class Post(object):
    pass

tags_table = Table('tags', metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('slug', String(20), nullable=False),
        Column('name', Unicode(20), nullable=False),
    )

class Tag(object):
    pass

feedtags_table = Table('feedtags', metadata,
        Column('feed_id', ForeignKey('feeds.id'), primary_key=True),
        Column('tag_id', ForeignKey('tags.id'), primary_key=True),
    )

posttags_table = Table('posttags', metadata,
        Column('post_id', ForeignKey('posts.id'), primary_key=True),
        Column('tag_id', ForeignKey('tags.id'), primary_key=True),
    )

mapper(Feed, feeds_table, properties={
    'posts' : relation(Post,
        backref='feed',
        cascade='all, delete, delete-orphan')
    })
mapper(Post, posts_table)
mapper(Tag, tags_table)

def main():
    if raw_input('Type YES to drop and recreate all tables: ') == 'YES':
        metadata.drop_all(engine)
        print('Dropped tables.')
        metadata.create_all(engine)
        print('Created tables.')
    else:
        print('Do nothing.')


if __name__ == '__main__':
    main()
