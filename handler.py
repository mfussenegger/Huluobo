#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from base import Base
from schema import Session, Feed

class Index(Base):
    def get(self):
        return self.render('index.html')
