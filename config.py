#!/usr/bin/env python
# -*- coding: utf-8 -*- 

### SqlAlchemy Connection

## 'mysql://foo:bar@localhost/fubar'
## 'postgres://foo:bar@localhost/fubar'
## 'oracle://foo:bar@localhost/fubar'
## 'mssql://foo:bar@mydsn'

## 'sqlite:///relative_path.db'
## 'sqlite:////absolute/path/to/foo.db'

#url = 'sqlite:///:memory:'
url = 'sqlite:///foo.db'
params = {
        'echo' : False,
        #'encoding' : 'latin1',
}

cookie_secret = 'asdf892'
max_post_age = 30
