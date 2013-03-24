#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import feedparser
import logging
import requests

from concurrent import futures
from datetime import datetime as dt
from time import mktime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import url, params
from schema import Feed, Post

session = sessionmaker(create_engine(url, **params))
logger = logging.getLogger('huluobo')


def parse_all():
    Session = session()
    feeds = Session.query(Feed.id).all()
    Session.close()
    for feed in feeds:
        parse_one(feed.id)


def parse_all_with_callback(ids, callback):
    with futures.ProcessPoolExecutor() as executor:
        executor.map(parse_one, ids, timeout=5)
    callback()


def parse_one(id):
    Session = session()

    logger.debug('Query feed %s', id)
    feed = Session.query(Feed).get(id)
    logger.debug('Parse feed %s: %s', id, feed.url)
    resp = requests.get(feed.url, timeout=2)
    parser = feedparser.parse(resp.content)
    logger.debug('Got %s posts', len(parser.entries))

    updated = (parser.feed.get('updated_parsed', None)
               or parser.feed.get('date_parsed', None))
    if updated:
        updated = dt.fromtimestamp(mktime(updated))

    if updated and feed.updated == updated:
        logger.debug('Feed %s already up-to-date. Exit', feed.title)
        return  # already up to date

    logger.debug('Query already fetched posts')
    fetched_ids = tuple((p.id for p in parser.entries if hasattr(p, 'id')))
    query = Session.query(Post).filter(Post.feed_id == feed.id)
    posts = query.filter(Post.entry_id.in_(fetched_ids)).all()
    logger.debug('%s posts are already in the database', len(posts))
    posts = {post.entry_id: post for post in posts}

    for post in parser.entries:
        if not hasattr(post, 'id'):
            logger.debug('Post has no attribute id %s', post)
            continue
        pubdate = (post.get('published_parsed', None)
                   or post.get('date_parsed', None))
        pubdate = pubdate and dt.fromtimestamp(mktime(pubdate)) or dt.utcnow()

        updated = post.get('updated_parsed', None)
        updated = updated and dt.fromtimestamp(mktime(updated))

        try:
            p = posts[post.id]
            if not updated or p.updated == updated:
                continue
            logger.debug('Updating post %s', post.title)
        except (KeyError, AttributeError):
            logger.debug('Creating new post %s', post.title)
            p = Post()
            feed.posts.append(p)
        p.read = False
        p.entry_id = post.id
        p.title = post.title[:400]
        p.link = post.link
        p.author = parser.feed.get('author', 'None')[:80]
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
