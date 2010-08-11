#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import sys
import feedparser

from datetime import datetime as dt
from time import mktime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

from config import url, params
from schema import Feed, Post

session = sessionmaker(create_engine(url, **params))

def parse_all():
    Session = session()
    for feed in Session.query(Feed):
        parse_one(feed.id)

def parse_one(id):
    Session = session()

    feed = Session.query(Feed).filter_by(id=id).one()
    print feed.title
    parser = feedparser.parse(feed.url)

    updated = parser.feed.get('updated_parsed', None) \
            or parser.feed.get('date_parsed', None)
    if updated:
        updated = dt.fromtimestamp(mktime(updated))

    if updated and feed.updated == updated:
        return # already up to date

    feed.updated = updated

    for post in parser.entries:
        pubdate = post.get('published_parsed', None) \
                or post.get('date_parsed', None)
        pubdate = pubdate and dt.fromtimestamp(mktime(pubdate)) or dt.utcnow()

        updated = post.get('updated_parsed', None)
        updated = updated and dt.fromtimestamp(mktime(updated)) or pubdate

        try:
            p = Session.query(Post).filter(
                    Post.entry_id == post.id and
                    Post.feed_id == feed.id).one()

            if p.updated == updated:
                return
        except NoResultFound:
            p = Post()
            feed.posts.append(p)
        p.read = False
        p.entry_id = post.id
        p.title = post.title
        p.link = post.link
        p.author = parser.feed.get('author', 'None')
        p.published = pubdate
        p.updated == updated
        p.summary = post.get('summary', '')

    Session.commit()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        parse_all()
    else:
        parse_one(sys.argv[1])

