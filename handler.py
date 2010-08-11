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

from config import max_post_age

from parser import parse_one

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
        Session.close()
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
        Session.close()
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
        Session.close()
        return self.redirect('/')

class Refresh(Base):
    def get(self):
        Session.query(Post).filter(Post.updated <=
                dt.now() - timedelta(days=max_post_age) ).delete()
        feeds = Session.query(Feed.id).all()
        Session.close()
        procs = []
        for feed in feeds:
            p = Process(target=parse_one, args=(feed.id,))
            p.start()
            if not hasattr(p, 'is_alive'):
                p.is_alive = p.isAlive
            procs.append(p)
        while any( p.is_alive() for p in procs):
            sleep(0.05)
        return self.redirect('/')
