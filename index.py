#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import tornado.web
import tornado.httpserver
import tornado.ioloop
import tornado.options
from tornado.options import define, options

from jinja2 import Environment, FileSystemLoader
from os.path import dirname, join, isfile

from base import NoDestinationHandler
from handler import (Index, Refresh, MarkAsRead)

define('port', default=8080, help='run on the given port', type=int)

class Application(tornado.web.Application):
    def __init__(self):
        static_path = join(dirname(__file__), 'static')
        
        handlers = (
                (r'/', Index)
                ,(r'/refresh/?', Refresh)
                ,(r'/mark_as_read/?', MarkAsRead)
                ,(r'/static/(.*)', tornado.web.StaticFileHandler,
                    { 'path' : static_path })
                ,(r'/.*$', NoDestinationHandler)
            )
        settings = dict(
                title = 'Huluobo',
                debug = isfile(join(dirname(__file__), 'debug')),
                xsrf_cookies = True,
                static_path = static_path,
            )

        template_path = join(dirname(__file__), 'templates')
        tornado.web.Application.__init__(self, handlers, **settings)
        self.env = Environment(loader=FileSystemLoader(template_path)
                ,extensions=['jinja2.ext.i18n'])
        self.env.install_null_translations(newstyle=True)
        self.env.globals['cfg'] = settings


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    print('Starting Tornado on port %d' % options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()
