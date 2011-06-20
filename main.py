#!/usr/bin/env python
import os
import wsgiref.handlers
from google.appengine.ext import webapp

import Flickrgram

Flickrgram.TEMPLATE_BASE = os.path.join(os.path.dirname(__file__), "templates")


if __name__ == '__main__':

  handlers = [
    ('/', Flickrgram.MainApp),
    ('/signout', Flickrgram.Signout),
    ('/signin', Flickrgram.Signin),    
    ('/auth', Flickrgram.TokenDance),
    ]

  application = webapp.WSGIApplication(handlers, debug=True)
  wsgiref.handlers.CGIHandler().run(application)
