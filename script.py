import feedparser, pprint, time, json, textwrap, lxml.html
from lxml.cssselect import CSSSelector
from threading import Thread
from discord_webhook import DiscordWebhook, DiscordEmbed
from feeds import feeds
from webhooks import webhooks

DEBUG = False

lastupdatedfile = open("lastupdated.json", "a+", encoding="utf-8")
lastupdatedfile.seek(0)
try:
    lastupdated = json.load(lastupdatedfile)
except:
    lastupdated = {}
lastupdatedfile.close()
print(lastupdated)

def dothething(feeds, webhooks):
    lastupdatedupdated = False
    newposts = {}
    for feedname, feeddata in feeds.items():
        newposts[feedname] = []
        print(str(feedname) + ": getting feed")
        feed = feedparser.parse(feeddata["url"])
        if "title" not in feeddata:
            feeds[feedname]["title"] = str(feed["feed"]["title"])
        if feedname not in lastupdated:
            print(str(feedname + " not on the list, adding xd"))
            lastupdated[feedname] = time.mktime(feed["entries"][0]["published_parsed"])
            lastupdatedupdated = True
        if DEBUG == True:
            f=open(feedname + ".txt", "w+", encoding="utf-8")
            pprint.PrettyPrinter(depth=16, stream=f). pprint(feed)
            f.close()
        for post in feed["entries"]:
            entrytime = time.mktime(post["published_parsed"])
            if entrytime > lastupdated[feedname]:
                newposts[feedname].append(post)
    for feedname, posts in newposts.items():
        print(str(feedname) + ": reading new items")
        if len(posts) == 0:
            continue
        newtime = time.mktime(posts[0]["published_parsed"])
        print("Setting new timestamp for " + str(feedname) + " to " + str(newtime))
        lastupdated[feedname] = newtime
        if DEBUG == False:
            lastupdatedupdated = True
    if lastupdatedupdated == True:
        lastupdatedupdated = False
        lastupdatedfile = open("lastupdated.json", "w+", encoding="utf-8")
        json.dump(lastupdated, lastupdatedfile, ensure_ascii=False)
        lastupdatedfile.close()
    for item in webhooks:
        for feed in webhooks[item]["feeds"]:
            print(len(newposts[feed]))
            if len(newposts[feed]) == 0:
                continue
            for post in newposts[feed]:
                if "content" in post:
                        content = post["content"][0]["value"]
                elif "summary" in post:
                        print(str(post["link"]) + " has no content, using summary")
                        content = post["summary"]
                else:
                        print(str(post["link"]) + " has no content or summary, blanking")
                        content = ""
                webhook = DiscordWebhook(url=webhooks[item]["url"], username=feeds[feed]["title"], rate_limit_retry=True)
                embed = DiscordEmbed(title=str(post["title"]), description=textwrap.shorten(lxml.html.fromstring(content).text_content(), width=500, placeholder="..."))
                embed.set_url(url=str(post["link"]))
                embed.set_author(name=str(post["author"]))
                embed.set_timestamp()
                #TODO: No, rewrite it lmao
                try:
                        if len(CSSSelector("img")(lxml.html.fromstring(post["content"][0]["value"]))) != 0:
                                embed.set_image(url=CSSSelector("img")(lxml.html.fromstring(post["content"][0]["value"]))[0].get("src"))
                except:
                        print(str(post["link"]) + " post content has no image link")
                if "media_thumbnail" in post:
                        print(str(post["link"]) + " has no content image, using media_thumbnail")
                        embed.set_image(str(post["media_thumbnail"][0]["url"]))
                webhook.add_embed(embed)
                response = webhook.execute()

while True:
    Thread(target=dothething, args=(feeds, webhooks)).start()
    time.sleep(600)
