#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from tornado.web import RequestHandler, HTTPError
from schema import Session
from jinja2 import TemplateNotFound

class Base(RequestHandler):
    @property
    def env(self):
        return self.application.env

    def get_error_html(self, status_code, **kwargs):
        try:
            self.render('error/%s.html' % status_code)
        except TemplateNotFound:
            try:
                self.render('error/50x.html', status_code=status_code)
            except TemplateNotFound:
                self.write('epic fail')
                Session.close()

    def render(self, template, **kwds):
        template = self.env.get_template(template)
        self.env.globals['static_url'] = self.static_url
        self.env.globals['xsrf_form_html'] = self.xsrf_form_html
        self.write(template.render(kwds))
        Session.close()

class NoDestinationHandler(Base):
    def get(self):
        raise HTTPError(404)
