# based on http://github.com/straup/gae-flickrapp/tree/master
import logging
import os
import time
import cgi

from google.appengine.ext.webapp import template

from FlickrApp import FlickrApp
from config import config

TEMPLATE_BASE="" # set from main

class FlickrProblem(Exception):
    pass

class FlickrgramApp (FlickrApp) :
    def __init__ (self) :
        FlickrApp.__init__(self, config['flickr_apikey'], config['flickr_apisecret'])
        self.config = config
        self.min_perms = config['flickr_minperms']
    
    def search(self, page):
        if not page:
            page = 1
        extras = "date_upload,date_taken,owner_name,icon_server,geo,path_alias"
        result = self.proxy_api_call("flickr.photos.getContactsPhotos", {
            "auth_token":self.user.token,
            "count":30, # can't paginate beyond this, alas
            "include_self":1,
            "extras":extras,
        }, ttl=120)

        logging.info("got data %s"%result)

        if not result["stat"] == "ok":
            logging.error("error response: %r"%result)
            raise FlickrProblem(result["message"])
            
        photos = result["photos"]["photo"]
        
        now = time.time()
        for photo in photos:
            ago = int( time.time() - int(photo["dateupload"]) )
            photo["ago"] = self.simplify(ago)

        return photos
        

    def simplify(self,ago):
        days = 0
        hours = 0
        minutes = 0
        seconds = ago
        
        if seconds > 60:
            minutes = seconds / 60
            seconds = seconds % 60
        
        if minutes > 60:
            hours = minutes / 60
            minutes = minutes % 60
        
        if hours > 24:
            days = hours / 24
            hours = hours % 24
        
        if days > 1:
            return "%s days ago"%days
        elif days or hours >= 20:
            return "yesterday"
        elif hours > 1:
            return "%s hours ago"%hours
        elif hours:
            return "an hour ago"
        elif minutes > 1:
            return "%s minutes ago"%minutes
        elif minutes:
            return "one minute ago"
        elif seconds > 10:
            return "%s seconds ago"%seconds
        else:
            return "just now"
        
    
    def render(self, name, params):
        path = os.path.join(TEMPLATE_BASE, name)
        self.response.out.write(template.render(path, params))
        return


class MainApp(FlickrgramApp) :

    def get (self) :
        if not self.check_logged_in(self.min_perms) :
            return self.render("login.html", locals())
        
        try:
            photos = self.search(1)
        except FlickrProblem, error:
            pass
        
        crumb = self.generate_crumb(self.user, 'logout')
        
        return self.render("index.html", locals())
    




# In Flickr-speak this is the "callback" URL that the user
# is redirected to once they have authed your application.

class TokenDance (FlickrgramApp) :

    def get (self):

        try :

            new_users = True
            self.do_token_dance(allow_new_users=new_users)
            
        except FlickrApp.FlickrAppNewUserException, e :
            self.response.out.write('New user signups are currently disabled.')

        except FlickrApp.FlickrAppAPIException, e :
            self.response.out.write('The Flickr API is being cranky.')

        except FlickrApp.FlickrAppException, e :
            self.response.out.write('Application error: %s' % e)
      
        except Exception, e:
            self.response.out.write('Unknown error: %s' % e)



# This is where you send a user to sign in. If they are not
# already authed then the application will take care generating
# Flickr Auth frobs and other details.

class Signin (FlickrgramApp) :
    
    def get (self) :
        if self.check_logged_in(self.min_perms) :
            self.redirect("/")
            
        self.do_flickr_auth(self.min_perms, '/')

# This is where you send a user to log them out of your
# application. The user may or may not still be logged in to
# Flickr. Note how we're explictly zero-ing out the cookies;
# that should probably be wrapped up in a helper method...

class Signout (FlickrgramApp) :

    def post (self) :

        if not self.check_logged_in(self.min_perms) :
            self.redirect("/")

        crumb = self.request.get('crumb')

        if not crumb :
            self.redirect("/")
            
        if not self.validate_crumb(self.user, "logout", crumb) :
            self.redirect("/")

        self.response.headers.add_header('Set-Cookie', 'ffo=')
        self.response.headers.add_header('Set-Cookie', 'fft=')    
        
        self.redirect("/")
    
