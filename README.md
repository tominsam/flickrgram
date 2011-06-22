## flickrgram

Instagram gives you a single, very very simple, view on the photos of your friends - a flat list in upload order. This is a quick hack that emulates a similar thing for your flickr photostream - just stuff your contacts have uploaded, in order. Formatted for iPhone.


## Running flickrgram


Check out gae-flickrapp and flickrgram next to each other:

```
git clone git://github.com/tominsam/flickrgram.git
git clone git://github.com/tominsam/gae-flickrapp.git
```

Copy config.py.template to config.py:

```
cd flickrgram
cp config.py.template config.py
```

Edit config.py to have your flickr keys in it. The auth response url for the flickr keys wants to be `http://localhost:8080/auth` for local development.

Run flickrgram using Google app engine:

```
dev_appserver.py .
```


