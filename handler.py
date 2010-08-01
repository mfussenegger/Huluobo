#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from sqlalchemy import desc
from base import Base
from schema import Session, Feed, Post
from datetime import datetime as dt
from datetime import timedelta
from time import mktime, sleep
try:
    from multiprocessing import Process, Lock
except ImportError:
    print('multiprocessing not found: fallback to threading')
    from threading import Thread as Process, Lock

import feedparser

from config import max_post_age

class Index(Base):
    def get(self):
        posts = Session.query(Post).filter_by(read=False).order_by(desc(
                    Post.published))
        return self.render('index.html', posts=posts)

class FeedDelete(Base):
    # TODO: rewrite to post or better: delete (if that is possible?)
    def get(self, id):
        # sqlite won't cascade-delete the posts
        Session.query(Post).filter_by(feed_id=id).delete()
        Session.query(Feed).filter_by(id=id).delete()
        Session.commit()
        return self.redirect('/')

class FeedEdit(Base):
    def get(self, id):
        feed = Session.query(Feed).filter_by(id=id).one()
        return self.render('feed_edit.html', feed=feed)

    def post(self, id):
        feed = Session.query(Feed).filter_by(id=id).one()
        feed.title = self.get_argument('name')
        feed.url = self.get_argument('url')
        Session.commit()
        return self.redirect('/')

class FeedAdd(Base):
    def get(self):
        return self.render('feed_add.html')

    def post(self):
        name = self.get_argument('name')
        url = self.get_argument('url')
        feed = Feed()
        feed.title = name
        feed.url = url
        Session.add(feed)
        Session.commit()
        return self.render('index.html')

class MarkAsRead(Base):
    def get(self):
        for post in Session.query(Post).filter_by(read=False):
            post.read = True
        Session.commit()
        self.redirect('/')
        return

def parse_feed(lock ,session, lfeed):
    d = feedparser.parse(lfeed.url)
    rfeed_updated = d.feed.get('updated_parsed', None) or \
            d.feed.get('date_parsed', None)
    if rfeed_updated:
        rfeed_updated = dt.fromtimestamp(mktime(rfeed_updated))

    if rfeed_updated and lfeed.updated == rfeed_updated:
        return
    for rpost in d.entries:
        rpost_pubd = rpost.get('published_parsed', None)
        rpost_pubd = rpost_pubd and dt.fromtimestamp(mktime(
            rpost.published_parsed)) or dt.now()

        rpost_updated = rpost.get('updated_parsed', None) or \
                rpost.get('date_parsed', None)

        if rpost_updated:
            rpost_updated = dt.fromtimestamp(mktime(rpost_updated))

        lpost = session.query(Post).filter(
                    Post.entry_id == rpost.id and 
                    Post.feed_id == lfeed.id).with_lockmode("update").first()
        if lpost:
            if lpost.updated == rpost_updated:
                continue
        else:
            lpost = Post()
            lfeed.posts.append(lpost)
        lpost.read = False
        lpost.entry_id = rpost.id
        lpost.title = rpost.title
        lpost.author = d.feed.get('author', 'unknown')
        lpost.link = rpost.link
        lpost.published = rpost_pubd
        lpost.updated = rpost_updated
        lpost.summary = rpost.get('summary')
        lpost.content = rpost.has_key('content') and \
            rpost.content[0].value
    lfeed.updated = rfeed_updated
    session.commit()

class Refresh(Base):
    def get(self):
        Session.query(Post).filter(Post.updated <=
                dt.now() - timedelta(days=max_post_age) ).delete()
        Session.commit()
        procs = []
        lock = Lock()
        for lfeed in Session.query(Feed):
            p = Process(target=parse_feed, args=(lock, Session, lfeed))
            p.start()
            if not hasattr(p, 'is_alive'):
                p.is_alive = p.isAlive
            procs.append(p)
        while any( p.is_alive() for p in procs):
            sleep(0.05)
        return self.redirect('/')
