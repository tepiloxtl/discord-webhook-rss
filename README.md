# discord-webhook-rss

Simple RSS feed to Discord webhook reposter. Requires `feedparser discord-webhook lxml` from pypi. Add your feeds to feeds.py and your webhooks to webhooks.py as in included examples. Additional key "title" can be added to feed in feeds.py to override default feed title/webhook name.

Run as a service or in screen or something

Setting DEBUG to True will print out contents of the feed as seen by feedparser to file, and prevent updating last feed item timestamp

Ideas for improvement: let user define their own embed fields in the config file