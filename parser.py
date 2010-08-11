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
    feeds = Session.query(Feed.id).all()
    Session.close()
    for feed in feeds:
        parse_one(feed.id)

def parse_one(id):
    Session = session()

    feed = Session.query(Feed).filter_by(id=id).one()
    parser = feedparser.parse(feed.url)

    updated = parser.feed.get('updated_parsed', None) \
            or parser.feed.get('date_parsed', None)
    if updated:
        updated = dt.fromtimestamp(mktime(updated))

    if updated and feed.updated == updated:
        return # already up to date

    for post in parser.entries:
        pubdate = post.get('published_parsed', None) \
                or post.get('date_parsed', None)
        pubdate = pubdate and dt.fromtimestamp(mktime(pubdate)) or dt.utcnow()

        updated = post.get('updated_parsed', None)
        updated = updated and dt.fromtimestamp(mktime(updated))

        try:
            p = Session.query(Post).filter(
                    Post.entry_id == post.id and
                    Post.feed_id == feed.id).one()

            if not updated or p.updated == updated:
                continue
        except NoResultFound:
            p = Post()
            feed.posts.append(p)
        p.read = False
        p.entry_id = post.id
        p.title = post.title
        p.link = post.link
        p.author = parser.feed.get('author', 'None')
        p.published = pubdate
        p.updated = updated
        p.summary = post.get('summary', '')

    feed.updated = updated
    Session.commit()
    Session.close()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        parse_all()
    else:
        parse_one(sys.argv[1])

