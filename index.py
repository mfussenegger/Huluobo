#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import tornado.web
import tornado.httpserver
import tornado.ioloop
import tornado.options
from tornado.options import define, options

from jinja2 import Environment, FileSystemLoader
from os.path import dirname, join, isfile

from base import NoDestinationHandler

from handler import (Index, Refresh, MarkAsRead, FeedAdd, FeedEdit, FeedDelete)
from config import cookie_secret

define('port', default=8080, help='run on the given port', type=int)


class Application(tornado.web.Application):
    def __init__(self):
        static_path = join(dirname(__file__), 'static')

        handlers = (
            (r'/', Index),
            (r'/feeds/edit/([0-9]+)/?', FeedEdit),
            (r'/feeds/delete/([0-9]+)/?', FeedDelete),
            (r'/feeds/add/?', FeedAdd),
            (r'/refresh/?', Refresh),
            (r'/mark_as_read/?', MarkAsRead),
            (r'/static/(.*)',
             tornado.web.StaticFileHandler,
             {'path': static_path}),
            (r'/.*$', NoDestinationHandler)
        )
        settings = dict(
            title='Huluobo',
            debug=isfile(join(dirname(__file__), 'debug')),
            xsrf_cookies=True,
            static_path=static_path,
            cookie_secret=cookie_secret
        )

        template_path = join(dirname(__file__), 'templates')
        tornado.web.Application.__init__(self, handlers, **settings)
        self.env = Environment(loader=FileSystemLoader(template_path),
                               extensions=['jinja2.ext.i18n'])
        self.env.install_null_translations(newstyle=True)
        self.env.globals['cfg'] = settings


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port, '0.0.0.0')
    print('Starting Tornado on http://localhost:%d/' % options.port)
    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == '__main__':
    main()
