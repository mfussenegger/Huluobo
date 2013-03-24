#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado.web import asynchronous
from tornado import gen

from sqlalchemy import desc
from base import Base
from schema import Session, Feed, Post
from datetime import datetime as dt
from datetime import timedelta

from config import max_post_age

from parser import parse_all_with_callback


class Index(Base):
    def get(self):
        posts = Session.query(Post).filter_by(read=False).order_by(
            desc(Post.published))
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
    @asynchronous
    @gen.engine
    def get(self):
        Session.query(Post).filter(
            Post.updated <= dt.now() - timedelta(days=max_post_age)).delete()
        feeds = Session.query(Feed.id).all()
        Session.close()
        __ = yield gen.Task(parse_all_with_callback, (f.id for f in feeds))
        return self.redirect('/')
