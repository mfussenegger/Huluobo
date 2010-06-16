#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from base import Base
from schema import Session, Feed, Post
from datetime import datetime
import time
import feedparser

class Index(Base):
    def get(self):
        return self.render('index.html')

class Refresh(Base):
    def get(self):
        for feed in Session.query(Feed).all():
            d = feedparser.parse(feed.url)
            if d.feed.updated_parsed == feed.updated:
                continue
            for post in d.entries:
                db_post = Session.query(Post).filter(
                        Post.entry_id == post.id).first()
                if db_post:
                    if db_post.updated == post.updated_parsed:
                        continue
                    db_post.read = False
                else:
                    db_post = Post()
                db_post.feed_id = feed.id
                db_post.entry_id = post.id
                db_post.title = post.title
                db_post.author = d.feed.author
                db_post.link = post.link
                db_post.published = datetime.fromtimestamp(
                        time.mktime(post.published_parsed))

                db_post.updated = datetime.fromtimestamp(
                        time.mktime(post.updated_parsed))

                db_post.summary = post.summary
                db_post.content = post.content[0]['value']
                Session.add(db_post)
        Session.commit()
        self.redirect('/')
        return
