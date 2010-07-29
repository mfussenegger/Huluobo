#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from sqlalchemy import desc
from base import Base
from schema import Session, Feed, Post
from datetime import datetime
import time
import feedparser

class Index(Base):
    def get(self):
        posts = Session.query(Post).filter_by(read=False).order_by(desc(
                    Post.published)).all()
        return self.render('index.html', posts=posts)

class FeedDelete(Base):
    # TODO: rewrite to post or better: delete (if that is possible?)
    def get(self, id):
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
        for post in Session.query(Post).filter_by(read=False).all():
            post.read = True
        Session.commit()
        self.redirect('/')
        return

class Refresh(Base):
    def get(self):
        for lfeed in Session.query(Feed).all():
            d = feedparser.parse(lfeed.url)
            if d.feed.has_key('updated_parsed'):
                rfeed_updated = datetime.fromtimestamp(time.mktime(
                    d.feed.updated_parsed))
            elif d.feed.has_key('date_parsed'):
                rfeed_updated = datetime.fromtimestamp(time.mktime(
                    d.feed.date_parsed))
            else:
                rfeed_updated = None

            if rfeed_updated and lfeed.updated == rfeed_updated:
                continue
            for rpost in d.entries:
                if rpost.has_key('updated_parsed'):
                    rpost_updated = datetime.fromtimestamp(time.mktime(
                        rpost.updated_parsed))
                elif rpost.has_key('date_parsed'):
                    rpost_updated = datetime.fromtimestamp(time.mktime(
                        rpost.date_parsed))
                else:
                    rpost_updated = None

                if hasattr(rpost, 'published_parsed'):
                    rpost_published = datetime.fromtimestamp(time.mktime(
                        rpost.published_parsed))
                else:
                    rpost_published = datetime.now()

                lpost = Session.query(Post).filter(
                            Post.entry_id == rpost.id).filter(
                                    Post.feed_id == lfeed.id).first()
                if lpost:
                    if rpost_updated and lpost.updated == rpost_updated:
                        continue
                else:
                    lpost = Post()
                    Session.add(lpost)
                lpost.read = False
                lpost.feed_id = lfeed.id
                lpost.entry_id = rpost.id
                lpost.title = rpost.title
                lpost.author = d.feed.get('author', '')
                lpost.link = rpost.link
                lpost.published = rpost_published
                lpost.updated = rpost_updated
                lpost.summary = rpost.get('summary')
                lpost.content = rpost.has_key('content') and \
                    rpost.content[0].value
            lfeed.updated = rfeed_updated
        Session.commit()
        self.redirect('/')
        return
